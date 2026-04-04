from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field, ValidationError, confloat
from sqlalchemy.orm import Session

from . import calculations, models, schemas
from .ingest_content import detect_input_hints, extract_text_from_upload, normalize_ingest_text
from .settings import Settings


DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
SUPPORTED_INGEST_TARGETS = {"recurring_cost", "subscription_contract", "loan", "income_source"}
SUPPORTED_INGEST_INPUT_MEDIUMS = {"text", "pdf_text", "uploaded_document", "uploaded_pdf", "image", "bank_paste"}


class AIProviderUnavailableError(RuntimeError):
    pass


class AIProviderResponseError(RuntimeError):
    pass


class AIInputNotSupportedError(RuntimeError):
    pass


class StrictModel(BaseModel):
    class Config:
        extra = "forbid"


class AnalysisStructuredOutput(StrictModel):
    answer_markdown: str


class IngestDocumentClassificationOutput(StrictModel):
    document_type: Literal["subscription_contract", "invoice", "recurring_cost_candidate", "transfer_or_saving_candidate", "bank_row_batch", "insurance_policy", "loan_or_credit", "financial_note", "unclear"]
    provider_name: str | None
    label: str | None
    amount: float | None
    currency: str | None
    due_date: str | None
    cadence: str | None
    category_hint: str | None
    suggested_target_entity_type: Literal["recurring_cost", "subscription_contract", "loan", "income_source"] | None
    household_relevance: Literal["low", "medium", "high"]
    confidence: confloat(ge=0.0, le=1.0) | None
    confirmed_fields: list[str]
    notes: list[str]
    uncertainty_reasons: list[str]


class IngestStructuredSuggestion(StrictModel):
    target_entity_type: Literal["recurring_cost", "subscription_contract", "loan", "income_source"]
    review_bucket: Literal["recurring_cost", "subscription_contract", "loan", "income_source", "transfer_or_saving", "unclear"]
    title: str
    rationale: str
    confidence: confloat(ge=0.0, le=1.0) | None
    proposed_json: str
    uncertainty_notes: list[str]


class IngestStructuredOutput(StrictModel):
    classification: IngestDocumentClassificationOutput
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


def _normalize_source_channel(source_channel: str | None, input_kind: str | None) -> str:
    candidate = (source_channel or "").strip().lower()
    if candidate in SUPPORTED_INGEST_INPUT_MEDIUMS:
        return candidate
    if candidate == "image_placeholder":
        return "image"

    legacy = (input_kind or "").strip().lower()
    if legacy in {"text", "paste", "subscription_contract", "invoice_or_bill", "financial_note", "unknown"}:
        return "text"
    if legacy == "bank_copy_paste":
        return "bank_paste"
    if legacy == "upload_text":
        return "uploaded_document"
    if legacy == "pdf_text":
        return "pdf_text"
    if legacy == "uploaded_pdf":
        return "uploaded_pdf"
    if legacy in {"image_placeholder", "image"}:
        return "image"
    return "text"


def _legacy_input_kind(input_kind: str | None) -> str:
    value = (input_kind or "unknown").strip().lower()
    if value in {"bank_copy_paste", "subscription_contract", "invoice_or_bill", "financial_note"}:
        return value
    return "unknown"


def _presented_input_kind(input_kind: str | None, source_channel: str) -> str:
    value = (input_kind or "").strip().lower()
    return value or source_channel


def _legacy_document_type_for_input(input_kind: str | None) -> str:
    mapping = {
        "bank_copy_paste": "bank_statement",
        "subscription_contract": "contract",
        "invoice_or_bill": "invoice",
        "financial_note": "receipt",
        "unknown": "receipt",
    }
    return mapping.get(_legacy_input_kind(input_kind), "receipt")


def _document_type_from_classification(document_type: str, source_channel: str) -> str:
    mapping = {
        "subscription_contract": "contract",
        "invoice": "invoice",
        "bank_row_batch": "bank_statement",
        "insurance_policy": "contract",
        "loan_or_credit": "contract",
        "transfer_or_saving_candidate": "receipt",
        "recurring_cost_candidate": "receipt",
        "financial_note": "receipt",
    }
    return mapping.get(document_type, "receipt")


