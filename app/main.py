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

    uvicorn economic_system.app.main:app --reload

The ``init_db`` function will ensure that database tables are created on
application startup. The database connection URL can be configured via
the ``DATABASE_URL`` environment variable. When deploying behind a
reverse proxy or within a Tailscale network, ensure that appropriate
authentication and transport security is applied at the proxy layer.
"""

from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import database, models, schemas

app = FastAPI(title="Household Economics Backend", version="0.1.0")

# Allow all CORS origins by default. In production you should set this
# to the specific origins used by your frontend (e.g. http://localhost:3000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    database.init_db()


def get_object_or_404(db: Session, model, obj_id: int):
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model.__name__} with id {obj_id} not found")
    return obj


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


@app.get("/documents/{doc_id}", response_model=schemas.DocumentRead)
def read_document(doc_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Document, doc_id)


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