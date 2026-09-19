# Problem Definition & Business Scope: Royal Square Financial Digital Backend
FSP Number: 29370 | Reg. No: 2009/022911/07

## 1. Problem Statement
- **Current State:** Royal Square Financial operates with excessive paper forms and high-friction compliance administrative overhead (FAIS disclosure documents, FICA checks, POPIA client consent forms, confidentiality agreements)[cite: 1, 2, 3]. Client interactions—ranging from roadside accident claims to policy valuations and annual reviews—are manually processed across multiple third-party product providers (Santam, Sanlam, Discovery, Old Mutual, Liberty, Momentum)[cite: 1, 2, 3].
- **Root Impact:** Advisors spend disproportionate hours on compliance paperwork and manual status communication instead of financial planning and advisory services[cite: 2, 3]. Clients face severe friction, delays, and potential data loss during roadside accident reporting without real-time tracking of claim milestones[cite: 1, 2].
- **Root Cause:** Lack of a unified, compliant, offline-first digital backend that connects client self-service, advisor portfolio management, straight-through provider dispatches, and automated compliance tracking[cite: 1, 2, 3].

## 2. Success Criteria (Definition of Done)
- [ ] **Unified API Layer:** Deployed REST API covering all required resource groups: Auth, Dashboards (Client & Advisor), Assets, Claims, Reminders, Goals, Service Requests, FNA, and Agreements[cite: 4].
- [ ] **Offline-First Roadside Claims:** Roadside claim draft registration (`POST /claims`) and media upload (`POST /claims/{id}/media`) handle network loss gracefully, saving locally and syncing idempotently once online[cite: 3, 4, 5].
- [ ] **Automated Reminders:** Automated trigger pipeline operational for driving licence expiries, 2-year valuation certificates, annual reviews, and client birthdays[cite: 2, 4, 5].
- [ ] **Advisor Practice Management:** Dedicated advisor routes for tracking assets under advice, managing client rosters, pushing weekly repair timeline updates, and monitoring compliance statuses[cite: 1, 2, 4].
- [ ] **POPIA & Cryptographic Compliance:** 
  - 100% of uploaded claim evidence (photos, discs, licences, voice notes) encrypted client-side via AES-256-GCM before transport and cloud bucket storage[cite: 1, 3, 5].
  - Transport strictly enforced over TLS 1.3[cite: 3].
  - Special Personal Information (13-digit SA ID numbers, encrypted banking details, medical underwriting questionnaires) protected under strict RBAC and immutable audit logging[cite: 3, 5].
- [ ] **Digital Compliance & FNA:** Backend intake and storage for digital signatures (Service Agreements, Client Consents, FAIS Disclosures) and multi-step FNA/Risk Profile calculations[cite: 2, 3].

## 3. Explicit Non-Goals (Out of Scope)
- Do NOT build an autonomous AI financial investment advisor or automated stock-trading engine.
- Do NOT integrate direct debit order processing or third-party bank clearing gateways (banking details are stored encrypted for brokerage administrative verification only)[cite: 5].
- Do NOT build live GPS telematics or vehicle IoT tracking engines.
- Do NOT implement an in-app instant chat messaging engine; communications follow structured timeline updates, push notifications, and service-request messages[cite: 1, 4].

## 4. Invariant Constraints & Legal/Security Rules
- **Regulatory Jurisdiction:** Strictly adhere to the South African Protection of Personal Information Act (POPIA), FAIS Act, and FICA requirements[cite: 2, 3].
- **Data Minimization:** Endpoints must expose only the specific fields necessary for the active view; never return raw unmasked banking details or sensitive medical histories on general dashboard endpoints[cite: 5].
- **Cryptographic Envelope:** Supabase storage buckets must store zero unencrypted evidence files; encryption keys are never persisted in plaintext database tables[cite: 3, 5].
- **Single Source of Truth:** Database schemas (`users`, `financial_products`, `claims`, `claim_evidence`, `reminders`, `goals`, `service_requests`) dictate entity structure; no dynamic unstructured tables[cite: 5].

## 5. Verification & Acceptance Steps
1. **POPIA Data Exposure Test:** Verify that unprivileged endpoints (`GET /users/me`, `GET /dashboard/summary`) never return plaintext `banking_details_encrypted` or unmasked ID numbers[cite: 4, 5].
2. **Offline-Sync Idempotency:** Transmit identical offline claim packages twice to `POST /claims` and `POST /claims/{id}/submit`; verify that only a single claim record and single insurer dispatch event are created[cite: 4, 5].
3. **Evidence Ciphertext Audit:** Directly inspect uploaded binary evidence in cloud storage to confirm files are AES-256-GCM encrypted blobs unreadable without the decryption key[cite: 3, 5].
4. **Compliance Status Verification:** Verify that submitting a signed consent form updates the advisor compliance dashboard record from pending to compliant[cite: 2].