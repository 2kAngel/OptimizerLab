"""
Servicio central de procesamiento y exportación de geometría.
"""

import hashlib
import trimesh
from pathlib import Path
from typing import Optional
from backend.core.geometry.base import GeometryProperties
from backend.core.geometry.validator import GeometryValidator
from backend.core.geometry.storage import store_artifact, artifact_exists, get_artifact_path


class GeometryService:
    """Gestiona la generación de mallas, validación, exportación a GLB/STL y persistencia."""

    @staticmethod
    def process_and_persist_mesh(mesh: trimesh.Trimesh, param_hash: str) -> GeometryProperties:
        """Valida una malla, calcula sus propiedades físicas y exporta artefactos STL y GLB."""
        is_valid, issues, props = GeometryValidator.validate_mesh(mesh)
        props.geometry_hash = param_hash

        # Exportar y persistir GLB (para Three.js en el frontend)
        try:
            glb_bytes = trimesh.exchange.gltf.export_glb(mesh)
            store_artifact(param_hash, "glb", glb_bytes)
        except Exception as e:
            issues.append(f"Fallo exportando a GLB: {e}")

        # Exportar y persistir STL (para impresión 3D / CAD)
        try:
            stl_bytes = trimesh.exchange.stl.export_stl(mesh)
            store_artifact(param_hash, "stl", stl_bytes)
        except Exception as e:
            issues.append(f"Fallo exportando a STL: {e}")

        return props

    @staticmethod
    def get_artifact(geometry_hash: str, extension: str) -> Optional[Path]:
        """Recupera la ruta del archivo si existe en el almacenamiento."""
        if artifact_exists(geometry_hash, extension):
            return get_artifact_path(geometry_hash, extension)
        return None
