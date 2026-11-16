"""
Pruebas de integración de la lógica de API de DesignLab.
"""

from backend.api.app import (
    health_check,
    list_modules,
    get_module_details,
    create_project,
    create_experiment,
    submit_job,
    process_single_job,
    ProjectCreate,
    ExperimentCreate,
    JobSubmitRequest,
)
from backend.database.session import SessionLocal, init_db
from backend.core.module_registry.registry import registry
from modules.test_module.module import TestBeamModule


def setup_module():
    init_db()
    if not registry.list_modules():
        registry.register(TestBeamModule())


def test_health_check_endpoint():
    res = health_check()
    assert res["status"] == "healthy"
    assert res["service"] == "DesignLab Core API"
    assert res["modules_registered"] >= 1


def test_list_and_details_module_endpoints():
    modules = list_modules()
    assert any(m.id == "structural_beam" for m in modules)

    details = get_module_details("structural_beam")
    assert "metadata" in details
    assert len(details["families"]) >= 2
    assert "cantilever_rectangular" in details["family_details"]


def test_project_experiment_and_job_endpoints_flow():
    db = SessionLocal()
    try:
        # 1. Crear proyecto
        p_data = ProjectCreate(name="Proyecto API Flow", description="Test de flujo completo")
        proj = create_project(p_data, db)
        assert proj.id is not None
        assert proj.name == "Proyecto API Flow"

        # 2. Crear experimento
        e_data = ExperimentCreate(
            project_id=proj.id,
            name="Experimento 1",
            module_id="structural_beam",
            family_id="cantilever_rectangular",
            configuration={"applied_load": 800.0},
        )
        exp = create_experiment(e_data, db)
        assert exp.id is not None
        assert exp.module_id == "structural_beam"

        # 3. Encolar trabajo de generación de candidato
        job_req = JobSubmitRequest(
            task_type="GENERATE_CANDIDATE",
            payload={
                "experiment_id": exp.id,
                "module_id": "structural_beam",
                "family_id": "cantilever_rectangular",
                "parameters": {
                    "length": 600.0,
                    "width": 50.0,
                    "height": 70.0,
                    "elastic_modulus": 70.0,
                    "density": 2700.0,
                },
            },
        )
        job = submit_job(exp.id, job_req, db)
        assert job.id is not None
        assert job.status == "PENDING"

        # 4. Procesar el trabajo
        processed = process_single_job(job.id, db)
        assert processed.status == "COMPLETED"
        assert processed.result["is_valid"] is True
        assert "candidate_id" in processed.result
        candidate_id = processed.result["candidate_id"]

        # 5. Encolar y procesar evaluación Nivel 1 del candidato generado
        eval_job_req = JobSubmitRequest(
            task_type="EVALUATE_CANDIDATE",
            payload={
                "candidate_id": candidate_id,
                "module_id": "structural_beam",
                "family_id": "cantilever_rectangular",
                "parameters": {
                    "length": 600.0,
                    "width": 50.0,
                    "height": 70.0,
                    "elastic_modulus": 70.0,
                    "density": 2700.0,
                },
                "operating_conditions": {"applied_load": 800.0},
            },
        )
        eval_job = submit_job(exp.id, eval_job_req, db)
        processed_eval = process_single_job(eval_job.id, db)
        assert processed_eval.status == "COMPLETED"
        assert processed_eval.result["is_valid"] is True
        assert "mass" in processed_eval.result["metrics"]
        assert "deflection" in processed_eval.result["metrics"]

    finally:
        db.close()
