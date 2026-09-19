# Architectural & Design Principles: Royal Square Financial Backend
FSP Number: 29370 | Reg. No: 2009/022911/07

## 1. Core Engineering Trade-offs
- **Security & Privacy over Convenience:** POPIA compliance and data integrity strictly override rapid development hacks. No temporary endpoints may bypass authorization checks or return unmasked PII.
- **Explicit Schema over Dynamic Typing:** All database interactions, request bodies, and external provider payloads must use strict relational schemas and explicit DTO validation models.
- **Idempotency over Speed in Dispatches:** Claim draft submissions (`/claims/{id}/submit`) and service requests must be idempotent to prevent duplicate records during network drops or roadside retries.
- **Simplicity over Premature Abstraction:** Do not invent generic multi-tenant layers or speculative factory patterns for services used only once. Keep business logic flat, direct, and readable.

## 2. Structural & Architectural Invariants
- **Domain Layering:**
  - **Controllers / Routes:** Handle HTTP transport, request schema validation, and status codes only. Zero database queries or raw business rules inside route handlers.
  - **Services / Use Cases:** Orchestrate core business logic, POPIA consent validation, insurer dispatch adapters, and notification triggers.
  ## Automated Workflow Invariants
- **48-Hour Police Reminder:** If a motor claim is initiated without a `police_case_number`, the system must immediately schedule an automated reminder with `type = 'police_report'` due 48 hours from `incident_timestamp`.

## Provider Integration & Simulation
- **Insurer Gateway Abstraction:** All dispatches to external providers (Santam, Sanlam, Discovery, etc.) must implement a unified `InsurerGateway` interface. In development/testing environments (`INSURER_ENV=mock`), this adapter must generate mock claim handler assignments and claim numbers locally without triggering network requests.

## Storage Security
- Supabase storage buckets holding claim evidence must have public access disabled (`public = false`). The backend must enforce signed URL generation with a maximum TTL of 60 seconds.
  - **Data Access Layer:** Repository interfaces abstracting PostgreSQL / Supabase client queries.
- **Database Naming Conventions:**
  - Tables: Plural, snake_case (`users`, `financial_products`, `claims`, `claim_evidence`, `reminders`, `goals`, `service_requests`).
  - Columns: Explicit snake_case (`incident_timestamp`, `is_resolved`, `banking_details_encrypted`).
  - Foreign Keys: Singular entity name appended with `_id` (`user_id`, `claim_id`, `product_id`).
  - Timestamps: Always UTC with timezone (`created_at TIMESTAMPTZ DEFAULT NOW()`).

## 3. Security, POPIA & Cryptographic Standards
- **Client-Side Document Encryption (AES-256-GCM):**
  - All binary evidence uploaded to `/claims/{id}/media` (licence discs, driver licences, scene photos, voice notes) must arrive as pre-encrypted binary streams using AES-256-GCM.
  - Supabase Storage buckets must never store unencrypted evidence blobs.
- **Transport Security:**
  - Reject all incoming connections below TLS 1.2; strictly enforce TLS 1.3 across all endpoints.
  - Enforce HTTP Strict Transport Security (HSTS).
- **POPIA Data Compliance & Minimization:**
  - **Sensitive Personal Information:** 13-digit SA ID numbers, banking records, biometric hashes, and Medical Underwriting questionnaire records must be encrypted at rest and never logged in plain text.
  - **Role-Based Access Control (RBAC):** Clients may access only their own records. Advisors may only access data for clients assigned to their brokerage portfolio.
  - **Audit Logging:** Maintain immutable access logs whenever sensitive client PII, banking details, or FNA medical histories are retrieved or exported.

## 4. Offline Sync & Resilience Invariants
- **Local-First Queue Synchronization:**
  - Accident reports captured offline must sync idempotently upon reconnection.
  - Endpoints receiving offline-queued data (`POST /claims`, `POST /claims/{id}/media`) must handle duplicate submission keys gracefully without creating duplicate database rows.
- **Signed URL Access:**
  - Stored files and policy schedules must never be exposed via public bucket URLs. Deliver attachments exclusively via short-lived, authenticated signed URLs.

## 5. Anti-Patterns & Banned Implementations
- ❌ **No Plaintext Sensitive Data:** Storing unencrypted bank account numbers, tax numbers, or medical underwriting answers in raw columns is strictly prohibited.
- ❌ **No Direct Insurer Hardcoding:** Santam, Sanlam, Discovery, Old Mutual API configurations must reside exclusively in environment configurations, never in application source code.
- ❌ **No Monolithic Route Handlers:** Do not mix file storage management, DB writes, and insurer API dispatches in a single procedural route block.
- ❌ **No Silent Fallbacks:** Never mask operational errors or database write failures with empty arrays or generic `200 OK` responses.

## 6. Agent Review Checklist
Before proposing or committing backend code, verify:
- [ ] Does this endpoint adhere to the expanded API blueprint (`/auth`, `/dashboard`, `/advisor`, `/claims`, `/reminders`, `/goals`, `/service-requests`, `/fna`, `/agreements`)?
- [ ] Is input validation applied at the boundary using schema validators before invoking business logic?
- [ ] Are all PII, banking data, and medical questionnaire responses encrypted according to POPIA and AES-256-GCM standards?
- [ ] Are database foreign keys, unique constraints, and index rules preserved as defined in the database schema?
- [ ] Does this route enforce role authorization (client vs. advisor)?