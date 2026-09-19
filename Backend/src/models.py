import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    String, Text, Boolean, Numeric, Date, DateTime, ForeignKey, func,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'client', 'advisor', 'admin'
    id_number: Mapped[str] = mapped_column(String(13), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    residential_address: Mapped[Optional[str]] = mapped_column(Text)
    banking_details_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    biometric_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    id_document_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    financial_products: Mapped[List["FinancialProduct"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    claims: Mapped[List["Claim"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reminders: Mapped[List["Reminder"]] = relationship(foreign_keys="Reminder.user_id", back_populates="user", cascade="all, delete-orphan")
    goals: Mapped[List["Goal"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    service_requests: Mapped[List["ServiceRequest"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    fna_records: Mapped[List["FNA"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    agreements: Mapped[List["Agreement"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class FinancialProduct(Base):
    __tablename__ = "financial_products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    policy_number: Mapped[str] = mapped_column(String(100), nullable=False)
    product_category: Mapped[str] = mapped_column(String(50), nullable=False)
    current_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    valuation_renewal_date: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="financial_products")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("financial_products.id", ondelete="SET NULL"))
    insurer_claim_number: Mapped[Optional[str]] = mapped_column(String(100))
    claims_handler_name: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default="draft")
    incident_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    incident_location: Mapped[str] = mapped_column(Text, nullable=False)
    incident_description: Mapped[str] = mapped_column(Text, nullable=False)
    police_case_number: Mapped[Optional[str]] = mapped_column(String(100))
    police_notified_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    driver_type: Mapped[str] = mapped_column(String(20), nullable=False)
    third_party_info: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="claims")
    evidence: Mapped[List["ClaimEvidence"]] = relationship(back_populates="claim", cascade="all, delete-orphan")


class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    encryption_iv: Mapped[str] = mapped_column(String(64), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    claim: Mapped["Claim"] = relationship(back_populates="evidence")


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        CheckConstraint(
            "type IN ('driving_licence_expiry', 'police_report', 'valuation_due', "
            "'annual_review', 'birthday', 'custom')",
            name="ck_reminders_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    advisor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    target_audience: Mapped[str] = mapped_column(String(20), nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(foreign_keys=[user_id], back_populates="reminders")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0.00)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    shared_with_user_ids: Mapped[List[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner: Mapped["User"] = relationship(back_populates="goals")


class ServiceRequest(Base):
    __tablename__ = "service_requests"
    __table_args__ = (
        CheckConstraint(
            "request_type IN ('change_of_address', 'bank_details', 'border_letter', "
            "'irp5', 'consultation', 'policy_document')",
            name="ck_service_requests_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="service_requests")


class FNA(Base):
    __tablename__ = "fna_records"
    __table_args__ = (
        CheckConstraint(
            "risk_profile_tier IN ('cautious', 'moderate', 'assertive')",
            name="ck_fna_records_risk_profile_tier",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    encrypted_fna_payload: Mapped[str] = mapped_column(Text, nullable=False)
    encryption_iv: Mapped[str] = mapped_column(String(128), nullable=False)
    risk_profile_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client: Mapped["User"] = relationship(back_populates="fna_records")


class Agreement(Base):
    __tablename__ = "agreements"
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('fais_disclosure', 'popia_consent', 'confidentiality')",
            name="ck_agreements_document_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    signature_token: Mapped[str] = mapped_column(Text, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    signed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="agreements")