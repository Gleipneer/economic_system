const API = {
  households: "/households",
  persons: "/persons",
  incomes: "/income_sources",
  loans: "/loans",
  recurringCosts: "/recurring_costs",
  subscriptions: "/subscription_contracts",
  insurancePolicies: "/insurance_policies",
  vehicles: "/vehicles",
  assets: "/assets",
  housing: "/housing_scenarios",
  documents: "/documents",
  opportunities: "/optimization_opportunities",
};

const PAGES = [
  { key: "overview", label: "Översikt" },
  { key: "household", label: "Hushållet" },
  { key: "incomes", label: "Inkomster" },
  { key: "loans", label: "Lån" },
  { key: "costs", label: "Fasta kostnader" },
  { key: "subscriptions", label: "Abonnemang och avtal" },
  { key: "vehicles", label: "Fordon" },
  { key: "assets", label: "Tillgångar" },
  { key: "housing", label: "Boendekalkyl" },
  { key: "documents", label: "Dokument" },
  { key: "improvements", label: "Förbättringar" },
];

const COPY = {
  overview: {
    title: "Översikt",
    intro: "Se läget utan demo-data och utan överflödiga instruktioner.",
  },
  household: {
    title: "Hushållet",
    intro: "Skapa hushållet och koppla personerna som ska ingå.",
  },
  incomes: {
    title: "Inkomster",
    intro: "Lägg in nettolön eller brutto om du behöver det.",
  },
  loans: {
    title: "Lån",
    intro: "Samla skuld, ränta och månadskostnad på ett ställe.",
  },
  costs: {
    title: "Fasta kostnader",
    intro: "Registrera återkommande kostnader och försäkringar.",
  },
  subscriptions: {
    title: "Abonnemang och avtal",
    intro: "Jämför pris, bindningstid och nästa granskning.",
  },
  vehicles: {
    title: "Fordon",
    intro: "Se vad bilen kostar varje månad.",
  },
  assets: {
    title: "Tillgångar",
    intro: "Samla konton, sparande och andra tillgångar.",
  },
  housing: {
    title: "Boendekalkyl",
    intro: "Testa ett boendescenario och se kvar att leva på.",
  },
  documents: {
    title: "Dokument",
    intro: "Ladda upp avtal, fakturor, kvitton och låneavier.",
  },
  improvements: {
    title: "Förbättringar",
    intro: "Här samlas förslag som kan sänka kostnader.",
  },
};

const OPTIONS = {
  role: [
    ["self", "Huvudperson"],
    ["partner", "Partner"],
    ["child", "Barn"],
    ["other", "Övrigt"],
  ],
  incomeType: [
    ["salary", "Lön"],
    ["csn", "CSN"],
    ["benefit", "Bidrag"],
    ["pension", "Pension"],
    ["freelance", "Frilans"],
    ["other", "Övrigt"],
  ],
  frequency: [
    ["monthly", "Varje månad"],
    ["yearly", "Per år"],
    ["weekly", "Varje vecka"],
    ["biweekly", "Varannan vecka"],
    ["daily", "Per dag"],
  ],
  regularity: [
    ["fixed", "Fast"],
    ["variable", "Varierar"],
  ],
  variabilityClass: [
    ["fixed", "Fast"],
    ["semi_fixed", "Halvfast"],
    ["variable", "Rörlig"],
  ],
  recurringCostCategory: [
    ["housing", "Boende"],
    ["transport", "Transport"],
    ["food", "Mat"],
    ["health", "Hälsa"],
    ["childcare", "Barn"],
    ["software", "Programvara"],
    ["debt", "Avbetalning"],
    ["other", "Övrigt"],
  ],
  insuranceType: [
    ["home", "Hem"],
    ["car", "Bil"],
    ["person", "Person"],
    ["child", "Barn"],
    ["other", "Övrigt"],
  ],
  loanType: [
    ["mortgage", "Bolån"],
    ["car", "Billån"],
    ["csn", "CSN"],
    ["personal_loan", "Privatlån"],
    ["credit_card", "Kreditkort"],
    ["other", "Övrigt"],
  ],
  loanStatus: [
    ["active", "Aktivt"],
    ["closed", "Avslutat"],
    ["delinquent", "Försenat"],
  ],
  repaymentModel: [
    ["annuity", "Annuitet"],
    ["fixed_amortization", "Rak amortering"],
    ["interest_only", "Endast ränta"],
    ["manual", "Manuell"],
  ],
  subscriptionCategory: [
    ["mobile", "Mobil"],
    ["broadband", "Bredband"],
    ["electricity", "El"],
    ["streaming", "Streaming"],
    ["gym", "Gym"],
    ["alarm", "Larm"],
    ["software", "Programvara"],
    ["insurance", "Försäkring"],
    ["membership", "Medlemskap"],
    ["other", "Övrigt"],
  ],
  subscriptionCriticality: [
    ["critical", "Viktigt i vardagen"],
    ["useful", "Bra att ha"],
    ["optional", "Kan ifrågasättas"],
    ["dead_weight", "Troligen onödigt"],
  ],
  assetType: [
    ["checking", "Lönekonto"],
    ["savings", "Sparkonto"],
    ["fund", "Fond eller investering"],
    ["cash", "Kontanter"],
    ["car", "Fordon"],
    ["house", "Bostad"],
    ["other", "Övrigt"],
  ],
  fuelType: [
    ["petrol", "Bensin"],
    ["diesel", "Diesel"],
    ["electric", "El"],
    ["hybrid", "Hybrid"],
    ["other", "Övrigt"],
  ],
  documentType: [
    ["receipt", "Kvitto"],
    ["invoice", "Faktura"],
    ["contract", "Avtal"],
    ["payslip", "Lönespecifikation"],
    ["bank_statement", "Kontoutdrag"],
    ["loan_statement", "Låneavi"],
  ],
};

const state = {
  page: localStorage.getItem("he_page") || "overview",
  selectedHouseholdId: Number(localStorage.getItem("he_household_id") || "") || null,
  data: {
    households: [],
    persons: [],
    incomes: [],
    recurringCosts: [],
    loans: [],
    subscriptions: [],
    insurancePolicies: [],
    vehicles: [],
    assets: [],
    housing: [],
    documents: [],
    opportunities: [],
  },
  summary: null,
  housingEvaluation: null,
  editing: {
    household: null,
    person: null,
    income: null,
    loan: null,
    cost: null,
    insurance: null,
    subscription: null,
    vehicle: null,
    asset: null,
    housing: null,
  },
};

const els = {};

document.addEventListener("DOMContentLoaded", boot);

async function boot() {
  bindElements();
  bindBaseEvents();
  await refreshAllData();
  render();
}

function bindElements() {
  els.nav = document.getElementById("mainNav");
  els.pageContent = document.getElementById("pageContent");
  els.householdSelect = document.getElementById("householdSelect");
  els.refreshButton = document.getElementById("refreshButton");
  els.toast = document.getElementById("toast");
}

function bindBaseEvents() {
  els.nav.addEventListener("click", (event) => {
    const target = event.target.closest("[data-nav]");
    if (!target) return;
    state.page = target.dataset.nav;
    persistPage();
    render();
  });

  els.refreshButton.addEventListener("click", async () => {
    await refreshAllData();
    render();
    showToast("Data uppdaterades.");
  });

  els.householdSelect.addEventListener("change", async (event) => {
    state.selectedHouseholdId = Number(event.target.value) || null;
    persistSelection();
    clearEdits();
    state.housingEvaluation = null;
    await ensureSummaryLoaded();
    render();
  });

  els.pageContent.addEventListener("click", handlePageClick);
  els.pageContent.addEventListener("submit", handlePageSubmit);
}

function persistSelection() {
  if (state.selectedHouseholdId) {
    localStorage.setItem("he_household_id", String(state.selectedHouseholdId));
  } else {
    localStorage.removeItem("he_household_id");
  }
}

