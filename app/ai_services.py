from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from . import calculations, models, schemas
from .settings import Settings


DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
SUPPORTED_INGEST_TARGETS = {"recurring_cost", "subscription_contract", "loan", "income_source"}


class AIProviderUnavailableError(RuntimeError):
    pass


class AIProviderResponseError(RuntimeError):
    pass


class StrictModel(BaseModel):
    class Config:
        extra = "forbid"


class AnalysisStructuredOutput(StrictModel):
    answer_markdown: str


class IngestStructuredSuggestion(StrictModel):
    target_entity_type: Literal["recurring_cost", "subscription_contract", "loan", "income_source"]
    title: str
    rationale: str
    confidence: float | None
    proposed_json: str
    uncertainty_notes: list[str]


class IngestStructuredOutput(StrictModel):
    detected_kind: Literal["bank_copy_paste", "subscription_contract", "invoice_or_bill", "financial_note", "unknown"]
    summary: str
    guidance: list[str]
    suggestions: list[IngestStructuredSuggestion]


def _require_openai(settings: Settings) -> None:
    if settings.openai_api_key:
        return
    raise AIProviderUnavailableError(
        "OpenAI är inte konfigurerat. Sätt OPENAI_API_KEY i .env innan AI-ytorna används."
    )


def _base_url(settings: Settings) -> str:
    return (settings.openai_base_url or DEFAULT_OPENAI_BASE_URL).rstrip("/")


def _usage_from_response(body: dict[str, Any]) -> schemas.AIUsageRead | None:
    usage = body.get("usage")
    if not usage:
        return None
    return schemas.AIUsageRead(
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        total_tokens=usage.get("total_tokens"),
    )


def _extract_output_text(body: dict[str, Any]) -> str:
    for item in body.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"]
    raise AIProviderResponseError("OpenAI svarade utan läsbar text.")


def _force_openai_strict(schema: dict[str, Any]) -> dict[str, Any]:
    if schema.get("type") == "object":
        properties = schema.get("properties", {})
        schema["required"] = list(properties.keys())
        schema["additionalProperties"] = False
        for child in properties.values():
            if isinstance(child, dict):
                _force_openai_strict(child)
    items = schema.get("items")
    if isinstance(items, dict):
        _force_openai_strict(items)
    for key in ("anyOf", "allOf", "oneOf"):
        for child in schema.get(key, []):
            if isinstance(child, dict):
                _force_openai_strict(child)
    for child in schema.get("$defs", {}).values():
        if isinstance(child, dict):
            _force_openai_strict(child)
    for child in schema.get("definitions", {}).values():
        if isinstance(child, dict):
            _force_openai_strict(child)
    return schema


def _structured_schema(model_class: type[BaseModel], name: str) -> dict[str, Any]:
    schema = _force_openai_strict(model_class.schema())
    return {
        "type": "json_schema",
        "name": name,
        "schema": schema,
        "strict": True,
    }


def _call_openai_structured(
    settings: Settings,
    *,
    model: str,
    instructions: str,
    payload: dict[str, Any],
    response_model: type[BaseModel],
    schema_name: str,
    max_output_tokens: int,
) -> tuple[BaseModel, str, schemas.AIUsageRead | None]:
    _require_openai(settings)
    body = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": instructions}]},
            {"role": "user", "content": [{"type": "input_text", "text": json.dumps(payload, ensure_ascii=False)}]},
        ],
        "text": {"format": _structured_schema(response_model, schema_name), "verbosity": "low"},
        "max_output_tokens": max_output_tokens,
    }

    with httpx.Client(timeout=settings.openai_timeout_seconds) as client:
        response = client.post(
            f"{_base_url(settings)}/responses",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=body,
        )

    if response.status_code >= 400:
        try:
            error_body = response.json()
        except ValueError:
            error_body = {}
        detail = (
            error_body.get("error", {}).get("message")
            or response.text
            or f"{response.status_code} {response.reason_phrase}"
        )
        raise AIProviderResponseError(f"OpenAI-anropet misslyckades: {detail}")

    response_body = response.json()
    output_text = _extract_output_text(response_body)
    try:
        parsed = response_model.parse_raw(output_text)
    except ValidationError as exc:
        raise AIProviderResponseError(f"OpenAI returnerade ogiltig JSON för {schema_name}: {exc}") from exc

    return parsed, response_body.get("model", model), _usage_from_response(response_body)


