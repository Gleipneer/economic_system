export function createAssistantRenderer({
  state,
  escapeHtml,
  selectedHousehold,
  renderPageHeader,
  renderAssistantMarkdown,
}) {
  function summarizeIntentAction(intent) {
    return {
      create_expense: "Skapa återkommande kostnad",
      create_income: "Skapa inkomstkälla",
      create_planned_purchase: "Skapa planerat köp",
      create_subscription: "Skapa abonnemang",
      update_entity: "Uppdatera befintlig post",
      delete_entity: "Avsluta/ta bort post",
    }[intent] || intent;
  }

  function formatIntentValue(value) {
    if (value === null || value === undefined || value === "") return "okänt";
    if (typeof value === "boolean") return value ? "Ja" : "Nej";
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  }

  function renderIntentFieldChanges(writeIntent) {
    const data = writeIntent.data || {};
    const changes = [];
    if (writeIntent.intent === "update_entity" && data.updates && typeof data.updates === "object") {
      Object.entries(data.updates).forEach(([key, nextValue]) => {
        const previous = data.previous_values && typeof data.previous_values === "object" ? data.previous_values[key] : undefined;
        changes.push(
          `<li><span>${escapeHtml(key)}</span><strong>${escapeHtml(formatIntentValue(previous))} → ${escapeHtml(formatIntentValue(nextValue))}</strong></li>`,
        );
      });
    } else {
      Object.entries(data)
        .filter(([key]) => !["entity_id", "entity_type", "updates", "previous_values", "proposed_updates"].includes(key))
        .forEach(([key, value]) => {
          changes.push(`<li><span>${escapeHtml(key)}</span><strong>${escapeHtml(formatIntentValue(value))}</strong></li>`);
        });
    }
    if (!changes.length) {
      changes.push("<li><span>Detaljer</span><strong>Inga fält specificerade</strong></li>");
    }
    return `<ul class="intent-change-list">${changes.join("")}</ul>`;
  }

  function renderAssistantDeterministicOverview() {
    const analysis = state.ui.assistantAnalysis;
    const isLoading = state.ui.assistantAnalysisLoading;
    if (isLoading) {
      return `
        <aside class="assistant-brief panel">
          <div class="assistant-brief-loading">Laddar analysmotorn...</div>
        </aside>
      `;
    }
    if (!analysis) return "";

    const presentation = analysis.presentation || {};
    const metrics = presentation.headline_metrics || [];
    const alerts = analysis.alerts || [];
    const actions = analysis.action_primitives || [];
    const summaries = presentation.summary_primitives || [];

    return `
      <aside class="assistant-brief panel">
        <div class="assistant-brief-head">
          <span class="section-eyebrow">Deterministisk motor</span>
          <h3>Ekonomilaget just nu</h3>
          <p class="muted">Chatten arbetar ovanpå hushållets beräknade kärndata, inte istället för den.</p>
        </div>
        <div class="assistant-brief-metrics">
          ${metrics.map(renderHeadlineMetric).join("")}
        </div>
        ${alerts.length ? `
          <div class="assistant-brief-section">
            <h4>Flaggor</h4>
            <div class="assistant-alert-list">
              ${alerts.map(renderAlertCard).join("")}
            </div>
          </div>
        ` : ""}
        ${actions.length ? `
          <div class="assistant-brief-section">
            <h4>Nästa steg</h4>
            <ul class="assistant-action-list">
              ${actions.slice(0, 5).map(renderActionPrimitive).join("")}
            </ul>
          </div>
        ` : ""}
        ${summaries.length ? `
          <div class="assistant-brief-section assistant-summary-grid">
            ${summaries.map(renderSummaryPrimitive).join("")}
          </div>
        ` : ""}
      </aside>
    `;
  }

  function renderAssistantPage() {
    const messages = state.ui.assistantMessages;
    const isLoading = state.ui.assistantThreadLoading;
    const prompts = [
      "Sammanfatta vår ekonomi just nu på ett enkelt sätt.",
      "Hur ser kalkylen ut för nästa lön?",
      "Planerat köp: Nya fälgar 4000kr",
      "Lägg till inkomst: Bonus 5000 kr denna månad",
      "Radera Netflix-abonnemanget",
    ];

    const mobileSummaryOpen = Boolean(state.ui.assistantMobileSummaryOpen);
    return `
      <section class="page-wrap assistant-page-central">
        ${renderPageHeader("Ekonomiassistent", "Din intelligenta huvudyta för att analysera och uppdatera systemet.")}
        <section class="assistant-workspace ${mobileSummaryOpen ? "mobile-summary-open" : ""}">
          <button class="ghost mobile-summary-toggle" type="button" data-action="toggle-assistant-summary" aria-expanded="${mobileSummaryOpen ? "true" : "false"}">
            ${mobileSummaryOpen ? "Dolj ekonomiläge" : "Ekonomiläge"}
          </button>
          ${renderAssistantDeterministicOverview()}
          <article class="panel chat-shell chat-shell-full">
            ${isLoading ? `
              <div class="chat-intro-banner">
                <h3>Laddar konversation</h3>
                <p class="muted">Hämtar sparad assistenthistorik för hushållet.</p>
              </div>
            ` : messages.length === 0 ? `
              <div class="chat-intro-banner">
                <h3>Välkommen till din ekonomiassistent</h3>
                <p class="muted">Fråga om nuläget, be om forecast eller be systemet lägga in/ta bort utgifter och inkomster med vanligt språk.</p>
                <div class="prompt-grid">
                  ${prompts.map((prompt) => `<button class="prompt-chip" type="button" data-prompt="${escapeHtml(prompt)}">${escapeHtml(prompt)}</button>`).join("")}
                </div>
              </div>
            ` : ""}
            <div class="chat-log ${messages.length === 0 ? "hidden" : ""}">
              ${messages.map(renderAssistantMessage).join("")}
            </div>
            <form id="assistantForm" class="chat-composer central-composer">
              <textarea name="prompt" placeholder="Skriv din fråga, be om analys eller beskriv något som ska registreras...">${escapeHtml(state.ui.assistantInput || "")}</textarea>
              <div class="actions-row assistant-composer-actions">
                <label class="ghost compact assistant-file-label">
                  <span>Bifoga dokument</span>
                  <input name="files" type="file" multiple accept="text/plain,text/csv,text/*,application/pdf,application/json,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,.txt,.text,.csv,.json,.xml,.yaml,.yml,.md,.xlsx,.xls" />
                </label>
                <button class="primary" type="submit" ${selectedHousehold() ? "" : "disabled"}>${state.ui.assistantPending ? "Analyserar..." : "Skicka"}</button>
              </div>
              <span class="chat-disclaimer ${messages.length ? "subtle-disclaimer" : ""}">Assistenten skapar alltid ett utkast som du får godkänna innan något sparas.</span>
            </form>
          </article>
        </section>
      </section>
    `;
  }

  function renderAssistantMessage(message) {
    if (state.ui.assistantDismissedIntentIds && state.ui.assistantDismissedIntentIds.includes(message.id)) {
      return "";
    }
    let extraContent = "";
    if (message.questions && message.questions.length > 0) {
      extraContent += `<div class="chat-questions"><strong>Frågor för att gå vidare:</strong><ul>${message.questions.map((q) => `<li>${escapeHtml(q)}</li>`).join("")}</ul></div>`;
    }
    if (message.write_intent && message.write_intent.intent !== "none") {
      const wi = message.write_intent;
      const isApplied = message.intent_applied;
      const hasMissingFields = Boolean(wi.missing_fields && wi.missing_fields.length);
      const hasOpenQuestions = Boolean(message.questions && message.questions.length);
      const hasPersistedMessageId = Number.isInteger(message.id);
      const batchUpdates = Array.isArray(wi.data?.proposed_updates) ? wi.data.proposed_updates : [];
      const hasUnsupportedBatch = batchUpdates.length > 1;
      const canApply = !hasMissingFields && !hasOpenQuestions && hasPersistedMessageId && !hasUnsupportedBatch;
      const btnAttrs = isApplied
        ? `disabled class="primary success"`
        : message.intent_apply_loading
          ? `disabled class="primary"`
          : `class="primary" data-action="apply-assistant-intent" data-message-id="${message.id}"`;
      const btnText = isApplied ? "✔ Sparad" : message.intent_apply_loading ? "Sparar..." : "Godkänn och spara";
      extraContent += `
        <div class="chat-intent-card panel">
          <div class="intent-card-head">
            <strong>Föreslagen ändring</strong>
            <span class="intent-status-pill ${canApply || isApplied ? "ready" : "blocked"}">${isApplied ? "Sparad" : hasMissingFields || hasOpenQuestions ? "Behöver mer information" : hasUnsupportedBatch ? "Batch kräver manuell delning" : "Kräver godkännande"}</span>
          </div>
          <p class="intent-summary">${escapeHtml(summarizeIntentAction(wi.intent))}${wi.target_entity_type ? ` · ${escapeHtml(wi.target_entity_type)}` : ""}</p>
          ${renderIntentFieldChanges(wi)}
          ${hasMissingFields ? `<p class="error-text subtle"><em>Behöver mer information: ${escapeHtml(wi.missing_fields.join(", "))}</em></p>` : ""}
          ${hasOpenQuestions ? `<p class="error-text subtle"><em>Besvara frågorna innan åtgärden kan sparas.</em></p>` : ""}
          ${hasUnsupportedBatch ? `<p class="error-text subtle"><em>Flera uppdateringar i samma write_intent stöds inte för apply ännu.</em></p>` : ""}
          ${!hasPersistedMessageId ? `<p class="error-text subtle"><em>Ladda om sparat förslag innan åtgärden kan sparas.</em></p>` : ""}
          <div class="actions-row">
            ${canApply || isApplied ? `<button type="button" ${btnAttrs}>${btnText}</button>` : ""}
            ${!isApplied && hasPersistedMessageId ? `<button type="button" class="ghost" data-action="dismiss-assistant-intent" data-message-id="${message.id}">Avvisa</button>` : ""}
          </div>
        </div>
      `;
    }
    if (message.content_json?.result) {
      extraContent += `
        <div class="chat-result-card">
          <strong>Systemresultat</strong>
          <p>${escapeHtml(message.content_json.result.entity_type || "ändring")} · ID ${escapeHtml(String(message.content_json.result.entity_id || ""))}</p>
        </div>
      `;
    }
    if (message.content_json?.document_ids?.length) {
      extraContent += `
        <div class="chat-result-card">
          <strong>Dokumentflöde</strong>
          <p>${message.content_json.document_ids.length} dokument stageades för granskning.</p>
        </div>
      `;
    }

    return `
      <article class="chat-message ${message.role} ${message.message_type || ""}">
        <div class="chat-avatar">${message.role === "assistant" ? "AI" : message.role === "system" ? "SYS" : "DU"}</div>
        <div class="chat-message-body">
          <div class="chat-role">${message.role === "assistant" ? "Ekonomiassistent" : message.role === "system" ? "System" : "Du"}</div>
          <div class="chat-bubble chat-bubble-card">${renderAssistantMarkdown(message.content)}</div>
          ${extraContent}
          ${message.role === "assistant" && message.model ? `<div class="muted">${escapeHtml(message.provider || "openai")} · ${escapeHtml(message.model)}${message.usage?.total_tokens ? ` · ${message.usage.total_tokens} tokens` : ""}</div>` : ""}
        </div>
      </article>
    `;
  }

  function renderHeadlineMetric(metric) {
    return `
      <article class="assistant-headline assistant-tone-${escapeHtml(metric.tone || "neutral")}">
        <span>${escapeHtml(metric.label)}</span>
        <strong>${escapeHtml(metric.value)}</strong>
        ${metric.detail ? `<small>${escapeHtml(metric.detail)}</small>` : ""}
      </article>
    `;
  }

  function renderAlertCard(alert) {
    return `
      <article class="assistant-alert assistant-severity-${escapeHtml(alert.severity || "info")}">
        <strong>${escapeHtml(alert.title)}</strong>
        <p>${escapeHtml(alert.message)}</p>
      </article>
    `;
  }

  function renderActionPrimitive(action) {
    return `<li><strong>${escapeHtml(action.title)}</strong><span>${escapeHtml(action.description)}</span></li>`;
  }

  function renderSummaryPrimitive(item) {
    return `
      <article class="assistant-summary assistant-tone-${escapeHtml(item.tone || "neutral")}">
        <span>${escapeHtml(item.title)}</span>
        <strong>${escapeHtml(item.value)}</strong>
        ${item.detail ? `<small>${escapeHtml(item.detail)}</small>` : ""}
      </article>
    `;
  }

  return {
    renderAssistantPage,
    renderAssistantDeterministicOverview,
    renderAssistantMessage,
  };
}