function persistPage() {
  localStorage.setItem("he_page", state.page);
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `${response.status} ${response.statusText}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

async function refreshAllData() {
  const entries = await Promise.all([
    request(`${API.households}?skip=0&limit=200`).then((value) => ["households", value]),
    request(`${API.persons}?skip=0&limit=200`).then((value) => ["persons", value]),
    request(`${API.incomes}?skip=0&limit=200`).then((value) => ["incomes", value]),
    request(`${API.recurringCosts}?skip=0&limit=200`).then((value) => ["recurringCosts", value]),
    request(`${API.loans}?skip=0&limit=200`).then((value) => ["loans", value]),
    request(`${API.subscriptions}?skip=0&limit=200`).then((value) => ["subscriptions", value]),
    request(`${API.insurancePolicies}?skip=0&limit=200`).then((value) => ["insurancePolicies", value]),
    request(`${API.vehicles}?skip=0&limit=200`).then((value) => ["vehicles", value]),
    request(`${API.assets}?skip=0&limit=200`).then((value) => ["assets", value]),
    request(`${API.housing}?skip=0&limit=200`).then((value) => ["housing", value]),
    request(`${API.documents}?skip=0&limit=200`).then((value) => ["documents", value]),
    request(`${API.opportunities}?skip=0&limit=200`).then((value) => ["opportunities", value]),
  ]);

  state.data = Object.fromEntries(entries);
  if (!selectedHousehold() && households().length) {
    state.selectedHouseholdId = households()[0].id;
    persistSelection();
  }
  await ensureSummaryLoaded();
}

async function ensureSummaryLoaded() {
  if (!state.selectedHouseholdId) {
    state.summary = null;
    return;
  }
  state.summary = await request(`/households/${state.selectedHouseholdId}/summary`);
}

async function loadHousingEvaluation(scenarioId) {
  state.housingEvaluation = await request(`/housing_scenarios/${scenarioId}/evaluate`);
}

function households() {
  return state.data.households;
}

function selectedHousehold() {
  return households().find((item) => item.id === state.selectedHouseholdId) || null;
}

function peopleForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.persons.filter((item) => item.household_id === householdId);
}

function incomesForHousehold(householdId = state.selectedHouseholdId) {
  const personIds = new Set(peopleForHousehold(householdId).map((item) => item.id));
  return state.data.incomes.filter((item) => personIds.has(item.person_id));
}

function recurringCostsForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.recurringCosts.filter((item) => item.household_id === householdId);
}

function loansForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.loans.filter((item) => item.household_id === householdId);
}

function subscriptionsForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.subscriptions.filter((item) => item.household_id === householdId);
}

function insuranceForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.insurancePolicies.filter((item) => item.household_id === householdId);
}

function vehiclesForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.vehicles.filter((item) => item.household_id === householdId);
}

function assetsForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.assets.filter((item) => item.household_id === householdId);
}

function housingForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.housing.filter((item) => item.household_id === householdId);
}

function documentsForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.documents.filter((item) => item.household_id === householdId);
}

function opportunitiesForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.opportunities.filter((item) => item.household_id === householdId);
}

function currentEdit(moduleKey) {
  return state.editing[moduleKey] || null;
}

function setEdit(moduleKey, item) {
  state.editing[moduleKey] = item ? { ...item } : null;
}

function clearEdits() {
  Object.keys(state.editing).forEach((key) => {
    state.editing[key] = null;
  });
}

function money(value) {
  return new Intl.NumberFormat("sv-SE", {
    style: "currency",
    currency: "SEK",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}

function number(value, digits = 0) {
  return new Intl.NumberFormat("sv-SE", {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  }).format(Number(value || 0));
}

function dateLabel(value) {
  if (!value) return "Ej angivet";
  return new Intl.DateTimeFormat("sv-SE").format(new Date(value));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function optionLabel(options, value) {
  return options.find(([optionValue]) => String(optionValue) === String(value))?.[1] || value || "Ej angivet";
}

function personName(personId) {
  return state.data.persons.find((item) => item.id === personId)?.name || "Ingen koppling";
}

function assetName(assetId) {
  const item = state.data.assets.find((asset) => asset.id === assetId);
  return item ? escapeHtml(item.label || item.institution || optionLabel(OPTIONS.assetType, item.type)) : "Ingen koppling";
}

function loanName(loanId) {
  const item = state.data.loans.find((loan) => loan.id === loanId);
  if (!item) return "Ingen koppling";
  return `${optionLabel(OPTIONS.loanType, item.type)}${item.lender ? ` · ${escapeHtml(item.lender)}` : ""}`;
}

function policyName(policyId) {
  const item = state.data.insurancePolicies.find((policy) => policy.id === policyId);
  return item ? `${escapeHtml(item.provider)} · ${money(item.premium_monthly)}` : "Ingen koppling";
}

function selectedSummary() {
  return state.summary;
}

function onboardingSteps() {
  if (!selectedHousehold()) {
    return [{ page: "household", title: "Skapa hushåll", text: "Börja här så kan resten kopplas rätt automatiskt." }];
  }

  const steps = [];
  if (!peopleForHousehold().length) {
    steps.push({ page: "household", title: "Lägg till personer", text: "Behövs för att koppla inkomster och fordon." });
  }
  if (!incomesForHousehold().length) {
    steps.push({ page: "incomes", title: "Lägg in inkomster", text: "Då blir översikten meningsfull direkt." });
  }
  if (!loansForHousehold().length) {
    steps.push({ page: "loans", title: "Lägg in lån", text: "Ger tydlig bild av skuld och månadskostnad." });
  }
  if (!subscriptionsForHousehold().length) {
    steps.push({ page: "subscriptions", title: "Registrera abonnemang", text: "Här finns ofta lätta besparingar att hitta." });
  }
  if (!housingForHousehold().length) {
    steps.push({ page: "housing", title: "Skapa boendekalkyl", text: "Bra för att se kvar att leva på och räntestress." });
  }
  return steps;
}

function warningsFromSummary(summary) {
  if (!summary) return [];
  const warnings = [];
  if (summary.monthly_net_cashflow < 0) {
    warnings.push("Hushållet går back varje månad. Börja med inkomster, avtal och lån.");
  }
  if (summary.gross_income_only_entries > 0) {
    warnings.push("Minst en inkomst saknar nettobelopp. Kassaflödet använder brutto tills du fyller i netto.");
  }
  if (summary.monthly_income > 0 && summary.monthly_loan_payments > summary.monthly_income * 0.35) {
    warnings.push("Lånekostnaden är hög i förhållande till hushållets inkomster.");
  }
  if (summary.monthly_subscriptions > 0 && summary.monthly_income > 0 && summary.monthly_subscriptions > summary.monthly_income * 0.05) {
    warnings.push("Abonnemang och avtal tar en ovanligt stor del av hushållets pengar.");
  }
  return warnings;
}

function dueForReviewCount() {
  return subscriptionsForHousehold().filter((item) => item.next_review_at && daysUntil(item.next_review_at) <= 30).length;
}

function priceJumpCount() {
  return subscriptionsForHousehold().filter((item) => Number(item.ordinary_cost || 0) > Number(item.current_monthly_cost || 0)).length;
}

function optionalContractsCount() {
  return subscriptionsForHousehold().filter((item) => ["optional", "dead_weight"].includes(item.household_criticality)).length;
}

function daysUntil(dateValue) {
  const target = new Date(dateValue);
  const now = new Date();
  return Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

function riskLabel(value) {
  const map = { low: "Låg", medium: "Medel", high: "Hög" };
  return map[value] || "Okänd";
}

function effortLabel(value) {
  const map = { low: "Liten insats", medium: "Måttlig insats", high: "Hög insats" };
  return map[value] || "Måttlig insats";
}

function badgeTone(value) {
  if (value === "high") return "danger";
  if (value === "medium") return "warning";
  if (value === "open") return "success";
  return "muted";
}

function subscriptionSignals(item) {
  const signals = [];
  if (Number(item.ordinary_cost || 0) > Number(item.current_monthly_cost || 0)) {
    signals.push({ tone: "warning", label: `Ordinarie pris ${money(item.ordinary_cost)}` });
  }
  if (item.binding_end_date) {
    signals.push({ tone: "muted", label: `Bindning till ${dateLabel(item.binding_end_date)}` });
  }
  if (item.next_review_at) {
    signals.push({
      tone: daysUntil(item.next_review_at) <= 30 ? "warning" : "muted",
      label: `Nästa granskning ${dateLabel(item.next_review_at)}`,
    });
  }
  if (["optional", "dead_weight"].includes(item.household_criticality)) {
    signals.push({ tone: "danger", label: "Kan sannolikt sänkas eller avslutas" });
  }
  return signals;
}

function opportunityAction(kind) {
  const map = {
    cancel: "Överväg att avsluta avtalet om hushållet klarar sig utan det.",
    renegotiate: "Kontakta leverantören och be om bättre pris eller villkor.",
    switch_provider: "Jämför med alternativ leverantör innan nästa förnyelse.",
    reduce_usage: "Se om kostnaden går att pressa genom lägre användning.",
    consolidate_debt: "Undersök om lån kan samlas eller göras om.",
  };
  return map[kind] || "Gå igenom förslaget och avgör om det passar hushållet.";
}

function render() {
  renderHouseholdSelect();
  renderNav();
  els.pageContent.innerHTML = renderPage();
}

function renderHouseholdSelect() {
  const items = households();
  if (!items.length) {
    els.householdSelect.innerHTML = `<option value="">Inget hushåll ännu</option>`;
    els.householdSelect.disabled = true;
    return;
  }

  els.householdSelect.disabled = false;
  els.householdSelect.innerHTML = items
    .map((item) => `<option value="${item.id}" ${item.id === state.selectedHouseholdId ? "selected" : ""}>${escapeHtml(item.name)}</option>`)
    .join("");
}

function renderNav() {
  els.nav.innerHTML = PAGES.map((page) => (
    `<button type="button" class="${page.key === state.page ? "active" : ""}" data-nav="${page.key}">${page.label}</button>`
  )).join("");
}

function renderPage() {
  const copy = COPY[state.page];
  return `
    <section class="page-header">
      <div>
        <span class="eyebrow">${copy.title}</span>
        <h2>${copy.title}</h2>
        <p class="section-intro">${copy.intro}</p>
      </div>
      <div class="page-actions">${renderPageActions()}</div>
    </section>
    ${renderPageBody()}
  `;
}

function renderPageActions() {
  if (state.page === "overview") {
    return `
      <button class="ghost" type="button" data-nav="subscriptions">Granska avtal</button>
      <button class="primary" type="button" data-nav="household">Hantera hushåll</button>
    `;
  }
  if (state.page === "improvements") {
    return `<button class="primary" type="button" data-action="scan-opportunities" ${selectedHousehold() ? "" : "disabled"}>Analysera hushållet</button>`;
  }
  if (["incomes", "loans", "costs", "subscriptions", "vehicles", "assets", "housing"].includes(state.page)) {
    return `<button class="primary" type="button" data-action="new-record" data-module="${moduleKeyForPage(state.page)}" ${selectedHousehold() ? "" : "disabled"}>Ny post</button>`;
  }
  return "";
}

function renderPageBody() {
  switch (state.page) {
    case "overview":
      return renderOverviewPage();
    case "household":
      return renderHouseholdPage();
    case "incomes":
      return renderCollectionLayout({
        moduleKey: "income",
        items: incomesForHousehold(),
        title: "Inkomster",
        emptyTitle: "Inga inkomster ännu",
        emptyCopy: peopleForHousehold().length
          ? "Lägg in lön, CSN, pension eller bidrag för att få en begriplig översikt."
          : "Lägg först till minst en person i hushållet så att inkomsten kan kopplas rätt.",
        stats: renderIncomeStats(),
        renderCard: renderIncomeCard,
        renderFormBlock: renderIncomeFormBlock,
      });
    case "loans":
      return renderCollectionLayout({
        moduleKey: "loan",
        items: loansForHousehold(),
        title: "Lån",
        emptyTitle: "Inga lån ännu",
        emptyCopy: "Lägg in bolån, billån, CSN eller kreditkort för att se månadskostnaden tydligt.",
        stats: renderLoanStats(),
        renderCard: renderLoanCard,
        renderFormBlock: renderLoanFormBlock,
      });
    case "costs":
      return renderCostsPage();
    case "subscriptions":
      return renderSubscriptionsPage();
    case "vehicles":
      return renderCollectionLayout({
        moduleKey: "vehicle",
        items: vehiclesForHousehold(),
        title: "Fordon",
        emptyTitle: "Inga fordon ännu",
        emptyCopy: "Lägg in bil eller annat fordon för att samla bränsle, service, skatt och parkering.",
        stats: renderVehicleStats(),
        renderCard: renderVehicleCard,
        renderFormBlock: renderVehicleFormBlock,
      });
    case "assets":
      return renderCollectionLayout({
        moduleKey: "asset",
        items: assetsForHousehold(),
        title: "Tillgångar",
        emptyTitle: "Inga tillgångar ännu",
        emptyCopy: "Lägg in konton, sparande, fonder och andra tillgångar för en tydligare nettobild.",
        stats: renderAssetStats(),
        renderCard: renderAssetCard,
        renderFormBlock: renderAssetFormBlock,
      });
    case "housing":
      return renderHousingPage();
    case "documents":
      return renderDocumentsPage();
    case "improvements":
      return renderImprovementsPage();
    default:
      return "";
  }
}

function renderOverviewPage() {
  const household = selectedHousehold();
  if (!household) {
    return `
      <section class="panel">
        <div class="empty-state">
          <h3>Börja med att skapa hushållet</h3>
          <p class="empty-copy">Skapa ett hushåll först så kan du lägga in personer, inkomster och kostnader.</p>
          <div class="button-row">
            <button class="primary" type="button" data-nav="household">Skapa hushåll</button>
          </div>
        </div>
      </section>
    `;
  }

  const summary = selectedSummary();
  const warnings = warningsFromSummary(summary);
  const steps = onboardingSteps();
  const improvements = opportunitiesForHousehold()
    .slice()
    .sort((a, b) => Number(b.estimated_monthly_saving || 0) - Number(a.estimated_monthly_saving || 0))
    .slice(0, 3);
  const fixedCosts = Number(summary?.monthly_recurring_costs || 0) + Number(summary?.monthly_insurance || 0);

  return `
    <section class="summary-hero">
      <article class="panel">
        <span class="eyebrow">Nuläge</span>
        <h3>${escapeHtml(household.name)}</h3>
        <p class="meta-text">Inkomster, fasta kostnader, avtal, lån och fordon i en vy.</p>
        <div class="metrics-grid">
          ${renderMetricCard("Inkomst", money(summary?.monthly_income), "Månadsinkomst enligt nuvarande data.")}
          ${renderMetricCard("Fasta kostnader", money(fixedCosts), "Återkommande kostnader och försäkringar.", "warning")}
          ${renderMetricCard("Avtal", money(summary?.monthly_subscriptions), `${subscriptionsForHousehold().length} avtal.`)}
          ${renderMetricCard("Lån", money(summary?.monthly_loan_payments), `${loansForHousehold().length} lån.`)}
          ${renderMetricCard("Fordon", money(summary?.monthly_vehicle_costs), `${vehiclesForHousehold().length} fordon.`)}
          ${renderMetricCard("Kvar", money(summary?.monthly_net_cashflow), "Efter allt som ligger inne.", summary?.monthly_net_cashflow >= 0 ? "positive" : "danger")}
        </div>
      </article>

      <article class="spotlight-card">
        <span class="eyebrow">Nästa steg</span>
        <h3>Det som saknas</h3>
        ${steps.length
          ? `<div class="journey-grid">${steps.map((step) => `
              <article class="journey-card">
                <h4>${escapeHtml(step.title)}</h4>
                <p class="meta-text">${escapeHtml(step.text)}</p>
                <button class="ghost" type="button" data-nav="${step.page}">Öppna</button>
              </article>
            `).join("")}</div>`
          : `<div class="empty-state"><p class="empty-copy">Grunden finns på plats.</p></div>`}
      </article>
    </section>

    <section class="overview-grid">
      <article class="panel">
        <div class="section-head">
          <div>
            <span class="kicker">Kontrollpunkter</span>
            <h3>Så ser läget ut just nu</h3>
          </div>
        </div>
        ${warnings.length
          ? `<ul class="warning-list">${warnings.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
          : `<p class="empty-copy">Inga tydliga varningssignaler just nu.</p>`}
        <div class="card-grid">
          <article class="record-card">
            <span class="mini-label">Tillgångar</span>
            <div class="spotlight-number">${money(summary?.asset_market_value)}</div>
            <p class="meta-text">Likvida medel: ${money(summary?.asset_liquid_value)}</p>
          </article>
          <article class="record-card">
            <span class="mini-label">Uppskattad nettoställning</span>
            <div class="spotlight-number">${money(summary?.net_worth_estimate)}</div>
            <p class="meta-text">Tillgångar minus registrerade lån.</p>
          </article>
        </div>
      </article>

      <article class="panel">
        <div class="section-head">
          <div>
            <span class="kicker">Förslag</span>
            <h3>Besparingar att titta på</h3>
          </div>
          <button class="ghost" type="button" data-nav="improvements">Visa alla</button>
        </div>
        ${improvements.length
          ? `<div class="card-stack">${improvements.map(renderOpportunityCard).join("")}</div>`
          : `<div class="empty-state">
              <p class="empty-copy">Det finns inga färdiga förslag ännu för det här hushållet.</p>
              <button class="primary" type="button" data-action="scan-opportunities">Hitta förbättringsförslag</button>
            </div>`}
      </article>
    </section>

    <section class="card-grid">
      <article class="panel">
        <span class="kicker">Avtal som bör granskas</span>
        <h3>Abonnemang och avtal</h3>
        <div class="stats-strip">
          ${renderStatPill("Avtal", subscriptionsForHousehold().length)}
          ${renderStatPill("Snart dags att granska", dueForReviewCount())}
          ${renderStatPill("Kan höjas till ordinarie pris", priceJumpCount())}
          ${renderStatPill("Kan ifrågasättas", optionalContractsCount())}
        </div>
        <div class="card-stack">
          ${subscriptionsForHousehold().slice(0, 3).map(renderSubscriptionCard).join("") || `<p class="empty-copy">Lägg in hushållets avtal här för att få bättre kontroll.</p>`}
        </div>
      </article>

      <article class="panel">
        <span class="kicker">Fasta kostnader</span>
        <h3>Det som drar pengar varje månad</h3>
        <div class="card-stack">
          ${renderFixedCostCards()}
        </div>
      </article>
    </section>
  `;
}

function renderHouseholdPage() {
  const household = selectedHousehold();
  const people = peopleForHousehold();
  return `
    <section class="split-layout">
      <article class="panel">
        <span class="kicker">Hushållets grund</span>
        <h3>${household ? escapeHtml(household.name) : "Skapa första hushållet"}</h3>
        <p class="meta-text">All annan data kopplas hit. Du ska inte behöva fylla i hushålls-id manuellt.</p>
        ${renderForm("householdForm", householdFields(), household || {}, {
          submitLabel: household ? "Spara hushåll" : "Skapa hushåll",
          canDelete: Boolean(household),
          deleteLabel: "Ta bort hushåll",
        })}
      </article>

      <article class="panel">
        <div class="section-head">
          <div>
            <span class="kicker">Personer i hushållet</span>
            <h3>${people.length ? `${people.length} personer registrerade` : "Lägg till första personen"}</h3>
          </div>
          ${selectedHousehold() ? `<button class="ghost" type="button" data-action="new-record" data-module="person">Ny person</button>` : ""}
        </div>
        <div class="card-stack">
          ${people.length ? people.map(renderPersonCard).join("") : `<div class="empty-state"><p class="empty-copy">Här lägger du in vuxna och barn som ekonomin rör.</p></div>`}
        </div>
        ${selectedHousehold() ? renderForm("personForm", personFields(), currentEdit("person") || {}, {
          submitLabel: currentEdit("person")?.id ? "Spara person" : "Lägg till person",
          canDelete: Boolean(currentEdit("person")?.id),
          deleteLabel: "Ta bort person",
        }) : ""}
      </article>
    </section>
  `;
}

function renderCollectionLayout({ moduleKey, items, title, emptyTitle, emptyCopy, stats, renderCard, renderFormBlock }) {
  return `
    ${stats}
    <section class="split-layout">
      <article class="panel">
        <div class="section-head">
          <div>
            <span class="kicker">${escapeHtml(title)}</span>
            <h3>${items.length ? `${items.length} poster` : escapeHtml(emptyTitle)}</h3>
          </div>
          ${selectedHousehold() ? `<button class="ghost" type="button" data-action="new-record" data-module="${moduleKey}">Ny post</button>` : ""}
        </div>
        <div class="card-stack">
          ${items.length ? items.map(renderCard).join("") : `<div class="empty-state"><p class="empty-copy">${escapeHtml(emptyCopy)}</p></div>`}
        </div>
      </article>

      <article class="panel">
        ${selectedHousehold()
          ? renderFormBlock()
          : `<div class="empty-state"><p class="empty-copy">Skapa eller välj först ett hushåll högst upp.</p></div>`}
      </article>
    </section>
  `;
}

function renderSubscriptionsPage() {
  const items = subscriptionsForHousehold();
  return `
    <section class="panel">
      <span class="kicker">Avtal som påverkar vardagen</span>
      <h3>Håll koll på pris, bindning och nästa granskning</h3>
      <div class="stats-strip">
        ${renderStatPill("Avtal", items.length)}
        ${renderStatPill("Månadskostnad", money(sum(items.map((item) => item.current_monthly_cost))))}
        ${renderStatPill("Snart att granska", dueForReviewCount())}
        ${renderStatPill("Möjliga att ifrågasätta", optionalContractsCount())}
      </div>
    </section>

    <section class="split-layout">
      <article class="panel">
        <div class="section-head">
          <div>
            <span class="kicker">Avtalslista</span>
            <h3>${items.length ? `${items.length} avtal sparade` : "Lägg till första avtalet"}</h3>
          </div>
          ${selectedHousehold() ? `<button class="ghost" type="button" data-action="new-record" data-module="subscription">Nytt avtal</button>` : ""}
        </div>
        <div class="card-stack">
          ${items.length ? items.map(renderSubscriptionCard).join("") : `<div class="empty-state"><p class="empty-copy">Mobil, bredband, el, streaming, gym och försäkringar hör hemma här.</p></div>`}
        </div>
      </article>

      <article class="panel">
        <span class="kicker">Avtalsformulär</span>
        <h3>${currentEdit("subscription")?.id ? "Redigera avtal" : "Lägg till avtal"}</h3>
        <p class="meta-text">Här är det viktigaste tydligt: leverantör, nuvarande pris, ordinarie pris, bindningstid och nästa granskning.</p>
        ${selectedHousehold()
          ? renderForm("subscriptionForm", subscriptionFields(), currentEdit("subscription") || {}, {
              submitLabel: currentEdit("subscription")?.id ? "Spara avtal" : "Skapa avtal",
              canDelete: Boolean(currentEdit("subscription")?.id),
              deleteLabel: "Ta bort avtal",
            })
          : ""}
      </article>
    </section>
  `;
}

function renderCostsPage() {
  const recurring = recurringCostsForHousehold();
  const policies = insuranceForHousehold();
  const totalRecurring = sum(recurring.map((item) => amountToMonthlyCost(item)));
  const totalInsurance = sum(policies.map((item) => item.premium_monthly));

  return `
    <section class="panel">
      <div class="section-head">
        <div>
          <span class="kicker">Fasta kostnader</span>
          <h3>Återkommande kostnader och försäkringar</h3>
          <p class="meta-text">Här lägger du in hushållets fasta månadsposter. För avbetalningar kan du skriva återstående belopp i anteckningen tills backend har ett eget fält.</p>
        </div>
        <button class="primary" type="button" data-action="new-record" data-module="cost" ${selectedHousehold() ? "" : "disabled"}>Ny kostnad</button>
      </div>
      <div class="stats-strip">
        ${renderStatPill("Kostnader", recurring.length)}
        ${renderStatPill("Försäkringar", policies.length)}
        ${renderStatPill("Totalt per månad", money(totalRecurring + totalInsurance))}
        ${renderStatPill("Avbetalning/övrigt", money(sum(recurring.filter((item) => String(item.category) === "debt").map((item) => amountToMonthlyCost(item)))))}
      </div>
    </section>

    <section class="split-layout">
      <article class="panel">
        <div class="section-head">
          <div>
            <span class="kicker">Återkommande kostnader</span>
            <h3>${recurring.length ? `${recurring.length} poster` : "Lägg till första kostnaden"}</h3>
          </div>
          ${selectedHousehold() ? `<button class="ghost" type="button" data-action="new-record" data-module="cost">Ny post</button>` : ""}
        </div>
        <div class="card-stack">
          ${recurring.length ? recurring.map(renderRecurringCostCard).join("") : `<div class="empty-state"><p class="empty-copy">Lägg in exempelvis avbetalning, daglig kostnad eller annan fast post.</p></div>`}
        </div>
      </article>

      <article class="panel">
        <span class="kicker">Kostnadsformulär</span>
        <h3>${currentEdit("cost")?.id ? "Redigera kostnad" : "Lägg till kostnad"}</h3>
        <p class="meta-text">Här fungerar avbetalningar också. Skriv gärna kvarvarande belopp i anteckningen om posten är en skuld som ska följas upp.</p>
        ${selectedHousehold()
          ? renderForm("costForm", recurringCostFields(), currentEdit("cost") || {}, {
              submitLabel: currentEdit("cost")?.id ? "Spara kostnad" : "Skapa kostnad",
              canDelete: Boolean(currentEdit("cost")?.id),
              deleteLabel: "Ta bort kostnad",
            })
          : `<div class="empty-state"><p class="empty-copy">Välj hushåll först.</p></div>`}
      </article>
    </section>

    <section class="split-layout">
      <article class="panel">
        <div class="section-head">
          <div>
            <span class="kicker">Försäkringar</span>
            <h3>${policies.length ? `${policies.length} försäkringar` : "Lägg till första försäkringen"}</h3>
          </div>
          ${selectedHousehold() ? `<button class="ghost" type="button" data-action="new-record" data-module="insurance">Ny försäkring</button>` : ""}
        </div>
        <div class="card-stack">
          ${policies.length ? policies.map(renderInsuranceCard).join("") : `<div class="empty-state"><p class="empty-copy">Lägg in hem-, bil- eller personförsäkringar här.</p></div>`}
        </div>
      </article>

      <article class="panel">
        <span class="kicker">Försäkringsformulär</span>
        <h3>${currentEdit("insurance")?.id ? "Redigera försäkring" : "Lägg till försäkring"}</h3>
        ${selectedHousehold()
          ? renderForm("insuranceForm", insuranceFields(), currentEdit("insurance") || {}, {
              submitLabel: currentEdit("insurance")?.id ? "Spara försäkring" : "Skapa försäkring",
              canDelete: Boolean(currentEdit("insurance")?.id),
              deleteLabel: "Ta bort försäkring",
            })
          : `<div class="empty-state"><p class="empty-copy">Välj hushåll först.</p></div>`}
      </article>
    </section>
  `;
}

function renderHousingPage() {
  const items = housingForHousehold();
  const current = currentEdit("housing") || {};
  const evaluation = state.housingEvaluation;
  const stress = evaluation ? stressScenarioTotal(current, evaluation) : null;

  return `
    <section class="summary-hero">
      <article class="panel">
        <span class="kicker">Boendekalkyl</span>
        <h3>Vad kostar bostaden per månad?</h3>
        <p class="meta-text">Här ser du ränta, amortering, drift/avgift, försäkring och kvar att leva på i samma vy.</p>
        ${evaluation
          ? `<div class="metrics-grid">
              ${renderMetricCard("Månadskostnad", money(evaluation.monthly_total_cost), "Total månadskostnad för scenariot.", "warning")}
              ${renderMetricCard("Årskostnad", money(evaluation.yearly_total_cost), "Årligt utfall om läget håller i sig.")}
              ${renderMetricCard("Ränta per månad", money(evaluation.monthly_interest), "Baserat på angiven ränta.")}
              ${renderMetricCard("Amortering per månad", money(evaluation.monthly_amortization), "Baserat på angiven amortering.")}
              ${renderMetricCard("Kvar efter boendet", money(Number(selectedSummary()?.monthly_net_cashflow || 0) - Number(evaluation.monthly_total_cost || 0)), "En enkel indikation mot nuvarande hushållsöversikt.", Number(selectedSummary()?.monthly_net_cashflow || 0) - Number(evaluation.monthly_total_cost || 0) >= 0 ? "positive" : "danger")}
              ${renderMetricCard("Stresscenario (+2 % ränta)", money(stress), "Snabb stresstest för ränteläget.", "danger")}
            </div>`
          : `<div class="empty-state"><p class="empty-copy">Skapa eller välj ett scenario för att få kalkylen här.</p></div>`}
      </article>

      <article class="panel">
        <div class="section-head">
          <div>
            <span class="kicker">Sparade scenarier</span>
            <h3>${items.length ? `${items.length} scenarier` : "Inga scenarier ännu"}</h3>
          </div>
          ${selectedHousehold() ? `<button class="ghost" type="button" data-action="new-record" data-module="housing">Nytt scenario</button>` : ""}
        </div>
        <div class="card-stack">
          ${items.length ? items.map(renderHousingCard).join("") : `<div class="empty-state"><p class="empty-copy">Skapa ett scenario för att jämföra boendekostnader och stressnivåer.</p></div>`}
        </div>
      </article>
    </section>

    <section class="panel">
      <span class="kicker">Scenarioformulär</span>
      <h3>${current.id ? "Redigera boendescenario" : "Skapa nytt boendescenario"}</h3>
      ${selectedHousehold()
        ? renderForm("housingForm", housingFields(), current, {
            submitLabel: current.id ? "Spara scenario" : "Skapa scenario",
            canDelete: Boolean(current.id),
            deleteLabel: "Ta bort scenario",
          })
        : `<div class="empty-state"><p class="empty-copy">Välj hushåll först.</p></div>`}
    </section>
  `;
}

function renderDocumentsPage() {
  const items = documentsForHousehold();
  return `
    <section class="split-layout">
      <article class="panel">
        <span class="kicker">Ladda upp dokument</span>
        <h3>Avtal, kvitton, fakturor och låneavier</h3>
        <p class="meta-text">Dokumenten kopplas till hushållet och kan laddas ner igen när du behöver dem.</p>
        ${selectedHousehold()
          ? renderDocumentUploadForm()
          : `<div class="empty-state"><p class="empty-copy">Välj hushåll först så att dokumentet hamnar rätt.</p></div>`}
      </article>

      <article class="panel">
        <div class="section-head">
          <div>
            <span class="kicker">Uppladdade dokument</span>
            <h3>${items.length ? `${items.length} dokument` : "Inga dokument ännu"}</h3>
          </div>
        </div>
        <div class="card-stack">
          ${items.length ? items.map(renderDocumentCard).join("") : `<div class="empty-state"><p class="empty-copy">När du laddar upp avtal eller kvitton visas de här med tydliga etiketter.</p></div>`}
        </div>
      </article>
    </section>
  `;
}

function renderImprovementsPage() {
  const items = opportunitiesForHousehold();
  return `
    <section class="panel">
      <div class="section-head">
        <div>
          <span class="kicker">Förbättringsförslag</span>
          <h3>Vad kan hushållet göra härnäst?</h3>
          <p class="meta-text">Förslagen översätts till begripligt språk: besparingspotential, risk och arbetsinsats.</p>
        </div>
        <button class="primary" type="button" data-action="scan-opportunities" ${selectedHousehold() ? "" : "disabled"}>Analysera hushållet</button>
      </div>
      <div class="card-stack">
        ${items.length ? items.map(renderOpportunityCard).join("") : `<div class="empty-state"><p class="empty-copy">Det finns ännu inga förbättringsförslag sparade för det här hushållet.</p></div>`}
      </div>
    </section>
  `;
}

function renderMetricCard(label, value, text, tone = "") {
  return `
    <article class="metric-card ${tone}">
      <span class="metric-label">${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      <p class="subtle">${escapeHtml(text)}</p>
    </article>
  `;
}

function renderStatPill(label, value) {
  return `
    <article class="stat-pill">
      <span class="mini-label">${escapeHtml(label)}</span>
      <strong>${escapeHtml(String(value))}</strong>
    </article>
  `;
}

function renderFixedCostCards() {
  const cards = [
    ...recurringCostsForHousehold().map((item) => `
      <article class="record-card">
        <div class="record-header">
          <div>
            <h4 class="record-title">${escapeHtml(item.vendor || item.category || "Återkommande kostnad")}</h4>
            <p class="meta-text">${escapeHtml(recurringCostLabel(item.category))}${item.person_id ? ` · ${escapeHtml(personName(item.person_id))}` : ""}</p>
          </div>
          <div class="record-value">${money(amountToMonthlyCost(item))}</div>
        </div>
      </article>
    `),
    ...insuranceForHousehold().map((item) => `
      <article class="record-card">
        <div class="record-header">
          <div>
            <h4 class="record-title">${escapeHtml(item.provider)}</h4>
            <p class="meta-text">${escapeHtml(optionLabel(OPTIONS.insuranceType, item.type))}</p>
          </div>
          <div class="record-value">${money(item.premium_monthly)}</div>
        </div>
      </article>
    `),
  ].slice(0, 6);
  return cards.join("") || `<p class="empty-copy">Inga fasta kostnader eller försäkringar finns registrerade ännu.</p>`;
}

function renderPersonCard(item) {
  return `
    <article class="record-card ${currentEdit("person")?.id === item.id ? "is-active" : ""}">
      <div class="record-header">
        <div>
          <h4 class="record-title">${escapeHtml(item.name)}</h4>
          <p class="meta-text">${optionLabel(OPTIONS.role, item.role)} · ${item.active ? "Aktiv" : "Vilande"}</p>
        </div>
        <div class="card-actions">
          <button class="ghost" type="button" data-edit="person" data-id="${item.id}">Redigera</button>
        </div>
      </div>
    </article>
  `;
}

function renderIncomeCard(item) {
  return `
    <article class="record-card ${currentEdit("income")?.id === item.id ? "is-active" : ""}">
      <div class="record-header">
        <div>
          <h4 class="record-title">${optionLabel(OPTIONS.incomeType, item.type)}${item.source ? ` · ${escapeHtml(item.source)}` : ""}</h4>
          <p class="meta-text">${escapeHtml(personName(item.person_id))} · ${optionLabel(OPTIONS.frequency, item.frequency)}</p>
        </div>
        <div class="record-value">${money(item.net_amount || item.gross_amount)}</div>
      </div>
      <div class="card-actions">
        <button class="ghost" type="button" data-edit="income" data-id="${item.id}">Redigera</button>
      </div>
    </article>
  `;
}

function renderLoanCard(item) {
  return `
    <article class="record-card ${currentEdit("loan")?.id === item.id ? "is-active" : ""}">
      <div class="record-header">
        <div>
          <h4 class="record-title">${escapeHtml(item.purpose || optionLabel(OPTIONS.loanType, item.type))}${item.lender ? ` · ${escapeHtml(item.lender)}` : ""}</h4>
          <p class="meta-text">${item.person_id ? `${escapeHtml(personName(item.person_id))} · ` : ""}${optionLabel(OPTIONS.loanStatus, item.status)}</p>
        </div>
        <div class="record-value">${money(item.required_monthly_payment)}</div>
      </div>
      <div class="badge-row">
        <span class="badge">Skuld ${money(item.current_balance)}</span>
        ${item.remaining_term_months ? `<span class="badge muted">${number(item.remaining_term_months)} mån kvar</span>` : ""}
        ${item.nominal_rate ? `<span class="badge">${number(item.nominal_rate, 2)} % ränta</span>` : ""}
      </div>
      <div class="card-actions">
        <button class="ghost" type="button" data-edit="loan" data-id="${item.id}">Redigera</button>
      </div>
    </article>
  `;
}

function renderSubscriptionCard(item) {
  return `
    <article class="record-card ${currentEdit("subscription")?.id === item.id ? "is-active" : ""}">
      <div class="record-header">
        <div>
          <h4 class="record-title">${escapeHtml(item.provider)}${item.product_name ? ` · ${escapeHtml(item.product_name)}` : ""}</h4>
          <p class="meta-text">${optionLabel(OPTIONS.subscriptionCategory, item.category)}${item.person_id ? ` · ${escapeHtml(personName(item.person_id))}` : ""}</p>
        </div>
        <div class="record-value">${money(item.current_monthly_cost)}</div>
      </div>
      <div class="badge-row">
        <span class="badge">${optionLabel(OPTIONS.subscriptionCriticality, item.household_criticality)}</span>
        ${subscriptionSignals(item).map((signal) => `<span class="badge ${signal.tone}">${escapeHtml(signal.label)}</span>`).join("")}
        ${item.notice_period_days ? `<span class="badge muted">${item.notice_period_days} dagars uppsägning</span>` : ""}
      </div>
      <div class="card-actions">
        <button class="ghost" type="button" data-edit="subscription" data-id="${item.id}">Redigera</button>
      </div>
    </article>
  `;
}

function renderVehicleCard(item) {
  return `
    <article class="record-card ${currentEdit("vehicle")?.id === item.id ? "is-active" : ""}">
      <div class="record-header">
        <div>
          <h4 class="record-title">${escapeHtml([item.make, item.model].filter(Boolean).join(" ") || "Fordon")}</h4>
          <p class="meta-text">${item.owner_person_id ? `${escapeHtml(personName(item.owner_person_id))} · ` : ""}${item.year || "År ej angivet"}</p>
        </div>
        <div class="record-value">${money(vehicleMonthlyCost(item))}</div>
      </div>
      <div class="badge-row">
        <span class="badge">${optionLabel(OPTIONS.fuelType, item.fuel_type)}</span>
        ${item.loan_id ? `<span class="badge muted">Lån kopplat</span>` : ""}
      </div>
      <div class="card-actions">
        <button class="ghost" type="button" data-edit="vehicle" data-id="${item.id}">Redigera</button>
      </div>
    </article>
  `;
}

function renderAssetCard(item) {
  return `
    <article class="record-card ${currentEdit("asset")?.id === item.id ? "is-active" : ""}">
      <div class="record-header">
        <div>
          <h4 class="record-title">${escapeHtml(item.label || item.institution || optionLabel(OPTIONS.assetType, item.type))}</h4>
          <p class="meta-text">${optionLabel(OPTIONS.assetType, item.type)}${item.person_id ? ` · ${escapeHtml(personName(item.person_id))}` : ""}</p>
        </div>
        <div class="record-value">${money(item.market_value)}</div>
      </div>
      <div class="badge-row">
        <span class="badge">Likvid del ${money(item.liquid_value)}</span>
        ${item.pledged ? `<span class="badge warning">Pantsatt</span>` : ""}
      </div>
      <div class="card-actions">
        <button class="ghost" type="button" data-edit="asset" data-id="${item.id}">Redigera</button>
      </div>
    </article>
  `;
}

function renderHousingCard(item) {
  const active = currentEdit("housing")?.id === item.id;
  return `
    <article class="record-card ${active ? "is-active" : ""}">
      <div class="record-header">
        <div>
          <h4 class="record-title">${escapeHtml(item.label)}</h4>
          <p class="meta-text">${money(item.purchase_price)} i bostadspris · ${number(item.rate_assumption, 2)} % ränta</p>
        </div>
        <div class="card-actions">
          <button class="ghost" type="button" data-edit="housing" data-id="${item.id}">Redigera</button>
          <button class="primary" type="button" data-evaluate-housing="${item.id}">Visa kalkyl</button>
        </div>
      </div>
    </article>
  `;
}

function renderDocumentCard(item) {
  return `
    <article class="record-card">
      <div class="record-header">
        <div>
          <h4 class="record-title">${escapeHtml(item.file_name)}</h4>
          <p class="meta-text">${optionLabel(OPTIONS.documentType, item.document_type)}${item.issuer ? ` · ${escapeHtml(item.issuer)}` : ""}</p>
        </div>
        <a class="download-link" href="/documents/${item.id}/download">Ladda ned</a>
      </div>
      <div class="badge-row">
        <span class="badge">${dateLabel(item.uploaded_at)}</span>
        <span class="badge muted">${escapeHtml(item.extraction_status || "pending")}</span>
      </div>
    </article>
  `;
}

function renderOpportunityCard(item) {
  return `
    <article class="record-card">
      <div class="record-header">
        <div>
          <h4 class="record-title">${escapeHtml(item.title)}</h4>
          <p class="meta-text">${escapeHtml(item.rationale || opportunityAction(item.kind))}</p>
        </div>
        <div class="record-value">${money(item.estimated_monthly_saving)}</div>
      </div>
      <div class="badge-row">
        <span class="badge success">Besparing ${money(item.estimated_monthly_saving)} / mån</span>
        <span class="badge ${badgeTone(item.risk_level)}">Risk: ${riskLabel(item.risk_level)}</span>
        <span class="badge muted">${effortLabel(item.effort_level)}</span>
      </div>
      <p class="meta-text"><strong>Vad du kan göra:</strong> ${escapeHtml(opportunityAction(item.kind))}</p>
    </article>
  `;
}

function recurringCostLabel(value) {
  const map = Object.fromEntries(OPTIONS.recurringCostCategory);
  return map[value] || value || "Återkommande kostnad";
}

function amountToMonthlyCost(item) {
  const amount = Number(item.amount || 0);
  const frequency = item.frequency || "monthly";
  if (frequency === "yearly") return amount / 12;
  if (frequency === "weekly") return amount * (52 / 12);
  if (frequency === "biweekly") return amount * (26 / 12);
  if (frequency === "daily") return amount * (365 / 12);
  return amount;
}

function renderIncomeStats() {
  const items = incomesForHousehold();
  const summary = selectedSummary();
  return `
    <section class="panel">
      <div class="stats-strip">
        ${renderStatPill("Inkomstkällor", items.length)}
        ${renderStatPill("Summa per månad", money(summary?.monthly_income))}
        ${renderStatPill("Personer med inkomst", new Set(items.map((item) => item.person_id)).size)}
        ${renderStatPill("Netto ifyllt", items.filter((item) => item.net_amount != null).length)}
      </div>
    </section>
  `;
}

function renderRecurringCostCard(item) {
  return `
    <article class="record-card ${currentEdit("cost")?.id === item.id ? "is-active" : ""}">
      <div class="record-header">
        <div>
          <h4 class="record-title">${escapeHtml(item.vendor || recurringCostLabel(item.category))}</h4>
          <p class="meta-text">${escapeHtml(recurringCostLabel(item.category))}${item.person_id ? ` · ${escapeHtml(personName(item.person_id))}` : ""}</p>
        </div>
        <div class="record-value">${money(amountToMonthlyCost(item))}</div>
      </div>
      <div class="badge-row">
        <span class="badge">${optionLabel(OPTIONS.frequency, item.frequency)}</span>
        <span class="badge muted">${optionLabel(OPTIONS.variabilityClass, item.variability_class || "fixed")}</span>
        ${item.mandatory === false ? `<span class="badge warning">Inte nödvändig</span>` : `<span class="badge success">Fast post</span>`}
        ${item.note ? `<span class="badge muted">${escapeHtml(item.note)}</span>` : ""}
      </div>
      <div class="card-actions">
        <button class="ghost" type="button" data-edit="cost" data-id="${item.id}">Redigera</button>
      </div>
    </article>
  `;
}

function renderInsuranceCard(item) {
  return `
    <article class="record-card ${currentEdit("insurance")?.id === item.id ? "is-active" : ""}">
      <div class="record-header">
        <div>
          <h4 class="record-title">${escapeHtml(item.provider)}</h4>
          <p class="meta-text">${escapeHtml(optionLabel(OPTIONS.insuranceType, item.type))}</p>
        </div>
        <div class="record-value">${money(item.premium_monthly)}</div>
      </div>
      <div class="badge-row">
        <span class="badge">${escapeHtml(item.type || "Försäkring")}</span>
        ${item.deductible ? `<span class="badge muted">Självrisk ${money(item.deductible)}</span>` : ""}
      </div>
      <div class="card-actions">
        <button class="ghost" type="button" data-edit="insurance" data-id="${item.id}">Redigera</button>
      </div>
    </article>
  `;
}

function renderLoanStats() {
  const items = loansForHousehold();
  return `
    <section class="panel">
      <div class="stats-strip">
        ${renderStatPill("Lån", items.length)}
        ${renderStatPill("Total skuld", money(sum(items.map((item) => item.current_balance))))}
        ${renderStatPill("Månadskostnad", money(sum(items.map((item) => item.required_monthly_payment))))}
        ${renderStatPill("Aktiva lån", items.filter((item) => item.status === "active").length)}
      </div>
    </section>
  `;
}

function renderVehicleStats() {
  const items = vehiclesForHousehold();
  return `
    <section class="panel">
      <div class="stats-strip">
        ${renderStatPill("Fordon", items.length)}
        ${renderStatPill("Månadskostnad", money(sum(items.map(vehicleMonthlyCost))))}
        ${renderStatPill("Kopplade lån", items.filter((item) => item.loan_id).length)}
        ${renderStatPill("Bilvärde", money(sum(items.map((item) => item.estimated_value))))}
      </div>
    </section>
  `;
}

function renderAssetStats() {
  const items = assetsForHousehold();
  return `
    <section class="panel">
      <div class="stats-strip">
        ${renderStatPill("Tillgångar", items.length)}
        ${renderStatPill("Marknadsvärde", money(sum(items.map((item) => item.market_value))))}
        ${renderStatPill("Likvida medel", money(sum(items.map((item) => item.liquid_value))))}
        ${renderStatPill("Pantsatta", items.filter((item) => item.pledged).length)}
      </div>
    </section>
  `;
}

function renderIncomeFormBlock() {
  return `
    <span class="kicker">Inkomstformulär</span>
    <h3>${currentEdit("income")?.id ? "Redigera inkomst" : "Lägg till inkomst"}</h3>
    <p class="meta-text">Person väljs i listan i stället för via internt id. Minst netto eller brutto bör fyllas i.</p>
    ${renderForm("incomeForm", incomeFields(), currentEdit("income") || {}, {
      submitLabel: currentEdit("income")?.id ? "Spara inkomst" : "Skapa inkomst",
      canDelete: Boolean(currentEdit("income")?.id),
      deleteLabel: "Ta bort inkomst",
    })}
  `;
}

function renderLoanFormBlock() {
  return `
    <span class="kicker">Låneformulär</span>
    <h3>${currentEdit("loan")?.id ? "Redigera lån" : "Lägg till lån"}</h3>
    <p class="meta-text">Använd även för avbetalningar som bil, säng och ögonlaser.</p>
    ${renderForm("loanForm", loanFields(), currentEdit("loan") || {}, {
      submitLabel: currentEdit("loan")?.id ? "Spara lån" : "Skapa lån",
      canDelete: Boolean(currentEdit("loan")?.id),
      deleteLabel: "Ta bort lån",
    })}
  `;
}

function renderVehicleFormBlock() {
  return `
    <span class="kicker">Fordonsformulär</span>
    <h3>${currentEdit("vehicle")?.id ? "Redigera fordon" : "Lägg till fordon"}</h3>
    <p class="meta-text">Det viktigaste är vad fordonet kostar varje månad: skatt, bränsle, service och parkering.</p>
    ${renderForm("vehicleForm", vehicleFields(), currentEdit("vehicle") || {}, {
      submitLabel: currentEdit("vehicle")?.id ? "Spara fordon" : "Skapa fordon",
      canDelete: Boolean(currentEdit("vehicle")?.id),
      deleteLabel: "Ta bort fordon",
    })}
  `;
}

function renderAssetFormBlock() {
  return `
    <span class="kicker">Tillgångsformulär</span>
    <h3>${currentEdit("asset")?.id ? "Redigera tillgång" : "Lägg till tillgång"}</h3>
    <p class="meta-text">Lägg in typ, namn och värde. Om det är sparade pengar kan du även ange likvid del.</p>
    ${renderForm("assetForm", assetFields(), currentEdit("asset") || {}, {
      submitLabel: currentEdit("asset")?.id ? "Spara tillgång" : "Skapa tillgång",
      canDelete: Boolean(currentEdit("asset")?.id),
      deleteLabel: "Ta bort tillgång",
    })}
  `;
}

function renderDocumentUploadForm() {
  return `
    <form id="documentUploadForm" class="form-grid">
      ${renderField({ key: "document_type", label: "Typ av dokument", type: "select", options: OPTIONS.documentType, required: true })}
      ${renderField({ key: "issuer", label: "Avsändare eller leverantör", type: "text", placeholder: "Till exempel banken eller Tele2" })}
      ${renderField({ key: "currency", label: "Valuta", type: "text", placeholder: "SEK", default: "SEK" })}
      <div class="field full">
        <label for="document_file">Välj fil</label>
        <div class="upload-drop">
          <input id="document_file" name="file" type="file" required />
        </div>
        <p class="helper-text">Backend försöker extrahera text ur uppladdade PDF:er och dokument där det går. Bild- och screenshot-avläsning är förberedd i gränssnittet men inte implementerad ännu.</p>
      </div>
      <div class="field full">
        <label for="document_extracted_text">Valfri notis</label>
        <textarea id="document_extracted_text" name="extracted_text" placeholder="Till exempel vad dokumentet gäller eller vilken period det avser."></textarea>
        <p class="helper-text">Det här är bara en notis. När text kan extraheras ska den komma från filen, inte från en manuell tolkning här.</p>
      </div>
      <div class="field full">
        <div class="form-actions">
          <button class="primary" type="submit">Ladda upp dokument</button>
        </div>
      </div>
    </form>
  `;
}

function renderForm(formId, fields, values, { submitLabel, canDelete, deleteLabel }) {
  return `
    <form id="${formId}" class="form-grid">
      ${fields.map((field) => renderField(field, values[field.key])).join("")}
      <div class="field full">
        <div class="form-actions">
          <button class="primary" type="submit">${submitLabel}</button>
          <button class="ghost" type="button" data-reset-form="${formId}">Rensa</button>
          ${canDelete ? `<button class="danger" type="button" data-delete-form="${formId}">${deleteLabel}</button>` : ""}
        </div>
      </div>
    </form>
  `;
}

function renderField(field, value = null) {
  const selectedValue = value ?? field.default ?? "";
  if (field.type === "checkbox") {
    return `
      <div class="field checkbox-field ${field.full ? "full" : ""}">
        <input id="${field.key}" name="${field.key}" type="checkbox" ${selectedValue ? "checked" : ""} />
        <label for="${field.key}">${field.label}</label>
      </div>
    `;
  }

  if (field.type === "select") {
    return `
      <div class="field ${field.full ? "full" : ""}">
        <label for="${field.key}">${field.label}</label>
        <select id="${field.key}" name="${field.key}" ${field.required ? "required" : ""}>
          <option value="">Välj...</option>
          ${field.options.map(([optionValue, optionLabel]) => `<option value="${escapeHtml(optionValue)}" ${String(optionValue) === String(selectedValue) ? "selected" : ""}>${escapeHtml(optionLabel)}</option>`).join("")}
        </select>
      </div>
    `;
  }

  if (field.type === "textarea") {
    return `
      <div class="field ${field.full ? "full" : ""}">
        <label for="${field.key}">${field.label}</label>
        <textarea id="${field.key}" name="${field.key}" placeholder="${escapeHtml(field.placeholder || "")}">${escapeHtml(selectedValue)}</textarea>
      </div>
    `;
  }

  return `
    <div class="field ${field.full ? "full" : ""}">
      <label for="${field.key}">${field.label}</label>
      <input
        id="${field.key}"
        name="${field.key}"
        type="${field.type || "text"}"
        value="${escapeHtml(selectedValue)}"
        placeholder="${escapeHtml(field.placeholder || "")}"
        ${field.required ? "required" : ""}
        ${field.step ? `step="${field.step}"` : ""}
      />
    </div>
  `;
}

function householdFields() {
  return [
    { key: "name", label: "Namn på hushållet", type: "text", required: true, placeholder: "Till exempel Familjen Andersson" },
    { key: "currency", label: "Valuta", type: "text", placeholder: "SEK", default: "SEK" },
    { key: "primary_country", label: "Land", type: "text", placeholder: "SE", default: "SE" },
  ];
}

function personFields() {
  return [
    { key: "name", label: "Namn", type: "text", required: true },
    { key: "role", label: "Roll i hushållet", type: "select", options: OPTIONS.role, required: true },
    { key: "income_share_mode", label: "Hur ekonomin delas", type: "select", options: [["pooled", "Gemensamt"], ["exact", "Exakt fördelning"], ["split", "Delad"]], required: true, default: "pooled" },
    { key: "active", label: "Aktiv person i hushållet", type: "checkbox", full: true, default: true },
  ];
}

function incomeFields() {
  return [
    { key: "person_id", label: "Person", type: "select", options: peopleOptions(), required: true },
    { key: "type", label: "Typ av inkomst", type: "select", options: OPTIONS.incomeType, required: true },
    { key: "net_amount", label: "Belopp efter skatt", type: "number", step: "0.01", placeholder: "Till exempel 28000" },
    { key: "gross_amount", label: "Belopp före skatt", type: "number", step: "0.01", placeholder: "Fyll i om du hellre vill lagra brutto" },
    { key: "frequency", label: "Hur ofta", type: "select", options: OPTIONS.frequency, required: true, default: "monthly" },
    { key: "regularity", label: "Stabilitet", type: "select", options: OPTIONS.regularity, required: true, default: "fixed" },
    { key: "source", label: "Arbetsgivare eller källa", type: "text", placeholder: "Till exempel Arbetsgivare AB" },
    { key: "start_date", label: "Startdatum", type: "date" },
    { key: "end_date", label: "Slutdatum", type: "date" },
    { key: "verified", label: "Verifierad inkomst", type: "checkbox", full: true, default: false },
    { key: "note", label: "Anteckning", type: "textarea", full: true, placeholder: "Till exempel extra timlön eller oregelbunden del." },
  ];
}

function loanFields() {
  return [
    { key: "type", label: "Typ av lån", type: "select", options: OPTIONS.loanType, required: true },
    { key: "purpose", label: "Vad gäller lånet?", type: "text", placeholder: "Till exempel Säng eller Bil" },
    { key: "lender", label: "Bank eller långivare", type: "text", placeholder: "Till exempel SEB" },
    { key: "person_id", label: "Koppla till person", type: "select", options: [["", "Ingen särskild person"], ...peopleOptions()] },
    { key: "current_balance", label: "Kvar att betala", type: "number", step: "0.01", placeholder: "Till exempel 12000" },
    { key: "remaining_term_months", label: "Månader kvar", type: "number", placeholder: "Till exempel 8" },
    { key: "planned_end_date", label: "Planerat slutdatum", type: "date" },
    { key: "nominal_rate", label: "Ränta (%)", type: "number", step: "0.01", placeholder: "Till exempel 4.29" },
    { key: "required_monthly_payment", label: "Månadskostnad", type: "number", step: "0.01", placeholder: "Till exempel 7200" },
    { key: "status", label: "Status", type: "select", options: OPTIONS.loanStatus, required: true, default: "active" },
    { key: "repayment_model", label: "Amorteringsmodell", type: "select", options: OPTIONS.repaymentModel, required: true, default: "annuity" },
    { key: "linked_asset_id", label: "Kopplad tillgång", type: "select", options: [["", "Ingen koppling"], ...assetOptions()] },
    { key: "secured", label: "Säkrat lån", type: "checkbox", default: false },
    { key: "autopay", label: "Autogiro", type: "checkbox", default: false },
    { key: "note", label: "Anteckning", type: "textarea", full: true },
  ];
}

function recurringCostFields() {
  return [
    { key: "category", label: "Kategori", type: "select", options: OPTIONS.recurringCostCategory, required: true },
    { key: "vendor", label: "Leverantör eller namn", type: "text", placeholder: "Till exempel Resurs Bank" },
    { key: "person_id", label: "Koppla till person", type: "select", options: [["", "Ingen särskild person"], ...peopleOptions()] },
    { key: "amount", label: "Belopp", type: "number", required: true, step: "0.01" },
    { key: "frequency", label: "Hur ofta", type: "select", options: OPTIONS.frequency, required: true, default: "monthly" },
    { key: "mandatory", label: "Nödvändig", type: "checkbox", default: true },
    { key: "variability_class", label: "Typ", type: "select", options: OPTIONS.variabilityClass, required: true, default: "fixed" },
    { key: "controllability", label: "Kontroll", type: "select", options: [["locked", "Låst"], ["negotiable", "Förhandlingsbar"], ["reducible", "Kan sänkas"], ["discretionary", "Valbar"]], required: true, default: "locked" },
    { key: "due_day", label: "Förfallodag", type: "number" },
    { key: "start_date", label: "Startdatum", type: "date" },
    { key: "end_date", label: "Slutdatum", type: "date" },
    { key: "note", label: "Anteckning", type: "textarea", full: true, placeholder: "Skriv gärna kvarvarande avbetalning här, till exempel 12 000 kr kvar." },
  ];
}

function insuranceFields() {
  return [
    { key: "type", label: "Typ", type: "select", options: OPTIONS.insuranceType, required: true },
    { key: "provider", label: "Försäkringsbolag", type: "text", required: true, placeholder: "Till exempel Folksam" },
    { key: "premium_monthly", label: "Premie per månad", type: "number", required: true, step: "0.01" },
    { key: "deductible", label: "Självrisk", type: "number", step: "0.01" },
    { key: "coverage_tier", label: "Omfattning", type: "text", placeholder: "Till exempel Bas eller Plus" },
    { key: "renewal_date", label: "Förnyas", type: "date" },
    { key: "binding_end_date", label: "Bindningstid till", type: "date" },
    { key: "linked_asset_id", label: "Koppla tillgång", type: "select", options: [["", "Ingen koppling"], ...assetOptions()] },
    { key: "note", label: "Anteckning", type: "textarea", full: true },
  ];
}

function subscriptionFields() {
  return [
    { key: "category", label: "Typ av avtal", type: "select", options: OPTIONS.subscriptionCategory, required: true },
    { key: "provider", label: "Leverantör", type: "text", required: true, placeholder: "Till exempel Telia" },
    { key: "product_name", label: "Produkt eller plan", type: "text", placeholder: "Till exempel Mobilabonnemang 20 GB" },
    { key: "person_id", label: "Koppla till person", type: "select", options: [["", "Ingen särskild person"], ...peopleOptions()] },
    { key: "current_monthly_cost", label: "Nuvarande pris per månad", type: "number", required: true, step: "0.01" },
    { key: "ordinary_cost", label: "Ordinarie pris per månad", type: "number", step: "0.01" },
    { key: "promotional_cost", label: "Kampanjpris", type: "number", step: "0.01" },
    { key: "promotional_end_date", label: "Kampanjen slutar", type: "date" },
    { key: "binding_end_date", label: "Bindningstid till", type: "date" },
    { key: "notice_period_days", label: "Uppsägningstid i dagar", type: "number" },
    { key: "household_criticality", label: "Hur viktigt är avtalet?", type: "select", options: OPTIONS.subscriptionCriticality, required: true, default: "optional" },
    { key: "next_review_at", label: "Nästa granskning", type: "date" },
    { key: "auto_renew", label: "Förnyas automatiskt", type: "checkbox", default: true },
    { key: "market_checkable", label: "Går lätt att jämföra mot marknaden", type: "checkbox", default: true },
    { key: "note", label: "Anteckning", type: "textarea", full: true, placeholder: "Till exempel uppsägningsväg, lojalitetspris eller vad ni använder avtalet till." },
  ];
}

function vehicleFields() {
  return [
    { key: "owner_person_id", label: "Ägare", type: "select", options: [["", "Ingen särskild person"], ...peopleOptions()] },
    { key: "make", label: "Märke", type: "text", placeholder: "Volvo" },
    { key: "model", label: "Modell", type: "text", placeholder: "V60" },
    { key: "year", label: "Årsmodell", type: "number" },
    { key: "fuel_type", label: "Drivmedel", type: "select", options: OPTIONS.fuelType },
    { key: "estimated_value", label: "Uppskattat värde", type: "number", step: "0.01" },
    { key: "loan_id", label: "Kopplat lån", type: "select", options: [["", "Inget lån"], ...loanOptions()] },
    { key: "insurance_policy_id", label: "Kopplad försäkring", type: "select", options: [["", "Ingen försäkring"], ...insuranceOptions()] },
    { key: "tax_monthly_estimate", label: "Skatt per månad", type: "number", step: "0.01" },
    { key: "fuel_monthly_estimate", label: "Bränsle/el per månad", type: "number", step: "0.01" },
    { key: "service_monthly_estimate", label: "Service per månad", type: "number", step: "0.01" },
    { key: "parking_monthly_estimate", label: "Parkering per månad", type: "number", step: "0.01" },
    { key: "note", label: "Anteckning", type: "textarea", full: true },
  ];
}

function assetFields() {
  return [
    { key: "type", label: "Typ av tillgång", type: "select", options: OPTIONS.assetType, required: true },
    { key: "label", label: "Namn eller etikett", type: "text", placeholder: "Till exempel Buffertsparande" },
    { key: "institution", label: "Bank eller aktör", type: "text", placeholder: "Till exempel Avanza eller Handelsbanken" },
    { key: "person_id", label: "Koppla till person", type: "select", options: [["", "Ingen särskild person"], ...peopleOptions()] },
    { key: "market_value", label: "Marknadsvärde", type: "number", step: "0.01" },
    { key: "liquid_value", label: "Likvid del", type: "number", step: "0.01" },
    { key: "pledged", label: "Pantsatt", type: "checkbox", default: false },
    { key: "note", label: "Anteckning", type: "textarea", full: true },
  ];
}

function housingFields() {
  return [
    { key: "label", label: "Namn på scenario", type: "text", required: true, placeholder: "Till exempel Lägenhet i Solna" },
    { key: "purchase_price", label: "Bostadspris", type: "number", step: "0.01" },
    { key: "down_payment", label: "Kontantinsats", type: "number", step: "0.01" },
    { key: "mortgage_needed", label: "Bolån", type: "number", step: "0.01" },
    { key: "rate_assumption", label: "Ränta (%)", type: "number", step: "0.01" },
    { key: "amortization_rate", label: "Amortering (%)", type: "number", step: "0.01" },
    { key: "monthly_fee_or_operating_cost", label: "Avgift eller drift per månad", type: "number", step: "0.01" },
    { key: "monthly_insurance", label: "Försäkring per månad", type: "number", step: "0.01" },
    { key: "monthly_property_cost_estimate", label: "Övriga boendekostnader per månad", type: "number", step: "0.01" },
    { key: "note", label: "Anteckning", type: "textarea", full: true },
  ];
}

function peopleOptions() {
  return peopleForHousehold().map((item) => [item.id, item.name]);
}

function assetOptions() {
  return assetsForHousehold().map((item) => [item.id, item.label || item.institution || optionLabel(OPTIONS.assetType, item.type)]);
}

function loanOptions() {
  return loansForHousehold().map((item) => [item.id, loanName(item.id)]);
}

function insuranceOptions() {
  return insuranceForHousehold().map((item) => [item.id, `${item.provider} · ${money(item.premium_monthly)}`]);
}

function vehicleMonthlyCost(item) {
  return sum([
    item.tax_monthly_estimate,
    item.fuel_monthly_estimate,
    item.service_monthly_estimate,
    item.parking_monthly_estimate,
    item.toll_monthly_estimate,
    item.tire_monthly_estimate,
  ]);
}

function stressScenarioTotal(current, evaluation) {
  const mortgage = Number(current.mortgage_needed || evaluation.mortgage_needed || 0);
  const rate = Number(current.rate_assumption || 0) + 2;
  const interest = mortgage * (rate / 100) / 12;
  return interest
    + Number(evaluation.monthly_amortization || 0)
    + Number(evaluation.monthly_operating_cost || 0)
    + Number(evaluation.monthly_insurance || 0)
    + Number(evaluation.monthly_property_cost_estimate || 0);
}

function sum(values) {
  return values.reduce((total, value) => total + Number(value || 0), 0);
}

async function handlePageClick(event) {
  const navTarget = event.target.closest("[data-nav]");
  if (navTarget) {
    state.page = navTarget.dataset.nav;
    persistPage();
    render();
    return;
  }

  const editTarget = event.target.closest("[data-edit]");
  if (editTarget) {
    const moduleKey = editTarget.dataset.edit;
    const item = findItemByModuleAndId(moduleKey, Number(editTarget.dataset.id));
    setEdit(moduleKey, item);
    if (moduleKey === "housing" && item) {
      await loadHousingEvaluation(item.id);
    }
    render();
    return;
  }

  const evaluateTarget = event.target.closest("[data-evaluate-housing]");
  if (evaluateTarget) {
    const scenarioId = Number(evaluateTarget.dataset.evaluateHousing);
    const item = housingForHousehold().find((scenario) => scenario.id === scenarioId);
    setEdit("housing", item);
    await loadHousingEvaluation(scenarioId);
    render();
    return;
  }

  const newTarget = event.target.closest("[data-action='new-record']");
  if (newTarget) {
    setEdit(newTarget.dataset.module, null);
    if (newTarget.dataset.module === "housing") {
      state.housingEvaluation = null;
    }
    render();
    return;
  }

  const scanTarget = event.target.closest("[data-action='scan-opportunities']");
  if (scanTarget) {
    await scanOpportunities();
    return;
  }

  const promoteIngestTarget = event.target.closest("[data-action='promote-ingest']");
  if (promoteIngestTarget) {
    await promoteIngestSuggestions();
    return;
  }

  const clearIngestTarget = event.target.closest("[data-action='clear-ingest']");
  if (clearIngestTarget) {
    state.ui.ingestInput = "";
    state.ui.ingestKind = "text";
    state.ui.ingestDocumentId = null;
    state.ui.ingestSourceName = "";
    state.ui.ingestResult = null;
    render();
    return;
  }

  const analyzeDocumentTarget = event.target.closest("[data-action='analyze-document']");
  if (analyzeDocumentTarget) {
    await analyzeStoredDocument(Number(analyzeDocumentTarget.dataset.documentId));
    return;
  }

  const resetTarget = event.target.closest("[data-reset-form]");
  if (resetTarget) {
    resetFormState(resetTarget.dataset.resetForm);
    render();
    return;
  }

  const deleteTarget = event.target.closest("[data-delete-form]");
  if (deleteTarget) {
    await deleteFromForm(deleteTarget.dataset.deleteForm);
  }
}

async function handlePageSubmit(event) {
  event.preventDefault();
  const form = event.target;

  try {
    switch (form.id) {
      case "householdForm":
        await saveHousehold(form);
        break;
      case "personForm":
        await savePerson(form);
        break;
      case "incomeForm":
        await saveIncome(form);
        break;
      case "loanForm":
        await saveLoan(form);
        break;
      case "costForm":
        await saveRecurringCost(form);
        break;
      case "insuranceForm":
        await saveInsurance(form);
        break;
      case "subscriptionForm":
        await saveSubscription(form);
        break;
      case "vehicleForm":
        await saveVehicle(form);
        break;
      case "assetForm":
        await saveAsset(form);
        break;
      case "housingForm":
        await saveHousing(form);
        break;
      case "documentUploadForm":
        await uploadDocument(form);
        break;
      default:
        return;
    }
  } catch (error) {
    showToast(readError(error), "error");
  }
}

function resetFormState(formId) {
  const map = {
    householdForm: "household",
    personForm: "person",
    incomeForm: "income",
    loanForm: "loan",
    costForm: "cost",
    insuranceForm: "insurance",
    subscriptionForm: "subscription",
    vehicleForm: "vehicle",
    assetForm: "asset",
    housingForm: "housing",
  };
  const moduleKey = map[formId];
  if (moduleKey) setEdit(moduleKey, null);
}

async function deleteFromForm(formId) {
  const map = {
    householdForm: async () => {
      if (!selectedHousehold()) return;
      await request(`/households/${selectedHousehold().id}`, { method: "DELETE" });
      state.selectedHouseholdId = null;
      persistSelection();
      clearEdits();
      state.summary = null;
      state.housingEvaluation = null;
    },
    personForm: async () => deleteRecord("person", API.persons, currentEdit("person")),
    incomeForm: async () => deleteRecord("income", API.incomes, currentEdit("income")),
    loanForm: async () => deleteRecord("loan", API.loans, currentEdit("loan")),
    costForm: async () => deleteRecord("cost", API.recurringCosts, currentEdit("cost")),
    insuranceForm: async () => deleteRecord("insurance", API.insurancePolicies, currentEdit("insurance")),
    subscriptionForm: async () => deleteRecord("subscription", API.subscriptions, currentEdit("subscription")),
    vehicleForm: async () => deleteRecord("vehicle", API.vehicles, currentEdit("vehicle")),
    assetForm: async () => deleteRecord("asset", API.assets, currentEdit("asset")),
    housingForm: async () => {
      await deleteRecord("housing", API.housing, currentEdit("housing"));
      state.housingEvaluation = null;
    },
  };

  if (!map[formId]) return;
  await map[formId]();
  await refreshAllData();
  render();
  showToast("Posten togs bort.");
}

async function deleteRecord(moduleKey, endpoint, item) {
  if (!item?.id) return;
  await request(`${endpoint}/${item.id}`, { method: "DELETE" });
  setEdit(moduleKey, null);
}

function serializeForm(form, fields) {
  const payload = {};
  fields.forEach((field) => {
    const element = form.elements[field.key];
    if (!element) return;

    if (field.type === "checkbox") {
      payload[field.key] = element.checked;
      return;
    }

    const rawValue = element.value.trim();
    if (!rawValue) return;

    if (field.type === "number") {
      payload[field.key] = Number(rawValue);
      return;
    }

    payload[field.key] = rawValue;
  });
  return payload;
}

async function saveHousehold(form) {
  const payload = serializeForm(form, householdFields());
  const current = currentEdit("household") || selectedHousehold();
  const result = current?.id
    ? await request(`/households/${current.id}`, { method: "PUT", body: JSON.stringify(payload) })
    : await request(API.households, { method: "POST", body: JSON.stringify(payload) });
  state.selectedHouseholdId = result.id;
  persistSelection();
  setEdit("household", result);
  await refreshAllData();
  render();
  showToast(current?.id ? "Hushållet sparades." : "Hushållet skapades.");
}

async function savePerson(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const payload = serializeForm(form, personFields());
  payload.household_id = state.selectedHouseholdId;
  const current = currentEdit("person");
  await saveByMode(current, API.persons, payload);
  setEdit("person", null);
  await refreshAllData();
  render();
  showToast(current?.id ? "Personen sparades." : "Personen lades till.");
}

async function saveIncome(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  if (!peopleForHousehold().length) throw new Error("Lägg först till minst en person.");
  const payload = serializeForm(form, incomeFields());
  const current = currentEdit("income");
  await saveByMode(current, API.incomes, payload);
  setEdit("income", null);
  await refreshAllData();
  render();
  showToast(current?.id ? "Inkomsten sparades." : "Inkomsten skapades.");
}

async function saveLoan(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const payload = serializeForm(form, loanFields());
  payload.household_id = state.selectedHouseholdId;
  const current = currentEdit("loan");
  await saveByMode(current, API.loans, payload);
  setEdit("loan", null);
  await refreshAllData();
  render();
  showToast(current?.id ? "Lånet sparades." : "Lånet skapades.");
}

async function saveRecurringCost(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const payload = serializeForm(form, recurringCostFields());
  payload.household_id = state.selectedHouseholdId;
  const current = currentEdit("cost");
  await saveByMode(current, API.recurringCosts, payload);
  setEdit("cost", null);
  await refreshAllData();
  render();
  showToast(current?.id ? "Kostnaden sparades." : "Kostnaden skapades.");
}

async function saveInsurance(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const payload = serializeForm(form, insuranceFields());
  payload.household_id = state.selectedHouseholdId;
  const current = currentEdit("insurance");
  await saveByMode(current, API.insurancePolicies, payload);
  setEdit("insurance", null);
  await refreshAllData();
  render();
  showToast(current?.id ? "Försäkringen sparades." : "Försäkringen skapades.");
}

async function saveSubscription(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const payload = serializeForm(form, subscriptionFields());
  payload.household_id = state.selectedHouseholdId;
  const current = currentEdit("subscription");
  await saveByMode(current, API.subscriptions, payload);
  setEdit("subscription", null);
  await refreshAllData();
  render();
  showToast(current?.id ? "Avtalet sparades." : "Avtalet skapades.");
}

async function saveVehicle(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const payload = serializeForm(form, vehicleFields());
  payload.household_id = state.selectedHouseholdId;
  const current = currentEdit("vehicle");
  await saveByMode(current, API.vehicles, payload);
  setEdit("vehicle", null);
  await refreshAllData();
  render();
  showToast(current?.id ? "Fordonet sparades." : "Fordonet skapades.");
}

async function saveAsset(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const payload = serializeForm(form, assetFields());
  payload.household_id = state.selectedHouseholdId;
  const current = currentEdit("asset");
  await saveByMode(current, API.assets, payload);
  setEdit("asset", null);
  await refreshAllData();
  render();
  showToast(current?.id ? "Tillgången sparades." : "Tillgången skapades.");
}

async function saveHousing(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const payload = serializeForm(form, housingFields());
  payload.household_id = state.selectedHouseholdId;
  const current = currentEdit("housing");
  const result = await saveByMode(current, API.housing, payload);
  setEdit("housing", result);
  await refreshAllData();
  await loadHousingEvaluation(result.id);
  render();
  showToast(current?.id ? "Boendescenariot sparades." : "Boendescenariot skapades.");
}

async function uploadDocument(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const formData = new FormData(form);
  formData.set("household_id", String(state.selectedHouseholdId));
  const document = await request("/documents/upload", { method: "POST", body: formData, headers: {} });
  form.reset();
  await refreshAllData();
  render();
  const extraction = documentExtractionMeta(document.extraction_status);
  showToast(`Dokumentet laddades upp. ${extraction.label}.`);
}

async function saveByMode(current, endpoint, payload) {
  if (current?.id) {
    return request(`${endpoint}/${current.id}`, { method: "PUT", body: JSON.stringify(payload) });
  }
  return request(endpoint, { method: "POST", body: JSON.stringify(payload) });
}

async function scanOpportunities() {
  if (!selectedHousehold()) {
    showToast("Välj hushåll först.", "error");
    return;
  }
  try {
    await request(`/households/${state.selectedHouseholdId}/optimization_scan`, { method: "POST" });
    await refreshAllData();
    render();
    showToast("Förbättringsförslag uppdaterades.");
  } catch (error) {
    showToast(readError(error), "error");
  }
}

function moduleKeyForPage(pageKey) {
  const map = {
    incomes: "income",
    loans: "loan",
    costs: "cost",
    insurance: "insurance",
    subscriptions: "subscription",
    vehicles: "vehicle",
    assets: "asset",
    housing: "housing",
  };
  return map[pageKey];
}

function findItemByModuleAndId(moduleKey, id) {
  const collections = {
    person: peopleForHousehold(),
    income: incomesForHousehold(),
    loan: loansForHousehold(),
    cost: recurringCostsForHousehold(),
    insurance: insuranceForHousehold(),
    subscription: subscriptionsForHousehold(),
    vehicle: vehiclesForHousehold(),
    asset: assetsForHousehold(),
    housing: housingForHousehold(),
  };
  return collections[moduleKey]?.find((item) => item.id === id) || null;
}

function showToast(message, tone = "success") {
  els.toast.className = `toast ${tone}`;
  els.toast.textContent = message;
  els.toast.hidden = false;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    els.toast.hidden = true;
  }, 3200);
}