def _person_map(records: dict[str, list[dict[str, Any]]]) -> dict[int, str]:
    return {int(item["id"]): item["name"] for item in records["persons"] if item.get("id") is not None}


def _compact_household_context(db: Session, household_id: int) -> dict[str, Any]:
    records = calculations.load_household_records(db, household_id)
    summary = calculations.build_household_summary(records, household_id)
    people = _person_map(records)

    recurring_costs = sorted(
        records["recurring_costs"],
        key=lambda item: calculations.amount_to_monthly(item.get("amount"), item.get("frequency")),
        reverse=True,
    )[:8]
    subscriptions = sorted(
        records["subscription_contracts"],
        key=lambda item: calculations.amount_to_monthly(item.get("current_monthly_cost"), item.get("billing_frequency")),
        reverse=True,
    )[:8]
    loans = sorted(records["loans"], key=calculations.estimate_loan_monthly_payment, reverse=True)[:6]
    opportunities = sorted(
        records["optimization_opportunities"],
        key=lambda item: float(item.get("estimated_monthly_saving") or 0.0),
        reverse=True,
    )[:6]

    housing = (
        db.query(models.HousingScenario)
        .filter_by(household_id=household_id)
        .order_by(models.HousingScenario.id.desc())
        .first()
    )
    latest_housing = calculations.evaluate_housing_scenario(housing) if housing else None

    def recurring_item(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "vendor": item.get("vendor"),
            "category": item.get("category"),
            "monthly_amount": round(calculations.amount_to_monthly(item.get("amount"), item.get("frequency")), 2),
            "person": people.get(item.get("person_id")),
            "mandatory": bool(item.get("mandatory")),
            "controllability": item.get("controllability"),
        }

    def subscription_item(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": item.get("provider"),
            "product_name": item.get("product_name"),
            "category": item.get("category"),
            "monthly_cost": round(
                calculations.amount_to_monthly(item.get("current_monthly_cost"), item.get("billing_frequency")), 2
            ),
            "ordinary_cost": item.get("ordinary_cost"),
            "criticality": item.get("household_criticality"),
            "next_review_at": str(item.get("next_review_at") or ""),
        }

    def loan_item(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "lender": item.get("lender"),
            "purpose": item.get("purpose"),
            "monthly_payment": round(calculations.estimate_loan_monthly_payment(item), 2),
            "current_balance": item.get("current_balance"),
            "remaining_term_months": item.get("remaining_term_months"),
        }

    return {
        "summary": summary,
        "people": [{"id": person_id, "name": name} for person_id, name in people.items()],
        "recurring_costs": [recurring_item(item) for item in recurring_costs],
        "subscriptions": [subscription_item(item) for item in subscriptions],
        "loans": [loan_item(item) for item in loans],
        "opportunities": [
            {
                "title": item.get("title"),
                "estimated_monthly_saving": item.get("estimated_monthly_saving"),
                "rationale": item.get("rationale"),
            }
            for item in opportunities
        ],
        "document_counts": {
            "documents": len(records["documents"]),
            "drafts_pending_review": len(
                [item for item in records["extraction_drafts"] if item.get("status") == "pending_review"]
            ),
            "reports": len(records["report_snapshots"]),
        },
        "latest_housing_evaluation": latest_housing,
    }


def _analysis_model(settings: Settings) -> str:
    return settings.openai_analysis_model or settings.openai_model


def _ingest_model(settings: Settings) -> str:
    return settings.openai_ingest_model or settings.openai_model


def _format_analysis_answer(structured: AnalysisStructuredOutput) -> str:
    return structured.answer_markdown.strip()


