"""
FastAPI application entry point for the household economics backend.

This module wires together the database, models, schemas and API routes to
expose a RESTful interface for manipulating the core domain objects defined
in ``models.py``. Each entity has endpoints for listing, creating,
retrieving, updating and deleting records. The API is intentionally
minimalistic and CRUD-focused in order to provide a solid foundation for
future business logic, calculations and integrations. More complex
operations (e.g. scenario simulation or optimization) should be added in
dedicated routes or services without polluting basic CRUD handlers.

Usage::

    uvicorn app.main:app --reload

The ``init_db`` function will ensure that database tables are created on
application startup. The database connection URL can be configured via
the ``DATABASE_URL`` environment variable. When deploying behind a
reverse proxy or within a Tailscale network, ensure that appropriate
authentication and transport security is applied at the proxy layer.
"""

import hashlib
from datetime import date
from pathlib import Path
from uuid import uuid4
from typing import List

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import ai_services, calculations, database, models, pdf_export, schemas
from .ingest_content import extract_text_from_upload, normalize_ingest_text
from .settings import get_settings

settings = get_settings()
app = FastAPI(title="Household Economics Backend", version="0.1.0")
STATIC_ROOT = Path(__file__).resolve().parent / "static"
UPLOAD_ROOT = Path(settings.upload_dir).resolve()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency that provides a database session per request. The session
# is cleaned up automatically once the request is finished. If you
# require transactional behaviour across multiple requests you should
# implement that at a higher abstraction level.
def get_db() -> Session:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    """Initialise the database on application startup."""
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    database.init_db()


def get_object_or_404(db: Session, model, obj_id: int):
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model.__name__} with id {obj_id} not found")
    return obj


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/system/validation_markdown", include_in_schema=False)
def system_validation_markdown():
    return FileResponse(Path(__file__).resolve().parents[1] / "docs" / "SYSTEM_VALIDATION.md")

if STATIC_ROOT.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_ROOT), name="assets")


@app.get("/")
def home():
    return FileResponse(STATIC_ROOT / "index.html")


def ensure_household_exists(db: Session, household_id: int):
    return get_object_or_404(db, models.Household, household_id)


def upload_to_disk(household_id: int, file: UploadFile) -> tuple[str, str, bytes]:
    household_dir = UPLOAD_ROOT / str(household_id)
    household_dir.mkdir(parents=True, exist_ok=True)
    raw = file.file.read()
    checksum = hashlib.sha256(raw).hexdigest()
    safe_name = f"{uuid4().hex}_{Path(file.filename or 'document.bin').name}"
    destination = household_dir / safe_name
    destination.write_bytes(raw)
    return str(destination.resolve()), checksum, raw


def draft_target_config(target_entity_type: str):
    mapping = {
        "person": (schemas.PersonCreate, models.Person),
        "income_source": (schemas.IncomeSourceCreate, models.IncomeSource),
        "loan": (schemas.LoanCreate, models.Loan),
        "recurring_cost": (schemas.RecurringCostCreate, models.RecurringCost),
        "subscription_contract": (schemas.SubscriptionContractCreate, models.SubscriptionContract),
        "insurance_policy": (schemas.InsurancePolicyCreate, models.InsurancePolicy),
        "vehicle": (schemas.VehicleCreate, models.Vehicle),
        "asset": (schemas.AssetCreate, models.Asset),
        "housing_scenario": (schemas.HousingScenarioCreate, models.HousingScenario),
        "document": (schemas.DocumentCreate, models.Document),
        "optimization_opportunity": (schemas.OptimizationOpportunityCreate, models.OptimizationOpportunity),
        "scenario": (schemas.ScenarioCreate, models.Scenario),
        "scenario_result": (schemas.ScenarioResultCreate, models.ScenarioResult),
        "report_snapshot": (schemas.ReportSnapshotCreate, models.ReportSnapshot),
    }
    normalized = target_entity_type.strip().lower()
    if normalized not in mapping:
        raise HTTPException(status_code=400, detail=f"Unsupported draft target_entity_type: {target_entity_type}")
    return mapping[normalized], normalized

