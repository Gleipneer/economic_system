import importlib
import io
import os
import subprocess
import sys
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect


def load_app(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["UPLOAD_DIR"] = str(tmp_path / "uploads")
    os.environ["OPENAI_API_KEY"] = ""
    os.environ["OPENAI_ANALYSIS_MODEL"] = ""
    os.environ["OPENAI_INGEST_MODEL"] = ""

    import app.database as database
    import app.models as models
    import app.schemas as schemas
    import app.main as main

    importlib.reload(database)
    importlib.reload(models)
    importlib.reload(schemas)
    main = importlib.reload(main)

    return main.app


def create_household_fixture(client: TestClient) -> dict[str, int]:
    household = client.post(
        "/households",
        json={"name": "Joakim & Jakobine", "currency": "SEK", "primary_country": "SE"},
    )
    assert household.status_code == 201
    household_id = household.json()["id"]

    joakim = client.post(
        "/persons",
        json={
            "household_id": household_id,
            "name": "Joakim",
            "role": "self",
            "income_share_mode": "pooled",
            "active": True,
        },
    )
    assert joakim.status_code == 201

    jakobine = client.post(
        "/persons",
        json={
            "household_id": household_id,
            "name": "Jakobine",
            "role": "partner",
            "income_share_mode": "pooled",
            "active": True,
        },
    )
    assert jakobine.status_code == 201

    child_1 = client.post(
        "/persons",
        json={
            "household_id": household_id,
            "name": "Barn 1",
            "role": "child",
            "income_share_mode": "pooled",
            "active": True,
        },
    )
    assert child_1.status_code == 201

    child_2 = client.post(
        "/persons",
        json={
            "household_id": household_id,
            "name": "Barn 2",
            "role": "child",
            "income_share_mode": "pooled",
            "active": True,
        },
    )
    assert child_2.status_code == 201

    joakim_id = joakim.json()["id"]
    jakobine_id = jakobine.json()["id"]

    salary_net = client.post(
        "/income_sources",
        json={
            "person_id": joakim_id,
            "type": "salary",
            "net_amount": 21500,
            "frequency": "monthly",
            "regularity": "fixed",
            "source": "Lön efter skatt",
        },
    )
    assert salary_net.status_code == 201

    salary_gross = client.post(
        "/income_sources",
        json={
            "person_id": jakobine_id,
            "type": "salary",
            "gross_amount": 430000,
            "frequency": "yearly",
            "regularity": "fixed",
            "source": "Årslön före skatt",
        },
    )
    assert salary_gross.status_code == 201

    car_loan = client.post(
        "/loans",
        json={
            "household_id": household_id,
            "person_id": joakim_id,
            "type": "car",
            "purpose": "Bil",
            "lender": "Billån",
            "required_monthly_payment": 2400,
            "status": "active",
            "repayment_model": "manual",
        },
    )
    assert car_loan.status_code == 201

    bed_loan = client.post(
        "/loans",
        json={
            "household_id": household_id,
            "person_id": joakim_id,
            "type": "other",
            "purpose": "Säng",
            "lender": "Resurs Bank",
            "current_balance": 12000,
            "remaining_term_months": 8,
            "required_monthly_payment": 1616,
            "status": "active",
            "repayment_model": "manual",
        },
    )
    assert bed_loan.status_code == 201

    eye_loan = client.post(
        "/loans",
        json={
            "household_id": household_id,
            "person_id": jakobine_id,
            "type": "other",
            "purpose": "Memira ögonlaser",
            "lender": "Memira",
            "required_monthly_payment": 399,
            "status": "active",
            "repayment_model": "manual",
        },
    )
    assert eye_loan.status_code == 201

    lovable = client.post(
        "/subscription_contracts",
        json={
            "household_id": household_id,
            "person_id": joakim_id,
            "category": "software",
            "provider": "Lovable",
            "product_name": "Starter",
            "current_monthly_cost": 5,
            "billing_frequency": "monthly",
            "household_criticality": "optional",
            "market_checkable": True,
        },
    )
    assert lovable.status_code == 201

    vehicle = client.post(
        "/vehicles",
        json={
            "household_id": household_id,
            "owner_person_id": joakim_id,
            "make": "Bil",
            "model": "Familjebil",
            "loan_id": car_loan.json()["id"],
        },
    )
    assert vehicle.status_code == 201

    recurring_cost = client.post(
        "/recurring_costs",
        json={
            "household_id": household_id,
            "category": "barn",
            "subcategory": "Övriga familjekostnader",
            "amount": 0,
            "frequency": "monthly",
            "mandatory": True,
            "variability_class": "fixed",
            "controllability": "locked",
        },
    )
    assert recurring_cost.status_code == 201

    scenario = client.post(
        "/scenarios",
        json={
            "household_id": household_id,
            "label": "Avsluta Lovable",
            "change_set_json": {
                "adjustments": [
                    {"entity": "subscription_contracts", "operation": "delete", "id": lovable.json()["id"]},
                ]
            },
        },
    )
    assert scenario.status_code == 201

    housing = client.post(
        "/housing_scenarios",
        json={
            "household_id": household_id,
            "label": "Bostadstest",
            "purchase_price": 3500000,
            "down_payment": 525000,
            "mortgage_needed": 2975000,
            "rate_assumption": 4.0,
            "amortization_rate": 2.0,
            "monthly_fee_or_operating_cost": 4200,
            "monthly_insurance": 250,
            "monthly_property_cost_estimate": 450,
        },
    )
    assert housing.status_code == 201

    return {
        "household_id": household_id,
        "joakim_id": joakim_id,
        "jakobine_id": jakobine_id,
        "scenario_id": scenario.json()["id"],
        "housing_id": housing.json()["id"],
        "bed_loan_id": bed_loan.json()["id"],
    }


def test_healthz_and_home(tmp_path):
    app = load_app(tmp_path)
    with TestClient(app) as client:
        assert client.get("/healthz").json() == {"status": "ok"}
        response = client.get("/")
        assert response.status_code == 200
        assert "Ekonomi" in response.text


def test_alembic_upgrade_head_creates_schema(tmp_path):
    db_path = tmp_path / "alembic.db"
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"
    env["AUTO_CREATE_SCHEMA"] = "false"

    result = subprocess.run(
        ["./venv/bin/alembic", "upgrade", "head"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["AUTO_CREATE_SCHEMA"] = "false"
    import app.settings as settings_module
    import app.database as database

    settings_module.get_settings.cache_clear()
    database = importlib.reload(database)
    inspector = inspect(database.engine)
    assert "households" in inspector.get_table_names()
    assert "alembic_version" in inspector.get_table_names()


def test_household_crud_partial_update(tmp_path):
    app = load_app(tmp_path)
    with TestClient(app) as client:
        created = client.post(
            "/households",
            json={"name": "Andersson Household", "currency": "SEK", "primary_country": "SE"},
        )
        assert created.status_code == 201
        household = created.json()
        household_id = household["id"]

        updated = client.put(f"/households/{household_id}", json={"name": "Updated Household"})
        assert updated.status_code == 200
        data = updated.json()
        assert data["name"] == "Updated Household"
        assert data["currency"] == "SEK"
        assert data["primary_country"] == "SE"

        listed = client.get("/households")
        assert listed.status_code == 200
        assert len(listed.json()) == 1

        deleted = client.delete(f"/households/{household_id}")
        assert deleted.status_code == 204


def test_summary_document_scenario_and_report_flow(tmp_path):
    app = load_app(tmp_path)
    with TestClient(app) as client:
        ids = create_household_fixture(client)
        household_id = ids["household_id"]

        summary = client.get(f"/households/{household_id}/summary")
        assert summary.status_code == 200
        payload = summary.json()
        assert payload["monthly_income_net"] == 21500
        assert payload["monthly_income_gross_only"] == 35833.33
        assert payload["monthly_income"] == 57333.33
        assert payload["gross_income_only_entries"] == 1
        assert payload["monthly_loan_payments"] == 4415
        assert payload["monthly_subscriptions"] == 5
        assert payload["monthly_total_expenses"] == 4420
        assert payload["monthly_net_cashflow"] == 52913.33
        assert payload["loan_balance_total"] == 12000
        assert payload["net_worth_estimate"] == -12000
        assert payload["counts"]["persons"] == 4

        upload = client.post(
            "/documents/upload",
            data={"household_id": str(household_id), "document_type": "invoice", "issuer": "Resurs Bank"},
            files={"file": ("invoice.txt", io.BytesIO(b"resurs invoice"), "text/plain")},
        )
        assert upload.status_code == 201
        document_id = upload.json()["id"]
        assert upload.json()["extracted_text"] == "resurs invoice"
        assert upload.json()["extraction_status"] == "parsed"

        download = client.get(f"/documents/{document_id}/download")
        assert download.status_code == 200
        assert download.content == b"resurs invoice"

        evaluate = client.get(f"/housing_scenarios/{ids['housing_id']}/evaluate")
        assert evaluate.status_code == 200
        assert evaluate.json()["monthly_total_cost"] == 19775.0

        scenario_result = client.post(f"/scenarios/{ids['scenario_id']}/run")
        assert scenario_result.status_code == 200
        result_json = scenario_result.json()["result_json"]
        assert result_json["baseline"]["monthly_net_cashflow"] == 52913.33
        assert result_json["projected"]["monthly_net_cashflow"] == 52918.33
        assert scenario_result.json()["monthly_delta"] == 5

        report = client.post(f"/households/{household_id}/report_snapshots/generate", json={})
        assert report.status_code == 200
        assert report.json()["type"] == "monthly_overview"
        assert report.json()["result_json"]["monthly_loan_payments"] == 4415

        opportunities = client.post(f"/households/{household_id}/optimization_scan")
        assert opportunities.status_code == 200
        titles = [item["title"] for item in opportunities.json()]
        assert any("Lovable" in title for title in titles)

        updated_loan = client.put(
            f"/loans/{ids['bed_loan_id']}",
            json={"current_balance": 10000, "remaining_term_months": 6},
        )
        assert updated_loan.status_code == 200
        assert updated_loan.json()["purpose"] == "Säng"
        assert updated_loan.json()["remaining_term_months"] == 6


def test_calculation_helpers_cover_frequency_and_estimated_loan_payment(tmp_path):
    app = load_app(tmp_path)
    with TestClient(app):
        from app import calculations

        assert calculations.amount_to_monthly(430000, "yearly") == pytest.approx(35833.333333333336)
        assert calculations.amount_to_monthly(1000, "weekly") == pytest.approx(4333.333333333333)
        assert calculations.estimate_loan_monthly_payment(
            {
                "current_balance": 12000,
                "nominal_rate": 6.0,
                "amortization_amount_monthly": 1000,
                "required_monthly_payment": None,
            }
        ) == pytest.approx(1060)


def test_ai_routes_fail_cleanly_without_provider(tmp_path):
    app = load_app(tmp_path)
    with TestClient(app) as client:
        ids = create_household_fixture(client)
        household_id = ids["household_id"]

        analysis = client.post(
            f"/households/{household_id}/assistant/respond",
            json={"prompt": "Hur ser vår ekonomi ut just nu?"},
        )
        assert analysis.status_code == 503
        assert "OPENAI_API_KEY" in analysis.json()["detail"]

        ingest = client.post(
            f"/households/{household_id}/ingest_ai/analyze",
            json={"input_text": "2026-04-01 GYM AB -299,00", "input_kind": "bank_copy_paste"},
        )
        assert ingest.status_code == 503
        assert "OPENAI_API_KEY" in ingest.json()["detail"]


def test_extract_text_from_upload_handles_text_and_pdf_branches(monkeypatch):
    from app.ingest_content import extract_text_from_upload

    text_result = extract_text_from_upload(b"  Rad 1\nRad 2  ", file_name="note.txt", mime_type="text/plain")
    assert text_result.text == "Rad 1\nRad 2"
    assert text_result.extraction_mode == "text_file"

    class FakePage:
        def extract_text(self):
            return "  Faktura april\n  Resurs Bank  \n  299 kr  "

    class FakeReader:
        def __init__(self, _stream):
            self.pages = [FakePage()]

    monkeypatch.setattr("app.ingest_content.PdfReader", FakeReader)
    pdf_result = extract_text_from_upload(b"%PDF-1.4 fake", file_name="invoice.pdf", mime_type="application/pdf")
    assert "Faktura april" in pdf_result.text
    assert pdf_result.extraction_mode == "pdf_text"
    assert any("PDF" in note for note in pdf_result.notes)


def test_ingest_analyze_returns_document_summary_and_review_groups(tmp_path, monkeypatch):
    app = load_app(tmp_path)
    from app import ai_services
    from app import schemas

    app_response = ai_services.IngestStructuredOutput(
        classification=ai_services.IngestDocumentClassificationOutput(
            document_type="invoice",
            provider_name="Resurs Bank",
            label="Resurs Bank faktura april",
            amount=299.0,
            currency="SEK",
            due_date="2026-04-12",
            cadence="monthly",
            category_hint="subscription",
            suggested_target_entity_type="recurring_cost",
            household_relevance="high",
            confidence=0.94,
            confirmed_fields=["provider_name", "amount", "due_date"],
            notes=["Belopp och förfallodag framgår tydligt."],
            uncertainty_reasons=["Cadence bygger på textens månadslogik."],
        ),
        summary="Det här ser ut som en återkommande faktura för ett hushåll.",
        guidance=["Skapa ett reviewutkast om kostnaden är hushållsrelevant."],
        suggestions=[
            ai_services.IngestStructuredSuggestion(
                target_entity_type="recurring_cost",
                review_bucket="recurring_cost",
                title="Resurs Bank - återkommande kostnad",
                rationale="Månadsfaktura med tydligt belopp.",
                confidence=0.91,
                proposed_json='{"household_id": 1, "category": "debt", "amount": 299, "frequency": "monthly", "vendor": "Resurs Bank", "mandatory": true, "variability_class": "fixed", "controllability": "locked"}',
                uncertainty_notes=["Beloppet verkar vara totalbeloppet."],
            )
        ],
    )

    def fake_call_openai_structured(*_args, **_kwargs):
        return app_response, "gpt-test", schemas.AIUsageRead(input_tokens=120, output_tokens=60, total_tokens=180)

    monkeypatch.setattr(ai_services, "_call_openai_structured", fake_call_openai_structured)

    with TestClient(app) as client:
        ids = create_household_fixture(client)
        household_id = ids["household_id"]

        document = client.post(
            "/documents",
            json={
                "household_id": household_id,
                "document_type": "invoice",
                "file_name": "resurs.pdf",
                "mime_type": "application/pdf",
                "extracted_text": "Resurs Bank faktura april 299 kr förfaller 2026-04-12.",
            },
        )
        assert document.status_code == 201
        document_id = document.json()["id"]

        response = client.post(
            f"/households/{household_id}/ingest_ai/analyze",
            json={
                "document_id": document_id,
                "source_channel": "uploaded_pdf",
                "source_name": "Resurs Bank",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["document_summary"]["document_type"] == "invoice"
        assert payload["document_summary"]["provider_name"] == "Resurs Bank"
        assert payload["document_summary"]["confirmed_fields"] == ["provider_name", "amount", "due_date"]
        assert payload["document_summary"]["confidence"] == 0.94
        assert payload["suggestions"][0]["review_bucket"] == "recurring_cost"
        assert payload["review_groups"][0]["suggestion_count"] == 1
        assert payload["input_details"]["source_channel"] == "uploaded_pdf"
        assert payload["input_details"]["document_id"] == document_id
        assert payload["future_image_readiness"]["supported"] is False


def test_ingest_analyze_ignores_invalid_due_date_from_model(tmp_path, monkeypatch):
    app = load_app(tmp_path)
    from app import ai_services
    from app import schemas

    app_response = ai_services.IngestStructuredOutput(
        classification=ai_services.IngestDocumentClassificationOutput(
            document_type="invoice",
            provider_name="Oklart AB",
            label="Stökig faktura",
            amount=87.5,
            currency="EUR",
            due_date="not-a-date",
            cadence="monthly",
            category_hint="unknown",
            suggested_target_entity_type="recurring_cost",
            household_relevance="medium",
            confidence=0.61,
            confirmed_fields=["provider_name", "amount", "currency"],
            notes=["Texten är osäker."],
            uncertainty_reasons=["Datumet kunde inte läsas säkert."],
        ),
        summary="Osäker faktura.",
        guidance=["Behandla som osäkert underlag."],
        suggestions=[],
    )

    def fake_call_openai_structured(*_args, **_kwargs):
        return app_response, "gpt-test", schemas.AIUsageRead(input_tokens=80, output_tokens=40, total_tokens=120)

    monkeypatch.setattr(ai_services, "_call_openai_structured", fake_call_openai_structured)

    with TestClient(app) as client:
        ids = create_household_fixture(client)
        household_id = ids["household_id"]

        response = client.post(
            f"/households/{household_id}/ingest_ai/analyze",
            json={
                "input_text": "Kund: ACME. Betala helst snart. Något med 87,50 EUR, kanske månadsvis?",
                "input_kind": "pdf_text",
                "source_channel": "pdf_text",
                "source_name": "Oklart underlag",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["document_summary"]["due_date"] is None
        assert any("förfallodatum" in item.lower() for item in payload["document_summary"]["uncertainty_reasons"])


def test_ingest_promote_reuses_existing_document_id(tmp_path):
    app = load_app(tmp_path)
    with TestClient(app) as client:
        ids = create_household_fixture(client)
        household_id = ids["household_id"]
        recurring_before = client.get("/recurring_costs?skip=0&limit=100")
        assert recurring_before.status_code == 200
        recurring_before_count = len([item for item in recurring_before.json() if item["household_id"] == household_id])

        document = client.post(
            "/documents",
            json={
                "household_id": household_id,
                "document_type": "invoice",
                "file_name": "existing.txt",
                "mime_type": "text/plain",
                "extracted_text": "Resurs Bank faktura april 299 kr förfaller 2026-04-12.",
            },
        )
        assert document.status_code == 201
        document_id = document.json()["id"]

        suggestion = {
            "target_entity_type": "recurring_cost",
            "review_bucket": "recurring_cost",
            "title": "Resurs Bank - återkommande kostnad",
            "rationale": "Tydlig månadsfaktura.",
            "confidence": 0.9,
            "proposed_json": {
                "household_id": household_id,
                "category": "debt",
                "amount": 299,
                "frequency": "monthly",
                "vendor": "Resurs Bank",
                "mandatory": True,
                "variability_class": "fixed",
                "controllability": "locked",
            },
            "validation_status": "valid",
            "validation_errors": [],
            "uncertainty_notes": ["Viss avrundning kan förekomma."],
        }

        response = client.post(
            f"/households/{household_id}/ingest_ai/promote",
            json={
                "document_id": document_id,
                "source_channel": "uploaded_document",
                "source_name": "Resurs Bank",
                "provider": "openai",
                "model": "gpt-test",
                "document_summary": {
                    "document_type": "invoice",
                    "provider_name": "Resurs Bank",
                    "label": "Resurs Bank faktura april",
                    "amount": 299,
                    "currency": "SEK",
                    "due_date": "2026-04-12",
                    "cadence": "monthly",
                    "category_hint": "subscription",
                    "suggested_target_entity_type": "recurring_cost",
                    "household_relevance": "high",
                    "confidence": 0.94,
                    "confirmed_fields": ["provider_name", "amount", "due_date"],
                    "notes": ["Beloppet är tydligt."],
                    "uncertainty_reasons": ["Cadence är tolkad."],
                },
                "suggestions": [suggestion],
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["document_id"] == document_id
        assert payload["document_type"] == "invoice"
        assert payload["created_drafts"][0]["validation_status"] == "valid"

        documents = client.get("/documents?skip=0&limit=100")
        assert documents.status_code == 200
        household_documents = [item for item in documents.json() if item["household_id"] == household_id]
        assert len(household_documents) == 1

        drafts = client.get("/extraction_drafts?skip=0&limit=100")
        assert drafts.status_code == 200
        household_drafts = [item for item in drafts.json() if item["household_id"] == household_id]
        assert len(household_drafts) == 1

        recurring_after = client.get("/recurring_costs?skip=0&limit=100")
        assert recurring_after.status_code == 200
        recurring_after_count = len([item for item in recurring_after.json() if item["household_id"] == household_id])
        assert recurring_after_count == recurring_before_count


def test_ingest_analyze_rejects_image_placeholder(tmp_path):
    app = load_app(tmp_path)
    with TestClient(app) as client:
        ids = create_household_fixture(client)
        household_id = ids["household_id"]

        response = client.post(
            f"/households/{household_id}/ingest_ai/analyze",
            json={"input_text": "något", "source_channel": "image_placeholder"},
        )
        assert response.status_code == 501
        assert "bild" in response.json()["detail"].lower()


def test_document_upload_marks_image_as_ocr_pending(tmp_path):
    app = load_app(tmp_path)
    with TestClient(app) as client:
        ids = create_household_fixture(client)
        household_id = ids["household_id"]

        upload = client.post(
            "/documents/upload",
            data={"household_id": str(household_id), "document_type": "receipt", "issuer": "Telefon"},
            files={"file": ("screen.png", io.BytesIO(b"\x89PNG\r\n\x1a\nfake"), "image/png")},
        )
        assert upload.status_code == 201
        payload = upload.json()
        assert payload["extracted_text"] is None
        assert payload["extraction_status"] == "ocr_pending"


def test_normalize_ingest_text_handles_pdf_paste_artifacts():
    from app.ingest_content import normalize_ingest_text

    raw = "Faktura\u00a0123\r\nBelopp:\u200b 1\u00a0500,00\fSida 2\r\nLeverantör: Test AB"
    result = normalize_ingest_text(raw)
    assert "\u00a0" not in result
    assert "\u200b" not in result
    assert "\f" not in result
    assert "Faktura 123" in result
    assert "Sida 2" in result


def test_detect_input_hints_finds_invoice_keywords():
    from app.ingest_content import detect_input_hints

    invoice_text = "Faktura 2026-04-01\nFörfallodatum: 2026-04-30\nBelopp: 1 299,00 SEK\nBankgiro: 123-4567"
    hints = detect_input_hints(invoice_text)
    assert "invoice_keywords" in hints
    assert "iso_dates" in hints
    assert "swedish_amounts" in hints


def test_detect_input_hints_finds_subscription_keywords():
    from app.ingest_content import detect_input_hints

    sub_text = "Abonnemang: Telia Bredband\nBindningstid: 24 månader\nKostnad: 399 kr/mån"
    hints = detect_input_hints(sub_text)
    assert "subscription_keywords" in hints
    assert "monthly_cost_pattern" in hints


def test_detect_input_hints_returns_empty_for_generic_text():
    from app.ingest_content import detect_input_hints

    hints = detect_input_hints("Hej, detta är en generisk text utan specifika nyckelord.")
    assert hints == []


def test_ingest_analyze_includes_input_hints_in_payload(tmp_path, monkeypatch):
    app = load_app(tmp_path)
    from app import ai_services
    from app import schemas

    captured_payload = {}

    app_response = ai_services.IngestStructuredOutput(
        classification=ai_services.IngestDocumentClassificationOutput(
            document_type="invoice",
            provider_name="Telia",
            label="Telia faktura",
            amount=399.0,
            currency="SEK",
            due_date="2026-04-30",
            cadence="monthly",
            category_hint="broadband",
            suggested_target_entity_type="subscription_contract",
            household_relevance="high",
            confidence=0.88,
            confirmed_fields=["provider_name", "amount", "currency"],
            notes=["Bredbandsabonnemang med tydligt belopp."],
            uncertainty_reasons=["Bindningstiden tolkas från text."],
        ),
        summary="En faktura för ett bredbandsabonnemang hos Telia.",
        guidance=["Tydligt abonnemang. Granska om bindningstid stämmer."],
        suggestions=[
            ai_services.IngestStructuredSuggestion(
                target_entity_type="subscription_contract",
                review_bucket="subscription_contract",
                title="Telia Bredband",
                rationale="Tydlig faktura med månatlig kostnad.",
                confidence=0.85,
                proposed_json='{"household_id": 1, "category": "broadband", "provider": "Telia", "current_monthly_cost": 399, "billing_frequency": "monthly"}',
                uncertainty_notes=["Bindningstid tolkas som 24 månader."],
            )
        ],
    )

    original_call = ai_services._call_openai_structured

    def fake_call_openai_structured(settings, *, model, instructions, payload, response_model, schema_name, max_output_tokens):
        captured_payload.update(payload)
        return app_response, "gpt-test", schemas.AIUsageRead(input_tokens=150, output_tokens=80, total_tokens=230)

    monkeypatch.setattr(ai_services, "_call_openai_structured", fake_call_openai_structured)

    with TestClient(app) as client:
        ids = create_household_fixture(client)
        household_id = ids["household_id"]

        response = client.post(
            f"/households/{household_id}/ingest_ai/analyze",
            json={
                "input_text": "Faktura 2026-04-01\nTelia Bredband\nKostnad: 399 kr/mån\nFörfallodatum: 2026-04-30",
                "input_kind": "text",
                "source_channel": "text",
                "source_name": "Telia",
            },
        )
        assert response.status_code == 200
        assert "input_hints" in captured_payload
        assert "invoice_keywords" in captured_payload["input_hints"]
        assert "monthly_cost_pattern" in captured_payload["input_hints"]

        payload = response.json()
        assert payload["document_summary"]["document_type"] == "invoice"
        assert payload["document_summary"]["provider_name"] == "Telia"
        assert payload["document_summary"]["amount"] == 399.0
        assert payload["suggestions"][0]["review_bucket"] == "subscription_contract"
