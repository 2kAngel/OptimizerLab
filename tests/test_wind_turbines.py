"""
Pruebas exhaustivas de aerodinámica y geometría para múltiples familias de turbinas:
- Savonius (Eje vertical - arrastre)
- HAWT (Eje horizontal 3 palas de sustentación tipo Iberdrola)
- Esférica Omnidireccional (Cúpula urbana)
"""

from modules.wind_turbines.module import WindTurbineModule
from backend.core.geometry.storage import artifact_exists


def test_wind_turbine_metadata_and_families():
    mod = WindTurbineModule()
    meta = mod.get_metadata()
    assert meta.id == "wind_turbines"
    
    families = mod.get_design_families()
    assert len(families) == 3
    assert any(f.id == "savonius_vawt" for f in families)
    assert any(f.id == "hawt_conventional" for f in families)
    assert any(f.id == "spherical_vawt" for f in families)


def test_hawt_conventional_3_blades_geometry_and_physics():
    mod = WindTurbineModule()
    params = {
        "rotor_diameter": 2000.0,  # 2 metros de diámetro
        "blade_count": 3,
        "root_chord": 150.0,
        "pitch_angle": 5.0,
        "tower_height": 2500.0,
    }
    
    # 1. Generar geometría 3D (Buje, góndola, torre y 3 palas)
    geom = mod.generate_geometry("hawt_conventional", params)
    assert geom.is_valid is True
    assert geom.mesh_vertices_count > 0
    assert geom.mesh_faces_count > 0
    assert artifact_exists(geom.geometry_hash, "glb") is True

    # 2. Evaluación de física (Sustentación pura con BEM)
    cond = {"wind_speed": 10.0, "air_density": 1.225}
    eval_res = mod.evaluate_fast("hawt_conventional", params, cond)

    # HAWT tiene un Cp superior (~0.44 - 0.46) frente a Savonius (~0.20)
    assert eval_res.metrics["power_coefficient"] > 0.40
    # A = pi * 1^2 = 3.14 m2; P_wind = 0.5 * 1.225 * 3.14 * 1000 = 1923 W
    # Con Cp ~ 0.45 -> P_mech ~ 860 W
    assert eval_res.metrics["power_output"] > 700.0
    assert eval_res.metrics["nominal_rpm"] > 300.0  # Alta velocidad de punta


def test_spherical_vawt_geometry_and_physics():
    mod = WindTurbineModule()
    params = {
        "rotor_diameter": 1200.0,
        "blade_count": 6,
        "blade_thickness": 3.5,
        "curvature_twist": 45.0,
    }
    geom = mod.generate_geometry("spherical_vawt", params)
    assert geom.is_valid is True
    assert artifact_exists(geom.geometry_hash, "glb") is True

    cond = {"wind_speed": 8.0, "air_density": 1.225}
    eval_res = mod.evaluate_fast("spherical_vawt", params, cond)
    assert 0.25 <= eval_res.metrics["power_coefficient"] <= 0.35
