import sys
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from main import app, get_current_user, get_db
from models import Agreement, FNA, FinancialProduct, Goal, Reminder, ServiceRequest


class FakeResult:
    def __init__(self, rows=()):
        self._rows = list(rows)

    def all(self):
        return self._rows

    def mappings(self):
        return self


class FakeDatabase:
    def __init__(self, scalar_values=(), scalar_result=None, rows=()):
        self.scalar_values = list(scalar_values)
        self.scalar_result = scalar_result
        self.rows = list(rows)
        self.added = []
        self.deleted = []

    def scalar(self, _query):
        if self.scalar_result is not None:
            return self.scalar_result
        return self.scalar_values.pop(0) if self.scalar_values else None

    def scalars(self, _query):
        return FakeResult(self.rows)

    def execute(self, _query):
        return FakeResult(self.rows)

    def add(self, instance):
        self.added.append(instance)
        if getattr(instance, "id", None) is None:
            instance.id = uuid4()
        now = datetime.now(timezone.utc)
        for field in ("created_at", "updated_at", "signed_at"):
            if hasattr(instance, field) and getattr(instance, field, None) is None:
                setattr(instance, field, now)
        if isinstance(instance, FinancialProduct) and instance.current_value is None:
            instance.current_value = Decimal("0.00")
        if isinstance(instance, Goal) and instance.current_amount is None:
            instance.current_amount = Decimal("0.00")
        if isinstance(instance, Reminder) and instance.is_resolved is None:
            instance.is_resolved = False
        if isinstance(instance, ServiceRequest) and instance.status is None:
            instance.status = "pending"

    def commit(self):
        return None

    def refresh(self, _instance):
        return None

    def delete(self, instance):
        self.deleted.append(instance)


def make_user(role="client", user_id=None):
    return SimpleNamespace(id=user_id or uuid4(), role=role)


@pytest.fixture
def client():
    user = make_user()
    database = FakeDatabase(scalar_values=[Decimal("125000.00"), 2])
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: database
    with TestClient(app) as test_client:
        yield test_client, user, database
    app.dependency_overrides.clear()


def reject_authentication():
    raise HTTPException(status_code=401, detail="Invalid JWT")


def test_dashboard_summary_success(client):
    test_client, _, _ = client
    response = test_client.get("/dashboard/summary")
    assert response.status_code == 200
    assert response.json()["net_worth"] == "125000.00"


def test_dashboard_summary_requires_authentication(client):
    test_client, _, database = client
    app.dependency_overrides[get_current_user] = reject_authentication
    response = test_client.get("/dashboard/summary")
    app.dependency_overrides[get_current_user] = lambda: make_user()
    assert response.status_code == 401
    assert database.added == []


def test_asset_creation_success(client):
    test_client, _, _ = client
    response = test_client.post(
        "/assets",
        json={
            "provider_name": "Santam",
            "policy_number": "POL-123",
            "product_category": "insurance",
            "current_value": "1500.00",
        },
    )
    assert response.status_code == 201
    assert response.json()["policy_number"] == "POL-123"


def test_claim_submission_success(client):
    test_client, _, _ = client
    response = test_client.post(f"/claims/{uuid4()}/submit")
    assert response.status_code == 200


def test_claim_submission_requires_authentication(client):
    test_client, _, _ = client
    app.dependency_overrides[get_current_user] = reject_authentication
    response = test_client.post(f"/claims/{uuid4()}/submit")
    assert response.status_code == 401


def test_reminder_creation_success(client):
    test_client, _, _ = client
    response = test_client.post(
        "/reminders",
        json={
            "type": "annual_review",
            "title": "Annual review",
            "due_date": "2026-12-01T09:00:00Z",
            "target_audience": "client",
        },
    )
    assert response.status_code == 201
    assert response.json()["type"] == "annual_review"


def test_goal_creation_success(client):
    test_client, user, _ = client
    response = test_client.post(
        "/goals",
        json={
            "title": "House deposit",
            "target_amount": "250000.00",
            "target_date": "2030-01-01",
            "is_shared": True,
            "shared_with_user_ids": [str(uuid4())],
        },
    )
    assert response.status_code == 201
    assert response.json()["owner_id"] == str(user.id)


def test_service_request_advisor_update_success(client):
    test_client, _, database = client
    advisor = make_user("advisor")
    request = ServiceRequest(
        id=uuid4(),
        user_id=uuid4(),
        request_type="consultation",
        status="pending",
        payload={"topic": "review"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    database.scalar_result = request
    app.dependency_overrides[get_current_user] = lambda: advisor
    response = test_client.patch(
        f"/service-requests/{request.id}",
        json={"status": "processing"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "processing"


def test_service_request_status_update_forbidden_for_client(client):
    test_client, _, _ = client
    response = test_client.patch(
        f"/service-requests/{uuid4()}",
        json={"status": "completed"},
    )
    assert response.status_code == 403


def test_fna_accepts_encrypted_payload(client):
    test_client, user, database = client
    encrypted_payload = "ciphertext-must-remain-unchanged"
    response = test_client.post(
        "/fna",
        json={
            "client_id": str(user.id),
            "encrypted_fna_payload": encrypted_payload,
            "encryption_iv": "0123456789abcdef",
            "risk_profile_tier": "moderate",
        },
    )
    assert response.status_code == 201
    assert isinstance(database.added[-1], FNA)
    assert database.added[-1].encrypted_fna_payload == encrypted_payload
    assert response.json()["encrypted_fna_payload"] == encrypted_payload


def test_fna_requires_authentication(client):
    test_client, user, _ = client
    app.dependency_overrides[get_current_user] = reject_authentication
    response = test_client.post(
        "/fna",
        json={
            "client_id": str(user.id),
            "encrypted_fna_payload": "ciphertext",
            "encryption_iv": "0123456789abcdef",
            "risk_profile_tier": "cautious",
        },
    )
    assert response.status_code == 401


def test_agreement_signing_success(client):
    test_client, _, database = client
    response = test_client.post(
        "/agreements/sign",
        json={
            "document_type": "fais_disclosure",
            "signature_token": "base64-or-hash",
            "ip_address": "192.0.2.10",
        },
    )
    assert response.status_code == 201
    assert isinstance(database.added[-1], Agreement)


def test_domain_two_through_six_routes_registered():
    registered = {
        (route.path, method)
        for route in app.routes
        for method in route.methods
    }
    expected = {
        ("/dashboard/summary", "GET"),
        ("/advisor/dashboard", "GET"),
        ("/assets", "GET"),
        ("/assets", "POST"),
        ("/assets/{asset_id}", "GET"),
        ("/assets/{asset_id}", "PATCH"),
        ("/claims", "POST"),
        ("/claims/{claim_id}/media", "POST"),
        ("/claims/{claim_id}/submit", "POST"),
        ("/reminders", "GET"),
        ("/reminders", "POST"),
        ("/reminders/{reminder_id}", "PATCH"),
        ("/reminders/{reminder_id}", "DELETE"),
        ("/compliance/report", "GET"),
        ("/goals", "GET"),
        ("/goals", "POST"),
        ("/goals/{goal_id}", "PATCH"),
        ("/goals/{goal_id}", "DELETE"),
        ("/service-requests", "GET"),
        ("/service-requests", "POST"),
        ("/service-requests/{request_id}", "GET"),
        ("/service-requests/{request_id}", "PATCH"),
        ("/fna", "POST"),
        ("/fna/{client_id}", "GET"),
        ("/agreements/sign", "POST"),
        ("/agreements", "GET"),
    }
    assert expected <= registered