def create_or_get_opportunity(
    db: Session,
    household_id: int,
    *,
    kind: str,
    target_entity_type: str,
    target_entity_id: int,
    title: str,
    rationale: str,
    estimated_monthly_saving: float,
    confidence: float,
):
    existing = (
        db.query(models.OptimizationOpportunity)
        .filter_by(
            household_id=household_id,
            kind=kind,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            title=title,
            status="open",
        )
        .first()
    )
    if existing:
        return existing

    opportunity = models.OptimizationOpportunity(
        household_id=household_id,
        kind=kind,
        target_entity_type=target_entity_type,
        target_entity_id=target_entity_id,
        title=title,
        rationale=rationale,
        estimated_monthly_saving=round(estimated_monthly_saving, 2),
        estimated_yearly_saving=round(estimated_monthly_saving * 12, 2),
        confidence=confidence,
        effort_level="medium",
        risk_level="low" if kind == "cancel" else "medium",
        reversibility="high",
        status="open",
    )
    db.add(opportunity)
    db.flush()
    return opportunity


# --- Household Endpoints ---
@app.get("/households", response_model=List[schemas.HouseholdRead])
def list_households(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Household).offset(skip).limit(limit).all()


@app.post("/households", response_model=schemas.HouseholdRead, status_code=status.HTTP_201_CREATED)
def create_household(household: schemas.HouseholdCreate, db: Session = Depends(get_db)):
    db_household = models.Household(**household.dict())
    db.add(db_household)
    db.commit()
    db.refresh(db_household)
    return db_household


@app.get("/households/{household_id}", response_model=schemas.HouseholdRead)
def read_household(household_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Household, household_id)


@app.put("/households/{household_id}", response_model=schemas.HouseholdRead)
def update_household(household_id: int, household: schemas.HouseholdUpdate, db: Session = Depends(get_db)):
    db_household = get_object_or_404(db, models.Household, household_id)
    for field, value in household.dict(exclude_unset=True).items():
        setattr(db_household, field, value)
    db.commit()
    db.refresh(db_household)
    return db_household


@app.delete("/households/{household_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_household(household_id: int, db: Session = Depends(get_db)):
    db_household = get_object_or_404(db, models.Household, household_id)
    db.delete(db_household)
    db.commit()
    return


@app.get("/households/{household_id}/summary", response_model=schemas.HouseholdSummaryRead)
def get_household_summary(household_id: int, db: Session = Depends(get_db)):
    ensure_household_exists(db, household_id)
    return calculations.build_household_summary(calculations.load_household_records(db, household_id), household_id)


@app.post("/households/{household_id}/report_snapshots/generate", response_model=schemas.ReportSnapshotRead)
def generate_household_report_snapshot(
    household_id: int,
    request: schemas.ReportGenerateRequest,
    db: Session = Depends(get_db),
):
    ensure_household_exists(db, household_id)
    summary = calculations.build_household_summary(calculations.load_household_records(db, household_id), household_id)
    snapshot = models.ReportSnapshot(
        household_id=household_id,
        type=request.type,
        as_of_date=request.as_of_date or date.today(),
        assumption_json=request.assumption_json,
        result_json=summary,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


@app.get("/households/{household_id}/export/bank_pdf")
def export_bank_pdf(household_id: int, db: Session = Depends(get_db)):
    ensure_household_exists(db, household_id)
    pdf_bytes = pdf_export.generate_bank_pdf(db, household_id)
    household = db.get(models.Household, household_id)
    filename = f"bankkalkyl-{household.name.lower().replace(' ', '-')}-{date.today().isoformat()}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/households/{household_id}/optimization_scan", response_model=List[schemas.OptimizationOpportunityRead])
def optimization_scan(household_id: int, db: Session = Depends(get_db)):
    ensure_household_exists(db, household_id)
    results = []

    subscriptions = db.query(models.SubscriptionContract).filter_by(household_id=household_id).all()
    for subscription in subscriptions:
        if subscription.ordinary_cost and subscription.current_monthly_cost and subscription.ordinary_cost > subscription.current_monthly_cost:
            results.append(
                create_or_get_opportunity(
                    db,
                    household_id,
                    kind="renegotiate",
                    target_entity_type="subscription_contract",
                    target_entity_id=subscription.id,
                    title=f"Review {subscription.provider} pricing",
                    rationale="Ordinary price is above current price and likely worth renegotiating.",
                    estimated_monthly_saving=subscription.ordinary_cost - subscription.current_monthly_cost,
                    confidence=0.72,
                )
            )
        if subscription.household_criticality == "optional" and (subscription.current_monthly_cost or 0) > 0:
            results.append(
                create_or_get_opportunity(
                    db,
                    household_id,
                    kind="cancel",
                    target_entity_type="subscription_contract",
                    target_entity_id=subscription.id,
                    title=f"Cancel optional subscription: {subscription.provider}",
                    rationale="Marked optional and contributes recurring monthly cost.",
                    estimated_monthly_saving=subscription.current_monthly_cost,
                    confidence=0.61,
                )
            )

    recurring_costs = db.query(models.RecurringCost).filter_by(household_id=household_id).all()
    for cost in recurring_costs:
        if cost.controllability in {models.Controllability.reducible, models.Controllability.discretionary}:
            monthly_amount = calculations.amount_to_monthly(cost.amount, cost.frequency)
            if monthly_amount > 0:
                results.append(
                    create_or_get_opportunity(
                        db,
                        household_id,
                        kind="reduce_usage",
                        target_entity_type="recurring_cost",
                        target_entity_id=cost.id,
                        title=f"Reduce {cost.category}",
                        rationale="Cost is marked reducible/discretionary.",
                        estimated_monthly_saving=monthly_amount * 0.15,
                        confidence=0.55,
                    )
                )

    db.commit()
    for item in results:
        db.refresh(item)
    return results


# --- Person Endpoints ---
@app.get("/persons", response_model=List[schemas.PersonRead])
def list_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Person).offset(skip).limit(limit).all()


