from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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