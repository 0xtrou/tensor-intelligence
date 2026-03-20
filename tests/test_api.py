"""Test FastAPI endpoints."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import select
from fastapi.testclient import TestClient

from src.api.main import app
from src.models.subnet import Subnet
from src.models.flow_snapshot import FlowSnapshot
from src.models.signal import Signal


def test_health_endpoint():
    """Test GET /health returns correct status."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"