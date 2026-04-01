# API & Data Schema for Frontend Integration

This document serves as a reference for frontend developers who will build
the user interface for the household economics system. It describes the
data models, their relationships and the RESTful API endpoints exposed by
the backend. Use this guide to build forms, tables and workflows that
interact correctly with the backend service.

## Entity Overview

The backend manages a number of entities, each representing a different
aspect of a household's finances. Most entities are related to a
`household` and optionally a `person` within that household. Entities
carry their own identifiers (`id`) which are stable primary keys.

| Entity                   | Description                                                       |
|--------------------------|-------------------------------------------------------------------|
| Household                | Top‑level container for persons and financial data               |
| Person                   | Individual belonging to a household                               |
| IncomeSource             | Regular income items (salary, benefits, pensions)                |
| Loan                     | Borrowed money with repayment details                            |
| RecurringCost            | Fixed or variable costs that recur on a schedule                 |
| SubscriptionContract     | Services billed periodically (mobile, electricity, streaming)    |
| InsurancePolicy          | Insurance contracts with premiums and coverage details           |
| Vehicle                  | Cars or other vehicles with associated costs                     |
| Asset                    | Assets such as accounts, savings, cars, houses                  |
| HousingScenario          | Hypothetical or planned housing purchase scenarios              |
| Document                 | Uploaded documents (receipts, invoices, contracts)               |
| ExtractionDraft          | AI‑generated structured data awaiting approval                   |
| OptimizationOpportunity  | Suggestions to reduce costs or improve finances                  |
| Scenario                 | Set of changes to apply in a simulation                          |
| ScenarioResult           | Results of applying a scenario to the household data            |
| ReportSnapshot           | Frozen report based on data at a specific point in time         |

## Common Conventions

* All timestamps are returned in ISO 8601 format (`YYYY‑MM‑DDTHH:MM:SS.sssZ`).
* Pagination is supported by `skip` and `limit` query parameters on
  collection endpoints. Defaults are 0 and 100.
* For creation (`POST`) and update (`PUT`) endpoints, unspecified fields
  will take their default values defined by the backend. To partially
  update an entity, send only the fields you wish to change.
* `DELETE` endpoints return HTTP status **204** on success and no
  response body.
* Many entities have optional foreign key references (e.g. `person_id` or
  `linked_asset_id`). These should be provided when the relationship is
  known; otherwise they can be omitted.

## API Endpoints

Below is a summary of each endpoint. Replace `:id` with the numeric
identifier of the entity.

### Household

* `GET /households` – List households
* `POST /households` – Create a new household (body: `HouseholdCreate`)
* `GET /households/:id` – Retrieve a household
* `PUT /households/:id` – Update a household (body: `HouseholdUpdate`)
* `DELETE /households/:id` – Delete a household

### Person

* `GET /persons` – List persons
* `POST /persons` – Create a new person
* `GET /persons/:id` – Retrieve a person
* `PUT /persons/:id` – Update a person
* `DELETE /persons/:id` – Delete a person

### IncomeSource

* `GET /income_sources` – List income sources
* `POST /income_sources` – Create an income source
* `GET /income_sources/:id` – Retrieve an income source
* `PUT /income_sources/:id` – Update an income source
* `DELETE /income_sources/:id` – Delete an income source

### Loan

* `GET /loans` – List loans
* `POST /loans` – Create a loan
* `GET /loans/:id` – Retrieve a loan
* `PUT /loans/:id` – Update a loan
* `DELETE /loans/:id` – Delete a loan

### RecurringCost

* `GET /recurring_costs` – List recurring costs
* `POST /recurring_costs` – Create a recurring cost
* `GET /recurring_costs/:id` – Retrieve a recurring cost
* `PUT /recurring_costs/:id` – Update a recurring cost
* `DELETE /recurring_costs/:id` – Delete a recurring cost

### SubscriptionContract

* `GET /subscription_contracts` – List subscription contracts
* `POST /subscription_contracts` – Create a subscription
* `GET /subscription_contracts/:id` – Retrieve a subscription
* `PUT /subscription_contracts/:id` – Update a subscription
* `DELETE /subscription_contracts/:id` – Delete a subscription

