"""
Validadores de integridad geométrica y física para modelos 3D.
"""

from typing import List, Tuple
import trimesh
from backend.core.geometry.base import GeometryProperties, GeometryKind


class GeometryValidator:
    """Valida la estanqueidad, solidez e integridad física de una malla 3D."""

    @staticmethod
    def validate_mesh(mesh: trimesh.Trimesh) -> Tuple[bool, List[str], GeometryProperties]:
        issues = []
        is_valid = True

        # 1. Comprobar que no esté vacía
        if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
            return False, ["La geometría no contiene vértices o caras."], GeometryProperties(is_watertight=False)

        # 2. Comprobar estanqueidad (watertight / sólido 2-manifold)
        is_watertight = bool(mesh.is_watertight)
        if not is_watertight:
            issues.append("La malla no es estanca (no es 2-manifold cerrado).")
            # No necesariamente inválida para superficies abiertas, pero se registra

        # 3. Comprobar volumen positivo
        volume = float(mesh.volume) if is_watertight else 0.0
        if is_watertight and volume <= 0.0:
            is_valid = False
            issues.append("El volumen calculado es menor o igual a cero.")

        # 4. Comprobar caras degeneradas
        valid_face_mask = mesh.nondegenerate_faces()
        degenerate_count = len(mesh.faces) - int(valid_face_mask.sum())
        if degenerate_count > 0:
            issues.append(f"Se detectaron {degenerate_count} caras degeneradas de área cero.")

        # 5. Bounding box y centro de masa
        bounds = mesh.bounds
        bbox_min = bounds[0].tolist() if bounds is not None else [0.0, 0.0, 0.0]
        bbox_max = bounds[1].tolist() if bounds is not None else [0.0, 0.0, 0.0]
        center = mesh.center_mass.tolist() if is_watertight else mesh.centroid.tolist()

        props = GeometryProperties(
            kind=GeometryKind.POLYGONAL_MESH,
            units="mm",
            volume=volume,
            surface_area=float(mesh.area),
            vertex_count=len(mesh.vertices),
            face_count=len(mesh.faces),
            is_watertight=is_watertight,
            bounding_box_min=bbox_min,
            bounding_box_max=bbox_max,
            center_of_mass=center,
        )

        return is_valid, issues, props
