"""
Pydantic schemas used for validation and serialization of API payloads.

Each SQLAlchemy model defined in ``models.py`` has a corresponding pair
of Pydantic models: one for incoming data (``Create`` / ``Update``) and
one for outgoing data (``Read``). Create/Update models omit primary key
fields so that clients cannot set them. Read models include all columns
and enable ``orm_mode`` so that they can be constructed directly from
SQLAlchemy ORM objects.

Complex nested relationships are not included in the default schemas to
avoid deep recursion and large payloads. Endpoints can provide richer
responses by composing nested schemas explicitly.
"""

from datetime import date, datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field

from .models import IncomeFrequency, LoanRepaymentModel, VariabilityClass, Controllability, SubscriptionCategory


# -------- Household --------
class HouseholdBase(BaseModel):
    name: str
    currency: Optional[str] = Field(default="SEK")
    primary_country: Optional[str] = Field(default="SE")


class HouseholdCreate(HouseholdBase):
    pass


class HouseholdUpdate(HouseholdBase):
    pass


class HouseholdRead(HouseholdBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------- Person --------
class PersonBase(BaseModel):
    household_id: int
    name: str
    role: Optional[str] = Field(default="self")
    income_share_mode: Optional[str] = Field(default="pooled")
    active: Optional[bool] = Field(default=True)


class PersonCreate(PersonBase):
    pass


class PersonUpdate(PersonBase):
    pass


class PersonRead(PersonBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------- IncomeSource --------
class IncomeSourceBase(BaseModel):
    person_id: int
    type: str
    gross_amount: Optional[float] = None
    net_amount: Optional[float] = None
    frequency: IncomeFrequency = IncomeFrequency.monthly
    regularity: Optional[str] = Field(default="fixed")
    source: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    verified: Optional[bool] = False
    verification_doc_id: Optional[int] = None
    note: Optional[str] = None


class IncomeSourceCreate(IncomeSourceBase):
    pass


class IncomeSourceUpdate(IncomeSourceBase):
    pass


class IncomeSourceRead(IncomeSourceBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------- Loan --------
class LoanBase(BaseModel):
    household_id: int
    person_id: Optional[int] = None
    type: str
    lender: Optional[str] = None
    original_amount: Optional[float] = None
    current_balance: Optional[float] = None
    nominal_rate: Optional[float] = None
    effective_rate: Optional[float] = None
    repayment_model: LoanRepaymentModel = LoanRepaymentModel.annuity
    required_monthly_payment: Optional[float] = None
    amortization_amount_monthly: Optional[float] = None
    due_day: Optional[int] = None
    fixed_rate_until: Optional[date] = None
    secured: Optional[bool] = False
    linked_asset_id: Optional[int] = None
    autopay: Optional[bool] = False
    statement_doc_id: Optional[int] = None
    status: Optional[str] = Field(default="active")
    note: Optional[str] = None


class LoanCreate(LoanBase):
    pass


class LoanUpdate(LoanBase):
    pass


class LoanRead(LoanBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------- RecurringCost --------
class RecurringCostBase(BaseModel):
    household_id: int
    person_id: Optional[int] = None
    category: str
    subcategory: Optional[str] = None
    amount: float
    frequency: IncomeFrequency = IncomeFrequency.monthly
    mandatory: Optional[bool] = True
    variability_class: VariabilityClass = VariabilityClass.fixed
    controllability: Controllability = Controllability.locked
    vendor: Optional[str] = None
    payment_method: Optional[str] = None
    due_day: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    note: Optional[str] = None


class RecurringCostCreate(RecurringCostBase):
    pass


class RecurringCostUpdate(RecurringCostBase):
    pass


class RecurringCostRead(RecurringCostBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------- SubscriptionContract --------
class SubscriptionContractBase(BaseModel):
    household_id: int
    person_id: Optional[int] = None
    category: SubscriptionCategory = SubscriptionCategory.other
    provider: str
    product_name: Optional[str] = None
    contract_type: Optional[str] = Field(default="subscription")
    current_monthly_cost: float
    promotional_cost: Optional[float] = None
    promotional_end_date: Optional[date] = None
    ordinary_cost: Optional[float] = None
    billing_frequency: IncomeFrequency = IncomeFrequency.monthly
    binding_start_date: Optional[date] = None
    binding_end_date: Optional[date] = None
    notice_period_days: Optional[int] = None
    auto_renew: Optional[bool] = True
    cancellation_method: Optional[str] = None
    cancellation_url: Optional[str] = None
    service_address: Optional[str] = None
    usage_metric_type: Optional[str] = None
    usage_metric_estimate: Optional[float] = None
    included_allowance: Optional[float] = None
    overage_risk: Optional[str] = None
    bundling_flag: Optional[bool] = False
    household_criticality: Optional[str] = Field(default="optional")
    market_checkable: Optional[bool] = True
    last_negotiated_at: Optional[date] = None
    next_review_at: Optional[date] = None
    latest_invoice_doc_id: Optional[int] = None
    note: Optional[str] = None


class SubscriptionContractCreate(SubscriptionContractBase):
    pass


class SubscriptionContractUpdate(SubscriptionContractBase):
    pass


class SubscriptionContractRead(SubscriptionContractBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------- InsurancePolicy --------
class InsurancePolicyBase(BaseModel):
    household_id: int
    type: str
    provider: str
    premium_monthly: float
    deductible: Optional[float] = None
    coverage_tier: Optional[str] = None
    renewal_date: Optional[date] = None
    binding_end_date: Optional[date] = None
    linked_asset_id: Optional[int] = None
    comparison_score: Optional[float] = None
    note: Optional[str] = None


class InsurancePolicyCreate(InsurancePolicyBase):
    pass


class InsurancePolicyUpdate(InsurancePolicyBase):
    pass


class InsurancePolicyRead(InsurancePolicyBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------- Vehicle --------
class VehicleBase(BaseModel):
    household_id: int
    owner_person_id: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    fuel_type: Optional[str] = None
    estimated_value: Optional[float] = None
    loan_id: Optional[int] = None
    insurance_policy_id: Optional[int] = None
    tax_monthly_estimate: Optional[float] = None
    fuel_monthly_estimate: Optional[float] = None
    service_monthly_estimate: Optional[float] = None
    parking_monthly_estimate: Optional[float] = None
    toll_monthly_estimate: Optional[float] = None
    tire_monthly_estimate: Optional[float] = None
    note: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(VehicleBase):
    pass


class VehicleRead(VehicleBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------- Asset --------
class AssetBase(BaseModel):
    household_id: int
    person_id: Optional[int] = None
    type: str
    institution: Optional[str] = None
    label: Optional[str] = None
    market_value: Optional[float] = None
    liquid_value: Optional[float] = None
    pledged: Optional[bool] = False
    updated_at: Optional[datetime] = None
    verification_doc_id: Optional[int] = None
    note: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(AssetBase):
    pass


class AssetRead(AssetBase):
    id: int
    # When reading assets we include ``updated_at`` from database
    updated_at: datetime
    class Config:
        orm_mode = True


# -------- HousingScenario --------
class HousingScenarioBase(BaseModel):
    household_id: int
    label: str
    purchase_price: Optional[float] = None
    down_payment: Optional[float] = None
    mortgage_needed: Optional[float] = None
    rate_assumption: Optional[float] = None
    amortization_rate: Optional[float] = None
    monthly_fee_or_operating_cost: Optional[float] = None
    monthly_insurance: Optional[float] = None
    monthly_property_cost_estimate: Optional[float] = None
    note: Optional[str] = None


class HousingScenarioCreate(HousingScenarioBase):
    pass


class HousingScenarioUpdate(HousingScenarioBase):
    pass


class HousingScenarioRead(HousingScenarioBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------- Document --------
class DocumentBase(BaseModel):
    household_id: int
    document_type: str
    file_name: str
    mime_type: Optional[str] = None
    checksum: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[date] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    total_amount: Optional[float] = None
    vat_amount: Optional[float] = None
    currency: Optional[str] = None
    extracted_text: Optional[str] = None
    extraction_status: Optional[str] = Field(default="pending")
    storage_path: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    id: int
    uploaded_at: datetime

    class Config:
        orm_mode = True


# -------- ExtractionDraft --------
class ExtractionDraftBase(BaseModel):
    household_id: int
    document_id: int
    target_entity_type: str
    proposed_json: Any
    confidence: Optional[float] = None
    status: Optional[str] = Field(default="pending_review")
    model_name: Optional[str] = None


class ExtractionDraftCreate(ExtractionDraftBase):
    pass


class ExtractionDraftUpdate(ExtractionDraftBase):
    pass


class ExtractionDraftRead(ExtractionDraftBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------- OptimizationOpportunity --------
class OptimizationOpportunityBase(BaseModel):
    household_id: int
    kind: str
    target_entity_type: str
    target_entity_id: int
    title: str
    rationale: Optional[str] = None
    estimated_monthly_saving: Optional[float] = None
    estimated_yearly_saving: Optional[float] = None
    confidence: Optional[float] = None
    effort_level: Optional[str] = Field(default="medium")
    risk_level: Optional[str] = Field(default="medium")
    reversibility: Optional[str] = Field(default="medium")
    evidence_json: Optional[Any] = None
    source_refs_json: Optional[Any] = None
    status: Optional[str] = Field(default="open")


class OptimizationOpportunityCreate(OptimizationOpportunityBase):
    pass


class OptimizationOpportunityUpdate(OptimizationOpportunityBase):
    pass


class OptimizationOpportunityRead(OptimizationOpportunityBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# -------- Scenario --------
class ScenarioBase(BaseModel):
    household_id: int
    label: str
    change_set_json: Any


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(ScenarioBase):
    pass


class ScenarioRead(ScenarioBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# -------- ScenarioResult --------
class ScenarioResultBase(BaseModel):
    household_id: int
    scenario_id: int
    result_json: Any
    monthly_delta: Optional[float] = None
    yearly_delta: Optional[float] = None
    liquidity_delta: Optional[float] = None


class ScenarioResultCreate(ScenarioResultBase):
    pass


class ScenarioResultUpdate(ScenarioResultBase):
    pass


class ScenarioResultRead(ScenarioResultBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# -------- ReportSnapshot --------
class ReportSnapshotBase(BaseModel):
    household_id: int
    type: str
    as_of_date: date
    assumption_json: Optional[Any] = None
    result_json: Any


class ReportSnapshotCreate(ReportSnapshotBase):
    pass


class ReportSnapshotUpdate(ReportSnapshotBase):
    pass


class ReportSnapshotRead(ReportSnapshotBase):
    id: int
    generated_at: datetime
    class Config:
        orm_mode = True