def _review_bucket_for_suggestion(
    suggestion: IngestStructuredSuggestion,
    classification: IngestDocumentClassificationOutput,
) -> str:
    if suggestion.review_bucket != "unclear":
        return suggestion.review_bucket
    if classification.suggested_target_entity_type:
        return classification.suggested_target_entity_type
    return suggestion.target_entity_type


def _review_group_title(group_type: str) -> str:
    return {
        "subscription_contract": "Abonnemang och avtal",
        "recurring_cost": "Återkommande kostnad",
        "loan": "Lån och avbetalning",
        "income_source": "Inkomstkälla",
        "transfer_or_saving": "Överföringar och sparande",
        "unclear": "Oklara förslag",
    }.get(group_type, "Oklara förslag")


def _get_household_document_or_404(db: Session, household_id: int, document_id: int) -> models.Document:
    document = db.get(models.Document, document_id)
    if document is None or document.household_id != household_id:
        raise AIProviderResponseError(f"Document med id {document_id} finns inte för hushållet.")
    return document


def _read_uploaded_document_text(document: models.Document) -> tuple[str | None, str, list[str]]:
    if document.extracted_text:
        channel = "pdf_text" if (document.mime_type or "").lower() == "application/pdf" else "document_text"
        note = (
            "Redan extraherad PDF-text återanvändes från dokumentet."
            if channel == "pdf_text"
            else "Redan extraherad text återanvändes från dokumentet."
        )
        return normalize_ingest_text(document.extracted_text), channel, [note]

    if not document.storage_path:
        return document.extracted_text, "document_text", ["Dokumentet saknar lagrad fil."]

    file_path = Path(document.storage_path)
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    if not file_path.exists():
        return document.extracted_text, "document_text", ["Den lagrade filen hittades inte."]

    raw = file_path.read_bytes()
    extracted = extract_text_from_upload(raw, file_name=document.file_name, mime_type=document.mime_type)
    notes = ["Text försöktes läsas ur lagrad fil."] + extracted.notes
    return extracted.text, extracted.extraction_mode, notes


def _resolve_ingest_input(
    db: Session,
    household_id: int,
    *,
    request_input: str | None,
    source_channel: str,
    document_id: int | None,
    source_name: str | None,
) -> tuple[str, schemas.IngestInputRead]:
    text = request_input.strip() if request_input else ""
    extraction_notes: list[str] = []
    extraction_mode = "user_paste"
    input_origin = "user_paste"
    document_file_name: str | None = None
    resolved_document_id = document_id
    resolved_source_name = source_name

    if document_id is not None:
        document = _get_household_document_or_404(db, household_id, document_id)
        document_text, extraction_mode, document_notes = _read_uploaded_document_text(document)
        extraction_notes.extend(document_notes)
        resolved_document_id = document.id
        document_file_name = document.file_name
        resolved_source_name = source_name or document.issuer or document.file_name
        if document_text:
            text = document_text
        if extraction_mode in {"ocr_tesseract", "pdf_ocr"}:
            input_origin = "ocr_image" if extraction_mode == "ocr_tesseract" else "ocr_pdf"
        elif extraction_mode == "pdf_text":
            input_origin = "pdf_text"
        elif extraction_mode.startswith("document"):
            input_origin = "document_text"
        else:
            input_origin = "file_text"
    else:
        if source_channel == "image":
            input_origin = "ocr_image"
        elif source_channel == "bank_paste":
            input_origin = "bank_paste"
        elif source_channel in {"uploaded_document", "uploaded_pdf"}:
            input_origin = "file_text"
        elif source_channel == "pdf_text":
            input_origin = "pdf_text"
        else:
            input_origin = "user_paste"

    if not text:
        raise AIProviderResponseError("Ingest kräver text eller ett dokument_id med extraherbar text.")

    normalized_text = normalize_ingest_text(text)
    was_truncated = len(normalized_text) > 6000
    limited_text = normalized_text[:6000] if was_truncated else normalized_text
    if was_truncated:
        extraction_notes.append("Texten trunkerades till 6000 tecken för att hålla tokenkostnaden nere.")

    input_details = schemas.IngestInputRead(
        source_channel=source_channel,
        input_origin=input_origin,
        document_id=resolved_document_id,
        document_file_name=document_file_name,
        source_name=resolved_source_name,
        text_length=len(normalized_text),
        text_truncated=was_truncated,
        extraction_mode=extraction_mode,
        extraction_notes=extraction_notes,
    )
    return limited_text, input_details


