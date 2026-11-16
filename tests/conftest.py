"""
Configuración de fixtures para pytest con base de datos SQLite de prueba aislada.
Garantiza que ninguna prueba escriba jamás en storage/designlab.db.
"""

import os
from pathlib import Path

# Configurar entorno de pruebas con base de datos SQLite temporal y completamente aislada
TEST_DB_PATH = Path(__file__).resolve().parent / "test_designlab.db"
# Limpiar previo si existiera
for ext in ["", "-wal", "-shm"]:
    f = Path(f"{TEST_DB_PATH}{ext}")
    if f.exists():
        try:
            f.unlink()
        except Exception:
            pass

os.environ["DESIGNLAB_DB_PATH"] = str(TEST_DB_PATH)
os.environ["DESIGNLAB_DB_URL"] = f"sqlite:///{TEST_DB_PATH}"

import pytest
from backend.database.session import Base, engine, SessionLocal, init_db
import backend.database.session as session_module


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Inicializa la base de datos de test y la elimina al finalizar la suite."""
    init_db()
    yield
    # Limpieza final
    for ext in ["", "-wal", "-shm"]:
        f = Path(f"{TEST_DB_PATH}{ext}")
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass

