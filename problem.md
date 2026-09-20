# Royal Square Financial

## The Problem
Financial advisory is highly fragmented and inherently insecure. Advisors and clients currently share highly sensitive PII (ID numbers, bank statements) over unencrypted channels like email and WhatsApp, violating POPIA compliance and creating massive liability.

## Our Solution (The X-Factor)
Royal Square Financial is a mathematically secure, zero-trust data logistics pipeline designed specifically for the South African regulatory environment. We solve the advisor's problem of documentation first by delivering an automated, unified system[cite: 2].

*   **Integrated Onboarding:** We provide a seamless client onboarding experience that focuses entirely on the client side, eliminating manual paperwork and friction[cite: 2].
*   **Automated e-KYC Pipelines:** Natively orchestrates local identity verification by integrating with the Department of Home Affairs (DHA) Hanis database and CIPC records for instant FICA compliance.
*   **Automated System Assistance:** By replacing manual documentation processing with a secure digital pipeline, we directly answer how we assist Royal automate their most tedious, high-liability workflows[cite: 4].
*   **Client-Side Encryption:** Our FastAPI backend acts strictly as a blind courier. It never stores plaintext Financial Needs Analyses (FNAs) or unencrypted identity documents.

## Hackathon Demo Architecture (Frontend-Focused)
For the final presentation, the live API integration is temporarily bypassed in favor of a high-fidelity frontend mockup to guarantee a zero-latency, flawless execution for the judges.

*   **Mocked e-KYC Flows:** Features simulated biometric liveness spinners ("Verifying FICA details with Department of Home Affairs...") to demonstrate our local compliance engine in real-time.
*   **Simulated State Routing:** Uses `setTimeout` functions to replicate network latency, proving the UI gracefully handles asynchronous state changes without live backend bottlenecks. 
*   **Static Payload Integration:** Pre-populated JSON mock data simulates client profiles, Kanban-style service request queues, and automated AML risk scoring ("PEP & Sanctions Screened via LexisNexis"). 

## Technical Foundation (Backend)
*   **Core Stack:** FastAPI, SQLAlchemy 2.0, Supabase.
*   **Authentication:** Offloaded entirely to Supabase Auth & JWT verification (zero passwords stored or handled locally).
*   **Access Control:** Strict Role-Based Access Control (RBAC) ensuring mathematical data isolation between standard clients and advisors.
*   **Reliability:** 13/13 passing automated Pytest suite verifying the backend contract and security dependencies.