def _build_document_summary_read(structured: IngestDocumentClassificationOutput) -> schemas.IngestDocumentSummaryRead:
    uncertainty_reasons = list(structured.uncertainty_reasons)
    due_date: date | None = None
    if structured.due_date:
        parsed_due_date = structured.due_date.strip()
        if parsed_due_date:
            try:
                candidate = date.fromisoformat(parsed_due_date)
                if 1900 <= candidate.year <= 2100:
                    due_date = candidate
                else:
                    uncertainty_reasons.append("Ogiltigt eller osannolikt förfallodatum från modellen ignorerades.")
            except ValueError:
                uncertainty_reasons.append("Ogiltigt förfallodatum från modellen ignorerades.")
    return schemas.IngestDocumentSummaryRead(
        document_type=structured.document_type,
        provider_name=structured.provider_name,
        label=structured.label,
        amount=structured.amount,
        currency=structured.currency,
        due_date=due_date,
        cadence=structured.cadence,
        category_hint=structured.category_hint,
        suggested_target_entity_type=structured.suggested_target_entity_type,
        household_relevance=structured.household_relevance,
        confidence=structured.confidence,
        confirmed_fields=list(structured.confirmed_fields),
        notes=list(structured.notes),
        uncertainty_reasons=uncertainty_reasons,
    )


def _group_ingest_suggestions(
    suggestions: list[schemas.IngestSuggestionRead],
    classification: schemas.IngestDocumentSummaryRead,
) -> list[schemas.IngestReviewGroupRead]:
    grouped: dict[str, list[schemas.IngestSuggestionRead]] = defaultdict(list)
    for suggestion in suggestions:
        grouped[suggestion.review_bucket].append(suggestion)

    review_groups: list[schemas.IngestReviewGroupRead] = []
    for group_type, group_suggestions in grouped.items():
        confidence_values = [item.confidence for item in group_suggestions if item.confidence is not None]
        review_groups.append(
            schemas.IngestReviewGroupRead(
                group_type=group_type,
                title=_review_group_title(group_type),
                summary=classification.label
                or classification.provider_name
                or classification.document_type.replace("_", " "),
                confidence=max(confidence_values) if confidence_values else classification.confidence,
                suggestion_count=len(group_suggestions),
                uncertainty_reasons=list(classification.uncertainty_reasons),
                suggestions=group_suggestions,
            )
        )

    if not review_groups:
        review_groups.append(
            schemas.IngestReviewGroupRead(
                group_type="unclear",
                title="Oklara förslag",
                summary=classification.label or "Inga validerade förslag kunde skapas.",
                confidence=classification.confidence,
                suggestion_count=0,
                uncertainty_reasons=list(classification.uncertainty_reasons),
                suggestions=[],
            )
        )

    return review_groups


