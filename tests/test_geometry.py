"""
Pruebas del subsistema de geometría de DesignLab.
"""

import trimesh
from backend.core.geometry.validator import GeometryValidator
from backend.core.geometry.service import GeometryService
from backend.core.geometry.storage import artifact_exists, get_artifact_path
from modules.test_module.module import TestBeamModule


def test_trimesh_validation():
    # 1. Cubo cerrado y estanco
    box = trimesh.creation.box(extents=[100.0, 50.0, 30.0])
    is_valid, issues, props = GeometryValidator.validate_mesh(box)
    assert is_valid is True
    assert props.is_watertight is True
    assert abs(props.volume - (100.0 * 50.0 * 30.0)) < 1e-3

    # 2. Superficie plana abierta (un triángulo, no cerrado/no estanco)
    open_mesh = trimesh.Trimesh(vertices=[[0, 0, 0], [10, 0, 0], [0, 10, 0]], faces=[[0, 1, 2]])
    is_valid_plane, issues_plane, props_plane = GeometryValidator.validate_mesh(open_mesh)
    assert props_plane.is_watertight is False


def test_geometry_generation_and_artifact_export():
    module = TestBeamModule()
    params = {
        "length": 450.0,
        "width": 60.0,
        "height": 90.0,
        "elastic_modulus": 70.0,
        "density": 2700.0,
    }
    geom_output = module.generate_geometry("cantilever_rectangular", params)
    assert geom_output.is_valid is True
    assert geom_output.geometry_hash != ""

    # Comprobar que los artefactos GLB y STL existen en disco
    h = geom_output.geometry_hash
    assert artifact_exists(h, "glb") is True
    assert artifact_exists(h, "stl") is True

    glb_path = get_artifact_path(h, "glb")
    stl_path = get_artifact_path(h, "stl")
    assert glb_path.stat().st_size > 0
    assert stl_path.stat().st_size > 0
