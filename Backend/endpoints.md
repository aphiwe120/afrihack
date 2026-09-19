# Royal Square Financial (Pty) Ltd — Core Backend API Specification
FSP Number: 29370 | Reg. No: 2009/022911/07

All endpoints enforce TLS 1.3 in transit. Binary uploads and sensitive payloads (ID docs, bank details, FNA medical records) must be client-side encrypted using AES-256-GCM prior to transmission.

---

## 1. Authentication & Profiles
- `POST /auth/register` — Client and advisor registration (validates 13-digit SA ID, roles, FAIS accreditations).
- `POST /auth/login` — Session token issuance, biometric key exchange, and 2FA challenge.
- `POST /auth/verify-biometrics` — Biometric face recognition and liveness verification during onboarding.
- `GET /users/me` — Fetch authenticated user profile and roles.
- `PUT /users/me` — Update contact numbers, residential address, or encrypted banking details.

---

## 2. Dashboards & Assets
- `GET /dashboard/summary` — Aggregate real-time net worth calculation (assets vs. liabilities) and quick-action metrics.
- `GET /advisor/dashboard` — Advisor KPI summary (total clients, assets under advice, active claims, overdue compliance).
- `GET /assets` — List user's linked policies and investment products.
- `POST /assets` — Manually register/link a financial policy (Santam, Sanlam, Discovery, Old Mutual).
- `GET /assets/{id}` — Fetch detailed asset breakdown, policy schedule, and history.
- `PATCH /assets/{id}` — Update asset valuation (Advisor restricted) or modify policy metadata.

---

## 3. Claims & Incident Workflow (Roadside & Offline-First)
- `GET /claims` — List claims (filterable by status: draft, submitted, assessment_booked, repair_authorised, closed).
- `POST /claims` — Create or sync accident report draft (supports offline batch sync; auto-triggers 48-hour police reminder if case number is missing).
- `GET /claims/{id}` — Fetch detailed incident record and third-party details.
- `PATCH /claims/{id}/police-report` — Attach SAPS case number and notified timestamp post-incident; resolves 48-hour police reminder.
- `POST /claims/{id}/media` — Upload pre-encrypted evidence blobs (scene photos, licence discs, voice notes, sketches).
- `GET /claims/{id}/media/{evidence_id}` — Generate short-lived (60s) authenticated signed URL to access private encrypted evidence.
- `POST /claims/{id}/submit` — Idempotent final submission and dispatch to insurer API / broker simulator queue.
- `GET /claims/{id}/timeline` — Fetch vertical status progression and weekly repair milestones.
- `POST /claims/{id}/timeline` — Advisor/system endpoint to append repair updates or advance workflow status.
- `POST /claims/{id}/reviews` — Submit 1–5 star rating, client commentary, and trigger claim archival.

---

## 4. Reminders & Compliance
- `GET /reminders` — Fetch reminders (driving licence expiries, 48-hour police reports, 2-year valuations, annual reviews, birthdays).
- `POST /reminders` — Create custom reminders (supports client-level and bulk advisor scheduling).
- `PATCH /reminders/{id}` — Mark reminder as acknowledged or set `is_resolved = true`.
- `DELETE /reminders/{id}` — Remove an active or obsolete reminder.
- `GET /compliance/report` — Advisor overview of FAIS disclosure, FICA, and POPIA consent statuses across clients.

---

## 5. Goals & Service Requests
- `GET /goals` — Fetch individual and shared financial goals with target progress.
- `POST /goals` — Initialize a new financial goal with milestone targets.
- `PATCH /goals/{id}` — Quick-update goal balance ("Add Funds"), edit targets, or toggle milestone checkboxes.
- `DELETE /goals/{id}` — Archive or delete a goal.
- `GET /service-requests` — List client service requests (Pending, Processing, Completed).
- `POST /service-requests` — Submit request (Change of Address, Bank Details, Border Letter, IRP5, Consultation).
- `GET /service-requests/{id}` — View request payload, attached documents, and status timeline.
- `PATCH /service-requests/{id}` — Cancel request (client) or transition processing state (advisor).

---

## 6. Advisor Management, FNA & Legal Documents
- `GET /advisor/clients` — Searchable and filterable client roster (includes net worth, risk profile, review dates).
- `GET /advisor/clients/{id}` — Complete 360-degree client dossier (FNA summary, policies, claims, compliance flags).
- `POST /fna` — Save Financial Needs Analysis steps (Personal, Assets/Liabilities, Income/Expenditure, Risk Profile).
- `GET /fna/{client_id}` — Retrieve latest completed FNA record and calculated risk tier (Cautious, Moderate, Assertive).
- `POST /agreements/sign` — Submit digital signature tokens for FAIS Disclosure, Client Consent, and Confidentiality.
- `GET /agreements` — Fetch signed legal agreements and historical consent records.