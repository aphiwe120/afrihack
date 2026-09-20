# Royal Square Financial 
**Zero-Trust, Fully Compliant Client Onboarding & Advisor Management Platform**

Built for AfriHack 2026, Royal Square Financial bridges the gap between stringent South African financial regulations (FICA, FAIS, POPIA) and a seamless, modern user experience. The platform replaces fragmented, paper-heavy onboarding processes with an end-to-end digital pipeline, protecting both the client's data privacy and the advisor's legal compliance.

---

## 🏗️ Architecture & Compliance (The X-Factor)

This application is built on a strict zero-trust architecture, gating access to financial dashboards until regulatory compliance is mathematically proven. 

*   **FICA (Financial Intelligence Centre Act):** Integrates automated identity verification flows (via ThisIsMe mock) to process South African IDs, proof of address, and SARS tax documents before granting platform access.
*   **FAIS (Financial Advisory and Intermediary Services Act):** Utilizes Open Banking architecture (via Stitch API mock) to instantly aggregate client assets and liabilities, automatically generating a legally binding FAIS Recommendation/Advice Record. 
*   **POPIA (Protection of Personal Information Act):** Enforces explicit digital consent for data processing and automatically encrypts uploaded documents.

---

## ✨ Core Features

### 👤 Client Portal
*   **Smart Onboarding State Machine:** Prevents unauthorized dashboard access until the 3-step KYC/KYB pipeline (Identity, Profiling, Consent) is complete.
*   **Dynamic Financial Dashboard:** Displays net worth summaries, active policies, and the official FAIS Advice Record.
*   **Secure Document Vault:** Client-side encryption UI for uploading sensitive FICA documents.
*   **Wealth Tracking:** Interactive financial goal tracking with real-time compliance and advisor reminders.

### 💼 Advisor Portal
*   **HTML5 Drag-and-Drop Kanban Board:** Replaces messy spreadsheets with a visual pipeline to manage client onboarding states (Pending, Under Review, Approved).
*   **Automated Compliance Webhooks:** Moving a client card visually triggers backend state changes to secure ephemeral documents.

---

## 🛠️ Tech Stack

| Domain | Technology | Implementation Details |
| :--- | :--- | :--- |
| **Frontend** | Vanilla HTML5, CSS3, JavaScript | Lightweight, dependency-free DOM manipulation and CSS Grid/Flexbox layouts. |
| **Authentication** | Supabase Auth | Secure JWT session management, login/registration routing, and state preservation. |
| **State Management** | Local Storage API | Ephemeral session state and demo-mode routing variables. |
| **Design System** | Custom CSS Variables | Executive palette (Slate, Blue, White, Purple) ensuring visual concurrency. |

---

## 🚀 Getting Started (Local Development)

### Prerequisites
*   A modern web browser.
*   VS Code with the **Live Server** extension installed.
*   A Supabase project with an active `SUPABASE_URL` and `SUPABASE_ANON_KEY`.

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/royal-square-financial.git](https://github.com/your-username/royal-square-financial.git)