function readError(error) {
  if (error instanceof Error) {
    try {
      const parsed = JSON.parse(error.message);
      if (parsed?.detail) return parsed.detail;
    } catch (_ignored) {
      // Fall through to the original message when the backend returned plain text.
    }
    return error.message;
  }
  return String(error);
}

Object.assign(API, {
  drafts: "/extraction_drafts",
  scenarios: "/scenarios",
  scenarioResults: "/scenario_results",
  reports: "/report_snapshots",
  assistant: "/assistant/respond",
  ingestAnalyze: "/ingest_ai/analyze",
  ingestPromote: "/ingest_ai/promote",
});

PAGES.splice(
  0,
  PAGES.length,
  { key: "overview", label: "Översikt", path: "/" },
  { key: "register", label: "Registrera ekonomi", path: "/registrera" },
  { key: "persons", label: "Personer", path: "/personer" },
  { key: "incomes", label: "Inkomster", path: "/inkomster" },
  { key: "loans", label: "Lån", path: "/lan" },
  { key: "costs", label: "Återkommande kostnader", path: "/kostnader" },
  { key: "subscriptions", label: "Abonnemang och avtal", path: "/abonnemang" },
  { key: "insurance", label: "Försäkringar", path: "/forsakringar" },
  { key: "vehicles", label: "Fordon", path: "/fordon" },
  { key: "assets", label: "Tillgångar", path: "/tillgangar" },
  { key: "housing", label: "Boendekalkyl", path: "/boendekalkyl" },
  { key: "documents", label: "Dokument", path: "/dokument" },
  { key: "improvements", label: "Förbättringsförslag", path: "/forbattringsforslag" },
  { key: "scenarios", label: "Scenarier", path: "/scenarier" },
  { key: "reports", label: "Sparade rapporter", path: "/rapporter" },
  { key: "assistant", label: "Ekonomiassistent", path: "/ekonomiassistent" },
  { key: "household", label: "Hushåll", path: "/hushall" },
);

