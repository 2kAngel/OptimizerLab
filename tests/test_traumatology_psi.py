"""
Pruebas unitarias y de integración para el módulo de Traumatología y Guías PSI (modules/traumatology_psi).
"""

import pytest
from modules.traumatology_psi.module import TraumatologyPsiModule
from backend.core.module_registry.registry import registry
from backend.core.optimization.optimizer import EvolutionaryOptimizer
from backend.database.session import SessionLocal
from backend.database.models import Project, Experiment


@pytest.fixture(scope="module")
def psi_module():
    mod = TraumatologyPsiModule()
    try:
        registry.register(mod)
    except ValueError:
        pass
    return mod


def test_traumatology_metadata_and_families(psi_module):
    meta = psi_module.get_metadata()
    assert meta.id == "traumatology_psi"
    assert "Traumatología" in meta.name

    families = psi_module.get_design_families()
    assert len(families) == 2
    f_ids = [f.id for f in families]
    assert "distal_femur_cutting_guide" in f_ids
    assert "proximal_tibia_cutting_guide" in f_ids


def test_femur_parameters_objectives_constraints(psi_module):
    params = psi_module.get_parameters("distal_femur_cutting_guide")
    param_names = [p.name for p in params]
    assert "valgus_angle" in param_names
    assert "resection_thickness" in param_names
    assert "saw_blade_thickness" in param_names
    assert "rib_count" in param_names
    assert "wall_thickness" in param_names

    objs = psi_module.get_objectives("distal_femur_cutting_guide")
    obj_names = [o.name for o in objs]
    assert "resin_volume_ml" in obj_names
    assert "blade_deflection_mm" in obj_names
    assert "stability_score" in obj_names

    constraints = psi_module.get_constraints("distal_femur_cutting_guide")
    assert len(constraints) >= 2


def test_femur_geometry_generation(psi_module):
    test_params = {
        "femur_width_ml": 72.0,
        "femur_depth_ap": 64.0,
        "valgus_angle": 5.5,
        "resection_thickness": 9.0,
        "saw_blade_thickness": 1.19,
        "pin_diameter": 3.2,
        "pin_spread": 48.0,
        "wall_thickness": 3.5,
        "rib_count": 4,
        "rib_thickness": 2.5,
        "cortical_offset": 0.15,
        "material_modulus_gpa": 2.8,
    }

    geo = psi_module.generate_geometry("distal_femur_cutting_guide", test_params)
    assert geo.is_valid is True
    assert geo.mesh_vertices_count > 100
    assert geo.mesh_faces_count > 100
    assert geo.volume > 0.0
    assert len(geo.geometry_hash) == 64
    assert len(geo.bounding_box) == 6


def test_tibia_geometry_generation(psi_module):
    test_params = {
        "tibia_plateau_width": 74.0,
        "posterior_slope": 3.0,
        "varus_valgus_angle": 0.0,
        "resection_depth": 8.0,
        "saw_blade_thickness": 1.19,
        "wall_thickness": 3.5,
        "rib_count": 3,
        "rib_thickness": 2.2,
    }

    geo = psi_module.generate_geometry("proximal_tibia_cutting_guide", test_params)
    assert geo.is_valid is True
    assert geo.volume > 0.0
    assert geo.mesh_vertices_count > 30


def test_femur_evaluation_physics(psi_module):
    test_params = {
        "femur_width_ml": 72.0,
        "wall_thickness": 3.5,
        "rib_count": 5,
        "rib_thickness": 2.5,
        "material_modulus_gpa": 2.8,
        "cortical_offset": 0.15,
    }

    res = psi_module.evaluate("distal_femur_cutting_guide", test_params)
    assert res.is_valid is True
    assert res.convergence_status == "CONVERGED"

    metrics = res.metrics
    # La deflexión debe ser inferior a 0.1 mm gracias a las nervaduras
    assert metrics["blade_deflection_mm"] < 0.10
    # Consumo de resina médica razonable (< 35 ml)
    assert metrics["resin_volume_ml"] < 35.0
    # Tiempo de impresión < 65 minutos
    assert metrics["print_time_minutes"] < 65.0
    # Estabilidad anatómica > 80 puntos
    assert metrics["stability_score"] > 80.0
    # Frecuencia natural no debe entrar en resonancia destructiva con 250 Hz
    assert metrics["frequency_safety_margin_pct"] > 10.0


def test_nsga2_optimization_on_psi_guide(psi_module):
    """Verifica que el optimizador NSGA-II puede optimizar la guía PSI en Pareto."""
    db = SessionLocal()
    try:
        proj = Project(name="Test Traumatology Project", description="Testing PSI Optimization")
        db.add(proj)
        db.commit()

        exp = Experiment(
            project_id=proj.id,
            name="Opt Femur PSI - Ribs vs Deflection",
            module_id="traumatology_psi",
            family_id="distal_femur_cutting_guide",
            configuration={"femur_width_ml": 72.0, "valgus_angle": 5.5},
        )
        db.add(exp)
        db.commit()

        # Ejecutar 20 variantes (pop=10, gen=2)
        result = EvolutionaryOptimizer.run_optimization(
            db=db,
            experiment_id=exp.id,
            pop_size=10,
            n_gen=2,
            seed=42,
        )

        assert result["total_evaluated"] >= 10
        assert result["pareto_count"] >= 1
        assert len(result["pareto_front"]) >= 1
        first_opt = result["pareto_front"][0]
        assert "blade_deflection_mm" in first_opt["metrics"]
        assert "resin_volume_ml" in first_opt["metrics"]
        assert first_opt["metrics"]["blade_deflection_mm"] > 0.0
    finally:
        db.close()


def test_embossed_3d_marking_on_guide(psi_module):
    """Verifica el grabado en relieve 3D en la guía para trazabilidad física en quirófano."""
    params = {
        "femur_width_ml": 75.0,
        "femur_depth_ap": 60.0,
        "valgus_angle": 5.5,
        "patient_id": "P1",
        "prescribed_laterality": "right",
    }
    geo = psi_module.generate_geometry("distal_femur_cutting_guide", params)
    assert geo.is_valid is True
    # La geometría con texto 3D en relieve procedural tiene suficientes vértices
    assert geo.mesh_vertices_count > 300


def test_export_surgical_pack_endpoint():
    """Verifica la generación del ZIP con todas las piezas y el informe MDR Anexo XIII."""
    import zipfile
    import io
    from backend.api.app import export_surgical_pack, ExportSurgicalPackRequest

    req_payload = ExportSurgicalPackRequest(
        patient_id="PACIENTE-01",
        dossier={
            "femurRight": {"width_ml": 72.0, "depth_ap": 50.0},
            "tibiaRight": {"width_ml": 71.0},
        },
    )

    resp = export_surgical_pack(req_payload)
    assert resp.status_code == 200
    assert resp.media_type == "application/zip"

    # Verificar contenido del ZIP
    zf = zipfile.ZipFile(io.BytesIO(resp.body))
    namelist = zf.namelist()
    assert "INSPECCION_Y_TRAZABILIDAD_MDR.txt" in namelist
    assert any("Femoral" in name for name in namelist)
    assert any("Tibial" in name for name in namelist)

    report_content = zf.read("INSPECCION_Y_TRAZABILIDAD_MDR.txt").decode("utf-8")
    assert "PACIENTE-01" in report_content
    assert "MDR 2017/745" in report_content