@app.post("/persons", response_model=schemas.PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    db_person = models.Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


@app.get("/persons/{person_id}", response_model=schemas.PersonRead)
def read_person(person_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Person, person_id)


@app.put("/persons/{person_id}", response_model=schemas.PersonRead)
def update_person(person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)):
    db_person = get_object_or_404(db, models.Person, person_id)
    for field, value in person.dict(exclude_unset=True).items():
        setattr(db_person, field, value)
    db.commit()
    db.refresh(db_person)
    return db_person


@app.delete("/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    db_person = get_object_or_404(db, models.Person, person_id)
    db.delete(db_person)
    db.commit()
    return


# --- IncomeSource Endpoints ---
@app.get("/income_sources", response_model=List[schemas.IncomeSourceRead])
def list_income_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.IncomeSource).offset(skip).limit(limit).all()


@app.post("/income_sources", response_model=schemas.IncomeSourceRead, status_code=status.HTTP_201_CREATED)
def create_income_source(income_source: schemas.IncomeSourceCreate, db: Session = Depends(get_db)):
    db_income = models.IncomeSource(**income_source.dict())
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income


@app.get("/income_sources/{income_id}", response_model=schemas.IncomeSourceRead)
def read_income_source(income_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.IncomeSource, income_id)


@app.put("/income_sources/{income_id}", response_model=schemas.IncomeSourceRead)
def update_income_source(income_id: int, income_source: schemas.IncomeSourceUpdate, db: Session = Depends(get_db)):
    db_income = get_object_or_404(db, models.IncomeSource, income_id)
    for field, value in income_source.dict(exclude_unset=True).items():
        setattr(db_income, field, value)
    db.commit()
    db.refresh(db_income)
    return db_income


@app.delete("/income_sources/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income_source(income_id: int, db: Session = Depends(get_db)):
    db_income = get_object_or_404(db, models.IncomeSource, income_id)
    db.delete(db_income)
    db.commit()
    return


# --- Loan Endpoints ---
@app.get("/loans", response_model=List[schemas.LoanRead])
def list_loans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Loan).offset(skip).limit(limit).all()


