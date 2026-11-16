"""
Pruebas de la base de datos y configuración SQLite WAL.
"""

from sqlalchemy import text
from backend.database.session import SessionLocal, init_db


def test_sqlite_wal_mode():
    init_db()
    db = SessionLocal()
    try:
        result = db.execute(text("PRAGMA journal_mode;")).scalar()
        assert str(result).lower() == "wal", f"El modo de journal esperado era 'wal', obtenido: {result}"
        
        busy_timeout = db.execute(text("PRAGMA busy_timeout;")).scalar()
        assert busy_timeout >= 5000, f"busy_timeout esperado >= 5000, obtenido: {busy_timeout}"
    finally:
        db.close()