Object.assign(state.data, {
  drafts: [],
  scenarios: [],
  scenarioResults: [],
  reports: [],
});

state.ui = {
  sidebarOpen: false,
  openReportId: null,
  assistantMessages: [],
  assistantInput: "",
  assistantPending: false,
  ingestInput: "",
  ingestKind: "text",
  ingestDocumentId: null,
  ingestSourceName: "",
  ingestPending: false,
  ingestPromoting: false,
  ingestResult: null,
};

state.editing.scenario = null;

function pageConfigByKey(key) {
  return PAGES.find((page) => page.key === key) || PAGES[0];
}

function pageConfigByPath(pathname) {
  return PAGES.find((page) => page.path === pathname) || pageConfigByKey("overview");
}

function navigateTo(pageKey, historyMode = "push") {
  const page = pageConfigByKey(pageKey);
  state.page = page.key;
  persistPage();
  if (historyMode === "push") {
    history.pushState({}, "", page.path);
  } else if (historyMode === "replace") {
    history.replaceState({}, "", page.path);
  }
  render();
}

function bindElements() {
  els.nav = document.getElementById("mainNav");
  els.pageContent = document.getElementById("pageContent");
  els.householdSelect = document.getElementById("householdSelect");
  els.refreshButton = document.getElementById("refreshButton");
  els.toast = document.getElementById("toast");
  els.menuButton = document.getElementById("menuButton");
  els.closeSidebarButton = document.getElementById("closeSidebarButton");
  els.sidebar = document.getElementById("sidebar");
  els.sidebarOverlay = document.getElementById("sidebarOverlay");
  els.assistantNav = document.getElementById("assistantNav");
  els.dateStamp = document.getElementById("dateStamp");
}