def _apply_document_summary_to_document(
    document: models.Document,
    *,
    document_summary: schemas.IngestDocumentSummaryRead | None,
    source_channel: str,
    source_name: str | None,
) -> str:
    if source_name and not document.issuer:
        document.issuer = source_name

    if document_summary is None:
        return document.document_type

    if document_summary.provider_name and not document.issuer:
        document.issuer = document_summary.provider_name
    if document_summary.amount is not None and document.total_amount is None:
        document.total_amount = document_summary.amount
    if document_summary.currency and not document.currency:
        document.currency = document_summary.currency

    document_type = _document_type_from_classification(document_summary.document_type, source_channel)
    if document_summary.document_type != "unclear":
        document.document_type = document_type
    return document_type


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
        "document_types": [
            "subscription_contract",
            "invoice",
            "recurring_cost_candidate",
            "transfer_or_saving_candidate",
            "bank_row_batch",
            "insurance_policy",
            "loan_or_credit",
            "financial_note",
            "unclear",
        ],
        "review_buckets": ["recurring_cost", "subscription_contract", "loan", "income_source", "transfer_or_saving", "unclear"],
        "document_summary_shape": {
            "required": [
                "document_type",
                "provider_name",
                "label",
                "amount",
                "currency",
                "due_date",
                "cadence",
                "category_hint",
                "suggested_target_entity_type",
                "household_relevance",
                "confidence",
                "confirmed_fields",
                "notes",
                "uncertainty_reasons",
            ],
            "notes": "Sätt null om ett fält inte framgår tydligt. confirmed_fields får bara innehålla säkert lästa fält.",
        },
        "frequency_values": ["monthly", "yearly", "weekly", "biweekly", "daily"],
        "frequency_notes": "VIKTIGT: bara dessa frekvenser är tillåtna. Kvartal/quarterly finns inte. Använd yearly med beloppet * 4 om originalet är kvartalsvis. Halvår = yearly med beloppet * 2.",
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
            "variability_class_values": ["fixed", "semi_fixed", "variable"],
            "controllability_values": ["locked", "negotiable", "reducible", "discretionary"],
        },
        "subscription_contract_shape": {
            "required": ["category", "provider", "current_monthly_cost", "billing_frequency"],
            "optional": ["product_name", "person_id", "ordinary_cost", "next_review_at", "household_criticality", "note"],
        },
        "loan_shape": {
            "required": ["type"],
            "optional": [
                "person_id",
                "lender",
                "current_balance",
                "required_monthly_payment",
                "remaining_term_months",
                "nominal_rate",
                "amortization_amount_monthly",
                "due_day",
                "purpose",
                "note",
                "interest_rate",
                "debt_before_amortization",
                "payment_amount",
                "payment_due_date",
                "object_vehicle",
                "contract_number",
                "amortization",
                "interest_cost",
                "fees",
            ],
        },
        "income_source_shape": {
            "required": ["person_id", "type"],
            "optional": ["net_amount", "gross_amount", "frequency", "source", "note"],
        },
    }


SHARED_CATEGORIES = {"mat", "boende", "transport", "barn", "hushåll", "broadband", "electricity", "alarm"}
PRIVATE_CATEGORIES = {"gym", "streaming", "software", "membership", "mobile"}


def _infer_ownership_candidate(target: str, proposed_json: dict, title: str) -> str:
    """Conservative ownership heuristic: private, shared, or unclear."""
    category = (proposed_json.get("category") or "").lower()
    provider = (proposed_json.get("provider") or proposed_json.get("vendor") or "").lower()

    if category in SHARED_CATEGORIES:
        return "shared"
    if category in PRIVATE_CATEGORIES:
        return "private"
    if any(kw in provider for kw in ["ica", "coop", "hemköp", "willys", "hyra", "el ", "vatten"]):
        return "shared"
    return "unclear"


def _build_why_suggested(target: str, proposed_json: dict, confidence: float | None) -> str:
    """Build a human-readable explanation for why this suggestion was created."""
    parts = []
    if target == "subscription_contract":
        parts.append("Klassad som abonnemang")
    elif target == "recurring_cost":
        parts.append("Klassad som återkommande kostnad")
    elif target == "loan":
        parts.append("Klassad som lån/kredit")
    elif target == "income_source":
        parts.append("Klassad som inkomst")

    provider = proposed_json.get("provider") or proposed_json.get("vendor")
    if provider:
        parts.append(f"leverantör: {provider}")
    amount = proposed_json.get("amount") or proposed_json.get("current_monthly_cost") or proposed_json.get("net_amount")
    if amount:
        parts.append(f"belopp: {amount} kr")
    if confidence is not None:
        parts.append(f"confidence: {round(confidence * 100)}%")
    return ". ".join(parts) + "." if parts else "Baserat på AI-tolkning av underlaget."


