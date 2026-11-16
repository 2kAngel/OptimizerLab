"""
Controladores de tareas en segundo plano para el gestor de experimentos.
"""

from typing import Any, Dict
from sqlalchemy.orm import Session
from backend.core.module_registry.registry import registry
from backend.database.models import Candidate, Evaluation, Experiment


def handle_generate_candidate(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Controlador que procesa la generación y validación geométrica de un candidato."""
    experiment_id = payload["experiment_id"]
    family_id = payload["family_id"]
    module_id = payload["module_id"]
    parameters = payload["parameters"]
    generation_index = payload.get("generation_index", 0)
    candidate_index = payload.get("candidate_index", 0)

    module = registry.get_module(module_id)
    geom_output = module.generate_geometry(family_id, parameters)
    is_valid, validation_msgs = module.validate_geometry(geom_output)

    candidate = Candidate(
        experiment_id=experiment_id,
        generation_index=generation_index,
        candidate_index=candidate_index,
        parameters=parameters,
        geometry_hash=geom_output.geometry_hash,
        validation_status="VALID" if is_valid else "INVALID",
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return {
        "candidate_id": candidate.id,
        "is_valid": is_valid,
        "validation_messages": validation_msgs,
        "geometry_hash": geom_output.geometry_hash,
        "volume": geom_output.volume,
    }


def handle_evaluate_candidate(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Controlador que ejecuta la evaluación Nivel 1 de un candidato."""
    candidate_id = payload["candidate_id"]
    module_id = payload["module_id"]
    family_id = payload["family_id"]
    parameters = payload["parameters"]
    operating_conditions = payload.get("operating_conditions", {})

    module = registry.get_module(module_id)
    eval_result = module.evaluate_fast(family_id, parameters, operating_conditions)

    evaluation = Evaluation(
        candidate_id=candidate_id,
        fidelity_level=eval_result.fidelity_level,
        solver_name=eval_result.solver_name,
        convergence_status=eval_result.convergence_status,
        metrics=eval_result.metrics,
        execution_time_seconds=eval_result.execution_time_seconds,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return {
        "evaluation_id": evaluation.id,
        "metrics": eval_result.metrics,
        "convergence_status": eval_result.convergence_status,
        "execution_time_seconds": eval_result.execution_time_seconds,
        "is_valid": eval_result.is_valid,
    }


def handle_run_optimization(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Controlador que ejecuta la optimización evolutiva multi-objetivo con NSGA-II."""
    from backend.core.optimization.optimizer import EvolutionaryOptimizer

    experiment_id = payload["experiment_id"]
    pop_size = int(payload.get("pop_size", 15))
    n_gen = int(payload.get("n_gen", 4))
    raw_seed = payload.get("seed")
    seed = int(raw_seed) if raw_seed is not None else None

    return EvolutionaryOptimizer.run_optimization(
        db=db,
        experiment_id=experiment_id,
        pop_size=pop_size,
        n_gen=n_gen,
        seed=seed,
    )

