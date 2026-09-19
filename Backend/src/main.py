from decimal import Decimal

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Claim, FinancialProduct, Reminder, User
from schemas import (
    AdvisorDashboardResponse,
    DashboardSummaryResponse,
    FinancialProductCreate,
    FinancialProductRead,
    FinancialProductUpdate,
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
@app.get("/reminders", tags=["Reminders"])
async def list_reminders(current_user = Depends(get_current_user)):
    pass

@app.patch("/reminders/{reminder_id}", tags=["Reminders"])
async def resolve_reminder(reminder_id: uuid.UUID, current_user = Depends(get_current_user)):
    pass

@app.get("/compliance/report", tags=["Compliance"])
async def generate_compliance_report(current_user = Depends(get_current_user)):
    pass

# ==============================================================================
# 5. GOALS & SERVICE REQUESTS
# ==============================================================================
@app.post("/goals", tags=["Goals"])
async def create_goal(current_user = Depends(get_current_user)):
    pass

@app.post("/service-requests", tags=["Service Requests"])
async def submit_service_request(current_user = Depends(get_current_user)):
    pass

# ==============================================================================
# 6. FNA & LEGAL AGREEMENTS
# ==============================================================================
@app.post("/fna", tags=["FNA"])
async def save_fna_data(current_user = Depends(get_current_user)):
    pass

@app.post("/agreements/sign", tags=["Agreements"])
async def sign_legal_document(current_user = Depends(get_current_user)):
    pass