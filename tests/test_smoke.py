import importlib
import io
import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect


def load_app(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["UPLOAD_DIR"] = str(tmp_path / "uploads")

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
        assert "Hushållsekonomi" in response.text


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
