"""
Pruebas del módulo de prueba de ingeniería TestBeamModule.
"""

from modules.test_module.module import TestBeamModule


def test_beam_geometry_generation_and_validation():
    module = TestBeamModule()
    
    # 1. Caso válido viga sólida
    params_valid = {
        "length": 600.0,
        "width": 40.0,
        "height": 60.0,
        "elastic_modulus": 70.0,
        "density": 2700.0,
    }
    geom = module.generate_geometry("cantilever_rectangular", params_valid)
    assert geom.is_valid is True
    assert geom.volume == 600.0 * 40.0 * 60.0
    assert geom.geometry_hash != ""

    # 2. Caso inválido: dimensiones negativas
    params_invalid = params_valid.copy()
    params_invalid["length"] = -10.0
    geom_invalid = module.generate_geometry("cantilever_rectangular", params_invalid)
    assert geom_invalid.is_valid is False
    assert len(geom_invalid.validation_messages) > 0


def test_beam_analytical_evaluation():
    module = TestBeamModule()
    params = {
        "length": 500.0,
        "width": 50.0,
        "height": 80.0,
        "elastic_modulus": 70.0,
        "density": 2700.0,
    }
    conditions = {"applied_load": 1000.0}  # 1000 N

    res = module.evaluate_fast("cantilever_rectangular", params, conditions)
    assert res.is_valid is True
    assert res.fidelity_level == "LEVEL_1_ANALYTICAL"
    assert res.convergence_status == "CONVERGED"
    assert "mass" in res.metrics
    assert "deflection" in res.metrics
    assert "max_stress" in res.metrics
    assert "natural_frequency" in res.metrics
    assert res.metrics["mass"] > 0.0
    assert res.metrics["deflection"] > 0.0