function bindBaseEvents() {
  els.nav.addEventListener("click", handlePageClick);
  els.assistantNav.addEventListener("click", handlePageClick);
  els.pageContent.addEventListener("click", handlePageClick);
  els.pageContent.addEventListener("submit", handlePageSubmit);
  els.pageContent.addEventListener("input", handlePageInput);
  els.pageContent.addEventListener("change", handlePageInput);

  els.refreshButton.addEventListener("click", async () => {
    await refreshAllData();
    render();
    showToast("Data uppdaterades.");
  });

  els.householdSelect.addEventListener("change", async (event) => {
    state.selectedHouseholdId = Number(event.target.value) || null;
    persistSelection();
    clearEdits();
    state.ui.assistantMessages = [];
    state.ui.ingestInput = "";
    state.ui.ingestDocumentId = null;
    state.ui.ingestResult = null;
    await ensureSummaryLoaded();
    render();
  });

  if (els.menuButton) {
    els.menuButton.addEventListener("click", () => toggleSidebar(true));
  }
  if (els.closeSidebarButton) {
    els.closeSidebarButton.addEventListener("click", () => toggleSidebar(false));
  }
  if (els.sidebarOverlay) {
    els.sidebarOverlay.addEventListener("click", () => toggleSidebar(false));
  }

  window.addEventListener("popstate", () => {
    state.page = pageConfigByPath(location.pathname).key;
    persistPage();
    render();
  });
}

function toggleSidebar(open) {
  state.ui.sidebarOpen = Boolean(open);
  els.sidebar.classList.toggle("open", state.ui.sidebarOpen);
  els.sidebarOverlay.hidden = !state.ui.sidebarOpen;
}

async function refreshAllData() {
  const entries = await Promise.all([
    request(`${API.households}?skip=0&limit=200`).then((value) => ["households", value]),
    request(`${API.persons}?skip=0&limit=200`).then((value) => ["persons", value]),
    request(`${API.incomes}?skip=0&limit=200`).then((value) => ["incomes", value]),
    request(`${API.recurringCosts}?skip=0&limit=200`).then((value) => ["recurringCosts", value]),
    request(`${API.loans}?skip=0&limit=200`).then((value) => ["loans", value]),
    request(`${API.subscriptions}?skip=0&limit=200`).then((value) => ["subscriptions", value]),
    request(`${API.insurancePolicies}?skip=0&limit=200`).then((value) => ["insurancePolicies", value]),
    request(`${API.vehicles}?skip=0&limit=200`).then((value) => ["vehicles", value]),
    request(`${API.assets}?skip=0&limit=200`).then((value) => ["assets", value]),
    request(`${API.housing}?skip=0&limit=200`).then((value) => ["housing", value]),
    request(`${API.documents}?skip=0&limit=200`).then((value) => ["documents", value]),
    request(`${API.opportunities}?skip=0&limit=200`).then((value) => ["opportunities", value]),
    request(`${API.drafts}?skip=0&limit=200`).then((value) => ["drafts", value]),
    request(`${API.scenarios}?skip=0&limit=200`).then((value) => ["scenarios", value]),
    request(`${API.scenarioResults}?skip=0&limit=200`).then((value) => ["scenarioResults", value]),
    request(`${API.reports}?skip=0&limit=200`).then((value) => ["reports", value]),
  ]);

  state.data = { ...state.data, ...Object.fromEntries(entries) };
  if (!selectedHousehold() && households().length) {
    state.selectedHouseholdId = households()[0].id;
    persistSelection();
  }
  await ensureSummaryLoaded();
}

function render() {
  const routePage = pageConfigByPath(location.pathname);
  if (routePage.key !== state.page) {
    state.page = routePage.key;
    persistPage();
  }
  renderHouseholdSelect();
  renderNav();
  renderTopbar();
  els.pageContent.innerHTML = renderPage();
  toggleSidebar(false);
}

function renderTopbar() {
  const today = new Intl.DateTimeFormat("sv-SE", { year: "numeric", month: "long" }).format(new Date());
  els.dateStamp.textContent = today.charAt(0).toUpperCase() + today.slice(1);
}

function renderNav() {
  const navItems = PAGES.filter((page) => !["assistant", "household"].includes(page.key));
  els.nav.innerHTML = navItems
    .map(
      (page) => `
        <button class="nav-link ${page.key === state.page ? "active" : ""}" type="button" data-route="${page.path}">
          <span class="nav-icon">${navGlyph(page.key)}</span>
          <span>${page.label}</span>
        </button>
      `
    )
    .join("");
  els.assistantNav.innerHTML = `
    <button class="nav-link ai-link ${state.page === "assistant" ? "active" : ""}" type="button" data-route="/ekonomiassistent">
      <span class="nav-icon">✦</span>
      <span>Ekonomiassistent</span>
    </button>
  `;
}

function navGlyph(key) {
  const icons = {
    overview: "◫",
    register: "✎",
    household: "⌂",
    persons: "☺",
    incomes: "₿",
    loans: "¤",
    costs: "≈",
    subscriptions: "☰",
    insurance: "⛨",
    vehicles: "▣",
    assets: "◌",
    housing: "▤",
    documents: "☷",
    improvements: "✷",
    scenarios: "△",
    reports: "☱",
    assistant: "✦",
  };
  return icons[key] || "•";
}

function renderPage() {
  switch (state.page) {
    case "overview":
      return renderOverviewPageV2();
    case "register":
      return renderRegisterPage();
    case "household":
      return renderHouseholdPageV2();
    case "persons":
      return renderPersonsPage();
    case "incomes":
      return renderIncomesPage();
    case "loans":
      return renderLoansPage();
    case "costs":
      return renderRecurringCostsPageV2();
    case "subscriptions":
      return renderSubscriptionsPageV2();
    case "insurance":
      return renderInsurancePageV2();
    case "vehicles":
      return renderVehiclesPageV2();
    case "assets":
      return renderAssetsPageV2();
    case "housing":
      return renderHousingPageV2();
    case "documents":
      return renderDocumentsPageV2();
    case "improvements":
      return renderImprovementsPageV2();
    case "scenarios":
      return renderScenariosPageV2();
    case "reports":
      return renderReportsPageV2();
    case "assistant":
      return renderAssistantPageV2();
    default:
      return renderOverviewPageV2();
  }
}

function renderPageHeader(title, description, actions = "") {
  return `
    <section class="page-head">
      <div>
        <span class="page-eyebrow">Ekonomi</span>
        <h2>${escapeHtml(title)}</h2>
        <p class="page-subtitle">${escapeHtml(description)}</p>
      </div>
      <div class="top-actions">${actions}</div>
    </section>
  `;
}

function renderStatCard(label, value, note = "") {
  return `
    <article class="stats-card">
      <label>${escapeHtml(label)}</label>
      <strong>${escapeHtml(String(value))}</strong>
      ${note ? `<span>${escapeHtml(note)}</span>` : ""}
    </article>
  `;
}

