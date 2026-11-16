"""
Definición de la aplicación FastAPI y endpoints REST para DesignLab.
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from backend.database.session import get_db, init_db
from backend.database.models import Project, Experiment, Job, Candidate, Evaluation, JobStatus
from backend.core.module_registry.registry import registry
from backend.core.module_registry.models import ModuleMetadata
from backend.workers.job_queue import job_queue
from backend.core.experiment_manager.handlers import (
    handle_generate_candidate,
    handle_evaluate_candidate,
    handle_run_optimization,
)

from contextlib import asynccontextmanager
import logging

logger = logging.getLogger("designlab")

# Registrar controladores por defecto en la cola de trabajos
job_queue.register_handler("GENERATE_CANDIDATE", handle_generate_candidate)
job_queue.register_handler("EVALUATE_CANDIDATE", handle_evaluate_candidate)
job_queue.register_handler("RUN_OPTIMIZATION", handle_run_optimization)

@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Iniciando DesignLab Core Backend...")
    init_db()
    from modules.test_module.module import TestBeamModule
    from modules.wind_turbines.module import WindTurbineModule
    
    # Registrar módulos si no están registrados
    try:
        registry.get_module("structural_beam")
    except KeyError:
        registry.register(TestBeamModule())

    try:
        registry.get_module("wind_turbines")
    except KeyError:
        registry.register(WindTurbineModule())
    
    # Recuperación de jobs huérfanos
    from backend.database.session import SessionLocal
    db = SessionLocal()
    try:
        job_queue.recover_orphaned_jobs(db)
    finally:
        db.close()
    
    yield
    logger.info("Deteniendo DesignLab Backend de forma ordenada.")

app = FastAPI(
    title="DesignLab API",
    description="API de ingeniería generativa y descubrimiento de diseño",
    version="0.1.0",
    lifespan=lifespan,
)

# Permitir CORS para desarrollo con Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Esquemas de Solicitud y Respuesta ---

class ProjectCreate(BaseModel):
    name: str = Field(..., description="Nombre del proyecto")
    description: Optional[str] = Field(None, description="Descripción del proyecto")

class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: Optional[str]
    created_at: Any
    updated_at: Any

class ExperimentCreate(BaseModel):
    project_id: str
    name: str
    module_id: str
    family_id: str
    configuration: Dict[str, Any] = Field(default_factory=dict)

class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    name: str
    module_id: str
    family_id: str
    status: str
    configuration: Dict[str, Any]
    created_at: Any
    updated_at: Any

class OptimizeRequest(BaseModel):
    pop_size: int = Field(15, ge=4, le=100, description="Tamaño de la población por generación")
    n_gen: int = Field(3, ge=1, le=50, description="Número de generaciones a evolucionar")
    seed: Optional[int] = Field(None, description="Semilla determinista opcional")

class JobSubmitRequest(BaseModel):
    task_type: str
    payload: Dict[str, Any]

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    experiment_id: str
    task_type: str
    status: str
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: Any
    completed_at: Optional[Any]


# --- Endpoints ---

@app.get("/api/health")
def health_check():
    """Comprobación de salud del sistema."""
    return {
        "status": "healthy",
        "service": "DesignLab Core API",
        "version": "0.1.0",
        "modules_registered": len(registry.list_modules()),
    }


@app.get("/api/modules", response_model=List[ModuleMetadata])
def list_modules():
    """Lista todos los módulos de ingeniería cargados en el sistema."""
    return registry.list_modules()


@app.get("/api/modules/{module_id}")
def get_module_details(module_id: str):
    """Devuelve los detalles de familias, parámetros y objetivos de un módulo."""
    try:
        module = registry.get_module(module_id)
        families = module.get_design_families()
        return {
            "metadata": module.get_metadata().model_dump(),
            "families": [f.model_dump() for f in families],
            "family_details": {
                f.id: {
                    "parameters": [p.model_dump() for p in module.get_parameters(f.id)],
                    "objectives": [o.model_dump() for o in module.get_objectives(f.id)],
                    "constraints": [c.model_dump() for c in module.get_constraints(f.id)],
                }
                for f in families
            },
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")


# --- Proyectos ---

@app.post("/api/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=data.name, description=data.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/api/projects", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    db.delete(project)
    db.commit()
    return {"status": "deleted", "id": project_id}


# --- Experimentos ---

@app.post("/api/experiments", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
def create_experiment(data: ExperimentCreate, db: Session = Depends(get_db)):
    # Validar que el proyecto existe
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Validar que el módulo está registrado
    try:
        registry.get_module(data.module_id)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Módulo '{data.module_id}' no está registrado.")

    experiment = Experiment(
        project_id=data.project_id,
        name=data.name,
        module_id=data.module_id,
        family_id=data.family_id,
        configuration=data.configuration,
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


@app.get("/api/experiments/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experimento no encontrado")
    return exp


@app.get("/api/projects/{project_id}/experiments", response_model=List[ExperimentResponse])
def get_experiments_by_project(project_id: str, db: Session = Depends(get_db)):
    return db.query(Experiment).filter(Experiment.project_id == project_id).all()


# --- Jobs & Cola de Tareas ---

@app.post("/api/experiments/{experiment_id}/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def submit_job(experiment_id: str, data: JobSubmitRequest, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experimento no encontrado")

    job = job_queue.submit_job(
        db=db,
        experiment_id=experiment_id,
        task_type=data.task_type,
        payload=data.payload,
    )
    return job


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return job


@app.post("/api/jobs/{job_id}/process", response_model=JobResponse)
def process_single_job(job_id: str, db: Session = Depends(get_db)):
    """Ejecuta sincrónicamente un trabajo en cola (para pruebas o workers)."""
    job = job_queue.process_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return job


@app.post("/api/jobs/process-next", response_model=Optional[JobResponse])
def process_next_job(db: Session = Depends(get_db)):
    """Procesa el siguiente trabajo pendiente de la cola."""
    return job_queue.process_next_pending(db)


@app.post("/api/jobs/recover")
def trigger_recovery(db: Session = Depends(get_db)):
    """Dispara manualmente el protocolo de recuperación de jobs huérfanos."""
    recovered = job_queue.recover_orphaned_jobs(db)
    return {"recovered_count": recovered}


from fastapi.responses import FileResponse
from backend.core.geometry.service import GeometryService

# --- Candidatos ---

@app.get("/api/experiments/{experiment_id}/candidates")
def get_experiment_candidates(experiment_id: str, db: Session = Depends(get_db)):
    candidates = db.query(Candidate).filter(Candidate.experiment_id == experiment_id).all()
    results = []
    for c in candidates:
        evals = [
            {
                "id": ev.id,
                "fidelity": ev.fidelity_level,
                "solver": ev.solver_name,
                "status": ev.convergence_status,
                "metrics": ev.metrics,
                "time": ev.execution_time_seconds,
            }
            for ev in c.evaluations
        ]
        results.append({
            "id": c.id,
            "generation": c.generation_index,
            "index": c.candidate_index,
            "parameters": c.parameters,
            "geometry_hash": c.geometry_hash,
            "status": c.validation_status,
            "evaluations": evals,
        })
    return results


# --- Geometría y Exportación 3D ---

@app.get("/api/geometry/{geometry_hash}/glb")
def get_geometry_glb(geometry_hash: str):
    """Devuelve el binario GLB de la geometría para visualización 3D."""
    path = GeometryService.get_artifact(geometry_hash, "glb")
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Archivo GLB no encontrado.")
    return FileResponse(path, media_type="model/gltf-binary", filename=f"{geometry_hash}.glb")


@app.get("/api/geometry/{geometry_hash}/export/{file_format}")
def export_geometry(geometry_hash: str, file_format: str):
    """Descarga el archivo 3D en formato STL o GLB."""
    clean_fmt = file_format.lower().lstrip(".")
    if clean_fmt not in {"stl", "glb"}:
        raise HTTPException(status_code=400, detail="Formato de exportación no soportado. Use 'stl' o 'glb'.")

    path = GeometryService.get_artifact(geometry_hash, clean_fmt)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail=f"Archivo {clean_fmt.upper()} no disponible.")

    media_type = "model/stl" if clean_fmt == "stl" else "model/gltf-binary"
    return FileResponse(
        path,
        media_type=media_type,
        filename=f"designlab_candidate_{geometry_hash[:10]}.{clean_fmt}",
    )


# --- Optimización Evolutiva Multi-Objetivo ---

@app.post("/api/experiments/{experiment_id}/optimize", response_model=JobResponse)
def launch_optimization(experiment_id: str, data: OptimizeRequest, db: Session = Depends(get_db)):
    """Encola un trabajo de optimización evolutiva multi-objetivo con NSGA-II."""
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experimento no encontrado.")

    job = job_queue.submit_job(
        db=db,
        experiment_id=experiment_id,
        task_type="RUN_OPTIMIZATION",
        payload={
            "experiment_id": experiment_id,
            "pop_size": data.pop_size,
            "n_gen": data.n_gen,
            "seed": data.seed,
        },
    )
    return job


