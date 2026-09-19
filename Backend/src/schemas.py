from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReminderType(str, Enum):
    DRIVING_LICENCE_EXPIRY = "driving_licence_expiry"
    POLICE_REPORT = "police_report"
    VALUATION_DUE = "valuation_due"
    ANNUAL_REVIEW = "annual_review"
    BIRTHDAY = "birthday"
    CUSTOM = "custom"


class ComplianceStatus(str, Enum):
    PENDING = "pending"
    COMPLIANT = "compliant"
    EXPIRED = "expired"
    NON_COMPLIANT = "non_compliant"


class ServiceRequestType(str, Enum):
    CHANGE_OF_ADDRESS = "change_of_address"
    BANK_DETAILS = "bank_details"
    BORDER_LETTER = "border_letter"
    IRP5 = "irp5"
    CONSULTATION = "consultation"
    POLICY_DOCUMENT = "policy_document"


class ServiceRequestStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FinancialProductCreate(BaseModel):
    """Payload for linking a financial product to the authenticated user."""

    provider_name: str = Field(min_length=1, max_length=100)
    policy_number: str = Field(min_length=1, max_length=100)
    product_category: str = Field(min_length=1, max_length=50)
    current_value: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    valuation_renewal_date: Optional[date] = None


class FinancialProductUpdate(BaseModel):
    """Partial payload for updating an existing financial product."""

    provider_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    policy_number: Optional[str] = Field(default=None, min_length=1, max_length=100)
    product_category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    current_value: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    valuation_renewal_date: Optional[date] = None


class FinancialProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    provider_name: str
    policy_number: str
    product_category: str
    current_value: Decimal
    valuation_renewal_date: Optional[date]
    created_at: datetime
    updated_at: datetime


class DashboardSummaryResponse(BaseModel):
    """Aggregate metrics returned by the client dashboard."""

    net_worth: Decimal
    total_assets: Decimal
    total_liabilities: Decimal
    quick_action_count: int = Field(ge=0)


class AdvisorDashboardResponse(BaseModel):
    """Aggregate KPIs returned by the advisor dashboard."""

    total_clients: int = Field(ge=0)
    assets_under_advice: Decimal
    active_claims: int = Field(ge=0)
    overdue_compliance: int = Field(ge=0)


class ReminderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: ReminderType
    title: str = Field(min_length=1, max_length=255)
    due_date: datetime
    target_audience: str = Field(min_length=1, max_length=20)
    advisor_id: Optional[UUID] = None


class ReminderUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_resolved: bool


class ReminderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    advisor_id: Optional[UUID]
    type: ReminderType
    title: str
    due_date: datetime
    target_audience: str
    is_resolved: bool
    created_at: datetime
    updated_at: datetime


class ComplianceClientStatus(BaseModel):
    client_id: UUID
    fais_disclosure_status: ComplianceStatus
    fica_status: ComplianceStatus
    popia_consent_status: ComplianceStatus


class ComplianceReportResponse(BaseModel):
    clients: list[ComplianceClientStatus]


class GoalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    target_amount: Decimal = Field(gt=0, decimal_places=2)
    target_date: date
    is_shared: bool = False
    shared_with_user_ids: list[UUID] = Field(default_factory=list)


class GoalUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    target_amount: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    current_amount: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    target_date: Optional[date] = None
    is_shared: Optional[bool] = None
    shared_with_user_ids: Optional[list[UUID]] = None


class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    title: str
    target_amount: Decimal
    current_amount: Decimal
    target_date: date
    is_shared: bool
    shared_with_user_ids: list[UUID]
    created_at: datetime
    updated_at: datetime


class ServiceRequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_type: ServiceRequestType
    payload: dict[str, Any] = Field(default_factory=dict)


class ServiceRequestUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ServiceRequestStatus


class ServiceRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    request_type: ServiceRequestType
    status: ServiceRequestStatus
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime