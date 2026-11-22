"""
Definición de la aplicación FastAPI y endpoints REST para DesignLab.
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
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
    from modules.traumatology_psi.module import TraumatologyPsiModule
    
    # Registrar módulos si no están registrados
    try:
        registry.get_module("structural_beam")
    except KeyError:
        registry.register(TestBeamModule())

    try:
        registry.get_module("wind_turbines")
    except KeyError:
        registry.register(WindTurbineModule())

    try:
        registry.get_module("traumatology_psi")
    except KeyError:
        registry.register(TraumatologyPsiModule())
    
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

class GenerativePromptRequest(BaseModel):
    project_id: str
    module_id: str = "wind_turbines"
    prompt: str = Field(..., min_length=3, description="Descripción del diseño o arquitectura deseada")
    scale: str = Field("domestic", description="Escala de aplicación")
    operating_conditions: Dict[str, Any] = Field(default_factory=dict)


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


# --- Ingesta de TAC / Malla Ósea (Traumatología PSI) ---

@app.post("/api/traumatology/load-sample-scan")
def load_sample_scan(family_id: str = "distal_femur_cutting_guide", is_right: bool = True):
    """Carga una anatomía ósea de referencia (fémur distal o tibia) para pruebas clínicas inmediatas."""
    from modules.traumatology_psi.bone_service import BoneAnatomyService
    from pathlib import Path
    import io

    # Priorizar mallas anatómicas de alta fidelidad NIH 3D si están disponibles
    nih_dir = Path("ImagenesTacs/DescargaMujer")
    bone_type = "tibia" if "tibia" in family_id else "femur"
    lat_prefix = "r" if is_right else "l"
    nih_file = nih_dir / f"{lat_prefix}_{bone_type}_female-nih3d.stl"

    if nih_file.exists():
        with open(nih_file, "rb") as f:
            data = f.read()
        return BoneAnatomyService.process_bone_mesh_file(data, nih_file.name)

    if "tibia" in family_id:
        bone = BoneAnatomyService.create_reference_proximal_tibia(width_ml=71.0, is_right=is_right)
        fname = f"sample_proximal_tibia_{'right' if is_right else 'left'}.stl"
    else:
        bone = BoneAnatomyService.create_reference_distal_femur(width_ml=75.0, depth_ap=58.0, is_right=is_right)
        fname = f"sample_distal_femur_{'right' if is_right else 'left'}.stl"

    buf = io.BytesIO()
    bone.export(buf, file_type="stl")
    return BoneAnatomyService.process_bone_mesh_file(buf.getvalue(), fname)


@app.post("/api/traumatology/upload-scan")
async def upload_scan(file: UploadFile = File(...)):
    """Sube y procesa una malla anatómica (STL/OBJ) o corte DICOM de un paciente."""
    from modules.traumatology_psi.bone_service import BoneAnatomyService
    contents = await file.read()
    return BoneAnatomyService.process_bone_mesh_file(contents, file.filename or "patient_scan.stl")


@app.get("/api/traumatology/download-sample-scan")
def download_sample_scan(scan_type: str = "femur", is_right: bool = True):
    """Permite al usuario descargar directamente una malla STL anatómica de paciente de muestra."""
    from modules.traumatology_psi.bone_service import BoneAnatomyService
    from pathlib import Path
    import io
    from fastapi.responses import Response

    nih_dir = Path("ImagenesTacs/DescargaMujer")
    bone_type = "tibia" if "tibia" in scan_type.lower() else "femur"
    lat_prefix = "r" if is_right else "l"
    nih_file = nih_dir / f"{lat_prefix}_{bone_type}_female-nih3d.stl"

    if nih_file.exists():
        with open(nih_file, "rb") as f:
            data = f.read()
        return Response(
            content=data,
            media_type="model/stl",
            headers={"Content-Disposition": f'attachment; filename="{nih_file.name}"'},
        )

    if "tibia" in scan_type.lower():
        bone = BoneAnatomyService.create_reference_proximal_tibia(width_ml=71.0, is_right=is_right)
        fname = f"PACIENTE_TIBIA_PROXIMAL_{'DERECHA' if is_right else 'IZQUIERDA'}.stl"
    else:
        bone = BoneAnatomyService.create_reference_distal_femur(width_ml=75.0, depth_ap=58.0, is_right=is_right)
        fname = f"PACIENTE_FEMUR_DISTAL_{'DERECHO' if is_right else 'IZQUIERDO'}.stl"

    buf = io.BytesIO()
    bone.export(buf, file_type="stl")
    return Response(
        content=buf.getvalue(),
        media_type="model/stl",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


class ClinicalDebateRequest(BaseModel):
    patient_id: str = "PACIENTE-84021"
    family_id: str = "distal_femur_cutting_guide"
    parameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    custom_query: Optional[str] = None
    use_ollama: bool = False


@app.post("/api/traumatology/clinical-debate")
def run_clinical_debate(req: ClinicalDebateRequest):
    """Ejecuta una Sesión Clínica Multidisciplinar (MiroFish) con 7 perfiles hospitalarios."""
    from modules.traumatology_psi.debate_service import ClinicalDebateService

    report = ClinicalDebateService.generate_debate(
        patient_id=req.patient_id,
        family_id=req.family_id,
        parameters=req.parameters,
        metrics=req.metrics,
        custom_query=req.custom_query,
        use_ollama=req.use_ollama,
    )
    return report.model_dump()


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


# --- Síntesis Generativa Asistida por Prompt ---

@app.post("/api/generative/prompt-design")
def generate_design_from_prompt(data: GenerativePromptRequest, db: Session = Depends(get_db)):
    """Sintetiza una arquitectura no convencional a partir de un prompt en lenguaje natural."""
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    try:
        module = registry.get_module(data.module_id)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Módulo '{data.module_id}' no encontrado.")

    try:
        synthesis = module.synthesize_from_prompt(
            prompt=data.prompt,
            scale=data.scale,
            operating_conditions=data.operating_conditions,
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en síntesis generativa: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al sintetizar diseño: {str(e)}")

    family_id = synthesis["family_id"]
    exp = (
        db.query(Experiment)
        .filter(Experiment.project_id == data.project_id, Experiment.family_id == family_id)
        .first()
    )
    if not exp:
        exp = Experiment(
            project_id=data.project_id,
            name=f"Generativo: {synthesis['family_name']}",
            module_id=data.module_id,
            family_id=family_id,
            configuration={"scale": data.scale, "source": "prompt", "prompt": data.prompt},
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)

    import uuid
    candidate = Candidate(
        id=str(uuid.uuid4()),
        experiment_id=exp.id,
        generation_index=0,
        candidate_index=len(exp.candidates) + 1,
        parameters=synthesis["parameters"],
        geometry_hash=synthesis["geometry_hash"],
        validation_status="VALID",
    )
    db.add(candidate)

    eval_rec = Evaluation(
        id=str(uuid.uuid4()),
        candidate_id=candidate.id,
        fidelity_level="LEVEL_1_ANALYTICAL",
        solver_name=f"{family_id}_generative_solver",
        convergence_status="CONVERGED",
        metrics=synthesis["metrics"],
        execution_time_seconds=0.01,
    )
    db.add(eval_rec)
    db.commit()
    db.refresh(candidate)

    return {
        "candidate": {
            "id": candidate.id,
            "generation": candidate.generation_index,
            "index": candidate.candidate_index,
            "parameters": candidate.parameters,
            "geometry_hash": candidate.geometry_hash,
            "status": candidate.validation_status,
            "evaluations": [
                {
                    "id": eval_rec.id,
                    "fidelity": eval_rec.fidelity_level,
                    "solver": eval_rec.solver_name,
                    "status": eval_rec.convergence_status,
                    "metrics": eval_rec.metrics,
                    "time": eval_rec.execution_time_seconds,
                }
            ],
        },
        "synthesis": synthesis,
    }