def generate_analysis_answer(
    db: Session,
    household_id: int,
    prompt: str,
    settings: Settings,
) -> tuple[str, str, schemas.AIUsageRead | None]:
    context = _compact_household_context(db, household_id)
    instructions = (
        "Du är en svensk, lugn och konkret ekonomicoach för ett hushåll. "
        "Använd bara datan du får. Hitta inte på konton, kostnader eller framtida utfall. "
        "Svara på svenska. Var read-only och föreslå inga tysta dataskrivningar. "
        "Om data saknas ska du säga det tydligt. "
        "Returnera bara kort markdown i fältet answer_markdown. "
        "Håll svaret under 140 ord och fokusera på 2-4 viktigaste observationerna."
    )
    payload = {
        "question": prompt,
        "household_context": context,
    }
    structured, model_name, usage = _call_openai_structured(
        settings,
        model=_analysis_model(settings),
        instructions=instructions,
        payload=payload,
        response_model=AnalysisStructuredOutput,
        schema_name="analysis_response",
        max_output_tokens=220,
    )
    return _format_analysis_answer(structured), model_name, usage


def _ingest_field_guides(records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    people = [{"id": item["id"], "name": item["name"]} for item in records["persons"]]
    return {
        "people": people,
        "frequency_values": ["monthly", "yearly", "weekly", "biweekly", "daily"],
        "subscription_categories": [
            "mobile",
            "broadband",
            "electricity",
            "streaming",
            "gym",
            "alarm",
            "software",
            "insurance",
            "membership",
            "other",
        ],
        "recurring_cost_shape": {
            "required": ["category", "amount", "frequency"],
            "optional": ["vendor", "person_id", "mandatory", "variability_class", "controllability", "note"],
        },
        "subscription_contract_shape": {
            "required": ["category", "provider", "current_monthly_cost", "billing_frequency"],
            "optional": ["product_name", "person_id", "ordinary_cost", "next_review_at", "household_criticality", "note"],
        },
        "loan_shape": {
            "required": ["type"],
            "optional": ["person_id", "lender", "current_balance", "required_monthly_payment", "remaining_term_months", "note"],
        },
        "income_source_shape": {
            "required": ["person_id", "type"],
            "optional": ["net_amount", "gross_amount", "frequency", "source", "note"],
        },
    }


def _validated_ingest_suggestion(
    household_id: int,
    suggestion: IngestStructuredSuggestion,
) -> schemas.IngestSuggestionRead:
    try:
        parsed_json = json.loads(suggestion.proposed_json)
        if not isinstance(parsed_json, dict):
            raise ValueError("proposed_json måste vara ett JSON-objekt.")
        proposed_json = dict(parsed_json)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        proposed_json = {}
        validation_errors = [f"proposed_json kunde inte läsas som JSON-objekt: {exc}"]
    else:
        validation_errors: list[str] = []
    target = suggestion.target_entity_type

    if target not in SUPPORTED_INGEST_TARGETS:
        validation_errors.append(f"Targettypen {target} stöds inte i nuvarande ingest-lager.")
    else:
        schema_mapping = {
            "recurring_cost": schemas.RecurringCostCreate,
            "subscription_contract": schemas.SubscriptionContractCreate,
            "loan": schemas.LoanCreate,
            "income_source": schemas.IncomeSourceCreate,
        }
        schema_class = schema_mapping[target]
        if "household_id" in getattr(schema_class, "__fields__", {}) and "household_id" not in proposed_json:
            proposed_json["household_id"] = household_id
        try:
            validated_payload = schema_class(**proposed_json)
            proposed_json = validated_payload.dict(exclude_none=True)
        except ValidationError as exc:
            validation_errors.extend(error["msg"] for error in exc.errors())

    return schemas.IngestSuggestionRead(
        target_entity_type=target,
        title=suggestion.title,
        rationale=suggestion.rationale,
        confidence=suggestion.confidence,
        proposed_json=proposed_json,
        validation_status="invalid" if validation_errors else "valid",
        validation_errors=validation_errors,
        uncertainty_notes=suggestion.uncertainty_notes,
    )


def analyze_ingest_input(
    db: Session,
    household_id: int,
    *,
    input_text: str,
    input_kind: str,
    source_name: str | None,
    settings: Settings,
) -> tuple[schemas.IngestAnalyzeResponse, str]:
    records = calculations.load_household_records(db, household_id)
    truncated_input = input_text.strip()
    was_truncated = len(truncated_input) > 6000
    if was_truncated:
        truncated_input = truncated_input[:6000]

    instructions = (
        "Du analyserar rå ekonomitext för en svensk hushållsekonomiapp. "
        "Var konservativ. Föreslå bara strukturerade poster när texten ger tydligt stöd. "
        "Om transaktionsdata inte kan mappas säkert till befintliga tabeller ska du hellre lämna suggestions tom och förklara varför. "
        "Du får bara föreslå target_entity_type som finns i payload.supported_shapes. "
        "Inkludera inte household_id om backend kan fylla det. "
        "Fältet proposed_json måste vara ett JSON-objekt serialiserat som en sträng. "
        "Inga direkta skrivningar sker nu."
    )
    payload = {
        "input_kind": input_kind,
        "source_name": source_name,
        "raw_text": truncated_input,
        "supported_shapes": _ingest_field_guides(records),
    }
    structured, model_name, usage = _call_openai_structured(
        settings,
        model=_ingest_model(settings),
        instructions=instructions,
        payload=payload,
        response_model=IngestStructuredOutput,
        schema_name="ingest_response",
        max_output_tokens=800,
    )
    suggestions = [_validated_ingest_suggestion(household_id, suggestion) for suggestion in structured.suggestions]
    guidance = list(structured.guidance)
    if was_truncated:
        guidance.append("Råtexten trunkerades till 6000 tecken för låg tokenkostnad. Dela upp större underlag vid behov.")
    return (
        schemas.IngestAnalyzeResponse(
            household_id=household_id,
            source_name=source_name,
            input_kind=input_kind,
            detected_kind=structured.detected_kind,
            summary=structured.summary,
            guidance=guidance,
            suggestions=suggestions,
            provider="openai",
            model=model_name,
            usage=usage,
        ),
        model_name,
    )


def _document_type_for_input(input_kind: str) -> str:
    mapping = {
        "bank_copy_paste": "bank_statement",
        "subscription_contract": "contract",
        "invoice_or_bill": "invoice",
        "financial_note": "receipt",
        "unknown": "receipt",
    }
    return mapping.get(input_kind, "receipt")


def promote_ingest_suggestions(
    db: Session,
    household_id: int,
    request_body: schemas.IngestPromoteRequest,
) -> schemas.IngestPromoteResponse:
    valid_suggestions = [item for item in request_body.suggestions if item.validation_status == "valid"]
    if not valid_suggestions:
        raise AIProviderResponseError("Det finns inga validerade förslag att skapa reviewutkast från.")

    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    document_type = _document_type_for_input(request_body.input_kind or "unknown")
    source_stub = (request_body.source_name or "ai-ingest").strip().replace(" ", "-").lower()
    document = models.Document(
        household_id=household_id,
        document_type=document_type,
        file_name=f"{source_stub}-{timestamp}.txt",
        mime_type="text/plain",
        issuer=request_body.source_name,
        extracted_text=request_body.input_text,
        extraction_status="pending",
    )
    db.add(document)
    db.flush()

    created_drafts: list[schemas.CreatedDraftRead] = []
    for suggestion in valid_suggestions:
        draft = models.ExtractionDraft(
            household_id=household_id,
            document_id=document.id,
            target_entity_type=suggestion.target_entity_type,
            proposed_json=suggestion.proposed_json,
            confidence=suggestion.confidence,
            status="pending_review",
            model_name=(
                f"{request_body.provider}:{request_body.model}"
                if request_body.provider and request_body.model
                else request_body.model
            ),
        )
        db.add(draft)
        db.flush()
        created_drafts.append(
            schemas.CreatedDraftRead(
                draft_id=draft.id,
                target_entity_type=draft.target_entity_type,
                confidence=draft.confidence,
                validation_status=suggestion.validation_status,
            )
        )

    db.commit()
    return schemas.IngestPromoteResponse(
        household_id=household_id,
        document_id=document.id,
        document_type=document_type,
        created_drafts=created_drafts,
        skipped_suggestions=len(request_body.suggestions) - len(valid_suggestions),
    )
