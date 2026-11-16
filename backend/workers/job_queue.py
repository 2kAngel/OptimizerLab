"""
Motor de cola de trabajos persistente en base de datos SQLite con recuperación ante fallos.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional
from sqlalchemy.orm import Session
from backend.database.models import Job, JobStatus
from backend.database.session import SessionLocal

logger = logging.getLogger("designlab.workers")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobQueueManager:
    """Gestiona el ciclo de vida de los trabajos asíncronos en base de datos."""

    def __init__(self):
        self._handlers: Dict[str, Callable[[Dict[str, Any], Session], Dict[str, Any]]] = {}

    def register_handler(
        self, task_type: str, handler: Callable[[Dict[str, Any], Session], Dict[str, Any]]
    ) -> None:
        """Registra una función para procesar un tipo de tarea determinado."""
        self._handlers[task_type] = handler

    def submit_job(
        self, db: Session, experiment_id: str, task_type: str, payload: Dict[str, Any]
    ) -> Job:
        """Crea y persiste un nuevo trabajo con estado PENDING."""
        job = Job(
            experiment_id=experiment_id,
            task_type=task_type,
            status=JobStatus.PENDING.value,
            payload=payload,
            created_at=utc_now(),
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def recover_orphaned_jobs(self, db: Session) -> int:
        """
        Escanea la cola de trabajos buscando tareas que quedaron en estado RUNNING
        debido a un cierre inesperado o caída del sistema, y las marca como FAILED_ORPHANED
        o las reencola de forma segura.
        """
        running_jobs = db.query(Job).filter(Job.status == JobStatus.RUNNING.value).all()
        recovered_count = 0
        for job in running_jobs:
            job.status = JobStatus.FAILED_ORPHANED.value
            job.error_message = (
                "El trabajo fue interrumpido abruptamente por un reinicio o caída del backend. "
                "Estado preservado para diagnóstico y reintento."
            )
            job.completed_at = utc_now()
            recovered_count += 1
        if recovered_count > 0:
            db.commit()
            logger.warning(
                f"[Recovery] Se recuperaron y protegieron {recovered_count} trabajos huérfanos."
            )
        return recovered_count

    def process_job(self, db: Session, job_id: str) -> Optional[Job]:
        """Ejecuta un trabajo específico de forma controlada y actualiza su estado."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job or job.status != JobStatus.PENDING.value:
            return job

        job.status = JobStatus.RUNNING.value
        job.heartbeat_at = utc_now()
        db.commit()

        handler = self._handlers.get(job.task_type)
        if not handler:
            job.status = JobStatus.FAILED.value
            job.error_message = f"No existe un controlador registrado para la tarea '{job.task_type}'."
            job.completed_at = utc_now()
            db.commit()
            return job

        try:
            result = handler(job.payload, db)
            job.result = result
            job.status = JobStatus.COMPLETED.value
            job.completed_at = utc_now()
        except Exception as exc:
            logger.exception(f"Error ejecutando el trabajo {job.id}: {exc}")
            job.status = JobStatus.FAILED.value
            job.error_message = str(exc)
            job.completed_at = utc_now()
        finally:
            db.commit()
            db.refresh(job)

        return job

    def process_next_pending(self, db: Session) -> Optional[Job]:
        """Obtiene y procesa el siguiente trabajo pendiente en orden FIFO."""
        job = (
            db.query(Job)
            .filter(Job.status == JobStatus.PENDING.value)
            .order_by(Job.created_at.asc())
            .first()
        )
        if job:
            return self.process_job(db, job.id)
        return None


# Instancia global del gestor de cola
job_queue = JobQueueManager()
