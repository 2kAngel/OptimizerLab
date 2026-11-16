"""
Pruebas del gestor de cola de tareas y el protocolo de recuperación tras caídas (Crash Recovery).
"""

from backend.database.session import SessionLocal, init_db
from backend.database.models import Project, Experiment, Job, JobStatus
from backend.workers.job_queue import JobQueueManager


def test_job_submission_and_execution():
    init_db()
    db = SessionLocal()
    queue = JobQueueManager()

    # Registrar handler de prueba
    queue.register_handler("TEST_ADD", lambda p, s: {"sum": p["a"] + p["b"]})

    # Crear proyecto y experimento
    proj = Project(name="Test Project")
    db.add(proj)
    db.commit()

    exp = Experiment(
        project_id=proj.id,
        name="Test Exp",
        module_id="structural_beam",
        family_id="cantilever_rectangular",
    )
    db.add(exp)
    db.commit()

    # Encolar trabajo
    job = queue.submit_job(db, exp.id, "TEST_ADD", {"a": 10, "b": 25})
    assert job.status == JobStatus.PENDING.value

    # Procesar
    processed_job = queue.process_job(db, job.id)
    assert processed_job.status == JobStatus.COMPLETED.value
    assert processed_job.result == {"sum": 35}
    db.close()


def test_crash_recovery_of_orphaned_jobs():
    """
    Simula una caída del servidor mientras un trabajo estaba en ejecución (RUNNING)
    y verifica que el protocolo de recuperación lo protege y marca como FAILED_ORPHANED.
    """
    init_db()
    db = SessionLocal()
    queue = JobQueueManager()

    proj = Project(name="Crash Test Project")
    db.add(proj)
    db.commit()

    exp = Experiment(
        project_id=proj.id,
        name="Crash Exp",
        module_id="structural_beam",
        family_id="cantilever_rectangular",
    )
    db.add(exp)
    db.commit()

    # Crear un trabajo simulando que estaba en RUNNING cuando el sistema se apagó
    orphaned_job = Job(
        experiment_id=exp.id,
        task_type="HEAVY_SIMULATION",
        status=JobStatus.RUNNING.value,
        payload={"param": 123},
    )
    db.add(orphaned_job)
    db.commit()
    db.refresh(orphaned_job)

    # Simular reinicio del backend ejecutando el protocolo de recuperación
    recovered_count = queue.recover_orphaned_jobs(db)
    assert recovered_count >= 1

    # Verificar que el trabajo huérfano cambió a FAILED_ORPHANED con diagnóstico
    db.refresh(orphaned_job)
    assert orphaned_job.status == JobStatus.FAILED_ORPHANED.value
    assert "interrumpido abruptamente por un reinicio o caída" in orphaned_job.error_message
    db.close()
