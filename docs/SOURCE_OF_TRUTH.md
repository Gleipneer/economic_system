# Source of Truth

Kanoniskt sanningsdokument för hushållsekonomiprojektet.
Last verified against code: 2026-04-10.

## Vad systemet är

Ett svenskt hushållsekonomisystem — en enda FastAPI-app med inbäddad
vanilla-JS-frontend — för planering, översikt och rådgivning kring
ett hushålls ekonomi.

Systemet lagrar strukturerad hushållsekonomidata (inkomster, lån,
abonnemang, försäkringar, fordon, tillgångar, kostnader), beräknar
deterministiska sammanfattningar, erbjuder scenariojämförelse,
dokumenthantering och rapportgenerering.

AI-funktioner (hushållsassistent och data-ingest) är separata ytor
som kräver extern OpenAI-nyckel. De skriver aldrig tyst till
kanonisk data.

## Vem det är till för

- Primärt: ett svenskt hushåll som vill ha praktisk koll på sin ekonomi
- Sekundärt: framtida AI-modeller/utvecklare som ska vidareutveckla systemet

## Scope — vad systemet gör idag

| Förmåga | Status |
|---|---|
| CRUD för 16 domänentiteter | ✅ Implementerat |
| Deterministisk hushållssammanfattning | ✅ Implementerat |
| Boendekalkyl / housing evaluation | ✅ Implementerat |
| Scenariokörning med resultatjämförelse | ✅ Implementerat |
| Rapportögonblicksbilder (snapshots) | ✅ Implementerat |
| Dokumentuppladdning/nedladdning | ✅ Implementerat |
| Extraktionsutkast + explicit applicering | ✅ Implementerat |
| Optimeringsförslag (heuristisk scan) | ✅ Implementerat |
| Data-In AI (klassificering + extrahering) | ✅ Kräver OpenAI |
| Hushållsassistent (read-only analys) | ✅ Kräver OpenAI |
| OCR (Tesseract swe+eng) | ✅ Kräver systemberoenden |
| Bank-PDF export (reportlab) | ✅ Implementerat |
| Merchant alias-normalisering | ✅ Implementerat |
| Risk-/readiness-signaler på sammanfattning | ✅ Implementerat |
| Autentisering | ❌ Saknas |
| Bankkopplingar / transaktionsingest | ❌ Saknas |
| Bakgrundsjobb | ❌ Saknas |
| AI-gateway / provider-abstraktion | ❌ Saknas |
| Metrics / observability | ❌ Saknas |

## Kärnprinciper

1. **Sanning före allt.** Dokumentation speglar faktisk kod, aldrig tvärtom.
2. **AI skriver aldrig tyst.** All AI-output landar i workflow-artefakter. Kanonisk data ändras bara via explicit apply.
3. **Backend äger all finansmatematik.** Inga beräkningar i frontend.
4. **SQLite-first, filesystem-first.** Enkel drift utan externa beroenden.
5. **Svenska i UI.** Hushållsapp, inte enterprise-dashboard.
6. **Determinism framför magi.** Förutsägbar, reproducerbar logik.
7. **Explicit hellre än implicit.** Varje AI-interaktion kräver explicit prompt och explicit promote/apply.

## Systemgränser

```
┌──────────────────────────────────────────┐
│            Trusted Network               │
│         (Tailscale / localhost)           │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │         FastAPI (app.main:app)     │  │
│  │  ┌──────────┐  ┌───────────────┐  │  │
│  │  │ REST API │  │  Static SPA   │  │  │
│  │  │  (JSON)  │  │  (HTML/JS/CSS)│  │  │
│  │  └────┬─────┘  └───────────────┘  │  │
│  │       │                            │  │
│  │  ┌────┴─────┐  ┌───────────────┐  │  │
│  │  │ SQLAlch. │  │  ai_services  │──┼──┼──→ OpenAI API
│  │  │ + SQLite │  │   (httpx)     │  │  │    (extern)
│  │  └──────────┘  └───────────────┘  │  │
│  │       │                            │  │
│  │  ┌────┴─────┐                      │  │
│  │  │ Filesystem│ (uploaded_files/)   │  │
│  │  └──────────┘                      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Separation: nuläge vs målbild vs deferred

### Nuläge (implementerat och verifierat)
- Fullständig CRUD-backend för alla domänentiteter
- Deterministiska beräkningar (sammanfattning, boende, scenario, rapport)
- Real OpenAI-integration med Responses API
- Data-In med 9 klassificeringstyper, OCR, bank-paste
- Svensk SPA-frontend med 16 routade sidor
- start_app.sh med venv, alembic, port-fallback, Tailscale-URL

### Planerad målbild (ej implementerat)
- Starkare dubblettkontroll mot kanonisk data
- Evidenskedja (document → draft → applied entity)
- Regelmotor för godkända mönster
- Återkommande-motor och påminnelser
- Read models för AI (kompakt, lägre tokenkostnad)
- Käll-/auditspårning

### Medvetet deferred
- Full banksync / bankinloggning
- Finance core / ledger
- Brett AI-gateway med flera providers
- Autonom AI-skrivning till kanonisk data
- Autentisering (trust boundary = nätverksnivå via Tailscale)
- Broad frontend redesign
