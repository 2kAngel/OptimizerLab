"""
Configuración de fixtures para pytest con base de datos aislada en memoria.
Evita que las pruebas escriban en storage/designlab.db.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.session import Base
import backend.database.session as session_module

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def isolate_database(monkeypatch):
    """Aísla cada test en una base de datos SQLite en memoria limpia."""
    Base.metadata.drop_all(bind=TEST_ENGINE)
    Base.metadata.create_all(bind=TEST_ENGINE)

    monkeypatch.setattr(session_module, "engine", TEST_ENGINE)
    monkeypatch.setattr(session_module, "SessionLocal", TestingSessionLocal)
    yield
