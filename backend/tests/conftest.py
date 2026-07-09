"""Test fixtures.

Unit tests (test_run_engine.py, test_evaluator.py, test_channel_adapters.py, test_script_generator.py)
need no fixtures from here and run fully offline — no Postgres, no network.

API tests (test_api_*.py) use `client`, which requires a running Postgres pointed at a DEDICATED
test database (never the dev/demo one — see README "Don't run pytest with the default DATABASE_URL").
"""

import os

os.environ.setdefault("APP_ENV", "test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db import Base, SessionLocal, engine, get_db
from app.dependencies import get_llm
from app.main import app
from app.services.llm_client import MockLLMProvider

TABLES = "contacts, workflow_templates, campaigns, runs, messages, tool_calls, evaluations, webhook_events, llm_call_logs"


@pytest.fixture(scope="session")
def _schema_ready():
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def db_session(_schema_ready):
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        with engine.connect() as conn:
            conn.execute(text(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE"))
            conn.commit()


@pytest.fixture
def mock_llm():
    return MockLLMProvider(responses=[])


@pytest.fixture
def client(_schema_ready, mock_llm):
    def _get_db_override():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_llm] = lambda: mock_llm
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    with engine.connect() as conn:
        conn.execute(text(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE"))
        conn.commit()
