"""
Pruebas de la Fase 2: Optimización evolutiva multi-objetivo con NSGA-II (pymoo).
Verifica la evaluación, comparación y persistencia de 100 variantes candidatas y el frente de Pareto.
"""

from backend.database.session import SessionLocal
from backend.database.models import Project, Experiment, Candidate
from backend.core.optimization.optimizer import EvolutionaryOptimizer
from backend.core.module_registry.registry import registry
from modules.test_module.module import TestBeamModule
from modules.wind_turbines.module import WindTurbineModule


def setup_module():
    try:
        registry.get_module("structural_beam")
    except KeyError:
        registry.register(TestBeamModule())

    try:
        registry.get_module("wind_turbines")
    except KeyError:
        registry.register(WindTurbineModule())


def test_evolutionary_optimization_100_candidates_acceptance():
    """
    Criterio de Aceptación Fase 2:
    Ejecutar un experimento con 100 variantes candidatas, evaluarlas,
    compararlas, persistirlas y calcular el Frente de Pareto no dominado.
    """
    db = SessionLocal()
    try:
        proj = Project(name="Test Opt Project", description="Acceptance Phase 2")
        db.add(proj)
        db.commit()

        exp = Experiment(
            project_id=proj.id,
            name="Opt 100 Variantes - Turbina Savonius",
            module_id="wind_turbines",
            family_id="savonius_vawt",
            configuration={"wind_speed": 8.5, "air_density": 1.225},
        )
        db.add(exp)
        db.commit()

        # Ejecutar optimización evolutiva con pop_size=20 y n_gen=5 (Total = 100 variantes)
        result = EvolutionaryOptimizer.run_optimization(
            db=db,
            experiment_id=exp.id,
            pop_size=20,
            n_gen=5,
            seed=42,
        )

        assert result["total_evaluated"] == 100, f"Se esperaban 100 evaluaciones, obtenidas: {result['total_evaluated']}"
        assert result["pareto_count"] > 0, "El frente de Pareto debe contener al menos un candidato óptimo."

        # Verificar que los 100 candidatos se persistieron en la base de datos
        db_candidates = db.query(Candidate).filter(Candidate.experiment_id == exp.id).all()
        assert len(db_candidates) == 100, f"Se esperaban 100 candidatos en BD, encontrados: {len(db_candidates)}"

        # Verificar que el frente de Pareto contiene parámetros válidos y métricas físicas
        pareto_front = result["pareto_front"]
        first_opt = pareto_front[0]
        assert "rotor_diameter" in first_opt["parameters"]
        assert "power_output" in first_opt["metrics"]
        assert "rotor_mass" in first_opt["metrics"]
        assert first_opt["metrics"]["power_output"] > 0.0

    finally:
        db.close()