def _check_duplicate_indicator(
    db: Session,
    household_id: int,
    suggestion: schemas.IngestSuggestionRead,
) -> str | None:
    """Check if a similar draft or canonical record already exists."""
    proposed = suggestion.proposed_json
    provider = (proposed.get("provider") or proposed.get("vendor") or proposed.get("lender") or "").strip().lower()
    amount = proposed.get("amount") or proposed.get("current_monthly_cost") or proposed.get("required_monthly_payment")

    if not provider and amount is None:
        return None

    try:
        existing_drafts = db.query(models.ExtractionDraft).filter_by(
            household_id=household_id,
            target_entity_type=suggestion.target_entity_type,
        ).filter(models.ExtractionDraft.status.in_(["pending_review", "deferred"])).all()
    except Exception:
        return None

    for draft in existing_drafts:
        dj = draft.proposed_json or {}
        d_provider = (dj.get("provider") or dj.get("vendor") or dj.get("lender") or "").strip().lower()
        d_amount = dj.get("amount") or dj.get("current_monthly_cost") or dj.get("required_monthly_payment")
        if provider and d_provider and provider == d_provider:
            if amount is not None and d_amount is not None and abs(float(amount) - float(d_amount)) < 1.0:
                return f"Möjlig dubblett: liknande utkast #{draft.id} ({d_provider}, {d_amount} kr) väntar redan."
            return f"Samma leverantör finns redan i utkast #{draft.id} ({d_provider})."

    return None


def _validated_ingest_suggestion(
    household_id: int,
    suggestion: IngestStructuredSuggestion,
    classification: IngestDocumentClassificationOutput,
) -> schemas.IngestSuggestionRead:
    try:
        parsed_json = json.loads(suggestion.proposed_json)
        if not isinstance(parsed_json, dict):
            raise ValueError("proposed_json måste vara ett JSON-objekt.")
        proposed_json = dict(parsed_json)
        review_json = dict(parsed_json)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        proposed_json = {}
        review_json = {}
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

    review_bucket = _review_bucket_for_suggestion(suggestion, classification)

    ownership = _infer_ownership_candidate(target, proposed_json, suggestion.title)
    why = suggestion.rationale or _build_why_suggested(target, proposed_json, suggestion.confidence)

    return schemas.IngestSuggestionRead(
        target_entity_type=target,
        review_bucket=(
            review_bucket
            if review_bucket in {"recurring_cost", "subscription_contract", "loan", "income_source", "transfer_or_saving", "unclear"}
            else "unclear"
        ),
        title=suggestion.title,
        rationale=suggestion.rationale,
        confidence=suggestion.confidence,
        proposed_json=proposed_json,
        review_json=review_json,
        validation_status="invalid" if validation_errors else "valid",
        validation_errors=validation_errors,
        uncertainty_notes=suggestion.uncertainty_notes,
        ownership_candidate=ownership,
        why_suggested=why,
    )


def _load_merchant_aliases(db: Session, household_id: int) -> list[tuple[str, str]]:
    """Load merchant aliases for a household. Returns [(lowercase_alias, canonical_name)].
    Gracefully returns empty list if table doesn't exist yet."""
    try:
        aliases = db.query(models.MerchantAlias).filter_by(household_id=household_id).all()
        return [(a.alias.lower(), a.canonical_name) for a in aliases]
    except Exception:
        return []


def _apply_merchant_normalization(text: str, aliases: list[tuple[str, str]]) -> str:
    """Replace known merchant aliases in text with their canonical names."""
    if not aliases:
        return text
    import re
    for alias, canonical in aliases:
        pattern = re.compile(re.escape(alias), re.IGNORECASE)
        text = pattern.sub(canonical, text)
    return text


