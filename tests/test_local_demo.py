"""Smoke tests for the local, no-cloud Helpdesk demonstration."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ["AI_MODE"] = "fallback"
os.environ["ZENDESK_ENABLED"] = "false"
os.environ["DATA_DIR"] = str(Path(tempfile.mkdtemp()) / "helpdesk-test-data")

from fastapi.testclient import TestClient

import main
from ai.ai_pipeline import full_ticket_analysis
from backend import database


def setup_function() -> None:
    """Start each test with an empty temporary SQLite database."""
    database.Base.metadata.drop_all(bind=database.engine)
    database.init_db()


def test_fallback_classifies_an_order_ticket() -> None:
    result = full_ticket_analysis("My order has not arrived. I need tracking help.")

    assert result["category"] == "ORDER"
    assert "tracking reference" in result["response"]


def test_create_ticket_runs_local_background_analysis() -> None:
    client = TestClient(main.app)

    created = client.post(
        "/tickets", json={"message": "My order has not arrived. I need tracking help."}
    )

    assert created.status_code == 200
    ticket_id = created.json()["id"]

    saved = client.get(f"/ticket/{ticket_id}")

    assert saved.status_code == 200
    assert saved.json()["analyzed"] is True
    assert saved.json()["category"] == "ORDER"


def test_missing_ticket_returns_not_found() -> None:
    client = TestClient(main.app)

    response = client.get("/ticket/9999")

    assert response.status_code == 404