function renderOverviewPageV2() {
  const household = selectedHousehold();
  if (!household) {
    return `
      <section class="page-wrap">
        ${renderPageHeader("Ekonomi", "Börja med att skapa ett hushåll för att koppla riktiga data och flöden.")}
        <article class="panel">
          <div class="empty-state">
            <p>Inget hushåll är valt ännu.</p>
            <div class="actions-row">
              <button class="primary" type="button" data-route="/hushall">Skapa hushåll</button>
              <button class="ghost" type="button" data-route="/registrera">Guidad registrering</button>
            </div>
          </div>
        </article>
      </section>
    `;
  }

  const summary = selectedSummary() || {};
  const opportunities = opportunitiesForHousehold().slice().sort((a, b) => Number(b.estimated_monthly_saving || 0) - Number(a.estimated_monthly_saving || 0)).slice(0, 3);
  const subscriptions = subscriptionsForHousehold().slice().sort((a, b) => Number(b.current_monthly_cost || 0) - Number(a.current_monthly_cost || 0)).slice(0, 4);
  const drafts = draftsForHousehold();
  const reports = reportsForHousehold().slice().sort((a, b) => new Date(b.generated_at).getTime() - new Date(a.generated_at).getTime()).slice(0, 2);
  return `
    <section class="page-wrap">
      ${renderPageHeader("Ekonomi", household.name, `
        <button class="ghost" type="button" data-route="/abonnemang">Granska avtal</button>
        <button class="primary" type="button" data-route="/ekonomiassistent">Fråga AI</button>
      `)}
      <section class="stats-grid">
        ${renderStatCard("Nettoinkomst / månad", money(summary.monthly_income), `${summary.counts?.income_sources || 0} inkomstkällor`)}
        ${renderStatCard("Totala kostnader / månad", money(summary.monthly_total_expenses), `${summary.counts?.recurring_costs || 0} kostnader, ${summary.counts?.subscription_contracts || 0} avtal`)}
        ${renderStatCard("Kvar efter kostnader", money(summary.monthly_net_cashflow), summary.monthly_net_cashflow >= 0 ? "Positivt kassaflöde" : "Negativt kassaflöde")}
        ${renderStatCard("Nettoförmögenhet", money(summary.net_worth_estimate), `${money(summary.asset_market_value)} tillgångar minus ${money(summary.loan_balance_total)} lån`)}
      </section>

      <section class="hero-grid">
        <article class="panel">
          <span class="section-eyebrow">Vad bör ni göra nu?</span>
          <h3>Prioriterade nästa steg</h3>
          <div class="record-grid">
            ${onboardingSteps().slice(0, 3).map((step, index) => `
              <article class="record-card">
                <div class="record-title-row">
                  <div>
                    <div class="badge">${index + 1}</div>
                    <h4 class="record-title">${escapeHtml(step.title)}</h4>
                  </div>
                  <button class="ghost compact" type="button" data-nav="${step.page}">Öppna</button>
                </div>
                <p class="muted">${escapeHtml(step.text)}</p>
              </article>
            `).join("") || `<div class="empty-state"><p>Grunden finns på plats.</p></div>`}
          </div>
        </article>
        <article class="panel">
          <span class="section-eyebrow">Kommande händelser</span>
          <h3>Sådant att hålla koll på</h3>
          <div class="record-grid">
            ${renderEventCard("Avtal att granska", `${dueForReviewCount()} st`, dueForReviewCount() ? "warning" : "muted")}
            ${renderEventCard("Dokumentutkast", `${drafts.length} st`, drafts.length ? "info" : "muted")}
            ${renderEventCard("Rapporter sparade", `${reportsForHousehold().length} st`, reportsForHousehold().length ? "success" : "muted")}
          </div>
        </article>
      </section>

      <section class="split-layout">
        <article class="panel">
          <span class="section-eyebrow">Kostnader att granska</span>
          <h3>Abonnemang och avtal</h3>
          <div class="record-grid">
            ${subscriptions.map((item) => renderSubscriptionRowV2(item)).join("") || `<div class="empty-state"><p>Det finns inga abonnemang registrerade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel">
          <span class="section-eyebrow">Förbättringsförslag</span>
          <h3>Riktiga besparingsmöjligheter</h3>
          <div class="record-grid">
            ${opportunities.map((item) => renderOpportunityCardV2(item)).join("") || `<div class="empty-state"><p>Det finns ännu inga förbättringsförslag. Kör en skanning för att skapa riktiga förslag.</p><button class="primary" type="button" data-action="scan-opportunities">Kör ny skanning</button></div>`}
          </div>
        </article>
      </section>

      <section class="split-layout">
        <article class="panel">
          <span class="section-eyebrow">Senaste dokument</span>
          <h3>Dokument och draft-flöden</h3>
          <div class="record-grid">
            ${documentsForHousehold().slice(0, 3).map((item) => renderDocumentRowV2(item)).join("") || `<div class="empty-state"><p>Inga dokument uppladdade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel">
          <span class="section-eyebrow">Rapporter</span>
          <h3>Sparade sammanfattningar</h3>
          <div class="record-grid">
            ${reports.map((item) => renderReportRowV2(item)).join("") || `<div class="empty-state"><p>Inga sparade rapporter ännu.</p></div>`}
          </div>
        </article>
      </section>
    </section>
  `;
}

function renderEventCard(label, value, tone) {
  return `<article class="record-card"><div class="badge ${tone}">${escapeHtml(value)}</div><h4 class="record-title">${escapeHtml(label)}</h4></article>`;
}

function renderHouseholdPageV2() {
  const householdsList = households();
  const household = selectedHousehold();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Hushåll", "Er gemensamma ekonomi", `
        <button class="primary" type="button" data-action="new-household">Nytt hushåll</button>
      `)}
      <section class="split-layout">
        <article class="panel">
          <span class="section-eyebrow">Hushåll</span>
          <h3>${household ? escapeHtml(household.name) : "Skapa första hushållet"}</h3>
          <div class="record-grid">
            ${householdsList.map((item) => `
              <article class="record-card">
                <div class="record-title-row">
                  <div>
                    <h4 class="record-title">${escapeHtml(item.name)}</h4>
                    <p class="muted">${escapeHtml(item.primary_country || "SE")} · ${escapeHtml(item.currency || "SEK")}</p>
                  </div>
                  <div class="actions-row">
                    <button class="ghost compact" type="button" data-select-household="${item.id}">Välj</button>
                    <button class="ghost compact" type="button" data-edit-household="${item.id}">Redigera</button>
                  </div>
                </div>
              </article>
            `).join("") || `<div class="empty-state"><p>Inga hushåll finns ännu.</p></div>`}
          </div>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Hushållets grund</span>
          <h3>${household ? "Redigera hushåll" : "Skapa hushåll"}</h3>
          ${renderForm("householdForm", householdFields(), currentEdit("household") || household || {}, {
            submitLabel: household ? "Spara hushåll" : "Skapa hushåll",
            canDelete: Boolean((currentEdit("household") || household)?.id),
            deleteLabel: "Ta bort hushåll",
          })}
        </article>
      </section>
    </section>
  `;
}

function renderPersonsPage() {
  const items = peopleForHousehold();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Personer", "Personerna i ert hushåll", `<button class="primary" type="button" data-action="new-record" data-module="person">Lägg till person</button>`)}
      <section class="split-layout">
        <article class="panel">
          <div class="record-grid two">
            ${items.map((item) => `
              <article class="record-card">
                <div class="record-title-row">
                  <div>
                    <h4 class="record-title">${escapeHtml(item.name)}</h4>
                    <p class="muted">${optionLabel(OPTIONS.role, item.role)} · ${item.active ? "Aktiv" : "Vilande"}</p>
                  </div>
                  <button class="ghost compact" type="button" data-edit="person" data-id="${item.id}">Redigera</button>
                </div>
              </article>
            `).join("") || `<div class="empty-state"><p>Inga personer registrerade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Person</span>
          <h3>${currentEdit("person")?.id ? "Redigera person" : "Lägg till person"}</h3>
          ${selectedHousehold() ? renderForm("personForm", personFields(), currentEdit("person") || {}, {
            submitLabel: currentEdit("person")?.id ? "Spara person" : "Lägg till person",
            canDelete: Boolean(currentEdit("person")?.id),
            deleteLabel: "Ta bort person",
          }) : `<div class="empty-state"><p>Välj hushåll först.</p></div>`}
        </article>
      </section>
    </section>
  `;
}

function renderIncomesPage() {
  const items = incomesForHousehold();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Inkomster", "Alla inkomstkällor i hushållet", `<button class="primary" type="button" data-action="new-record" data-module="income">Lägg till inkomst</button>`)}
      <section class="stats-grid three">
        ${renderStatCard("Inkomstkällor", items.length)}
        ${renderStatCard("Netto / månad", money(selectedSummary()?.monthly_income_net || 0))}
        ${renderStatCard("Poster med netto", items.filter((item) => item.net_amount != null).length)}
      </section>
      <section class="split-layout">
        <article class="table-card">
          <table class="data-table">
            <thead>
              <tr>
                <th>Person</th>
                <th>Typ</th>
                <th class="align-right">Netto / mån</th>
                <th class="align-right">Brutto</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              ${items.map((item) => `
                <tr>
                  <td>${escapeHtml(personName(item.person_id))}</td>
                  <td>${escapeHtml(optionLabel(OPTIONS.incomeType, item.type))}</td>
                  <td class="align-right">${money(item.net_amount || 0)}</td>
                  <td class="align-right">${money(item.gross_amount || 0)}</td>
                  <td><span class="badge ${item.verified ? "success" : "muted"}">${item.verified ? "Verifierad" : "Ej verifierad"}</span></td>
                  <td class="align-right"><button class="ghost compact" type="button" data-edit="income" data-id="${item.id}">Redigera</button></td>
                </tr>
              `).join("") || `<tr><td colspan="6"><div class="empty-state"><p>Inga inkomster registrerade ännu.</p></div></td></tr>`}
            </tbody>
          </table>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Inkomst</span>
          <h3>${currentEdit("income")?.id ? "Redigera inkomst" : "Lägg till inkomst"}</h3>
          ${renderForm("incomeForm", incomeFields(), currentEdit("income") || {}, {
            submitLabel: currentEdit("income")?.id ? "Spara inkomst" : "Lägg till inkomst",
            canDelete: Boolean(currentEdit("income")?.id),
            deleteLabel: "Ta bort inkomst",
          })}
        </article>
      </section>
    </section>
  `;
}

function renderLoansPage() {
  const items = loansForHousehold();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Lån", "Alla lån i hushållet", `<button class="primary" type="button" data-action="new-record" data-module="loan">Lägg till lån</button>`)}
      <section class="stats-grid three">
        ${renderStatCard("Lån", items.length)}
        ${renderStatCard("Total skuld", money(sum(items.map((item) => item.current_balance))))}
        ${renderStatCard("Månadskostnad", money(sum(items.map((item) => item.required_monthly_payment))))}
      </section>
      <section class="split-layout">
        <article class="panel">
          <div class="record-grid">
            ${items.map((item) => `
              <article class="record-card">
                <div class="record-title-row">
                  <div>
                    <h4 class="record-title">${escapeHtml(item.lender || optionLabel(OPTIONS.loanType, item.type))}</h4>
                    <p class="muted">${escapeHtml(item.purpose || optionLabel(OPTIONS.loanType, item.type))}</p>
                  </div>
                  <button class="ghost compact" type="button" data-edit="loan" data-id="${item.id}">Redigera</button>
                </div>
                <div class="detail-grid">
                  ${detailCell("Skuld", money(item.current_balance))}
                  ${detailCell("Ränta", `${number(item.nominal_rate, 2)} %`)}
                  ${detailCell("Månadskostnad", money(item.required_monthly_payment))}
                  ${detailCell("Status", optionLabel(OPTIONS.loanStatus, item.status))}
                </div>
              </article>
            `).join("") || `<div class="empty-state"><p>Inga lån registrerade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Lån</span>
          <h3>${currentEdit("loan")?.id ? "Redigera lån" : "Lägg till lån"}</h3>
          ${renderForm("loanForm", loanFields(), currentEdit("loan") || {}, {
            submitLabel: currentEdit("loan")?.id ? "Spara lån" : "Lägg till lån",
            canDelete: Boolean(currentEdit("loan")?.id),
            deleteLabel: "Ta bort lån",
          })}
        </article>
      </section>
    </section>
  `;
}

function renderRecurringCostsPageV2() {
  const items = recurringCostsForHousehold();
  const monthlyTotal = sum(items.map((item) => amountToMonthlyCost(item)));
  const mandatoryCount = items.filter((item) => item.mandatory !== false).length;
  const reducibleMonthly = sum(
    items
      .filter((item) => ["negotiable", "reducible", "discretionary"].includes(String(item.controllability)))
      .map((item) => amountToMonthlyCost(item))
  );
  return `
    <section class="page-wrap">
      ${renderPageHeader(
        "Återkommande kostnader",
        "Månadsposter som inte är abonnemang eller försäkringar",
        `<button class="primary" type="button" data-action="new-record" data-module="cost">Lägg till kostnad</button>`
      )}
      <section class="stats-grid">
        ${renderStatCard("Poster", items.length)}
        ${renderStatCard("Total kostnad / månad", money(monthlyTotal))}
        ${renderStatCard("Nödvändiga poster", mandatoryCount)}
        ${renderStatCard("Möjliga att påverka", money(reducibleMonthly))}
      </section>
      <section class="split-layout">
        <article class="panel">
          <div class="section-head">
            <div>
              <span class="section-eyebrow">Kostnadslista</span>
              <h3>${items.length ? `${items.length} återkommande poster` : "Lägg till första återkommande kostnaden"}</h3>
              <p class="meta-text">Här ligger till exempel avbetalningar, fasta familjeposter och andra återkommande kostnader. Försäkringar har en egen modul.</p>
            </div>
          </div>
          <div class="record-grid">
            ${items.map((item) => renderRecurringCostCard(item)).join("") || `<div class="empty-state"><p>Inga återkommande kostnader registrerade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Kostnad</span>
          <h3>${currentEdit("cost")?.id ? "Redigera återkommande kostnad" : "Lägg till återkommande kostnad"}</h3>
          <p class="muted">Backend fortsätter äga summeringen. Här registrerar ni bara posten, inte själva ekonomimatematiken.</p>
          ${renderForm("costForm", recurringCostFields(), currentEdit("cost") || {}, {
            submitLabel: currentEdit("cost")?.id ? "Spara kostnad" : "Lägg till kostnad",
            canDelete: Boolean(currentEdit("cost")?.id),
            deleteLabel: "Ta bort kostnad",
          })}
        </article>
      </section>
    </section>
  `;
}

function renderSubscriptionsPageV2() {
  const items = subscriptionsForHousehold();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Abonnemang och avtal", "Alla löpande abonnemang och avtal i hushållet", `<button class="primary" type="button" data-action="new-record" data-module="subscription">Lägg till abonnemang</button>`)}
      <section class="stats-grid">
        ${renderStatCard("Antal avtal", items.length)}
        ${renderStatCard("Total kostnad / månad", money(sum(items.map((item) => item.current_monthly_cost))))}
        ${renderStatCard("Att granska", dueForReviewCount())}
        ${renderStatCard("Möjlig prisökning", money(sum(items.map((item) => Math.max(0, Number(item.ordinary_cost || 0) - Number(item.current_monthly_cost || 0))))))}
      </section>
      <section class="split-layout">
        <article class="panel">
          <div class="record-grid">
            ${items.map((item) => renderSubscriptionRowV2(item)).join("") || `<div class="empty-state"><p>Inga abonnemang registrerade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Avtal</span>
          <h3>${currentEdit("subscription")?.id ? "Redigera avtal" : "Lägg till avtal"}</h3>
          ${renderForm("subscriptionForm", subscriptionFields(), currentEdit("subscription") || {}, {
            submitLabel: currentEdit("subscription")?.id ? "Spara avtal" : "Lägg till avtal",
            canDelete: Boolean(currentEdit("subscription")?.id),
            deleteLabel: "Ta bort avtal",
          })}
        </article>
      </section>
    </section>
  `;
}

function renderSubscriptionRowV2(item) {
  return `
    <article class="record-card">
      <div class="record-title-row">
        <div>
          <h4 class="record-title">${escapeHtml(item.provider)}${item.product_name ? ` · ${escapeHtml(item.product_name)}` : ""}</h4>
          <p class="muted">${escapeHtml(optionLabel(OPTIONS.subscriptionCategory, item.category))}${item.next_review_at ? ` · nästa granskning ${dateLabel(item.next_review_at)}` : ""}</p>
        </div>
        <div class="actions-row">
          <span class="record-value">${money(item.current_monthly_cost)}</span>
          <button class="ghost compact" type="button" data-edit="subscription" data-id="${item.id}">Redigera</button>
        </div>
      </div>
      <div class="badge-row">
        <span class="badge">${escapeHtml(optionLabel(OPTIONS.subscriptionCriticality, item.household_criticality))}</span>
        ${item.ordinary_cost ? `<span class="badge warning">Ordinarie pris ${money(item.ordinary_cost)}</span>` : ""}
        ${item.binding_end_date ? `<span class="badge muted">Bindning till ${dateLabel(item.binding_end_date)}</span>` : ""}
      </div>
    </article>
  `;
}

function renderInsurancePageV2() {
  const items = insuranceForHousehold();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Försäkringar", "Alla försäkringar i hushållet", `<button class="primary" type="button" data-action="new-record" data-module="insurance">Lägg till försäkring</button>`)}
      <section class="split-layout">
        <article class="panel">
          <div class="record-grid two">
            ${items.map((item) => `
              <article class="record-card">
                <div class="record-title-row">
                  <div>
                    <h4 class="record-title">${escapeHtml(item.provider)}</h4>
                    <p class="muted">${escapeHtml(optionLabel(OPTIONS.insuranceType, item.type))}</p>
                  </div>
                  <button class="ghost compact" type="button" data-edit="insurance" data-id="${item.id}">Redigera</button>
                </div>
                <div class="detail-grid">
                  ${detailCell("Premie", money(item.premium_monthly))}
                  ${detailCell("Självrisk", money(item.deductible))}
                  ${detailCell("Förnyelse", dateLabel(item.renewal_date))}
                  ${detailCell("Täckning", item.coverage_tier || "Ej angiven")}
                </div>
              </article>
            `).join("") || `<div class="empty-state"><p>Inga försäkringar registrerade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Försäkring</span>
          <h3>${currentEdit("insurance")?.id ? "Redigera försäkring" : "Lägg till försäkring"}</h3>
          ${renderForm("insuranceForm", insuranceFields(), currentEdit("insurance") || {}, {
            submitLabel: currentEdit("insurance")?.id ? "Spara försäkring" : "Lägg till försäkring",
            canDelete: Boolean(currentEdit("insurance")?.id),
            deleteLabel: "Ta bort försäkring",
          })}
        </article>
      </section>
    </section>
  `;
}

function renderVehiclesPageV2() {
  const items = vehiclesForHousehold();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Fordon", "Fordon i hushållet och deras kostnader", `<button class="primary" type="button" data-action="new-record" data-module="vehicle">Lägg till fordon</button>`)}
      <section class="split-layout">
        <article class="panel">
          <div class="record-grid">
            ${items.map((item) => `
              <article class="record-card">
                <div class="record-title-row">
                  <div>
                    <h4 class="record-title">${escapeHtml([item.make, item.model, item.year].filter(Boolean).join(" ") || "Fordon")}</h4>
                    <p class="muted">${item.owner_person_id ? escapeHtml(personName(item.owner_person_id)) : "Ingen specifik ägare"}</p>
                  </div>
                  <button class="ghost compact" type="button" data-edit="vehicle" data-id="${item.id}">Redigera</button>
                </div>
                <div class="detail-grid four">
                  ${detailCell("Lån", item.loan_id ? loanName(item.loan_id) : "Inget")}
                  ${detailCell("Försäkring", item.insurance_policy_id ? policyName(item.insurance_policy_id) : "Ingen")}
                  ${detailCell("Bränsle", money(item.fuel_monthly_estimate))}
                  ${detailCell("Total / månad", money(vehicleMonthlyCost(item)))}
                </div>
              </article>
            `).join("") || `<div class="empty-state"><p>Inga fordon registrerade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Fordon</span>
          <h3>${currentEdit("vehicle")?.id ? "Redigera fordon" : "Lägg till fordon"}</h3>
          ${renderForm("vehicleForm", vehicleFields(), currentEdit("vehicle") || {}, {
            submitLabel: currentEdit("vehicle")?.id ? "Spara fordon" : "Lägg till fordon",
            canDelete: Boolean(currentEdit("vehicle")?.id),
            deleteLabel: "Ta bort fordon",
          })}
        </article>
      </section>
    </section>
  `;
}

function renderAssetsPageV2() {
  const items = assetsForHousehold();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Tillgångar", "Sparande, investeringar och andra tillgångar", `<button class="primary" type="button" data-action="new-record" data-module="asset">Lägg till tillgång</button>`)}
      <section class="split-layout">
        <article class="table-card">
          <table class="data-table">
            <thead>
              <tr>
                <th>Namn</th>
                <th>Typ</th>
                <th>Institution</th>
                <th class="align-right">Marknadsvärde</th>
                <th>Pantsatt</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              ${items.map((item) => `
                <tr>
                  <td>${escapeHtml(item.label || item.institution || optionLabel(OPTIONS.assetType, item.type))}</td>
                  <td>${escapeHtml(optionLabel(OPTIONS.assetType, item.type))}</td>
                  <td>${escapeHtml(item.institution || "Ej angiven")}</td>
                  <td class="align-right">${money(item.market_value)}</td>
                  <td>${item.pledged ? "Ja" : "Nej"}</td>
                  <td class="align-right"><button class="ghost compact" type="button" data-edit="asset" data-id="${item.id}">Redigera</button></td>
                </tr>
              `).join("") || `<tr><td colspan="6"><div class="empty-state"><p>Inga tillgångar registrerade ännu.</p></div></td></tr>`}
            </tbody>
          </table>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Tillgång</span>
          <h3>${currentEdit("asset")?.id ? "Redigera tillgång" : "Lägg till tillgång"}</h3>
          ${renderForm("assetForm", assetFields(), currentEdit("asset") || {}, {
            submitLabel: currentEdit("asset")?.id ? "Spara tillgång" : "Lägg till tillgång",
            canDelete: Boolean(currentEdit("asset")?.id),
            deleteLabel: "Ta bort tillgång",
          })}
        </article>
      </section>
    </section>
  `;
}

function renderHousingPageV2() {
  const items = housingForHousehold();
  const evaluation = state.housingEvaluation;
  return `
    <section class="page-wrap">
      ${renderPageHeader("Boendekalkyl", "Beräkna och jämför boendekostnader", `<button class="primary" type="button" data-action="new-record" data-module="housing">Ny boendekalkyl</button>`)}
      ${evaluation ? `
        <section class="stats-grid">
          ${renderStatCard("Boendekostnad / månad", money(evaluation.monthly_total_cost))}
          ${renderStatCard("Årskostnad", money(evaluation.yearly_total_cost))}
          ${renderStatCard("Ränta / månad", money(evaluation.monthly_interest))}
          ${renderStatCard("Kvar efter boendet", money((selectedSummary()?.monthly_net_cashflow || 0) - evaluation.monthly_total_cost))}
        </section>
      ` : ""}
      <section class="split-layout">
        <article class="panel">
          <div class="record-grid">
            ${items.map((item) => `
              <article class="record-card">
                <div class="record-title-row">
                  <div>
                    <h4 class="record-title">${escapeHtml(item.label)}</h4>
                    <p class="muted">${money(item.purchase_price)} · ${number(item.rate_assumption, 2)} % ränta</p>
                  </div>
                  <div class="actions-row">
                    <button class="ghost compact" type="button" data-edit="housing" data-id="${item.id}">Redigera</button>
                    <button class="primary compact" type="button" data-evaluate-housing="${item.id}">Utvärdera</button>
                  </div>
                </div>
              </article>
            `).join("") || `<div class="empty-state"><p>Inga boendescenarier registrerade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Scenario</span>
          <h3>${currentEdit("housing")?.id ? "Redigera boendescenario" : "Skapa boendescenario"}</h3>
          ${renderForm("housingForm", housingFields(), currentEdit("housing") || {}, {
            submitLabel: currentEdit("housing")?.id ? "Spara scenario" : "Skapa scenario",
            canDelete: Boolean(currentEdit("housing")?.id),
            deleteLabel: "Ta bort scenario",
          })}
        </article>
      </section>
    </section>
  `;
}

function ingestKindOptions() {
  return [
    ["text", "Klistrad text (faktura, avtal, kvitto)"],
    ["pdf_text", "Klistrad text från PDF"],
    ["bank_paste", "Bankrader / kontoutdrag (LF-format)"],
    ["image", "Bild eller screenshot (OCR)"],
  ];
}

function classificationLabel(docType) {
  return {
    subscription_contract: "Abonnemang / avtal",
    invoice: "Faktura",
    recurring_cost_candidate: "Återkommande kostnad",
    transfer_or_saving_candidate: "Överföring / sparande",
    bank_row_batch: "Bankrader / kontoutdrag",
    financial_note: "Finansiell anteckning",
    unclear: "Oklart underlag",
  }[docType] || docType || "Oklart";
}

function classificationBadgeTone(docType) {
  return {
    subscription_contract: "info",
    invoice: "success",
    recurring_cost_candidate: "info",
    transfer_or_saving_candidate: "info",
    bank_row_batch: "info",
    financial_note: "muted",
    unclear: "warning",
  }[docType] || "muted";
}

function confidenceBadge(confidence) {
  if (confidence == null) return `<span class="badge muted">Confidence ej angiven</span>`;
  const pct = Math.round(confidence * 100);
  if (pct >= 80) return `<span class="badge success">Confidence ${pct} %</span>`;
  if (pct >= 50) return `<span class="badge info">Confidence ${pct} %</span>`;
  return `<span class="badge warning">Confidence ${pct} %</span>`;
}

function relevanceBadge(relevance) {
  return {
    high: `<span class="badge success">Hög relevans</span>`,
    medium: `<span class="badge info">Medel relevans</span>`,
    low: `<span class="badge muted">Låg relevans</span>`,
  }[relevance] || `<span class="badge muted">${escapeHtml(relevance || "Okänd")}</span>`;
}

function normalizeIngestResult(result) {
  const documentSummary = result?.document_summary;
  const safeKeys = Array.isArray(documentSummary?.confirmed_fields) ? documentSummary.confirmed_fields : [];
  const safeFields = {};
  const uncertainFields = {};
  const summaryFactSource = {
    provider_name: documentSummary?.provider_name,
    title: documentSummary?.label,
    amount: documentSummary?.amount,
    currency: documentSummary?.currency,
    due_date: documentSummary?.due_date,
    cadence: documentSummary?.cadence,
    category_hint: documentSummary?.category_hint,
    household_relevance: documentSummary?.household_relevance,
  };

  Object.entries(summaryFactSource).forEach(([key, value]) => {
    if (value === null || value === undefined || String(value).trim() === "") return;
    if (safeKeys.includes(key)) {
      safeFields[key] = value;
    } else {
      uncertainFields[key] = value;
    }
  });

  if (Array.isArray(documentSummary?.notes) && documentSummary.notes.length) {
    uncertainFields.notes = documentSummary.notes;
  }

  const suggestions = Array.isArray(result?.suggestions) ? result.suggestions : [];
  const inferredRecommendation = documentSummary?.suggested_target_entity_type
    || {
      subscription_contract: "subscription_contract",
      recurring_cost_candidate: "recurring_cost",
      invoice: "document",
      financial_note: "document",
      unclear: "unclear",
    }[documentSummary?.document_type || "unclear"]
    || "unclear";
  return {
    inputKind: result?.source_channel || result?.input_kind || "text",
    inputDetails: result?.input_details || {},
    documentId: result?.document_id || result?.input_details?.document_id || null,
    documentType: documentSummary?.document_type || result?.detected_kind || "unclear",
    recommendation: inferredRecommendation,
    summary: result?.summary || result?.analysis_summary || result?.overview || "Ingen sammanfattning finns ännu.",
    confidence: documentSummary?.confidence ?? result?.confidence ?? null,
    rawSource: result?.input_details?.source_name || result?.source_name || null,
    providerName: documentSummary?.provider_name || null,
    title: documentSummary?.label || null,
    amount: documentSummary?.amount ?? null,
    currency: documentSummary?.currency || null,
    dueDate: documentSummary?.due_date || null,
    cadence: documentSummary?.cadence || null,
    householdRelevance: documentSummary?.household_relevance || null,
    notes: documentSummary?.notes || null,
    safeFields,
    uncertainFields,
    uncertaintyReasons: documentSummary?.uncertainty_reasons || [],
    guidance: result?.guidance || result?.review_notes || [],
    reviewGroups: Array.isArray(result?.review_groups) ? result.review_groups : [],
    suggestions,
    model: result?.model || null,
    provider: result?.provider || null,
    usage: result?.usage || null,
    imageReadiness: result?.image_readiness || null,
  };
}

function formatIngestAmount(value, currency) {
  if (value === null || value === undefined || value === "") return "Ej angivet";
  const amount = Number(value);
  if (Number.isNaN(amount)) return `${value}${currency ? ` ${currency}` : ""}`;
  const formatted = new Intl.NumberFormat("sv-SE", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
  return currency ? `${formatted} ${currency}` : formatted;
}

function renderIngestFactGrid(review) {
  const facts = [
    ["Leverantör", review.providerName],
    ["Titel", review.title],
    ["Belopp", formatIngestAmount(review.amount, review.currency)],
    ["Förfallodatum", review.dueDate ? dateLabel(review.dueDate) : null],
    ["Frekvens", review.cadence],
    ["Hushållsrelevans", review.householdRelevance],
    ["Anteckning", review.notes],
  ].filter(([, value]) => value !== null && value !== undefined && String(value).trim() !== "");

  if (!facts.length) {
    return `<div class="empty-state compact"><p>Inga säkra kärnfakta gick att extrahera. Det är bättre än att gissa.</p></div>`;
  }

  return `
    <div class="detail-grid three fact-grid">
      ${facts.map(([label, value]) => detailCell(label, value)).join("")}
    </div>
  `;
}

function renderIngestPipelineStrip() {
  return `
    <section class="record-grid four workflow-pipeline">
      <article class="workflow-step-card">
        <span class="badge info">1. Rå input</span>
        <h4>Klistra in text eller ladda upp underlag</h4>
        <p class="muted">Text, PDF-text eller uppladdade dokument ska kunna bli ingång till samma reviewflöde.</p>
      </article>
      <article class="workflow-step-card">
        <span class="badge info">2. Extraktion</span>
        <h4>Text normaliseras innan AI</h4>
        <p class="muted">När text går att extrahera ska den synas som workflow-data, inte som kanonisk sanning.</p>
      </article>
      <article class="workflow-step-card">
        <span class="badge info">3. AI-review</span>
        <h4>Klassificera och markera osäkerhet</h4>
        <p class="muted">Modellen ska visa vad som är säkert, vad som är tveksamt och vart underlaget pekar.</p>
      </article>
      <article class="workflow-step-card">
        <span class="badge info">4. Promote</span>
        <h4>Skapa reviewutkast explicit</h4>
        <p class="muted">Promote är ett separat steg. Det får inte skriva tyst till hushållets kanoniska data.</p>
      </article>
    </section>
  `;
}

function renderIngestImageReadiness() {
  return `
    <article class="workflow-callout future-readiness">
      <div class="record-title-row">
        <div>
          <h4 class="record-title">Bild- och screenshot-avläsning (OCR)</h4>
          <p class="muted">Tesseract OCR (svenska + engelska) stöds för bilder, screenshots och skannade PDF:er.</p>
        </div>
        <span class="badge success">Implementerad</span>
      </div>
      <p class="muted">Ladda upp en bild eller skannad PDF via uppladdningsformuläret. Text extraheras via OCR innan AI-analys. Observera att OCR-text kan innehålla felläsningar.</p>
    </article>
  `;
}

function labelizeIngestKey(key) {
  return String(key || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatIngestSummaryValue(value) {
  if (Array.isArray(value)) {
    return value.map((item) => formatIngestSummaryValue(item)).join(" · ");
  }
  if (value && typeof value === "object") {
    return JSON.stringify(value);
  }
  return value == null ? "" : String(value);
}

function renderIngestSummaryBlock(value, fallbackText) {
  if (!value || (typeof value === "object" && !Array.isArray(value) && !Object.keys(value).length)) {
    return `<p class="muted">${escapeHtml(fallbackText)}</p>`;
  }

  if (Array.isArray(value)) {
    return `<ul class="summary-list">${value.map((item) => `<li>${escapeHtml(formatIngestSummaryValue(item))}</li>`).join("")}</ul>`;
  }

  if (typeof value === "object") {
    const entries = Object.entries(value).filter(([, item]) => item !== null && item !== undefined && String(formatIngestSummaryValue(item)).trim() !== "");
    if (!entries.length) {
      return `<p class="muted">${escapeHtml(fallbackText)}</p>`;
    }
    return `
      <div class="detail-grid three fact-grid">
        ${entries.map(([key, item]) => detailCell(labelizeIngestKey(key), formatIngestSummaryValue(item))).join("")}
      </div>
    `;
  }

  return `<p class="muted">${escapeHtml(formatIngestSummaryValue(value))}</p>`;
}

function ingestSourceChannelLabel(value) {
  return {
    text: "Klistrad text",
    pdf_text: "Klistrad PDF-text",
    uploaded_document: "Uppladdat dokument",
    uploaded_pdf: "Uppladdad PDF",
    image: "Bild / screenshot (OCR)",
    bank_paste: "Bankrader / kontoutdrag",
  }[value] || "Okänd källa";
}

function documentExtractionMeta(status) {
  return {
    parsed: { tone: "success", label: "Text extraherad" },
    ocr_parsed: { tone: "success", label: "OCR-text extraherad" },
    ocr_pending: { tone: "warning", label: "OCR krävs" },
    parse_failed: { tone: "warning", label: "Text kunde inte läsas" },
    unsupported: { tone: "warning", label: "Filtypen stöds inte" },
    pending: { tone: "warning", label: "Ingen text ännu" },
    reviewed: { tone: "success", label: "Granskad" },
  }[status || "pending"] || { tone: "muted", label: status || "pending" };
}

function groupIngestSuggestions(suggestions) {
  const groups = new Map();
  suggestions.forEach((item) => {
    const bucket = item.review_bucket || item.recommended_direction || item.suggested_path || item.target_entity_type || item.document_type || "unclear";
    if (!groups.has(bucket)) {
      groups.set(bucket, []);
    }
    groups.get(bucket).push(item);
  });
  return Array.from(groups.entries()).map(([bucket, items]) => ({ bucket, items }));
}

function renderIngestSuggestionCard(item) {
  const confidence = item.confidence == null ? "Ej angiven" : number(item.confidence, 2);
  const documentType = item.document_type || item.detected_kind || item.classification || "unclear";
  const direction = item.recommended_direction || item.review_bucket || item.suggested_path || item.target_entity_type || "unclear";
  const uncertainty = item.uncertainty_reasons || item.uncertainty_notes || [];
  const fields = item.document_summary || item.extracted_fields || item.fields || item.core_facts || {};
  return `
    <article class="record-card">
      <div class="record-title-row">
        <div>
          <h4 class="record-title">${escapeHtml(item.title || item.provider_name || item.target_entity_type || "Förslag")}</h4>
          <p class="muted">${escapeHtml(documentType)} · ${escapeHtml(direction)} · confidence ${escapeHtml(confidence)}</p>
        </div>
        <span class="badge ${item.validation_status === "valid" ? "success" : "warning"}">${escapeHtml(item.validation_status)}</span>
      </div>
      <div class="detail-grid three fact-grid">
        ${fields.provider_name || item.provider_name ? detailCell("Leverantör", fields.provider_name || item.provider_name) : ""}
        ${fields.title || item.title ? detailCell("Titel", fields.title || item.title) : ""}
        ${(fields.amount ?? item.amount) !== undefined && (fields.amount ?? item.amount) !== null ? detailCell("Belopp", formatIngestAmount(fields.amount ?? item.amount, fields.currency || item.currency)) : ""}
        ${fields.due_date || item.due_date ? detailCell("Förfallodatum", dateLabel(fields.due_date || item.due_date)) : ""}
        ${fields.cadence || item.cadence ? detailCell("Frekvens", fields.cadence || item.cadence) : ""}
        ${fields.household_relevance || item.household_relevance ? detailCell("Hushållsrelevans", fields.household_relevance || item.household_relevance) : ""}
      </div>
      <p class="muted">${escapeHtml(item.rationale || item.summary || "Ingen rationale angiven.")}</p>
      ${uncertainty?.length ? `<p class="muted">Osäkerhet: ${escapeHtml(uncertainty.join(" · "))}</p>` : ""}
      ${item.validation_errors?.length ? `<p class="muted">Validering: ${escapeHtml(item.validation_errors.join(" · "))}</p>` : ""}
      <details class="raw-json">
        <summary>Visa strukturerad payload</summary>
        <pre>${escapeHtml(JSON.stringify(item.proposed_json, null, 2))}</pre>
      </details>
    </article>
  `;
}

function renderIngestResult() {
  const result = state.ui.ingestResult;
  if (!result) {
    return `<div class="empty-state"><p>Ingen AI-analys körd ännu. Klistra in underlag eller ladda in extraherad text från ett dokument och kör analys när du vill skapa reviewutkast utan tysta databasskrivningar.</p></div>`;
  }

  const review = normalizeIngestResult(result);
  const validSuggestions = review.suggestions.filter((item) => item.validation_status === "valid");
  const suggestionGroups = review.reviewGroups.length
    ? review.reviewGroups.map((group) => ({ bucket: group.group_type, title: group.title, summary: group.summary, items: group.suggestions || [] }))
    : groupIngestSuggestions(review.suggestions);
  const rawPreview = (state.ui.ingestInput || "").trim();
  const rawPreviewText = rawPreview.length > 1200 ? `${rawPreview.slice(0, 1200)}...` : rawPreview;
  return `
    <div class="workflow-stack">
      <article class="record-card ingest-classification-card">
        <div class="record-title-row">
          <div>
            <span class="badge ${classificationBadgeTone(review.documentType)}">${escapeHtml(classificationLabel(review.documentType))}</span>
            <h4 class="record-title">${escapeHtml(review.summary)}</h4>
            <p class="muted">${escapeHtml(ingestSourceChannelLabel(review.inputKind))}${review.provider ? ` · ${escapeHtml(review.provider)}` : ""}${review.model ? ` · ${escapeHtml(review.model)}` : ""}</p>
          </div>
          <span class="badge muted">${review.usage?.total_tokens ? `${review.usage.total_tokens} tokens` : "utan usage"}</span>
        </div>
        <div class="badge-row">
          ${confidenceBadge(review.confidence)}
          ${relevanceBadge(review.householdRelevance)}
          <span class="badge muted">Riktning: ${escapeHtml(review.recommendation)}</span>
        </div>
        ${review.guidance?.length ? `<div class="ingest-guidance"><ul class="summary-list">${review.guidance.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>` : ""}
        <div class="workflow-callout">
          <strong>AI-tolkningen är inte kanonisk data.</strong>
          <p class="muted">Promote skapar bara dokument- och reviewutkast. Inget skrivs tyst till hushållets slutgiltiga poster.</p>
        </div>
      </article>
      <article class="record-card">
        <div class="record-title-row">
          <div>
            <h4 class="record-title">Extraherade kärnfakta</h4>
            <p class="muted">Säkra fält (bekräftade i texten) visas med grön markering, osäkra med gul.</p>
          </div>
        </div>
        ${renderIngestFactGrid(review)}
        <div class="summary-panels">
          <article class="workflow-callout subtle safe-fields">
            <strong>✓ Bekräftade fält</strong>
            ${renderIngestSummaryBlock(review.safeFields, "Inga fält kunde bekräftas direkt ur texten.")}
          </article>
          <article class="workflow-callout subtle uncertain-fields">
            <strong>? Osäkra fält</strong>
            ${renderIngestSummaryBlock(review.uncertainFields, "Inga osäkra fält.")}
          </article>
        </div>
      </article>
      ${review.uncertaintyReasons?.length ? `
      <article class="record-card">
        <div class="record-title-row">
          <div>
            <h4 class="record-title">⚠ Osäkerhet och varningar</h4>
            <p class="muted">Modellen flaggar dessa punkter som osäkra. Granska innan du skapar utkast.</p>
          </div>
        </div>
        <ul class="summary-list uncertainty-list">${review.uncertaintyReasons.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </article>` : ""}
      <article class="record-card">
        <div class="record-title-row">
          <div>
            <h4 class="record-title">Reviewförslag</h4>
            <p class="muted">Validerade förslag grupperade efter typ.</p>
          </div>
          <span class="badge">${validSuggestions.length} validerade</span>
        </div>
        ${suggestionGroups.length ? suggestionGroups.map((group) => `
          <section class="workflow-group">
            <div class="record-title-row">
              <div>
                <h5 class="group-title">${escapeHtml(group.title || group.bucket)}</h5>
                <p class="muted">${group.items.length} förslag</p>
              </div>
              <span class="badge muted">${group.items.filter((item) => item.validation_status === "valid").length} validerade</span>
            </div>
            <div class="record-grid">
              ${group.items.map((item) => renderIngestSuggestionCard(item)).join("")}
            </div>
          </section>
        `).join("") : `<div class="empty-state compact"><p>Inga strukturerade förslag hittades.</p></div>`}
        <div class="actions-row" style="margin-top:var(--space-m)">
          <button class="primary" type="button" data-action="promote-ingest" ${validSuggestions.length ? "" : "disabled"}>
            ${state.ui.ingestPromoting ? "Skapar utkast..." : `Skapa ${validSuggestions.length} reviewutkast`}
          </button>
          <span class="chat-disclaimer">Detta skapar bara reviewutkast i workflow-lagret. Inget skrivs direkt till kanonisk ekonomi.</span>
        </div>
      </article>
      <details class="raw-json">
        <summary>Visa rå input (${review.inputDetails?.text_length || 0} tecken)</summary>
        <article class="record-card">
          <div class="detail-grid three fact-grid">
            ${detailCell("Källa", review.rawSource || "Ej angiven")}
            ${detailCell("Dokument", review.documentId ? `#${review.documentId}` : "Ingen")}
            ${detailCell("Extraktion", review.inputDetails?.extraction_mode || "manuell")}
          </div>
          ${rawPreviewText ? `<pre class="raw-preview">${escapeHtml(rawPreviewText)}</pre>` : `<div class="empty-state compact"><p>Ingen råtext.</p></div>`}
        </article>
      </details>
    </div>
  `;
}

function renderDocumentsPageV2() {
  const items = documentsForHousehold();
  const drafts = draftsForHousehold();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Dokument", "Ladda upp, extrahera och granska underlag utan att blanda ihop råinput och kanonisk data")}
      ${renderIngestPipelineStrip()}
      <section class="split-layout">
        <article class="panel form-card">
          <span class="section-eyebrow">Rå input</span>
          <h3>Klistra in text eller peka ut ett dokument</h3>
          <p class="muted">Välj underlagstyp, klistra in text från faktura eller avtal, eller ladda upp en PDF/dokumentfil för extraktion i workflow-lagret.</p>
          <form id="ingestAnalyzeForm" class="form-grid">
            ${renderField({ key: "ingest_input_kind", label: "Underlagstyp", type: "select", options: ingestKindOptions(), required: true }, state.ui.ingestKind || "text")}
            ${renderField({ key: "ingest_source_name", label: "Källa eller avsändare", type: "text" }, state.ui.ingestSourceName || "")}
            ${renderField({ key: "ingest_input_text", label: "Råtext", type: "textarea", full: true, required: true, placeholder: "Klistra in text från faktura, abonnemang eller PDF här." }, state.ui.ingestInput || "")}
            <div class="field full">
              <div class="form-actions">
                <button class="primary" type="submit" ${selectedHousehold() ? "" : "disabled"}>${state.ui.ingestPending ? "Analyserar..." : "Analysera underlag"}</button>
                <button class="ghost" type="button" data-action="clear-ingest">Rensa</button>
              </div>
            </div>
          </form>
          <div class="workflow-callout">
            <strong>Uppladdade dokument kan också användas som input.</strong>
            <p class="muted">Om dokumentet redan finns i listan nedan och har extraherad text kan du skicka texten direkt tillbaka till Data-In.</p>
          </div>
          <div class="upload-box">
            ${renderDocumentUploadForm()}
          </div>
          ${renderIngestImageReadiness()}
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">AI-review</span>
          <h3>Det som är säkert, tveksamt och nästa riktning</h3>
          <p class="muted">Här ska du se vad modellen tror, varför den tror det, och vad som fortfarande är osäkert innan du promtar vidare.</p>
        ${renderIngestResult()}
        </article>
      </section>
      <section class="split-layout">
        <article class="panel">
          <span class="section-eyebrow">Uppladdade dokument</span>
          <h3>${items.length ? `${items.length} dokument` : "Inga dokument ännu"}</h3>
          <p class="muted">När extraherad text finns kan du flytta den direkt in i Data-In utan att blanda ihop filen med analysen.</p>
          <div class="record-grid">
            ${items.map((item) => renderDocumentRowV2(item)).join("") || `<div class="empty-state"><p>Inga dokument uppladdade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel">
          <span class="section-eyebrow">Workflow-utkast</span>
          <h3>${drafts.length ? `${drafts.length} utkast att granska` : "Inga utkast att granska"}</h3>
          <p class="muted">Det här är inte kanoniska hushållsposter. Det är reviewobjekt som fortfarande kräver explicit apply senare.</p>
          <div class="record-grid">
            ${drafts.map((draft) => `
              <article class="record-card">
                <div class="record-title-row">
                  <div>
                    <h4 class="record-title">${escapeHtml(draft.target_entity_type)}</h4>
                    <p class="muted">Dokument ${draft.document_id} · status ${escapeHtml(draft.status)}</p>
                  </div>
                  <div class="actions-row">
                    <button class="primary compact" type="button" data-apply-draft="${draft.id}">Applicera</button>
                    <button class="danger compact" type="button" data-delete-draft="${draft.id}">Avvisa</button>
                  </div>
                </div>
                <pre>${escapeHtml(JSON.stringify(draft.proposed_json, null, 2))}</pre>
              </article>
            `).join("") || `<div class="empty-state"><p>Det finns inga väntande reviewutkast.</p></div>`}
          </div>
        </article>
      </section>
    </section>
  `;
}

function renderDocumentRowV2(item) {
  const snippet = item.extracted_text ? item.extracted_text.trim().slice(0, 180) : "";
  const extraction = documentExtractionMeta(item.extraction_status);
  return `
    <article class="record-card">
      <div class="record-title-row">
        <div>
          <h4 class="record-title">${escapeHtml(item.file_name)}</h4>
          <p class="muted">${escapeHtml(optionLabel(OPTIONS.documentType, item.document_type))}${item.issuer ? ` · ${escapeHtml(item.issuer)}` : ""}</p>
        </div>
        <div class="actions-row">
          <span class="badge ${escapeHtml(extraction.tone)}">${escapeHtml(extraction.label)}</span>
          <a class="ghost compact" href="/documents/${item.id}/download">Ladda ned</a>
          <button class="primary compact" type="button" data-action="analyze-document" data-document-id="${item.id}" ${item.extracted_text ? "" : "disabled"}>Analysera text</button>
        </div>
      </div>
      ${snippet ? `<p class="muted">${escapeHtml(snippet)}${item.extracted_text && item.extracted_text.trim().length > 180 ? "..." : ""}</p>` : `<p class="muted">Ingen extraherad text ännu. Dokument som kräver OCR markeras tydligt men OCR är ännu inte implementerad.</p>`}
    </article>
  `;
}

function renderImprovementsPageV2() {
  const items = opportunitiesForHousehold().slice().sort((a, b) => Number(b.estimated_monthly_saving || 0) - Number(a.estimated_monthly_saving || 0));
  return `
    <section class="page-wrap">
      ${renderPageHeader("Förbättringsförslag", "Konkreta åtgärder för att förbättra er ekonomi", `<button class="primary" type="button" data-action="scan-opportunities">Kör ny skanning</button>`)}
      <section class="record-grid">
        ${items.map((item) => renderOpportunityCardV2(item)).join("") || `<div class="empty-state"><p>Det finns ännu inga förbättringsförslag.</p></div>`}
      </section>
    </section>
  `;
}

function renderOpportunityCardV2(item) {
  return `
    <article class="record-card">
      <div class="record-title-row">
        <div>
          <h4 class="record-title">${escapeHtml(item.title)}</h4>
          <p class="muted">${escapeHtml(item.rationale || opportunityAction(item.kind))}</p>
        </div>
        <div class="record-value">${money(item.estimated_monthly_saving)}</div>
      </div>
      <div class="badge-row">
        <span class="badge success">Besparing ${money(item.estimated_monthly_saving)} / mån</span>
        <span class="badge ${badgeTone(item.risk_level)}">Risk: ${riskLabel(item.risk_level)}</span>
        <span class="badge muted">${effortLabel(item.effort_level)}</span>
      </div>
    </article>
  `;
}

function renderScenariosPageV2() {
  const items = scenariosForHousehold();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Scenarier", "Utforska vad som händer om ekonomin förändras", `<button class="primary" type="button" data-action="new-record" data-module="scenario">Skapa scenario</button>`)}
      <section class="split-layout">
        <article class="panel">
          <div class="record-grid">
            ${items.map((item) => {
              const result = latestScenarioResult(item.id);
              return `
                <article class="record-card">
                  <div class="record-title-row">
                    <div>
                      <h4 class="record-title">${escapeHtml(item.label)}</h4>
                      <p class="muted">${escapeHtml(JSON.stringify(item.change_set_json))}</p>
                    </div>
                    <div class="actions-row">
                      <button class="ghost compact" type="button" data-edit="scenario" data-id="${item.id}">Redigera</button>
                      <button class="primary compact" type="button" data-run-scenario="${item.id}">Kör</button>
                    </div>
                  </div>
                  ${result ? `<div class="detail-grid">${detailCell("Månadsdelta", money(result.monthly_delta))}${detailCell("Årsdelta", money(result.yearly_delta))}${detailCell("Likviditet", money(result.liquidity_delta))}</div>` : `<p class="muted">Scenariot är inte kört ännu.</p>`}
                </article>
              `;
            }).join("") || `<div class="empty-state"><p>Inga scenarier registrerade ännu.</p></div>`}
          </div>
        </article>
        <article class="panel form-card">
          <span class="section-eyebrow">Scenario</span>
          <h3>${currentEdit("scenario")?.id ? "Redigera scenario" : "Skapa scenario"}</h3>
          ${renderScenarioForm()}
        </article>
      </section>
    </section>
  `;
}

function renderScenarioForm() {
  const item = currentEdit("scenario") || {};
  const raw = item.change_set_json ? JSON.stringify(item.change_set_json, null, 2) : JSON.stringify({ adjustments: [] }, null, 2);
  return `
    <form id="scenarioForm" class="form-grid">
      ${renderField({ key: "label", label: "Namn", type: "text", required: true }, item.label)}
      ${renderField({ key: "change_set_json", label: "Ändringar (JSON)", type: "textarea", full: true }, raw)}
      <div class="field full">
        <div class="form-actions">
          <button class="primary" type="submit">${item.id ? "Spara scenario" : "Skapa scenario"}</button>
          <button class="ghost" type="button" data-reset-form="scenarioForm">Rensa</button>
          ${item.id ? `<button class="danger" type="button" data-delete-form="scenarioForm">Ta bort scenario</button>` : ""}
        </div>
      </div>
    </form>
  `;
}

function renderReportsPageV2() {
  const items = reportsForHousehold().slice().sort((a, b) => new Date(b.generated_at).getTime() - new Date(a.generated_at).getTime());
  const openReport = items.find((item) => item.id === state.ui.openReportId) || items[0] || null;
  return `
    <section class="page-wrap">
      ${renderPageHeader("Sparade rapporter", "Genererade rapporter och sammanfattningar")}
      <section class="split-layout">
        <article class="panel form-card">
          <span class="section-eyebrow">Generera rapport</span>
          <h3>Skapa ny rapportsnapshot</h3>
          ${renderReportGenerateForm()}
        </article>
        <article class="panel">
          <span class="section-eyebrow">Rapporter</span>
          <h3>${items.length ? `${items.length} sparade rapporter` : "Inga rapporter ännu"}</h3>
          <div class="record-grid">
            ${items.map((item) => renderReportRowV2(item)).join("") || `<div class="empty-state"><p>Inga rapporter sparade ännu.</p></div>`}
          </div>
        </article>
      </section>
      ${openReport ? `
        <article class="panel">
          <span class="section-eyebrow">Rapportdetalj</span>
          <h3 class="report-detail-title">${escapeHtml(openReport.type)} · ${dateLabel(openReport.as_of_date)}</h3>
          <pre>${escapeHtml(JSON.stringify(openReport.result_json, null, 2))}</pre>
        </article>
      ` : ""}
    </section>
  `;
}

function renderReportRowV2(item) {
  return `
    <article class="record-card">
      <div class="record-title-row">
        <div>
          <h4 class="record-title">${escapeHtml(item.type)}</h4>
          <p class="muted">${dateLabel(item.as_of_date)} · genererad ${dateLabel(item.generated_at)}</p>
        </div>
        <div class="actions-row">
          <button class="ghost compact" type="button" data-open-report="${item.id}">Öppna</button>
          <button class="danger compact" type="button" data-delete-report="${item.id}">Ta bort</button>
        </div>
      </div>
      <p class="report-summary">${escapeHtml(JSON.stringify(item.result_json).slice(0, 180))}...</p>
    </article>
  `;
}

function renderReportGenerateForm() {
  return `
    <form id="reportGenerateForm" class="form-grid">
      ${renderField({ key: "type", label: "Typ", type: "select", options: [["monthly_overview", "Månadsrapport"], ["optimization_report", "Förbättringsrapport"], ["bank_calc", "Bankkalkyl"]], required: true }, "monthly_overview")}
      ${renderField({ key: "as_of_date", label: "Per datum", type: "date", required: true }, new Date().toISOString().slice(0, 10))}
      ${renderField({ key: "assumption_json", label: "Antaganden (JSON, valfritt)", type: "textarea", full: true }, "{}")}
      <div class="field full">
        <div class="form-actions">
          <button class="primary" type="submit">Generera rapport</button>
        </div>
      </div>
    </form>
  `;
}

function renderAssistantPageV2() {
  const messages = state.ui.assistantMessages;
  const prompts = [
    "Sammanfatta vår ekonomi just nu på ett enkelt sätt.",
    "Vad borde vi fokusera på denna månad?",
    "Vilka abonnemang bör vi granska först?",
    "Förklara vår boendekalkyl enkelt.",
  ];
  return `
    <section class="page-wrap">
      ${renderPageHeader("Ekonomiassistent", "Read-only AI över hushållets riktiga data. Svar kan misslyckas öppet om provider saknas eller svar inte går att validera.")}
      <article class="panel chat-shell">
        <div class="prompt-grid">
          ${prompts.map((prompt) => `<button class="prompt-chip" type="button" data-prompt="${escapeHtml(prompt)}">${escapeHtml(prompt)}</button>`).join("")}
        </div>
        <div class="chat-log">
          ${messages.length ? messages.map(renderAssistantMessage).join("") : `<div class="chat-empty"><div><h3>Ekonomiassistent</h3><p class="muted">Svar bygger på hushållets read models. AI:n är read-only och får inte skriva till kärndata.</p></div></div>`}
        </div>
        <form id="assistantForm" class="chat-composer">
          <textarea name="prompt" placeholder="Ställ en fråga om hushållets ekonomi...">${escapeHtml(state.ui.assistantInput || "")}</textarea>
          <div class="actions-row">
            <button class="primary" type="submit" ${selectedHousehold() ? "" : "disabled"}>${state.ui.assistantPending ? "Analyserar..." : "Skicka fråga"}</button>
            <span class="chat-disclaimer">Inga låtsassvar används här. Vid saknad provider eller valideringsfel visas öppet fel.</span>
          </div>
        </form>
      </article>
    </section>
  `;
}

function renderAssistantMessage(message) {
  return `
    <article class="chat-message ${message.role}">
      <div class="chat-role">${message.role === "assistant" ? "Ekonomiassistent" : "Du"}</div>
      <div class="chat-bubble">${renderAssistantMarkdown(message.content)}</div>
      ${message.role === "assistant" && message.model ? `<div class="muted">${escapeHtml(message.provider || "openai")} · ${escapeHtml(message.model)}${message.usage?.total_tokens ? ` · ${message.usage.total_tokens} tokens` : ""}</div>` : ""}
    </article>
  `;
}

function renderAssistantMarkdown(text) {
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/^### (.*)$/gm, "<p><strong>$1</strong></p>")
    .replace(/^- (.*)$/gm, "<p>• $1</p>")
    .replace(/\n/g, "<br>");
}

function renderRegisterPage() {
  const steps = onboardingSteps();
  return `
    <section class="page-wrap">
      ${renderPageHeader("Registrera ekonomi", "Guidad onboarding mot riktiga backendflöden")}
      <article class="wizard-card">
        <div class="wizard-progress">
          <div class="wizard-steps">
            ${["Hushåll", "Personer", "Inkomster", "Lån", "Kostnader", "Abonnemang", "Tillgångar", "Boende", "Rapport", "Klart"].map((_, index) => `<div class="wizard-step ${index < steps.length ? "active" : "done"}"></div>`).join("")}
          </div>
          <p class="muted">Den här guidade vyn använder samma riktiga CRUD-flöden som övriga appen. Lägg först grunden, sedan resten stegvis.</p>
        </div>
        <div class="step-cards">
          <button class="choice-card" type="button" data-route="/hushall"><strong>1. Skapa hushåll</strong><br><span class="muted">Skapa eller välj hushåll med riktiga data.</span></button>
          <button class="choice-card" type="button" data-route="/personer"><strong>2. Lägg till personer</strong><br><span class="muted">Koppla hushållets personer.</span></button>
          <button class="choice-card" type="button" data-route="/inkomster"><strong>3. Fyll inkomster</strong><br><span class="muted">Skapa riktiga inkomster per person.</span></button>
          <button class="choice-card" type="button" data-route="/lan"><strong>4. Lägg till lån</strong><br><span class="muted">Samla skulder och månadskostnader.</span></button>
          <button class="choice-card" type="button" data-route="/kostnader"><strong>5. Lägg till återkommande kostnader</strong><br><span class="muted">Fasta poster och avbetalningar som inte är abonnemang.</span></button>
          <button class="choice-card" type="button" data-route="/abonnemang"><strong>6. Lägg till abonnemang</strong><br><span class="muted">Avtal, bindningar och granskningsdatum.</span></button>
          <button class="choice-card" type="button" data-route="/tillgangar"><strong>7. Lägg till tillgångar</strong><br><span class="muted">Konton, sparande och investeringar.</span></button>
          <button class="choice-card" type="button" data-route="/boendekalkyl"><strong>8. Skapa boendekalkyl</strong><br><span class="muted">Kalkyl mot riktiga kostnader.</span></button>
          <button class="choice-card" type="button" data-route="/rapporter"><strong>9. Generera rapport</strong><br><span class="muted">Skapa första riktiga snapshoten.</span></button>
        </div>
      </article>
    </section>
  `;
}

function detailCell(label, value) {
  return `<div class="detail-item"><label>${escapeHtml(label)}</label><div>${escapeHtml(String(value || "Ej angivet"))}</div></div>`;
}

function scenariosForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.scenarios.filter((item) => item.household_id === householdId);
}

function scenarioResultsForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.scenarioResults.filter((item) => item.household_id === householdId);
}

function reportsForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.reports.filter((item) => item.household_id === householdId);
}

function draftsForHousehold(householdId = state.selectedHouseholdId) {
  return state.data.drafts.filter((item) => item.household_id === householdId);
}

function latestScenarioResult(scenarioId) {
  return scenarioResultsForHousehold()
    .filter((item) => item.scenario_id === scenarioId)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0] || null;
}

async function handlePageClick(event) {
  const routeTarget = event.target.closest("[data-route]");
  if (routeTarget) {
    navigateTo(pageConfigByPath(routeTarget.dataset.route).key);
    return;
  }

  const promptTarget = event.target.closest("[data-prompt]");
  if (promptTarget) {
    state.ui.assistantInput = promptTarget.dataset.prompt;
    render();
    return;
  }

  const selectHouseholdTarget = event.target.closest("[data-select-household]");
  if (selectHouseholdTarget) {
    state.selectedHouseholdId = Number(selectHouseholdTarget.dataset.selectHousehold);
    persistSelection();
    await ensureSummaryLoaded();
    render();
    return;
  }

  const editHouseholdTarget = event.target.closest("[data-edit-household]");
  if (editHouseholdTarget) {
    setEdit("household", households().find((item) => item.id === Number(editHouseholdTarget.dataset.editHousehold)) || selectedHousehold());
    render();
    return;
  }

  const openReportTarget = event.target.closest("[data-open-report]");
  if (openReportTarget) {
    state.ui.openReportId = Number(openReportTarget.dataset.openReport);
    render();
    return;
  }

  const deleteReportTarget = event.target.closest("[data-delete-report]");
  if (deleteReportTarget) {
    await request(`/report_snapshots/${Number(deleteReportTarget.dataset.deleteReport)}`, { method: "DELETE" });
    await refreshAllData();
    render();
    showToast("Rapporten togs bort.");
    return;
  }

  const applyDraftTarget = event.target.closest("[data-apply-draft]");
  if (applyDraftTarget) {
    await request(`/extraction_drafts/${Number(applyDraftTarget.dataset.applyDraft)}/apply`, { method: "POST" });
    await refreshAllData();
    render();
    showToast("Utkastet applicerades.");
    return;
  }

  const deleteDraftTarget = event.target.closest("[data-delete-draft]");
  if (deleteDraftTarget) {
    await request(`/extraction_drafts/${Number(deleteDraftTarget.dataset.deleteDraft)}`, { method: "DELETE" });
    await refreshAllData();
    render();
    showToast("Utkastet togs bort.");
    return;
  }

  const runScenarioTarget = event.target.closest("[data-run-scenario]");
  if (runScenarioTarget) {
    await request(`/scenarios/${Number(runScenarioTarget.dataset.runScenario)}/run`, { method: "POST" });
    await refreshAllData();
    render();
    showToast("Scenariot kördes.");
    return;
  }

  const newHouseholdTarget = event.target.closest("[data-action='new-household']");
  if (newHouseholdTarget) {
    setEdit("household", null);
    navigateTo("household");
    return;
  }

  const navTarget = event.target.closest("[data-nav]");
  if (navTarget) {
    navigateTo(navTarget.dataset.nav);
    return;
  }

  const editTarget = event.target.closest("[data-edit]");
  if (editTarget) {
    const moduleKey = editTarget.dataset.edit;
    const item = findItemByModuleAndId(moduleKey, Number(editTarget.dataset.id));
    setEdit(moduleKey, item);
    if (moduleKey === "housing" && item) {
      await loadHousingEvaluation(item.id);
    }
    if (moduleKey === "scenario") {
      setEdit("scenario", state.data.scenarios.find((item) => item.id === Number(editTarget.dataset.id)) || null);
    }
    render();
    return;
  }

  const evaluateTarget = event.target.closest("[data-evaluate-housing]");
  if (evaluateTarget) {
    const scenarioId = Number(evaluateTarget.dataset.evaluateHousing);
    const item = housingForHousehold().find((scenario) => scenario.id === scenarioId);
    setEdit("housing", item);
    await loadHousingEvaluation(scenarioId);
    render();
    return;
  }

  const newTarget = event.target.closest("[data-action='new-record']");
  if (newTarget) {
    setEdit(newTarget.dataset.module, null);
    render();
    return;
  }

  const scanTarget = event.target.closest("[data-action='scan-opportunities']");
  if (scanTarget) {
    await scanOpportunities();
    return;
  }

  const promoteIngestTarget = event.target.closest("[data-action='promote-ingest']");
  if (promoteIngestTarget) {
    await promoteIngestSuggestions();
    return;
  }

  const clearIngestTarget = event.target.closest("[data-action='clear-ingest']");
  if (clearIngestTarget) {
    state.ui.ingestInput = "";
    state.ui.ingestKind = "text";
    state.ui.ingestDocumentId = null;
    state.ui.ingestSourceName = "";
    state.ui.ingestResult = null;
    render();
    return;
  }

  const analyzeDocumentTarget = event.target.closest("[data-action='analyze-document']");
  if (analyzeDocumentTarget) {
    await analyzeStoredDocument(Number(analyzeDocumentTarget.dataset.documentId));
    return;
  }

  const resetTarget = event.target.closest("[data-reset-form]");
  if (resetTarget) {
    resetFormState(resetTarget.dataset.resetForm);
    render();
    return;
  }

  const deleteTarget = event.target.closest("[data-delete-form]");
  if (deleteTarget) {
    await deleteFromForm(deleteTarget.dataset.deleteForm);
  }
}

function handlePageInput(event) {
  if (event.target.name === "prompt") {
    state.ui.assistantInput = event.target.value;
  } else if (event.target.name === "ingest_input_text") {
    state.ui.ingestInput = event.target.value;
  } else if (event.target.name === "ingest_input_kind") {
    state.ui.ingestKind = event.target.value;
  } else if (event.target.name === "ingest_source_name") {
    state.ui.ingestSourceName = event.target.value;
  }
}

async function handlePageSubmit(event) {
  event.preventDefault();
  const form = event.target;
  try {
    switch (form.id) {
      case "householdForm":
        await saveHousehold(form);
        break;
      case "personForm":
        await savePerson(form);
        break;
      case "incomeForm":
        await saveIncome(form);
        break;
      case "loanForm":
        await saveLoan(form);
        break;
      case "costForm":
        await saveRecurringCost(form);
        break;
      case "insuranceForm":
        await saveInsurance(form);
        break;
      case "subscriptionForm":
        await saveSubscription(form);
        break;
      case "vehicleForm":
        await saveVehicle(form);
        break;
      case "assetForm":
        await saveAsset(form);
        break;
      case "housingForm":
        await saveHousing(form);
        break;
      case "documentUploadForm":
        await uploadDocument(form);
        break;
      case "ingestAnalyzeForm":
        await analyzeIngestForm(form);
        break;
      case "scenarioForm":
        await saveScenario(form);
        break;
      case "reportGenerateForm":
        await generateReportSnapshot(form);
        break;
      case "assistantForm":
        await askAssistant(form);
        break;
      default:
        return;
    }
  } catch (error) {
    showToast(readError(error), "error");
  }
}

function resetFormState(formId) {
  const map = {
    householdForm: "household",
    personForm: "person",
    incomeForm: "income",
    loanForm: "loan",
    costForm: "cost",
    insuranceForm: "insurance",
    subscriptionForm: "subscription",
    vehicleForm: "vehicle",
    assetForm: "asset",
    housingForm: "housing",
    scenarioForm: "scenario",
  };
  if (map[formId]) setEdit(map[formId], null);
}

async function deleteFromForm(formId) {
  const map = {
    householdForm: async () => {
      const household = currentEdit("household") || selectedHousehold();
      if (!household) return;
      await request(`/households/${household.id}`, { method: "DELETE" });
      state.selectedHouseholdId = null;
      persistSelection();
      clearEdits();
    },
    personForm: async () => deleteRecord("person", API.persons, currentEdit("person")),
    incomeForm: async () => deleteRecord("income", API.incomes, currentEdit("income")),
    loanForm: async () => deleteRecord("loan", API.loans, currentEdit("loan")),
    costForm: async () => deleteRecord("cost", API.recurringCosts, currentEdit("cost")),
    insuranceForm: async () => deleteRecord("insurance", API.insurancePolicies, currentEdit("insurance")),
    subscriptionForm: async () => deleteRecord("subscription", API.subscriptions, currentEdit("subscription")),
    vehicleForm: async () => deleteRecord("vehicle", API.vehicles, currentEdit("vehicle")),
    assetForm: async () => deleteRecord("asset", API.assets, currentEdit("asset")),
    housingForm: async () => deleteRecord("housing", API.housing, currentEdit("housing")),
    scenarioForm: async () => deleteRecord("scenario", API.scenarios, currentEdit("scenario")),
  };
  if (!map[formId]) return;
  await map[formId]();
  await refreshAllData();
  render();
  showToast("Posten togs bort.");
}

async function saveScenario(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const payload = {
    household_id: state.selectedHouseholdId,
    label: form.elements.label.value.trim(),
    change_set_json: JSON.parse(form.elements.change_set_json.value || "{}"),
  };
  const current = currentEdit("scenario");
  await saveByMode(current, API.scenarios, payload);
  setEdit("scenario", null);
  await refreshAllData();
  render();
  showToast(current?.id ? "Scenariot sparades." : "Scenariot skapades.");
}

async function generateReportSnapshot(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const assumptionRaw = form.elements.assumption_json.value.trim();
  const payload = {
    type: form.elements.type.value,
    as_of_date: form.elements.as_of_date.value,
    assumption_json: assumptionRaw ? JSON.parse(assumptionRaw) : {},
  };
  const report = await request(`/households/${state.selectedHouseholdId}/report_snapshots/generate`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  state.ui.openReportId = report.id;
  await refreshAllData();
  render();
  showToast("Rapporten genererades.");
}

async function analyzeStoredDocument(documentId) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const document = state.data.documents.find((item) => item.id === documentId);
  if (!document?.extracted_text) {
    throw new Error("Dokumentet saknar extraherad text. OCR för bild/screenshot är inte implementerad ännu.");
  }
  const sourceChannel = (document.mime_type || "").toLowerCase() === "application/pdf" ? "uploaded_pdf" : "uploaded_document";
  state.ui.ingestPending = true;
  state.ui.ingestResult = null;
  render();
  try {
    const response = await request(`/households/${state.selectedHouseholdId}${API.ingestAnalyze}`, {
      method: "POST",
      body: JSON.stringify({
        document_id: documentId,
        input_kind: sourceChannel,
        source_channel: sourceChannel,
        source_name: document.issuer || document.file_name || null,
      }),
    });
    state.ui.ingestDocumentId = documentId;
    state.ui.ingestKind = sourceChannel;
    state.ui.ingestSourceName = document.issuer || document.file_name || "";
    state.ui.ingestInput = document.extracted_text;
    state.ui.ingestResult = response;
    showToast("Dokumenttexten analyserades i Data-In.");
  } finally {
    state.ui.ingestPending = false;
    render();
  }
}

async function analyzeIngestForm(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const inputText = form.elements.ingest_input_text.value.trim();
  if (!inputText) throw new Error("Klistra in råtext innan du kör AI-analysen.");
  const inputKind = form.elements.ingest_input_kind.value;
  state.ui.ingestPending = true;
  state.ui.ingestResult = null;
  render();
  try {
    const response = await request(`/households/${state.selectedHouseholdId}${API.ingestAnalyze}`, {
      method: "POST",
      body: JSON.stringify({
        input_text: inputText,
        input_kind: inputKind,
        source_channel: inputKind,
        source_name: form.elements.ingest_source_name.value.trim() || null,
      }),
    });
    state.ui.ingestDocumentId = null;
    state.ui.ingestKind = inputKind;
    state.ui.ingestSourceName = form.elements.ingest_source_name.value.trim();
    state.ui.ingestInput = inputText;
    state.ui.ingestResult = response;
    showToast("AI-analysen är klar. Granska förslagen innan du skapar reviewutkast.");
  } finally {
    state.ui.ingestPending = false;
    render();
  }
}

async function promoteIngestSuggestions() {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  if (!state.ui.ingestResult) throw new Error("Kör en AI-analys först.");
  state.ui.ingestPromoting = true;
  render();
  try {
    const ingestResult = normalizeIngestResult(state.ui.ingestResult);
    const response = await request(`/households/${state.selectedHouseholdId}${API.ingestPromote}`, {
      method: "POST",
      body: JSON.stringify({
        input_text: state.ui.ingestInput,
        input_kind: state.ui.ingestKind,
        source_channel: state.ui.ingestKind,
        document_id: state.ui.ingestDocumentId,
        source_name: state.ui.ingestSourceName || null,
        provider: ingestResult.provider,
        model: ingestResult.model,
        detected_kind: ingestResult.documentType,
        document_summary: state.ui.ingestResult.document_summary || null,
        suggestions: ingestResult.suggestions,
      }),
    });
    await refreshAllData();
    state.ui.ingestResult = null;
    state.ui.ingestInput = "";
    state.ui.ingestDocumentId = null;
    showToast(`Skapade ${response.created_drafts.length} reviewutkast.`);
  } finally {
    state.ui.ingestPromoting = false;
    render();
  }
}

async function askAssistant(form) {
  if (!selectedHousehold()) throw new Error("Välj hushåll först.");
  const prompt = form.elements.prompt.value.trim();
  if (!prompt) return;
  state.ui.assistantMessages.push({ role: "user", content: prompt });
  state.ui.assistantPending = true;
  render();
  try {
    const response = await request(`/households/${state.selectedHouseholdId}${API.assistant}`, {
      method: "POST",
      body: JSON.stringify({ prompt }),
    });
    state.ui.assistantMessages.push({
      role: "assistant",
      content: response.answer,
      provider: response.provider,
      model: response.model,
      usage: response.usage,
    });
    state.ui.assistantInput = "";
  } finally {
    state.ui.assistantPending = false;
    render();
  }
}

function findItemByModuleAndId(moduleKey, id) {
  const collections = {
    person: peopleForHousehold(),
    income: incomesForHousehold(),
    loan: loansForHousehold(),
    cost: recurringCostsForHousehold(),
    insurance: insuranceForHousehold(),
    subscription: subscriptionsForHousehold(),
    vehicle: vehiclesForHousehold(),
    asset: assetsForHousehold(),
    housing: housingForHousehold(),
    scenario: scenariosForHousehold(),
  };
  return collections[moduleKey]?.find((item) => item.id === id) || null;
}