@app.post("/loans", response_model=schemas.LoanRead, status_code=status.HTTP_201_CREATED)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    db_loan = models.Loan(**loan.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan


@app.get("/loans/{loan_id}", response_model=schemas.LoanRead)
def read_loan(loan_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Loan, loan_id)


@app.put("/loans/{loan_id}", response_model=schemas.LoanRead)
def update_loan(loan_id: int, loan: schemas.LoanUpdate, db: Session = Depends(get_db)):
    db_loan = get_object_or_404(db, models.Loan, loan_id)
    for field, value in loan.dict(exclude_unset=True).items():
        setattr(db_loan, field, value)
    db.commit()
    db.refresh(db_loan)
    return db_loan


@app.delete("/loans/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    db_loan = get_object_or_404(db, models.Loan, loan_id)
    db.delete(db_loan)
    db.commit()
    return


# --- RecurringCost Endpoints ---
@app.get("/recurring_costs", response_model=List[schemas.RecurringCostRead])
def list_recurring_costs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.RecurringCost).offset(skip).limit(limit).all()


@app.post("/recurring_costs", response_model=schemas.RecurringCostRead, status_code=status.HTTP_201_CREATED)
def create_recurring_cost(cost: schemas.RecurringCostCreate, db: Session = Depends(get_db)):
    db_cost = models.RecurringCost(**cost.dict())
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost


@app.get("/recurring_costs/{cost_id}", response_model=schemas.RecurringCostRead)
def read_recurring_cost(cost_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.RecurringCost, cost_id)


@app.put("/recurring_costs/{cost_id}", response_model=schemas.RecurringCostRead)
def update_recurring_cost(cost_id: int, cost: schemas.RecurringCostUpdate, db: Session = Depends(get_db)):
    db_cost = get_object_or_404(db, models.RecurringCost, cost_id)
    for field, value in cost.dict(exclude_unset=True).items():
        setattr(db_cost, field, value)
    db.commit()
    db.refresh(db_cost)
    return db_cost


@app.delete("/recurring_costs/{cost_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_cost(cost_id: int, db: Session = Depends(get_db)):
    db_cost = get_object_or_404(db, models.RecurringCost, cost_id)
    db.delete(db_cost)
    db.commit()
    return


# --- SubscriptionContract Endpoints ---
@app.get("/subscription_contracts", response_model=List[schemas.SubscriptionContractRead])
def list_subscription_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.SubscriptionContract).offset(skip).limit(limit).all()


@app.post(
    "/subscription_contracts",
    response_model=schemas.SubscriptionContractRead,
    status_code=status.HTTP_201_CREATED,
)
def create_subscription_contract(contract: schemas.SubscriptionContractCreate, db: Session = Depends(get_db)):
    db_contract = models.SubscriptionContract(**contract.dict())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@app.get("/subscription_contracts/{contract_id}", response_model=schemas.SubscriptionContractRead)
def read_subscription_contract(contract_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.SubscriptionContract, contract_id)


@app.put("/subscription_contracts/{contract_id}", response_model=schemas.SubscriptionContractRead)
def update_subscription_contract(contract_id: int, contract: schemas.SubscriptionContractUpdate, db: Session = Depends(get_db)):
    db_contract = get_object_or_404(db, models.SubscriptionContract, contract_id)
    for field, value in contract.dict(exclude_unset=True).items():
        setattr(db_contract, field, value)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@app.delete("/subscription_contracts/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription_contract(contract_id: int, db: Session = Depends(get_db)):
    db_contract = get_object_or_404(db, models.SubscriptionContract, contract_id)
    db.delete(db_contract)
    db.commit()
    return


# --- InsurancePolicy Endpoints ---
@app.get("/insurance_policies", response_model=List[schemas.InsurancePolicyRead])
def list_insurance_policies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.InsurancePolicy).offset(skip).limit(limit).all()


@app.post(
    "/insurance_policies",
    response_model=schemas.InsurancePolicyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_insurance_policy(policy: schemas.InsurancePolicyCreate, db: Session = Depends(get_db)):
    db_policy = models.InsurancePolicy(**policy.dict())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy


@app.get("/insurance_policies/{policy_id}", response_model=schemas.InsurancePolicyRead)
def read_insurance_policy(policy_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.InsurancePolicy, policy_id)


@app.put("/insurance_policies/{policy_id}", response_model=schemas.InsurancePolicyRead)
def update_insurance_policy(policy_id: int, policy: schemas.InsurancePolicyUpdate, db: Session = Depends(get_db)):
    db_policy = get_object_or_404(db, models.InsurancePolicy, policy_id)
    for field, value in policy.dict(exclude_unset=True).items():
        setattr(db_policy, field, value)
    db.commit()
    db.refresh(db_policy)
    return db_policy


@app.delete("/insurance_policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_insurance_policy(policy_id: int, db: Session = Depends(get_db)):
    db_policy = get_object_or_404(db, models.InsurancePolicy, policy_id)
    db.delete(db_policy)
    db.commit()
    return


# --- Vehicle Endpoints ---
@app.get("/vehicles", response_model=List[schemas.VehicleRead])
def list_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Vehicle).offset(skip).limit(limit).all()


@app.post("/vehicles", response_model=schemas.VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = models.Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@app.get("/vehicles/{vehicle_id}", response_model=schemas.VehicleRead)
def read_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Vehicle, vehicle_id)


@app.put("/vehicles/{vehicle_id}", response_model=schemas.VehicleRead)
def update_vehicle(vehicle_id: int, vehicle: schemas.VehicleUpdate, db: Session = Depends(get_db)):
    db_vehicle = get_object_or_404(db, models.Vehicle, vehicle_id)
    for field, value in vehicle.dict(exclude_unset=True).items():
        setattr(db_vehicle, field, value)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@app.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    db_vehicle = get_object_or_404(db, models.Vehicle, vehicle_id)
    db.delete(db_vehicle)
    db.commit()
    return


# --- Asset Endpoints ---
@app.get("/assets", response_model=List[schemas.AssetRead])
def list_assets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Asset).offset(skip).limit(limit).all()


@app.post("/assets", response_model=schemas.AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(get_db)):
    db_asset = models.Asset(**asset.dict())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@app.get("/assets/{asset_id}", response_model=schemas.AssetRead)
def read_asset(asset_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Asset, asset_id)


@app.put("/assets/{asset_id}", response_model=schemas.AssetRead)
def update_asset(asset_id: int, asset: schemas.AssetUpdate, db: Session = Depends(get_db)):
    db_asset = get_object_or_404(db, models.Asset, asset_id)
    for field, value in asset.dict(exclude_unset=True).items():
        setattr(db_asset, field, value)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@app.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    db_asset = get_object_or_404(db, models.Asset, asset_id)
    db.delete(db_asset)
    db.commit()
    return


# --- HousingScenario Endpoints ---
@app.get("/housing_scenarios", response_model=List[schemas.HousingScenarioRead])
def list_housing_scenarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.HousingScenario).offset(skip).limit(limit).all()


