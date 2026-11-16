"""
Motor de optimización evolutiva multi-objetivo (NSGA-II) para DesignLab.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.sampling.lhs import LHS
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM

from backend.core.module_registry.registry import registry
from backend.core.optimization.problem import DesignLabOptimizationProblem
from backend.database.models import Candidate, Evaluation, Experiment, ExperimentStatus


class EvolutionaryOptimizer:
    """Ejecuta algoritmos genéticos multi-objetivo y persiste frentes de Pareto en BD."""

    @staticmethod
    def run_optimization(
        db: Session,
        experiment_id: str,
        pop_size: int = 20,
        n_gen: int = 5,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Ejecuta la optimización evolutiva para un experimento y persiste todos los candidatos.
        Total de evaluaciones = pop_size * n_gen (ej. 20 * 5 = 100 variantes).
        """
        import random
        effective_seed = seed if seed is not None else random.randint(1, 1_000_000)

        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            raise ValueError(f"Experimento '{experiment_id}' no encontrado.")

        module = registry.get_module(experiment.module_id)
        family_id = experiment.family_id
        conditions = experiment.configuration or {}

        # 1. Instanciar problema pymoo
        problem = DesignLabOptimizationProblem(
            module=module,
            family_id=family_id,
            operating_conditions=conditions,
        )

        # 2. Configurar algoritmo NSGA-II con muestreo diverso (LHS)
        algorithm = NSGA2(
            pop_size=pop_size,
            sampling=LHS(),
            crossover=SBX(prob=0.9, eta=15),
            mutation=PM(eta=20),
            eliminate_duplicates=True,
        )

        # 3. Actualizar estado de experimento
        experiment.status = ExperimentStatus.RUNNING.value
        db.commit()

        # 4. Ejecutar optimización
        res = minimize(
            problem,
            algorithm,
            ("n_gen", n_gen),
            seed=effective_seed,
            verbose=False,
        )

        # 5. Persistir todos los candidatos evaluados en la base de datos
        candidates_persisted = []
        for idx, item in enumerate(problem.evaluated_candidates):
            gen_idx = idx // pop_size
            cand_idx = idx % pop_size
            params = item["parameters"]

            # Generar geometría real y calcular hash
            geom_out = module.generate_geometry(family_id, params)

            candidate = Candidate(
                experiment_id=experiment_id,
                generation_index=gen_idx,
                candidate_index=cand_idx,
                parameters=params,
                geometry_hash=geom_out.geometry_hash,
                validation_status="VALID" if geom_out.is_valid else "INVALID",
            )
            db.add(candidate)
            db.flush()

            # Guardar evaluación
            eval_record = Evaluation(
                candidate_id=candidate.id,
                fidelity_level="LEVEL_1_ANALYTICAL",
                solver_name="evolutionary_opt_evaluator",
                convergence_status="CONVERGED",
                metrics=item["metrics"],
                execution_time_seconds=0.001,
            )
            db.add(eval_record)
            candidates_persisted.append(candidate)

        experiment.status = ExperimentStatus.COMPLETED.value
        db.commit()

        # 6. Identificar los candidatos del Frente de Pareto
        pareto_candidates = []
        if res.opt is not None and len(res.opt) > 0:
            for opt_ind in res.opt:
                # Reconstruir dict de parámetros del individuo óptimo
                opt_params = {}
                for p_idx, p_name in enumerate(problem.param_names):
                    val = float(opt_ind.X[p_idx])
                    if problem.continuous_params[p_idx].data_type == "int":
                        val = int(round(val))
                    opt_params[p_name] = val

                # Métricas
                eval_out = module.evaluate_fast(family_id, opt_params, conditions)
                geom_out = module.generate_geometry(family_id, opt_params)

                pareto_candidates.append({
                    "parameters": opt_params,
                    "metrics": eval_out.metrics,
                    "geometry_hash": geom_out.geometry_hash,
                })

        return {
            "experiment_id": experiment_id,
            "total_evaluated": len(problem.evaluated_candidates),
            "pop_size": pop_size,
            "n_gen": n_gen,
            "seed": effective_seed,
            "pareto_count": len(pareto_candidates),
            "pareto_front": pareto_candidates,
        }