### InsurancePolicy

* `GET /insurance_policies` – List insurance policies
* `POST /insurance_policies` – Create an insurance policy
* `GET /insurance_policies/:id` – Retrieve an insurance policy
* `PUT /insurance_policies/:id` – Update an insurance policy
* `DELETE /insurance_policies/:id` – Delete an insurance policy

### Vehicle

* `GET /vehicles` – List vehicles
* `POST /vehicles` – Create a vehicle
* `GET /vehicles/:id` – Retrieve a vehicle
* `PUT /vehicles/:id` – Update a vehicle
* `DELETE /vehicles/:id` – Delete a vehicle

### Asset

* `GET /assets` – List assets
* `POST /assets` – Create an asset
* `GET /assets/:id` – Retrieve an asset
* `PUT /assets/:id` – Update an asset
* `DELETE /assets/:id` – Delete an asset

### HousingScenario

* `GET /housing_scenarios` – List housing scenarios
* `POST /housing_scenarios` – Create a scenario
* `GET /housing_scenarios/:id` – Retrieve a scenario
* `PUT /housing_scenarios/:id` – Update a scenario
* `DELETE /housing_scenarios/:id` – Delete a scenario

### Document

* `GET /documents` – List documents
* `POST /documents` – Create a document metadata record
* `GET /documents/:id` – Retrieve a document
* `PUT /documents/:id` – Update a document metadata record
* `DELETE /documents/:id` – Delete a document metadata record

> **Note:** File uploads are not implemented in this repository. The
> `storage_path` field can be used by your frontend/backend to store a
> path or URI to the uploaded file.

### ExtractionDraft

* `GET /extraction_drafts` – List extraction drafts
* `POST /extraction_drafts` – Create an extraction draft
* `GET /extraction_drafts/:id` – Retrieve a draft
* `PUT /extraction_drafts/:id` – Update a draft
* `DELETE /extraction_drafts/:id` – Delete a draft

### OptimizationOpportunity

* `GET /optimization_opportunities` – List optimisation opportunities
* `POST /optimization_opportunities` – Create an opportunity
* `GET /optimization_opportunities/:id` – Retrieve an opportunity
* `PUT /optimization_opportunities/:id` – Update an opportunity
* `DELETE /optimization_opportunities/:id` – Delete an opportunity

### Scenario

* `GET /scenarios` – List scenarios
* `POST /scenarios` – Create a scenario
* `GET /scenarios/:id` – Retrieve a scenario
* `PUT /scenarios/:id` – Update a scenario
* `DELETE /scenarios/:id` – Delete a scenario

### ScenarioResult

* `GET /scenario_results` – List scenario results
* `POST /scenario_results` – Create a scenario result
* `GET /scenario_results/:id` – Retrieve a scenario result
* `PUT /scenario_results/:id` – Update a scenario result
* `DELETE /scenario_results/:id` – Delete a scenario result

### ReportSnapshot

* `GET /report_snapshots` – List report snapshots
* `POST /report_snapshots` – Create a report snapshot
* `GET /report_snapshots/:id` – Retrieve a report snapshot
* `PUT /report_snapshots/:id` – Update a report snapshot
* `DELETE /report_snapshots/:id` – Delete a report snapshot

## Data Schemas

Below are the key fields for each entity. Additional fields may exist
and be returned by the API. See `app/models.py` and `app/schemas.py`
for the authoritative definition.

### Household

| Field            | Type     | Description                            |
|------------------|----------|----------------------------------------|
| `id`             | integer  | Primary key (read only)                |
| `name`           | string   | Name of the household                  |
| `currency`       | string   | Currency code (e.g. "SEK")            |
| `primary_country`| string   | Country code (e.g. "SE")             |
| `created_at`     | datetime | Creation timestamp (read only)         |

### Person

| Field              | Type     | Description                               |
|--------------------|----------|-------------------------------------------|
| `id`               | integer  | Primary key (read only)                   |
| `household_id`     | integer  | References the household                   |
| `name`             | string   | Person's name                              |
| `role`             | string   | Role in household (self, partner, child)  |
| `income_share_mode`| string   | How income is shared (exact, pooled, split)|
| `active`           | boolean  | Whether the person is currently active     |
| `created_at`       | datetime | Creation timestamp (read only)            |

