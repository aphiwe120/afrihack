from decimal import Decimal

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from models import Agreement, Claim, FNA, FinancialProduct, Goal, Reminder, ServiceRequest, User
from schemas import (
    AdvisorDashboardResponse,
    DashboardSummaryResponse,
    FinancialProductCreate,
    FinancialProductRead,
    FinancialProductUpdate,
    ComplianceReportResponse,
    ComplianceClientStatus,
    ReminderCreate,
    ReminderRead,
    ReminderUpdate,
    GoalCreate,
    GoalRead,
    GoalUpdate,
    ServiceRequestCreate,
    ServiceRequestRead,
    ServiceRequestUpdate,
    AgreementCreate,
    AgreementRead,
    FNACreate,
    FNARead,
)
import uuid

# ==============================================================================
# APP INITIALIZATION & MIDDLEWARE
# ==============================================================================
app = FastAPI(
    title="Royal Square Financial API",
    description="FSP No: 29370 | TLS 1.3 & POPIA Compliant Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Restrict to frontend domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# CORE DEPENDENCIES (Placeholders)
# ==============================================================================
def get_db():
    """Yields SQLAlchemy database session."""
    yield "db_session_placeholder"

def get_current_user():
    """Validates JWT and returns active user (enforces RBAC)."""
    pass

# ==============================================================================
# 1. AUTHENTICATION & PROFILES
# ==============================================================================
@app.post("/auth/register", tags=["Auth"])
async def register_user(db = Depends(get_db)):

    pass

@app.post("/auth/login", tags=["Auth"])
async def login(db = Depends(get_db)):
    pass

@app.post("/auth/verify-biometrics", tags=["Auth"])
async def verify_biometrics(db = Depends(get_db)):
    pass

@app.get("/users/me", tags=["Profiles"])
async def get_my_profile(current_user = Depends(get_current_user)):
    pass

# ==============================================================================
# 2. DASHBOARDS & ASSETS
# ==============================================================================
@app.get("/dashboard/summary", tags=["Dashboard"])
def client_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardSummaryResponse:
    total_assets = db.scalar(
        select(func.coalesce(func.sum(FinancialProduct.current_value), 0)).where(
            FinancialProduct.user_id == current_user.id
        )
    )
    quick_action_count = db.scalar(
        select(func.count(Reminder.id)).where(
            Reminder.user_id == current_user.id,
            Reminder.is_resolved.is_(False),
        )
    )
    total_assets = Decimal(total_assets or 0)
    total_liabilities = Decimal("0.00")

    return DashboardSummaryResponse(
        net_worth=total_assets - total_liabilities,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        quick_action_count=quick_action_count or 0,
    )

@app.get("/advisor/dashboard", tags=["Advisor"])
def advisor_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AdvisorDashboardResponse:
    if current_user.role != "advisor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Advisor access required")

    total_clients = db.scalar(
        select(func.count(User.id)).where(User.role == "client")
    )
    assets_under_advice = db.scalar(
        select(func.coalesce(func.sum(FinancialProduct.current_value), 0))
    )
    active_claims = db.scalar(
        select(func.count(Claim.id)).where(Claim.status != "closed")
    )
    overdue_compliance = db.scalar(
        select(func.count(Reminder.id)).where(
            Reminder.is_resolved.is_(False),
            Reminder.due_date < func.now(),
        )
    )

    return AdvisorDashboardResponse(
        total_clients=total_clients or 0,
        assets_under_advice=Decimal(assets_under_advice or 0),
        active_claims=active_claims or 0,
        overdue_compliance=overdue_compliance or 0,
    )


@app.get(
    "/assets",
    response_model=list[FinancialProductRead],
    tags=["Assets"],
)
def list_assets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FinancialProduct]:
    return list(
        db.scalars(
            select(FinancialProduct)
            .where(FinancialProduct.user_id == current_user.id)
            .order_by(FinancialProduct.created_at.desc())
        ).all()
    )