def analyze_ingest_input(
    db: Session,
    household_id: int,
    *,
    input_text: str | None,
    input_kind: str,
    source_channel: str,
    document_id: int | None,
    source_name: str | None,
    settings: Settings,
) -> tuple[schemas.IngestAnalyzeResponse, str]:
    normalized_source_channel = _normalize_source_channel(source_channel, input_kind)
    records = calculations.load_household_records(db, household_id)
    truncated_input, input_details = _resolve_ingest_input(
        db,
        household_id,
        request_input=input_text,
        source_channel=normalized_source_channel,
        document_id=document_id,
        source_name=source_name,
    )

    merchant_aliases = _load_merchant_aliases(db, household_id)
    truncated_input = _apply_merchant_normalization(truncated_input, merchant_aliases)

    input_hints = detect_input_hints(truncated_input)
    is_bank_paste = normalized_source_channel == "bank_paste" or "bank_statement_keywords" in input_hints
    is_ocr = input_details.input_origin in {"ocr_image", "ocr_pdf"}

    base_rules = (
        "Du analyserar svenskt hushållsunderlag konservativt. "
        "Ditt uppdrag: (1) klassificera dokumenttyp, (2) extrahera kärnfakta, (3) visa osäkerhet. "
        "Regler: "
        "- Sätt null när ett fält inte syns tydligt i texten. "
        "- confirmed_fields får bara innehålla fält som kan läsas direkt ur texten utan gissning. "
        "- Om texten ser ut som en faktura, identifiera leverantör, belopp, valuta, förfallodatum, frekvens. "
        "- Om texten ser ut som ett abonnemang, identifiera leverantör, kostnad/månad, bindning, kategori. "
        "- Skapa suggestions bara när det finns tydligt stöd. "
        "- review_bucket ska matcha den mest sannolika måltypen. "
        "- Hellre unclear med ärlig osäkerhet än säker med felaktig klassificering. "
        "- Inga direkta skrivningar sker nu."
    )
    bank_rules = (
        " Extra regler för bankrader: "
        "- Klassificera som bank_row_batch. "
        "- Gruppera rader konservativt: troliga abonnemang -> review_bucket subscription_contract, "
        "troliga återkommande kostnader -> recurring_cost, troliga överföringar/sparande -> transfer_or_saving, oklara -> unclear. "
        "- Skapa en suggestion per tydligt identifierbar rad eller grupp. "
        "- Varje suggestion ska ha en beskrivande title med mottagare/avsändare och belopp. "
        "- Belopp under 0 (negativt) = utgift/kostnad. Belopp över 0 = inkomst/insättning. "
        "- Ange uncertainty_notes för rader som kan tolkas på flera sätt."
    )
    ocr_rules = (
        " Extra: texten kommer från OCR (bildavläsning) och kan innehålla felläsningar. "
        "Var extra konservativ med confidence och confirmed_fields."
    )

    instructions = base_rules
    if is_bank_paste:
        instructions += bank_rules
    if is_ocr:
        instructions += ocr_rules
    payload = {
        "input_kind": _legacy_input_kind(input_kind),
        "source_channel": normalized_source_channel,
        "source_name": input_details.source_name,
        "document_id": document_id,
        "input_hints": input_hints,
        "raw_text": truncated_input,
        "supported_shapes": _ingest_field_guides(records),
    }
    max_tokens = 1400 if is_bank_paste else 720
    structured, model_name, usage = _call_openai_structured(
        settings,
        model=_ingest_model(settings),
        instructions=instructions,
        payload=payload,
        response_model=IngestStructuredOutput,
        schema_name="ingest_response",
        max_output_tokens=max_tokens,
    )
    suggestions = [
        _validated_ingest_suggestion(household_id, suggestion, structured.classification)
        for suggestion in structured.suggestions
    ]
    for s in suggestions:
        dup = _check_duplicate_indicator(db, household_id, s)
        if dup:
            s.duplicate_indicator = dup
    document_summary = _build_document_summary_read(structured.classification)
    review_groups = _group_ingest_suggestions(suggestions, document_summary)
    guidance = list(structured.guidance)
    guidance.extend(input_details.extraction_notes)
    if input_details.text_truncated:
        guidance.append("Råtexten trunkerades till 6000 tecken för låg tokenkostnad. Dela upp större underlag vid behov.")
    return (
        schemas.IngestAnalyzeResponse(
            household_id=household_id,
            source_name=input_details.source_name,
            input_kind=_presented_input_kind(input_kind, normalized_source_channel),
            source_channel=normalized_source_channel,
            document_id=input_details.document_id,
            input_details=input_details,
            detected_kind=document_summary.document_type,
            document_summary=document_summary,
            review_groups=review_groups,
            summary=structured.summary,
            guidance=guidance,
            suggestions=suggestions,
            image_readiness=schemas.IngestImageReadinessRead(),
            provider="openai",
            model=model_name,
            usage=usage,
        ),
        model_name,
    )


