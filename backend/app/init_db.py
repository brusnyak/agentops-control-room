"""Explicit dev-DB schema creation. Run with: python -m app.init_db
(Not needed for tests — conftest.py creates the test schema itself against the
dedicated test database.)"""

from app.db import Base, engine
import app.models  # noqa: F401 — registers models on Base.metadata


def init() -> None:
    Base.metadata.create_all(engine)
    print("Schema created.")


if __name__ == "__main__":
    init()