@app.post("/housing_scenarios", response_model=schemas.HousingScenarioRead, status_code=status.HTTP_201_CREATED)
def create_housing_scenario(scenario: schemas.HousingScenarioCreate, db: Session = Depends(get_db)):
    db_scenario = models.HousingScenario(**scenario.dict())
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


@app.get("/housing_scenarios/{scenario_id}", response_model=schemas.HousingScenarioRead)
def read_housing_scenario(scenario_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.HousingScenario, scenario_id)


@app.put("/housing_scenarios/{scenario_id}", response_model=schemas.HousingScenarioRead)
def update_housing_scenario(scenario_id: int, scenario: schemas.HousingScenarioUpdate, db: Session = Depends(get_db)):
    db_scenario = get_object_or_404(db, models.HousingScenario, scenario_id)
    for field, value in scenario.dict(exclude_unset=True).items():
        setattr(db_scenario, field, value)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


@app.delete("/housing_scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_housing_scenario(scenario_id: int, db: Session = Depends(get_db)):
    db_scenario = get_object_or_404(db, models.HousingScenario, scenario_id)
    db.delete(db_scenario)
    db.commit()
    return


# --- Document Endpoints ---
@app.get("/documents", response_model=List[schemas.DocumentRead])
def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Document).offset(skip).limit(limit).all()