@app.post(
    "/assets",
    response_model=FinancialProductRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Assets"],
)
def register_asset(
    payload: FinancialProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FinancialProduct:
    asset = FinancialProduct(user_id=current_user.id, **payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@app.get(
    "/assets/{asset_id}",
    response_model=FinancialProductRead,
    tags=["Assets"],
)
def get_asset(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FinancialProduct:
    asset = db.scalar(
        select(FinancialProduct).where(
            FinancialProduct.id == asset_id,
            FinancialProduct.user_id == current_user.id,
        )
    )
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


@app.patch(
    "/assets/{asset_id}",
    response_model=FinancialProductRead,
    tags=["Assets"],
)
def update_asset(
    asset_id: uuid.UUID,
    payload: FinancialProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FinancialProduct:
    if payload.current_value is not None and current_user.role != "advisor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advisors may update asset valuations",
        )

    asset_query = select(FinancialProduct).where(FinancialProduct.id == asset_id)
    if current_user.role != "advisor":
        asset_query = asset_query.where(FinancialProduct.user_id == current_user.id)
    asset = db.scalar(asset_query)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    return asset

# ==============================================================================
# 3. CLAIMS & INCIDENT WORKFLOW
# ==============================================================================
@app.post("/claims", tags=["Claims"])
async def create_claim_draft(current_user = Depends(get_current_user)):
    pass

@app.post("/claims/{claim_id}/media", tags=["Claims"])
async def upload_encrypted_evidence(claim_id: uuid.UUID, current_user = Depends(get_current_user)):
    pass

@app.get("/claims/{claim_id}/media/{evidence_id}", tags=["Claims"])
async def get_signed_evidence_url(claim_id: uuid.UUID, evidence_id: uuid.UUID, current_user = Depends(get_current_user)):
    pass

@app.post("/claims/{claim_id}/submit", tags=["Claims"])
async def dispatch_claim_to_insurer(claim_id: uuid.UUID, current_user = Depends(get_current_user)):
    pass

# ==============================================================================
# 4. REMINDERS & COMPLIANCE
# ==============================================================================
@app.get(
    "/reminders",
    response_model=list[ReminderRead],
    tags=["Reminders"],
)
def list_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Reminder]:
    reminder_query = select(Reminder).order_by(Reminder.due_date.asc())
    if current_user.role != "advisor":
        reminder_query = reminder_query.where(Reminder.user_id == current_user.id)
    return list(db.scalars(reminder_query).all())


@app.post(
    "/reminders",
    response_model=ReminderRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Reminders"],
)
def create_reminder(
    payload: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Reminder:
    reminder = Reminder(user_id=current_user.id, **payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@app.patch(
    "/reminders/{reminder_id}",
    response_model=ReminderRead,
    tags=["Reminders"],
)
def resolve_reminder(
    reminder_id: uuid.UUID,
    payload: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Reminder:
    reminder_query = select(Reminder).where(Reminder.id == reminder_id)
    if current_user.role != "advisor":
        reminder_query = reminder_query.where(Reminder.user_id == current_user.id)
    reminder = db.scalar(reminder_query)
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    reminder.is_resolved = payload.is_resolved
    db.commit()
    db.refresh(reminder)
    return reminder


@app.delete(
    "/reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Reminders"],
)
def delete_reminder(
    reminder_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    reminder_query = select(Reminder).where(Reminder.id == reminder_id)
    if current_user.role != "advisor":
        reminder_query = reminder_query.where(Reminder.user_id == current_user.id)
    reminder = db.scalar(reminder_query)
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    db.delete(reminder)
    db.commit()


@app.get(
    "/compliance/report",
    response_model=ComplianceReportResponse,
    tags=["Compliance"],
)
def generate_compliance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplianceReportResponse:
    if current_user.role != "advisor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Advisor access required")

    compliance_rows = db.execute(
        text(
            """
            SELECT
                u.id AS client_id,
                CASE WHEN MAX(CASE
                    WHEN a.agreement_type = 'fais_disclosure'
                        AND a.signed_at IS NOT NULL THEN 1 ELSE 0 END) = 1
                    THEN 'compliant' ELSE 'pending' END AS fais_disclosure_status,
                CASE WHEN MAX(CASE
                    WHEN a.agreement_type = 'fica'
                        AND a.signed_at IS NOT NULL THEN 1 ELSE 0 END) = 1
                    THEN 'compliant' ELSE 'pending' END AS fica_status,
                CASE WHEN MAX(CASE
                    WHEN a.agreement_type IN ('popia_consent', 'client_consent')
                        AND a.signed_at IS NOT NULL THEN 1 ELSE 0 END) = 1
                    THEN 'compliant' ELSE 'pending' END AS popia_consent_status
            FROM users AS u
            LEFT JOIN agreements AS a ON a.user_id = u.id
            WHERE u.role = 'client'
            GROUP BY u.id
            ORDER BY u.id
            """
        )
    ).mappings().all()

    clients = [ComplianceClientStatus.model_validate(row) for row in compliance_rows]
    return ComplianceReportResponse(clients=clients)

# ==============================================================================
# 5. GOALS & SERVICE REQUESTS
# ==============================================================================
@app.get(
    "/goals",
    response_model=list[GoalRead],
    tags=["Goals"],
)

def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Goal]:
    goal_query = select(Goal).where(
        (Goal.owner_id == current_user.id)
        | Goal.shared_with_user_ids.contains([current_user.id])
    )
    return list(db.scalars(goal_query.order_by(Goal.created_at.desc())).all())


@app.post(
    "/goals",
    response_model=GoalRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Goals"],
)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Goal:
    goal = Goal(owner_id=current_user.id, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@app.patch(
    "/goals/{goal_id}",
    response_model=GoalRead,
    tags=["Goals"],
)
def update_goal(
    goal_id: uuid.UUID,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Goal:
    goal = db.scalar(
        select(Goal).where(
            Goal.id == goal_id,
            (Goal.owner_id == current_user.id)
            | Goal.shared_with_user_ids.contains([current_user.id]),
        )
    )
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


@app.delete(
    "/goals/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Goals"],
)
def delete_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    goal = db.scalar(
        select(Goal).where(
            Goal.id == goal_id,
            (Goal.owner_id == current_user.id)
            | Goal.shared_with_user_ids.contains([current_user.id]),
        )
    )
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    db.delete(goal)
    db.commit()


@app.get(
    "/service-requests",
    response_model=list[ServiceRequestRead],
    tags=["Service Requests"],
)
def list_service_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ServiceRequest]:
    request_query = select(ServiceRequest).order_by(ServiceRequest.created_at.desc())
    if current_user.role != "advisor":
        request_query = request_query.where(ServiceRequest.user_id == current_user.id)
    return list(db.scalars(request_query).all())


@app.post(
    "/service-requests",
    response_model=ServiceRequestRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Service Requests"],
)
def submit_service_request(
    payload: ServiceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceRequest:
    request = ServiceRequest(
        user_id=current_user.id,
        request_type=payload.request_type.value,
        payload=payload.payload,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@app.get(
    "/service-requests/{request_id}",
    response_model=ServiceRequestRead,
    tags=["Service Requests"],
)
def get_service_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceRequest:
    request_query = select(ServiceRequest).where(ServiceRequest.id == request_id)
    if current_user.role != "advisor":
        request_query = request_query.where(ServiceRequest.user_id == current_user.id)
    request = db.scalar(request_query)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service request not found")
    return request


@app.patch(
    "/service-requests/{request_id}",
    response_model=ServiceRequestRead,
    tags=["Service Requests"],
)
def update_service_request(
    request_id: uuid.UUID,
    payload: ServiceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceRequest:
    if current_user.role != "advisor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advisors may update service request status",
        )

    request = db.scalar(
        select(ServiceRequest).where(ServiceRequest.id == request_id)
    )
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service request not found")

    request.status = payload.status.value
    db.commit()
    db.refresh(request)
    return request

# ==============================================================================
# 6. FNA & LEGAL AGREEMENTS
# ==============================================================================
@app.post(
    "/fna",
    response_model=FNARead,
    status_code=status.HTTP_201_CREATED,
    tags=["FNA"],
)
def save_fna_data(
    payload: FNACreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FNA:
    if current_user.role != "advisor" and payload.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clients may only submit their own FNA",
        )

    fna = FNA(
        client_id=payload.client_id,
        encrypted_fna_payload=payload.encrypted_fna_payload,
        encryption_iv=payload.encryption_iv,
        risk_profile_tier=payload.risk_profile_tier.value,
    )
    db.add(fna)
    db.commit()
    db.refresh(fna)
    return fna


@app.get(
    "/fna/{client_id}",
    response_model=list[FNARead],
    tags=["FNA"],
)
def get_fna_records(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FNA]:
    if current_user.role != "advisor" and client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FNA access denied")

    return list(
        db.scalars(
            select(FNA)
            .where(FNA.client_id == client_id)
            .order_by(FNA.created_at.desc())
        ).all()
    )

@app.post(
    "/agreements/sign",
    response_model=AgreementRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Agreements"],
)
def sign_legal_document(
    payload: AgreementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Agreement:
    agreement = Agreement(
        user_id=current_user.id,
        document_type=payload.document_type.value,
        signature_token=payload.signature_token,
        ip_address=str(payload.ip_address),
    )
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return agreement


@app.get(
    "/agreements",
    response_model=list[AgreementRead],
    tags=["Agreements"],
)
def list_agreements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Agreement]:
    agreement_query = select(Agreement).order_by(Agreement.signed_at.desc())
    if current_user.role != "advisor":
        agreement_query = agreement_query.where(Agreement.user_id == current_user.id)
    return list(db.scalars(agreement_query).all())