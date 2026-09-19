# Royal Square Financial Frontend – AI Agent & Architecture Contract
**FSP Number:** 29370 | **Project:** Secure Client & Advisor Portal
**Target Agents:** GitHub Copilot, DeepSeek, Cursor

## 1. System Overview & AI Directives
This document is the immutable architectural contract for the Royal Square Financial frontend. As an AI assistant generating or refactoring code for this repository, you must strictly adhere to these principles. Do not suggest introducing heavy frameworks (e.g., React, Vue, Tailwind) unless explicitly requested; the current mandate is modular, high-performance vanilla HTML, CSS, and JavaScript derived from the original `royalsquare.html` prototype[cite: 5].

## 2. Security & POPIA Compliance (Non-Negotiable)
As an FSP handling highly sensitive financial and medical data (FNA, banking, ID documents), the frontend must enforce strict data protection mechanisms natively.

* **Zero Plaintext Storage:** Never write unencrypted PII (ID numbers, bank details, FNA medical data) to `localStorage`. 
* **Session Management:** Store the Supabase JWT solely in `sessionStorage`. It must be attached as a `Bearer` token to all API requests. Clear it immediately upon logout or session timeout.
* **Client-Side Encryption (Media):** All binary evidence (scene photos, licence discs) uploaded to `POST /claims/{id}/media` must be encrypted in the browser using the Web Crypto API (`AES-256-GCM`) prior to transmission. Generate a random IV per file and send it alongside the encrypted blob.
* **Pre-Signed URLs & Caching:** Media files are retrieved via short-lived (60s) signed URLs. Do not cache these URLs in long-lived state or DOM attributes (`src` must be cleared/revoked when the view unmounts).

## 3. Architecture & Modularity
The monolithic `royalsquare.html` structure[cite: 5] must be refactored into clean, separated modules. AI agents must generate code that respects this separation of concerns:

* **`/css`:** Scoped, maintainable stylesheets using the established CSS variables (`--teal`, `--ink`, `--muted`, `--paper`)[cite: 5]. Avoid inline styles.
* **`/js/api.js`:** A centralized `fetch` wrapper that automatically handles TLS 1.3 enforcement, Bearer token injection, and unified error handling/toast notifications.
* **`/js/views/`:** Dedicated render scripts for isolated domains (e.g., `dashboard.js`, `claims.js`, `fna.js`).
* **DOM Manipulation:** Use efficient, vanilla DOM APIs (`document.getElementById`, `createElement`). Avoid destructive `innerHTML` assignments where targeted text/value updates suffice, to prevent XSS vulnerabilities.

## 4. State & Role Management
The portal serves two distinct user types with strictly isolated data contexts: **Clients** and **Advisors**.

* **Role Guarding:** UI state and visible DOM nodes must be dictated by the `role` returned from `GET /users/me`. Do not rely solely on CSS (`display: none`)[cite: 5] to hide sensitive advisor features from clients; sensitive DOM elements should not be rendered or populated in the client view at all.
* **Financial Planning Logic:** The frontend must support the 4-step Financial Needs Analysis (FNA) lifecycle, including dynamic asset/liability arrays and the cryptographic signature canvas for FAIS/POPIA compliance. 

## 5. Offline-First Resiliency (Claims)
Roadside accident claims must be resilient to poor network conditions.

* **IndexedDB Drafts:** If the network is unreachable, claim workflow steps (Scene Checklist, Incident Details, Base64 Encrypted Media) must be serialized to `IndexedDB`.
* **Idempotent Sync:** Implement an event listener for `window.addEventListener('online')` that triggers a background sync queue, pushing saved drafts to `POST /claims` using idempotent request IDs.

## 6. UX & Component Standards
* **Toasts & Feedback:** All state mutations (e.g., "Goal created", "Claim submitted") must trigger the centralized toast notification system for immediate user feedback[cite: 5].
* **Forms & Validation:** Leverage native HTML5 validation (`required`, `type="datetime-local"`, `pattern`)[cite: 5] before firing API requests. Block progression in multi-step modals (like the Claim Wizard) until the current step is valid.