def promote_ingest_suggestions(
    db: Session,
    household_id: int,
    request_body: schemas.IngestPromoteRequest,
) -> schemas.IngestPromoteResponse:
    normalized_source_channel = _normalize_source_channel(request_body.source_channel, request_body.input_kind)

    valid_suggestions = [item for item in request_body.suggestions if item.validation_status == "valid"]
    if not valid_suggestions:
        raise AIProviderResponseError("Det finns inga validerade förslag att skapa reviewutkast från.")

    normalized_input_text = normalize_ingest_text(request_body.input_text) if request_body.input_text else None
    document_summary = request_body.document_summary
    document: models.Document | None = None

    if request_body.document_id is not None:
        document = _get_household_document_or_404(db, household_id, request_body.document_id)
        if not document.extracted_text and normalized_input_text:
            document.extracted_text = normalized_input_text
            document.extraction_status = "interpreted"
        elif not document.extracted_text:
            document_text, _, _ = _read_uploaded_document_text(document)
            if document_text:
                document.extracted_text = document_text
                document.extraction_status = "interpreted"
        if not document.extracted_text:
            raise AIProviderResponseError("Det befintliga dokumentet saknar extraherbar text.")
        document_type = _apply_document_summary_to_document(
            document,
            document_summary=document_summary,
            source_channel=normalized_source_channel,
            source_name=request_body.source_name,
        )
    else:
        if normalized_input_text is None:
            raise AIProviderResponseError("Promote kräver input_text när document_id saknas.")
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        source_stub = (request_body.source_name or "ai-ingest").strip().replace(" ", "-").lower() or "ai-ingest"
        if document_summary is None:
            document_type = _legacy_document_type_for_input(request_body.input_kind or "unknown")
        else:
            document_type = _document_type_from_classification(document_summary.document_type, normalized_source_channel)
        document = models.Document(
            household_id=household_id,
            document_type=document_type,
            file_name=f"{source_stub}-{timestamp}.txt",
            mime_type="text/plain",
            issuer=request_body.source_name,
            extracted_text=normalized_input_text,
            extraction_status="interpreted",
        )
        db.add(document)
        db.flush()
        document_type = _apply_document_summary_to_document(
            document,
            document_summary=document_summary,
            source_channel=normalized_source_channel,
            source_name=request_body.source_name,
        )

    if document is None:
        raise AIProviderResponseError("Promote kunde inte knyta an till ett dokument.")

    document.extraction_status = "pending_review"
    document.processing_error = None
    created_drafts: list[schemas.CreatedDraftRead] = []
    for suggestion in valid_suggestions:
        draft = models.ExtractionDraft(
            household_id=household_id,
            document_id=document.id,
            target_entity_type=suggestion.target_entity_type,
            proposed_json=suggestion.proposed_json,
            review_json=suggestion.review_json,
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
                document_status=document.extraction_status,
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
