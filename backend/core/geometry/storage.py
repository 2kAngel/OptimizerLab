"""
Almacenamiento y persistencia de artefactos geométricos en disco.
"""

import os
import re
from pathlib import Path
from typing import Optional

# Directorio de almacenamiento de geometrías
STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "geometry"
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

# Expresión regular para hashes SHA-256 válidos (evita Path Traversal)
HASH_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")


def sanitize_hash(geometry_hash: str) -> str:
    """Valida y sanitiza el hash para evitar vulnerabilidades de path traversal."""
    clean_hash = geometry_hash.strip().lower()
    if not HASH_REGEX.match(clean_hash):
        raise ValueError(f"Hash geométrico inválido o no seguro: '{geometry_hash}'")
    return clean_hash


def get_artifact_path(geometry_hash: str, extension: str) -> Path:
    """Devuelve la ruta absoluta sanitizada del artefacto geométrico."""
    clean_hash = sanitize_hash(geometry_hash)
    ext = extension.lstrip(".").lower()
    if ext not in {"stl", "glb", "step", "stp", "obj", "json"}:
        raise ValueError(f"Extensión geométrica no soportada: '{extension}'")
    return STORAGE_ROOT / f"{clean_hash}.{ext}"


def store_artifact(geometry_hash: str, extension: str, data: bytes) -> Path:
    """Guarda en disco los bytes del artefacto y retorna su ruta."""
    path = get_artifact_path(geometry_hash, extension)
    with open(path, "wb") as f:
        f.write(data)
    return path


def artifact_exists(geometry_hash: str, extension: str) -> bool:
    """Comprueba si un artefacto ya existe en disco."""
    try:
        path = get_artifact_path(geometry_hash, extension)
        return path.exists() and path.stat().st_size > 0
    except ValueError:
        return False
