# Next Action

Canonical status: single recommended next task for the next agent pass.
Last reviewed: 2026-04-04.

## Next Task

Improve review UX for batched bank paste results and OCR-extracted documents.

## Why This Comes Next

This is the highest-value gap directly visible after the current pass:

- the app now has a real OpenAI-backed Data-In surface
- the next practical user problem is pasted bank data, especially LF-style account export text
- current ingest is conservative and safe, but it is strongest on simple contract text rather than bank-row interpretation
- there is still no transaction ledger, so the next step must stay inside the existing planning/workflow model

That makes bank-copy-paste-to-review-draft the next product and AI step with the best user value per unit of risk.

## What Must Stay Stable

- Keep `app.main:app` as the runtime entrypoint.
- Keep the current Swedish route-based frontend shell.
- Keep the global active-household selector.
- Keep the current recurring-cost, documents, and assistant flows working as they do now.
- Keep backend-owned money math out of the model output.
- Keep AI writes limited to workflow artifacts unless the user explicitly applies a draft later.

## What Not To Touch In That Pass

- Do not start auth work.
- Do not start bank sync, bank adapters, or finance core work.
- Do not split the whole backend into routers/services in the same pass.
- Do not redesign the whole visual language.
- Do not collapse Data-In AI and analysis AI into one generic chat.

## Acceptance Criteria

- LF-like pasted account text with fields such as `bokföringsdatum`, `transaktionsdatum`, `transaktionstext`, `belopp`, and `saldo` can be analysed in the product.
- The system can classify rows conservatively into likely recurring payment, likely subscription, likely transfer/saving, or unclear.
- Suggestions are validated and presented as reviewable workflow artifacts, not as silent canonical writes.
- The UI keeps raw input, AI interpretation, and later canonical application clearly separated.
- Existing assistant, recurring-cost, subscription, document, and report flows remain stable.
- Documentation is updated to reflect the real scope of the new ingest behavior.

## Useful Starting Files

- `app/static/app.js`
- `app/ai_services.py`
- `app/static/styles.css`
- `app/main.py`
- `app/schemas.py`
- `docs/AI_DIRECTION.md`
- `docs/CURRENT_STATE.md`
- `docs/AINEXTSTEPPATCH.md`
