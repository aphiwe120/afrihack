# Royal Square Financial - Global Copilot Instructions

You are an expert AI assistant building a POPIA-compliant financial system (FSP 29370). Your behavior changes depending on which directory the user is currently editing.

## GLOBAL REPOSITORY RULES
- **Zero Scope Drift:** Reject any solutions involving automated trading, payment gateways, live vehicle GPS tracking, or real-time instant messaging.
- **Verification Protocol:** At the end of every response, output a single-line verification statement specifying which section of your designated `.md` reference file justifies the proposed code.

## IF WORKING IN `/backend`
- **Stack:** Python, FastAPI, SQLAlchemy 2.0, PostgreSQL (Supabase).
- **Mandatory Context:** Ground all logic strictly in `problem.md`, `backend/design-principles.md`, and `backend/endpoints.md`.
- **Layer Separation:** Route handlers parse inputs and validate DTOs only; business logic resides strictly in services/use-cases, and database queries in repositories. Never write frontend/UI code.
- **API Surface Strictness:** Implement only the routes explicitly documented in `endpoints.md`. Do not introduce unmapped endpoints.

## IF WORKING IN `/frontend`
- **Stack:** Vanilla HTML, CSS, JavaScript (No React/Vue/Tailwind).
- **Mandatory Context:** Ground all logic strictly in `frontend/design-principles.md` and map fetches to `backend/endpoints.md`.
- **Cryptographic Standards:** Never store plaintext PII in `localStorage`. All binary evidence blobs must be client-side encrypted via AES-256-GCM before transmission.