### IncomeSource

| Field            | Type       | Description                                            |
|------------------|------------|--------------------------------------------------------|
| `id`             | integer    | Primary key (read only)                                |
| `person_id`      | integer    | References the person                                  |
| `type`           | string     | Salary, CSN, pension, benefit, freelance, other        |
| `gross_amount`   | float      | Gross amount before taxes (optional)                   |
| `net_amount`     | float      | Net amount after taxes (optional)                      |
| `frequency`      | enum       | Income frequency (monthly, yearly, weekly, etc.)       |
| `regularity`     | string     | Fixed or variable                                      |
| `source`         | string     | Employer or source name (optional)                     |
| `start_date`     | date       | When the income started (optional)                     |
| `end_date`       | date       | When the income ended (optional)                       |
| `verified`       | boolean    | Whether the income has been verified                   |
| `verification_doc_id`| integer| References a document verifying the income             |
| `note`           | string     | Additional notes (optional)                            |
| `created_at`     | datetime   | Creation timestamp (read only)                         |

### Loan

See `app/schemas.py` for the complete definition of the `Loan` fields.
Key fields include `type`, `lender`, `current_balance`, `nominal_rate`,
`repayment_model`, `required_monthly_payment`, `status` and an optional
link to an `asset`.

### RecurringCost

Stores costs that repeat periodically, such as groceries or fuel. Key
fields are `category`, `amount`, `frequency`, `mandatory`,
`variability_class` (fixed/semi_fixed/variable) and `controllability`
(locked/negotiable/reducible/discretionary).

### SubscriptionContract

Represents longer‑term agreements like mobile plans, electricity and
streaming services. Important fields include `provider`,
`product_name`, `current_monthly_cost`, `promotional_cost`,
`promotional_end_date`, `binding_end_date`, `notice_period_days`,
`auto_renew` and `household_criticality`. Frontend forms should allow
users to specify promotional and ordinary costs separately so that
calculations can account for future price increases.

### Document & ExtractionDraft

Documents store metadata about uploaded files; the actual file storage
must be implemented separately. Extraction drafts capture AI‑generated
data and include `proposed_json` which should be displayed to users for
approval or correction.

### OptimisationOpportunity

Captures suggestions to improve the household's finances. Key fields
include `kind` (e.g. cancel, renegotiate), `target_entity_type` and
`target_entity_id` which indicate what the suggestion applies to,
`estimated_monthly_saving`, `confidence`, `effort_level`, and
`risk_level`. Frontend workflows might allow users to accept or
dismiss opportunities.

### Scenario & ScenarioResult

`Scenario` records a set of hypothetical changes (e.g. sell a vehicle,
change interest rate) in JSON format. After running a simulation,
`ScenarioResult` stores the computed impact on monthly, yearly and
liquidity balances. The calculations themselves are not implemented in
this repository but can be added in future.

### ReportSnapshot

Snapshots are immutable JSON payloads captured at a specific point in
time. Use them to generate PDF or HTML reports for banks, auditors or
your own record keeping. The frontend can fetch snapshots, render the
results and export them as desired.

## Building the Frontend

To build a frontend against this API:

1. Read this document and `app/schemas.py` to understand each
   entity's fields.
2. Create forms corresponding to the create/update schemas. Use the
   API endpoints to persist data.
3. Display lists and details of entities using the read schemas.
4. For file uploads, implement storage (e.g. to local filesystem or
   cloud object storage) and save the resulting URI in the
   `storage_path` field of `Document`.
5. When AI integrations are added, surface `ExtractionDraft` and
   `OptimizationOpportunity` suggestions to users and allow them to
   accept or reject proposals.
6. Use snapshots for stable reporting and historical comparisons.

The API is intentionally general and does not prescribe how your UI
should look. You are free to implement a web app with React/Vue,
mobile app with Flutter or a desktop app. The only requirement is
conformity with the API contract described here.