@app.post("/documents", response_model=schemas.DocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(document: schemas.DocumentCreate, db: Session = Depends(get_db)):
    db_doc = models.Document(**document.dict())
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


@app.post("/documents/upload", response_model=schemas.DocumentRead, status_code=status.HTTP_201_CREATED)
def upload_document(
    household_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    issuer: str | None = Form(None),
    currency: str | None = Form(None),
    extracted_text: str | None = Form(None),
    db: Session = Depends(get_db),
):
    ensure_household_exists(db, household_id)
    storage_path, checksum, raw = upload_to_disk(household_id, file)
    extracted_payload = normalize_ingest_text(extracted_text) if extracted_text and extracted_text.strip() else None
    extraction_status = "parsed"
    if extracted_payload is None:
        auto_extracted = extract_text_from_upload(raw, file_name=file.filename, mime_type=file.content_type)
        extracted_payload = auto_extracted.text
        if extracted_payload:
            extraction_status = "ocr_parsed" if auto_extracted.extraction_mode.startswith("ocr") else "parsed"
        else:
            extraction_status = {
                "ocr_not_implemented": "ocr_pending",
                "ocr_image_unreadable": "parse_failed",
                "ocr_tesseract_missing": "ocr_pending",
                "ocr_failed": "parse_failed",
                "ocr_no_text": "parse_failed",
                "ocr_missing_dependency": "ocr_pending",
                "unsupported_binary": "unsupported",
                "pdf_unreadable": "parse_failed",
                "pdf_no_text": "parse_failed",
            }.get(auto_extracted.extraction_mode, "pending")
    document = models.Document(
        household_id=household_id,
        document_type=document_type,
        file_name=file.filename or "uploaded-file",
        mime_type=file.content_type,
        checksum=checksum,
        issuer=issuer,
        currency=currency,
        extracted_text=extracted_payload,
        extraction_status=extraction_status,
        storage_path=storage_path,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@app.get("/documents/{doc_id}", response_model=schemas.DocumentRead)
def read_document(doc_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Document, doc_id)


@app.get("/documents/{doc_id}/download", include_in_schema=False)
def download_document(doc_id: int, db: Session = Depends(get_db)):
    document = get_object_or_404(db, models.Document, doc_id)
    if not document.storage_path:
        raise HTTPException(status_code=404, detail="Document has no stored file")
    file_path = Path(document.storage_path)
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Stored file not found")
    return FileResponse(file_path, filename=document.file_name, media_type=document.mime_type)


@app.put("/documents/{doc_id}", response_model=schemas.DocumentRead)
def update_document(doc_id: int, document: schemas.DocumentUpdate, db: Session = Depends(get_db)):
    db_doc = get_object_or_404(db, models.Document, doc_id)
    for field, value in document.dict(exclude_unset=True).items():
        setattr(db_doc, field, value)
    db.commit()
    db.refresh(db_doc)
    return db_doc


@app.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    db_doc = get_object_or_404(db, models.Document, doc_id)
    db.delete(db_doc)
    db.commit()
    return


# --- ExtractionDraft Endpoints ---
@app.get("/extraction_drafts", response_model=List[schemas.ExtractionDraftRead])
def list_extraction_drafts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.ExtractionDraft).offset(skip).limit(limit).all()


@app.post("/extraction_drafts", response_model=schemas.ExtractionDraftRead, status_code=status.HTTP_201_CREATED)
def create_extraction_draft(draft: schemas.ExtractionDraftCreate, db: Session = Depends(get_db)):
    db_draft = models.ExtractionDraft(**draft.dict())
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    return db_draft


@app.get("/extraction_drafts/{draft_id}", response_model=schemas.ExtractionDraftRead)
def read_extraction_draft(draft_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.ExtractionDraft, draft_id)


@app.put("/extraction_drafts/{draft_id}", response_model=schemas.ExtractionDraftRead)
def update_extraction_draft(draft_id: int, draft: schemas.ExtractionDraftUpdate, db: Session = Depends(get_db)):
    db_draft = get_object_or_404(db, models.ExtractionDraft, draft_id)
    for field, value in draft.dict(exclude_unset=True).items():
        setattr(db_draft, field, value)
    db.commit()
    db.refresh(db_draft)
    return db_draft


@app.post("/extraction_drafts/{draft_id}/apply", response_model=schemas.ExtractionApplyRead)
def apply_extraction_draft(draft_id: int, db: Session = Depends(get_db)):
    draft = get_object_or_404(db, models.ExtractionDraft, draft_id)
    if draft.status == "approved":
        raise HTTPException(status_code=400, detail="Draft already approved")

    (schema_class, model_class), normalized = draft_target_config(draft.target_entity_type)
    proposed = dict(draft.proposed_json or {})
    if "household_id" in getattr(schema_class, "__fields__", {}) and "household_id" not in proposed:
        proposed["household_id"] = draft.household_id
    payload = schema_class(**proposed)
    entity = model_class(**payload.dict())
    db.add(entity)
    db.flush()
    draft.status = "approved"
    db.commit()
    return {
        "draft_id": draft.id,
        "target_entity_type": normalized,
        "target_entity_id": entity.id,
        "status": draft.status,
    }


@app.delete("/extraction_drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_extraction_draft(draft_id: int, db: Session = Depends(get_db)):
    db_draft = get_object_or_404(db, models.ExtractionDraft, draft_id)
    db.delete(db_draft)
    db.commit()
    return


# --- OptimizationOpportunity Endpoints ---
@app.get("/optimization_opportunities", response_model=List[schemas.OptimizationOpportunityRead])
def list_optimization_opportunities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.OptimizationOpportunity).offset(skip).limit(limit).all()


@app.post(
    "/optimization_opportunities",
    response_model=schemas.OptimizationOpportunityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_optimization_opportunity(op: schemas.OptimizationOpportunityCreate, db: Session = Depends(get_db)):
    db_op = models.OptimizationOpportunity(**op.dict())
    db.add(db_op)
    db.commit()
    db.refresh(db_op)
    return db_op


@app.get("/optimization_opportunities/{op_id}", response_model=schemas.OptimizationOpportunityRead)
def read_optimization_opportunity(op_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.OptimizationOpportunity, op_id)


@app.put("/optimization_opportunities/{op_id}", response_model=schemas.OptimizationOpportunityRead)
def update_optimization_opportunity(op_id: int, op: schemas.OptimizationOpportunityUpdate, db: Session = Depends(get_db)):
    db_op = get_object_or_404(db, models.OptimizationOpportunity, op_id)
    for field, value in op.dict(exclude_unset=True).items():
        setattr(db_op, field, value)
    db.commit()
    db.refresh(db_op)
    return db_op


@app.delete("/optimization_opportunities/{op_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_optimization_opportunity(op_id: int, db: Session = Depends(get_db)):
    db_op = get_object_or_404(db, models.OptimizationOpportunity, op_id)
    db.delete(db_op)
    db.commit()
    return


# --- Scenario Endpoints ---
@app.get("/scenarios", response_model=List[schemas.ScenarioRead])
def list_scenarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Scenario).offset(skip).limit(limit).all()


@app.post("/scenarios", response_model=schemas.ScenarioRead, status_code=status.HTTP_201_CREATED)
def create_scenario(scenario: schemas.ScenarioCreate, db: Session = Depends(get_db)):
    db_scenario = models.Scenario(**scenario.dict())
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


@app.get("/scenarios/{scenario_id}", response_model=schemas.ScenarioRead)
def read_scenario(scenario_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Scenario, scenario_id)


@app.post("/scenarios/{scenario_id}/run", response_model=schemas.ScenarioResultRead)
def run_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = get_object_or_404(db, models.Scenario, scenario_id)
    baseline_records = calculations.load_household_records(db, scenario.household_id)
    projected_records = calculations.apply_scenario_adjustments(
        baseline_records, list((scenario.change_set_json or {}).get("adjustments", []))
    )
    baseline_summary = calculations.build_household_summary(baseline_records, scenario.household_id)
    projected_summary = calculations.build_household_summary(projected_records, scenario.household_id)

    result = models.ScenarioResult(
        household_id=scenario.household_id,
        scenario_id=scenario.id,
        result_json={
            "baseline": baseline_summary,
            "projected": projected_summary,
            "adjustments": list((scenario.change_set_json or {}).get("adjustments", [])),
        },
        monthly_delta=round(projected_summary["monthly_net_cashflow"] - baseline_summary["monthly_net_cashflow"], 2),
        yearly_delta=round(projected_summary["yearly_net_cashflow"] - baseline_summary["yearly_net_cashflow"], 2),
        liquidity_delta=round(projected_summary["asset_liquid_value"] - baseline_summary["asset_liquid_value"], 2),
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@app.put("/scenarios/{scenario_id}", response_model=schemas.ScenarioRead)
def update_scenario(scenario_id: int, scenario: schemas.ScenarioUpdate, db: Session = Depends(get_db)):
    db_scenario = get_object_or_404(db, models.Scenario, scenario_id)
    for field, value in scenario.dict(exclude_unset=True).items():
        setattr(db_scenario, field, value)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


@app.delete("/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    db_scenario = get_object_or_404(db, models.Scenario, scenario_id)
    db.delete(db_scenario)
    db.commit()
    return


# --- ScenarioResult Endpoints ---
@app.get("/scenario_results", response_model=List[schemas.ScenarioResultRead])
def list_scenario_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.ScenarioResult).offset(skip).limit(limit).all()


@app.post("/scenario_results", response_model=schemas.ScenarioResultRead, status_code=status.HTTP_201_CREATED)
def create_scenario_result(result: schemas.ScenarioResultCreate, db: Session = Depends(get_db)):
    db_result = models.ScenarioResult(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


@app.get("/scenario_results/{result_id}", response_model=schemas.ScenarioResultRead)
def read_scenario_result(result_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.ScenarioResult, result_id)


@app.put("/scenario_results/{result_id}", response_model=schemas.ScenarioResultRead)
def update_scenario_result(result_id: int, result: schemas.ScenarioResultUpdate, db: Session = Depends(get_db)):
    db_result = get_object_or_404(db, models.ScenarioResult, result_id)
    for field, value in result.dict(exclude_unset=True).items():
        setattr(db_result, field, value)
    db.commit()
    db.refresh(db_result)
    return db_result


@app.delete("/scenario_results/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario_result(result_id: int, db: Session = Depends(get_db)):
    db_result = get_object_or_404(db, models.ScenarioResult, result_id)
    db.delete(db_result)
    db.commit()
    return


# --- ReportSnapshot Endpoints ---
@app.get("/report_snapshots", response_model=List[schemas.ReportSnapshotRead])
def list_report_snapshots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.ReportSnapshot).offset(skip).limit(limit).all()


@app.post(
    "/report_snapshots",
    response_model=schemas.ReportSnapshotRead,
    status_code=status.HTTP_201_CREATED,
)
def create_report_snapshot(snapshot: schemas.ReportSnapshotCreate, db: Session = Depends(get_db)):
    db_snapshot = models.ReportSnapshot(**snapshot.dict())
    db.add(db_snapshot)
    db.commit()
    db.refresh(db_snapshot)
    return db_snapshot


@app.get("/report_snapshots/{snapshot_id}", response_model=schemas.ReportSnapshotRead)
def read_report_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.ReportSnapshot, snapshot_id)


@app.put("/report_snapshots/{snapshot_id}", response_model=schemas.ReportSnapshotRead)
def update_report_snapshot(snapshot_id: int, snapshot: schemas.ReportSnapshotUpdate, db: Session = Depends(get_db)):
    db_snapshot = get_object_or_404(db, models.ReportSnapshot, snapshot_id)
    for field, value in snapshot.dict(exclude_unset=True).items():
        setattr(db_snapshot, field, value)
    db.commit()
    db.refresh(db_snapshot)
    return db_snapshot


@app.delete("/report_snapshots/{snapshot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    db_snapshot = get_object_or_404(db, models.ReportSnapshot, snapshot_id)
    db.delete(db_snapshot)
    db.commit()
    return


@app.get("/housing_scenarios/{scenario_id}/evaluate", response_model=schemas.HousingScenarioEvaluationRead)
def evaluate_housing_scenario_endpoint(scenario_id: int, db: Session = Depends(get_db)):
    scenario = get_object_or_404(db, models.HousingScenario, scenario_id)
    return calculations.evaluate_housing_scenario(scenario)


@app.post(
    "/households/{household_id}/assistant/respond",
    response_model=schemas.AssistantPromptResponse,
)
def household_assistant_respond(
    household_id: int,
    request_body: schemas.AssistantPromptRequest,
    db: Session = Depends(get_db),
):
    ensure_household_exists(db, household_id)
    try:
        answer, model_name, usage = ai_services.generate_analysis_answer(
            db,
            household_id,
            request_body.prompt,
            settings,
        )
    except ai_services.AIProviderUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except ai_services.AIProviderResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return {
        "household_id": household_id,
        "prompt": request_body.prompt,
        "answer": answer,
        "provider": "openai",
        "model": model_name,
        "usage": usage,
    }


@app.post(
    "/households/{household_id}/ingest_ai/analyze",
    response_model=schemas.IngestAnalyzeResponse,
)
def household_ingest_ai_analyze(
    household_id: int,
    request_body: schemas.IngestAnalyzeRequest,
    db: Session = Depends(get_db),
):
    ensure_household_exists(db, household_id)
    try:
        response, _ = ai_services.analyze_ingest_input(
            db,
            household_id,
            input_text=request_body.input_text,
            input_kind=request_body.input_kind or "unknown",
            source_channel=request_body.source_channel,
            document_id=request_body.document_id,
            source_name=request_body.source_name,
            settings=settings,
        )
        return response
    except ai_services.AIProviderUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except ai_services.AIInputNotSupportedError as exc:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(exc)) from exc
    except ai_services.AIProviderResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@app.post(
    "/households/{household_id}/ingest_ai/promote",
    response_model=schemas.IngestPromoteResponse,
)
def household_ingest_ai_promote(
    household_id: int,
    request_body: schemas.IngestPromoteRequest,
    db: Session = Depends(get_db),
):
    ensure_household_exists(db, household_id)
    try:
        return ai_services.promote_ingest_suggestions(db, household_id, request_body)
    except ai_services.AIInputNotSupportedError as exc:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(exc)) from exc
    except ai_services.AIProviderResponseError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.get("/{frontend_path:path}", include_in_schema=False)
def frontend_app(frontend_path: str):
    if frontend_path.startswith("assets/"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FileResponse(STATIC_ROOT / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=False)
