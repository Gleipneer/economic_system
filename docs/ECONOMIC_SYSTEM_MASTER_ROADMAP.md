# Economic System Master Roadmap

Canonical planning document. Describes the path from current state to a robust, intelligent household economics app with clear AI layers, strong ingest, high traceability, and total control.

Last updated: 2026-04-04.

## Locked Architecture Principle

```text
underlag
-> textutvinning (PDF-text eller OCR)
-> dokumentklassificering
-> fältextraktion
-> confidence/osäkerhet
-> normalisering
-> dubblettkontroll
-> återkommande-upptäckt
-> review queue
-> explicit promote
-> workflow artifacts
-> explicit apply
-> canonical data
-> read models
-> analysis AI
-> ekonomiska råd och förbättringsförslag
```

## Hard Invariants

- AI gets aldrig skriva tyst till kanonisk data
- Rå input != sanning
- OCR-text != dokumentförståelse
- AI-output != backendmath
- Promote skapar bara workflow artifacts
- Apply är separat och explicit
- Osäkerhet måste vara synlig
- Svenska överallt
- Lugn, varm, hushållsnära UX

---

## FAS 1 — Gör ingest verkligt starkt (NU)

### 1.1 Textutvinning
- [x] Inklistrad text
- [x] PDF-text (klistrad)
- [x] Uppladdad textfil
- [x] Uppladdad PDF (med textlager)
- [x] Screenshot / bild (Tesseract OCR swe+eng)
- [x] Skannad PDF (OCR fallback via page-images)
- [x] Tydlig markering av extraktionsmetod
- [x] Tydliga fel vid oläslig input

### 1.2 Dokumentklassificering
- [x] subscription_contract
- [x] invoice
- [x] recurring_cost_candidate
- [x] transfer_or_saving_candidate
- [x] bank_row_batch
- [x] financial_note
- [x] unclear
- [ ] insurance_policy (tillägg behövs i AI-schema)
- [ ] loan_or_credit (tillägg behövs i AI-schema)

### 1.3 Fältextraktion
- [x] provider_name
- [x] label/title
- [x] amount
- [x] currency
- [x] due_date
- [x] cadence/frekvens
- [x] category_hint
- [x] household_relevance
- [x] confidence
- [x] uncertainty_reasons
- [x] confirmed_fields vs uncertain_fields

### 1.4 Confirmed vs Uncertain
- [x] AI returnerar confirmed_fields-lista
- [x] Frontend visar bekräftade fält separat (grön border)
- [x] Frontend visar osäkra fält separat (gul border)
- [x] Uncertainty reasons visas explicit

### 1.5 Review Queue
- [x] ExtractionDraft med pending_review status
- [x] Applicera (apply) knapp per utkast
- [x] Avvisa (delete) knapp per utkast
- [ ] Redigera utkast innan apply
- [ ] Skjut upp (defer) funktion
- [ ] Bättre visuell status per utkast (confidence badge, typ-label)

### 1.6 LF Bank Copy-Paste
- [x] bank_paste source channel
- [x] Dedikerad AI-prompt med radgrupperingsregler
- [x] Review-buckets: recurring, subscription, transfer_or_saving, unclear
- [x] Högre max_output_tokens (1400) för batchsvar
- [x] Live-testat med LF-format

---

## FAS 2 — Smartare normalisering (SNART)

### 2.1 Merchant-normalisering
- [ ] Identifiera att NETFLIX.COM, Netflix, NETFLIX Amsterdam = samma aktör
- [ ] Normalisera leverantörsnamn vid review

### 2.2 Dubblettkontroll
- [ ] Detektera om samma faktura kom in via PDF och screenshot
- [ ] Varna vid möjlig dubblett i review queue

### 2.3 Ownership-förslag
- [ ] Föreslå privat / gemensam / oklar ägare
- [ ] Relevant för tvåpersonershushåll

### 2.4 Regelmotor
- [ ] Användaren kan godkänna mönster (t.ex. "Google One = abonnemang")
- [ ] Regler tillämpas vid framtida ingest

---

## FAS 3 — Återkommande och tid (SNART)

### 3.1 Återkommande-motor
- [ ] Upptäck återkommande mönster (månad, kvartal, år)
- [ ] Markera engångsköp vs återkommande

### 3.2 Tidsmotor / reminders
- [ ] Faktura förfaller snart
- [ ] Bindningstid närmar sig slut
- [ ] Utkast väntar på review

---

## FAS 4 — Analys som verkligt hjälper (SENARE)

### 4.1 Avvikelsemotor
- [ ] Ovanligt hög matkostnad
- [ ] Ny återkommande dragning
- [ ] Ökade bilkostnader

### 4.2 Abonnemangsoptimering
- [ ] Hitta icke-registrerade abonnemang
- [ ] Visa total abonnemangskostnad
- [ ] Identifiera dubbla/överlappande tjänster

### 4.3 Kassaflödesförståelse
- [ ] Fasta vs rörliga kostnader
- [ ] Sparande
- [ ] Skuldbelastning
- [ ] Privat vs gemensamt

### 4.4 Nästa-månad-stöd
- [ ] Sannolika utgifter nästa månad
- [ ] Låsta vs påverkbara kostnader

---

## FAS 5 — Fullt robust AI-lager (SENARE)

### 5.1 Read Models för analys
- [ ] Kompakta read models istället för rå databas-dump
- [ ] Lägre tokenkostnad, mindre hallucination

### 5.2 Källspårning / audit trail
- [ ] Spåra originalkälla → OCR → AI → review → apply

### 5.3 Semantisk sök
- [ ] Fråga om bilen, barn, abonnemang etc.

---

## Vad som INTE bör byggas nu

- Full bank-sync / bankinloggning
- Finance core / ledger
- Bred AI-gateway med flera leverantörer
- Autonom AI som skapar slutlig data
- Bred frontend redesign
- Stora arkitekturomkastningar
