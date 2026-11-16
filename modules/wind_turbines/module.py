"""
Módulo de Ingeniería Eólica Experimental para DesignLab.
Soporta múltiples arquitecturas aerodinámicas:
1. Savonius (Eje vertical de arrastre)
2. HAWT Convencional (Eje horizontal tripala tipo Iberdrola)
3. Turbina Esférica Omnidireccional (Eje vertical con álabes esféricos)
"""

import hashlib
import math
import numpy as np
import trimesh
from typing import Any, List, Tuple
from backend.core.geometry.service import GeometryService
from backend.core.module_registry.base import EngineeringModule
from backend.core.module_registry.models import (
    ModuleMetadata,
    DesignFamily,
    ParameterDefinition,
    ObjectiveDefinition,
    ConstraintDefinition,
    EvaluationResult,
    GeometryOutput,
)


class WindTurbineModule(EngineeringModule):
    """Módulo de diseño y optimización de turbinas eólicas experimentales multiescala."""

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="wind_turbines",
            name="Laboratorio Experimental de Turbinas Eólicas",
            version="1.2.0",
            description="Plataforma de exploración y optimización aerodinámica para turbinas eólicas de eje vertical (Savonius, Esférica) y horizontal (HAWT clásico 3 palas).",
            author="DesignLab Engineering Team",
        )

    def get_design_families(self) -> list[DesignFamily]:
        return [
            DesignFamily(
                id="conical_drill_vane",
                name="Turbina Cónica Tipo Taladro / Broca con Veleta",
                description="Rotor cónico con estrías helicoidales ranuradas que gira horizontalmente de cara al viento como una veleta.",
            ),
            DesignFamily(
                id="savonius_vawt",
                name="Turbina Savonius (Eje Vertical - Arrastre)",
                description="Rotor de eje vertical de alta solidez, excelente auto-arranque a bajas velocidades y operación omnidireccional.",
            ),
            DesignFamily(
                id="hawt_conventional",
                name="Turbina HAWT Clásica (3 Palas - Tipo Iberdrola)",
                description="Rotor de eje horizontal tripala de sustentación pura (alta eficiencia Cp ~ 0.45, alta velocidad de punta TSR ~ 7).",
            ),
            DesignFamily(
                id="spherical_vawt",
                name="Turbina Esférica Omnidireccional (Cúpula Urbana)",
                description="Rotor esférico con álabes curvados capaz de capturar viento horizontal y corrientes verticales ascendentes.",
            ),
            DesignFamily(
                id="helical_gorlov",
                name="Turbina Gorlov Helicoidal (Eje Vertical Silencioso)",
                description="Palas helicoidales con torsión continua en 360° que eliminan vibraciones cíclicas y ruido acústico en azoteas.",
            ),
            DesignFamily(
                id="wind_lens_ducted",
                name="Turbina con Difusor Venturi (Wind Lens)",
                description="Rotor horizontal encapsulado en un difusor anular con pestaña que acelera el viento local por depresión.",
            ),
            DesignFamily(
                id="hybrid_savonius_darrieus",
                name="Turbina Híbrida Savonius-Darrieus (Doble Etapa)",
                description="Núcleo interior de arrastre Savonius para auto-arranque y palas exteriores de sustentación Darrieus para alta velocidad.",
            ),
            DesignFamily(
                id="counter_rotating_crwt",
                name="Turbina Doble Rotor Contrarrotativo (CRWT)",
                description="Dos rotores axiales en tándem girando en sentidos opuestos para recuperar la energía cinética rotacional de la estela.",
            ),
            DesignFamily(
                id="bionic_whale_tubercle",
                name="Turbina Bioinspirada (Tubérculos de Ballena)",
                description="Palas con ondulaciones sinusoidales inspiradas en la aleta de ballena jorobada para retrasar la pérdida aerodinámica.",
            ),
        ]

    def get_parameters(self, family_id: str) -> list[ParameterDefinition]:
        return self.get_parameters_for_scale(family_id, "domestic")

    def get_parameters_for_scale(self, family_id: str, scale: str = "domestic") -> list[ParameterDefinition]:
        if scale == "domestic":
            # --- ESCALA DOMÉSTICA (Casas, azoteas, huertos residenciales) ---
            # Límites realistas: Diámetro <= 1.4m, masa ligera (manejable en tejado)
            if family_id == "savonius_vawt":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro D (Doméstico)", data_type="float", min_value=300.0, max_value=1000.0, default_value=650.0, units="mm"),
                    ParameterDefinition(name="rotor_height", description="Altura H (Doméstico)", data_type="float", min_value=400.0, max_value=1400.0, default_value=1000.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de palas", data_type="int", min_value=2, max_value=3, default_value=2, units=""),
                    ParameterDefinition(name="overlap_ratio", description="Relación de solapamiento (s/d)", data_type="float", min_value=0.10, max_value=0.28, default_value=0.18, units=""),
                    ParameterDefinition(name="blade_thickness", description="Espesor del material", data_type="float", min_value=1.5, max_value=3.5, default_value=2.0, units="mm"),
                    ParameterDefinition(name="shaft_diameter", description="Diámetro eje motriz", data_type="float", min_value=20.0, max_value=40.0, default_value=25.0, units="mm"),
                ]
            elif family_id == "hawt_conventional":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro rotor D (Doméstico)", data_type="float", min_value=600.0, max_value=1800.0, default_value=1400.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de palas", data_type="int", min_value=2, max_value=4, default_value=3, units=""),
                    ParameterDefinition(name="root_chord", description="Cuerda de pala en la raíz", data_type="float", min_value=50.0, max_value=160.0, default_value=100.0, units="mm"),
                    ParameterDefinition(name="pitch_angle", description="Ángulo de pitch", data_type="float", min_value=0.0, max_value=20.0, default_value=5.0, units="deg"),
                    ParameterDefinition(name="tower_height", description="Altura de torre (Doméstico)", data_type="float", min_value=1500.0, max_value=3500.0, default_value=2500.0, units="mm"),
                ]
            elif family_id == "helical_gorlov":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro D (Doméstico)", data_type="float", min_value=400.0, max_value=1200.0, default_value=800.0, units="mm"),
                    ParameterDefinition(name="rotor_height", description="Altura H (Doméstico)", data_type="float", min_value=500.0, max_value=1400.0, default_value=1000.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de palas helicoidales", data_type="int", min_value=2, max_value=4, default_value=3, units=""),
                    ParameterDefinition(name="curvature_twist", description="Ángulo de torsión de pala", data_type="float", min_value=60.0, max_value=180.0, default_value=120.0, units="deg"),
                    ParameterDefinition(name="blade_chord", description="Cuerda del perfil", data_type="float", min_value=60.0, max_value=180.0, default_value=120.0, units="mm"),
                ]
            elif family_id == "wind_lens_ducted":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro interior D (Doméstico)", data_type="float", min_value=500.0, max_value=1300.0, default_value=1000.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de palas", data_type="int", min_value=3, max_value=5, default_value=3, units=""),
                    ParameterDefinition(name="diffuser_length", description="Longitud del carenado", data_type="float", min_value=150.0, max_value=450.0, default_value=300.0, units="mm"),
                    ParameterDefinition(name="brim_height", description="Altura pestaña posterior (brim)", data_type="float", min_value=30.0, max_value=100.0, default_value=60.0, units="mm"),
                    ParameterDefinition(name="tower_height", description="Altura mástil", data_type="float", min_value=1500.0, max_value=3200.0, default_value=2200.0, units="mm"),
                ]
            elif family_id == "hybrid_savonius_darrieus":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro exterior Darrieus", data_type="float", min_value=500.0, max_value=1200.0, default_value=900.0, units="mm"),
                    ParameterDefinition(name="rotor_height", description="Altura rotor H", data_type="float", min_value=500.0, max_value=1400.0, default_value=1100.0, units="mm"),
                    ParameterDefinition(name="inner_diameter", description="Diámetro núcleo Savonius", data_type="float", min_value=200.0, max_value=500.0, default_value=380.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Palas exteriores", data_type="int", min_value=3, max_value=3, default_value=3, units=""),
                ]
            elif family_id == "counter_rotating_crwt":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro de rotores", data_type="float", min_value=600.0, max_value=1400.0, default_value=1100.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Palas por rotor", data_type="int", min_value=3, max_value=3, default_value=3, units=""),
                    ParameterDefinition(name="rotor_spacing", description="Distancia entre rotores", data_type="float", min_value=200.0, max_value=500.0, default_value=350.0, units="mm"),
                    ParameterDefinition(name="tower_height", description="Altura de mástil", data_type="float", min_value=1500.0, max_value=3000.0, default_value=2200.0, units="mm"),
                ]
            elif family_id == "bionic_whale_tubercle":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro del rotor D", data_type="float", min_value=600.0, max_value=1500.0, default_value=1200.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de palas", data_type="int", min_value=3, max_value=4, default_value=3, units=""),
                    ParameterDefinition(name="tubercle_count", description="Número de tubérculos por pala", data_type="int", min_value=4, max_value=10, default_value=6, units=""),
                    ParameterDefinition(name="tower_height", description="Altura mástil", data_type="float", min_value=1500.0, max_value=3200.0, default_value=2200.0, units="mm"),
                ]
            elif family_id == "conical_drill_vane":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro exterior base D", data_type="float", min_value=400.0, max_value=1300.0, default_value=900.0, units="mm"),
                    ParameterDefinition(name="cone_length", description="Longitud del cono / broca", data_type="float", min_value=500.0, max_value=1600.0, default_value=1000.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de estrías ranuradas", data_type="int", min_value=3, max_value=6, default_value=4, units=""),
                    ParameterDefinition(name="tower_height", description="Altura mástil veleta", data_type="float", min_value=1500.0, max_value=3200.0, default_value=2200.0, units="mm"),
                ]

            else:
                # spherical_vawt
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro esférico D (Doméstico)", data_type="float", min_value=400.0, max_value=1300.0, default_value=900.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de álabes meridianos", data_type="int", min_value=4, max_value=8, default_value=6, units=""),
                    ParameterDefinition(name="blade_thickness", description="Espesor de los álabes", data_type="float", min_value=1.5, max_value=4.0, default_value=2.5, units="mm"),
                    ParameterDefinition(name="curvature_twist", description="Ángulo de torsión helicoidal", data_type="float", min_value=15.0, max_value=60.0, default_value=45.0, units="deg"),
                ]

        elif scale == "medium":
            # --- ESCALA MEDIANA (Naves industriales, polideportivos, parques) ---
            if family_id == "savonius_vawt":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro D (Mediano)", data_type="float", min_value=1200.0, max_value=2500.0, default_value=1800.0, units="mm"),
                    ParameterDefinition(name="rotor_height", description="Altura H (Mediano)", data_type="float", min_value=1800.0, max_value=4000.0, default_value=2800.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de palas", data_type="int", min_value=2, max_value=3, default_value=2, units=""),
                    ParameterDefinition(name="overlap_ratio", description="Relación de solapamiento", data_type="float", min_value=0.10, max_value=0.28, default_value=0.18, units=""),
                    ParameterDefinition(name="blade_thickness", description="Espesor del material", data_type="float", min_value=3.0, max_value=6.0, default_value=4.0, units="mm"),
                    ParameterDefinition(name="shaft_diameter", description="Diámetro eje motriz", data_type="float", min_value=40.0, max_value=70.0, default_value=50.0, units="mm"),
                ]
            elif family_id == "hawt_conventional":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro rotor D (Mediano)", data_type="float", min_value=2500.0, max_value=6500.0, default_value=4500.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de palas", data_type="int", min_value=2, max_value=4, default_value=3, units=""),
                    ParameterDefinition(name="root_chord", description="Cuerda de pala en la raíz", data_type="float", min_value=150.0, max_value=400.0, default_value=250.0, units="mm"),
                    ParameterDefinition(name="pitch_angle", description="Ángulo de pitch", data_type="float", min_value=0.0, max_value=25.0, default_value=5.0, units="deg"),
                    ParameterDefinition(name="tower_height", description="Altura de torre (Mediano)", data_type="float", min_value=5000.0, max_value=12000.0, default_value=8000.0, units="mm"),
                ]
            else:
                # spherical_vawt
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro esférico D (Mediano)", data_type="float", min_value=1400.0, max_value=3000.0, default_value=2200.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de álabes meridianos", data_type="int", min_value=4, max_value=8, default_value=6, units=""),
                    ParameterDefinition(name="blade_thickness", description="Espesor de los álabes", data_type="float", min_value=3.0, max_value=7.0, default_value=4.5, units="mm"),
                    ParameterDefinition(name="curvature_twist", description="Ángulo de torsión helicoidal", data_type="float", min_value=15.0, max_value=60.0, default_value=45.0, units="deg"),
                ]

        else:
            # --- GRAN ESCALA (Empresas, montes, parques eólicos — Escala Iberdrola) ---
            if family_id == "savonius_vawt":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro D (Gran Escala)", data_type="float", min_value=3000.0, max_value=7000.0, default_value=4500.0, units="mm"),
                    ParameterDefinition(name="rotor_height", description="Altura H (Gran Escala)", data_type="float", min_value=5000.0, max_value=12000.0, default_value=8000.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de palas", data_type="int", min_value=2, max_value=3, default_value=2, units=""),
                    ParameterDefinition(name="overlap_ratio", description="Relación de solapamiento", data_type="float", min_value=0.10, max_value=0.28, default_value=0.18, units=""),
                    ParameterDefinition(name="blade_thickness", description="Espesor de las palas", data_type="float", min_value=5.0, max_value=12.0, default_value=8.0, units="mm"),
                    ParameterDefinition(name="shaft_diameter", description="Diámetro eje motriz", data_type="float", min_value=80.0, max_value=180.0, default_value=120.0, units="mm"),
                ]
            elif family_id == "hawt_conventional":
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro rotor D (Gran Escala)", data_type="float", min_value=15000.0, max_value=55000.0, default_value=35000.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de palas", data_type="int", min_value=2, max_value=4, default_value=3, units=""),
                    ParameterDefinition(name="root_chord", description="Cuerda de pala en la raíz", data_type="float", min_value=800.0, max_value=2500.0, default_value=1500.0, units="mm"),
                    ParameterDefinition(name="pitch_angle", description="Ángulo de pitch", data_type="float", min_value=0.0, max_value=25.0, default_value=5.0, units="deg"),
                    ParameterDefinition(name="tower_height", description="Altura de torre (Gran Escala)", data_type="float", min_value=25000.0, max_value=75000.0, default_value=50000.0, units="mm"),
                ]
            else:
                return [
                    ParameterDefinition(name="rotor_diameter", description="Diámetro esférico D (Gran Escala)", data_type="float", min_value=3000.0, max_value=7500.0, default_value=5000.0, units="mm"),
                    ParameterDefinition(name="blade_count", description="Número de álabes meridianos", data_type="int", min_value=4, max_value=8, default_value=6, units=""),
                    ParameterDefinition(name="blade_thickness", description="Espesor de los álabes", data_type="float", min_value=5.0, max_value=12.0, default_value=8.0, units="mm"),
                    ParameterDefinition(name="curvature_twist", description="Ángulo de torsión", data_type="float", min_value=15.0, max_value=60.0, default_value=45.0, units="deg"),
                ]

    def get_objectives(self, family_id: str) -> list[ObjectiveDefinition]:
        return [
            ObjectiveDefinition(name="power_output", description="Potencia mecánica generada a velocidad de diseño", direction="maximize", units="W"),
            ObjectiveDefinition(name="power_coefficient", description="Coeficiente de rendimiento aerodinámico (Cp)", direction="maximize", units=""),
            ObjectiveDefinition(name="rotor_mass", description="Masa total del conjunto (palas, buje, eje)", direction="minimize", units="kg"),
            ObjectiveDefinition(name="starting_torque", description="Par disponible para autoarranque a baja velocidad", direction="maximize", units="N·m"),
        ]

    def get_constraints(self, family_id: str) -> list[ConstraintDefinition]:
        return self.get_constraints_for_scale(family_id, "domestic")

    def get_constraints_for_scale(self, family_id: str, scale: str = "domestic") -> list[ConstraintDefinition]:
        base_constraints = [
            ConstraintDefinition(name="max_stress", description="Tensión máxima admisible", constraint_type="lte", limit_value=200.0, units="MPa"),
            ConstraintDefinition(name="cut_in_wind_speed", description="Velocidad de viento de arranque", constraint_type="lte", limit_value=4.0, units="m/s"),
        ]
        if scale == "domestic":
            # Límites realistas de instalación residencial en azotea o poste de jardín:
            # 1. Masa máxima del conjunto <= 25 kg (instalable por 1 o 2 personas sin grúa y seguro en forjado residencial)
            # 2. Par de arranque <= 12 N·m (para no transmitir momentos torsionales peligrosos al anclaje de la cubierta)
            base_constraints.extend([
                ConstraintDefinition(name="rotor_mass", description="Masa máxima admisible en azotea doméstica", constraint_type="lte", limit_value=25.0, units="kg"),
                ConstraintDefinition(name="starting_torque", description="Límite seguro de par en mástil residencial", constraint_type="lte", limit_value=12.0, units="N·m"),
            ])
        elif scale == "medium":
            base_constraints.extend([
                ConstraintDefinition(name="rotor_mass", description="Masa máxima para naves y parques", constraint_type="lte", limit_value=180.0, units="kg"),
                ConstraintDefinition(name="starting_torque", description="Par admisible en estructura comercial", constraint_type="lte", limit_value=100.0, units="N·m"),
            ])
        return base_constraints

    def generate_geometry(self, family_id: str, parameters: dict[str, Any]) -> GeometryOutput:
        d_mm = float(parameters.get("rotor_diameter", 1000.0))
        param_repr = f"{family_id}_" + "_".join(f"{k}:{v}" for k, v in sorted(parameters.items()))
        geom_hash = hashlib.sha256(param_repr.encode()).hexdigest()

        meshes = []

        if family_id == "hawt_conventional":
            # --- HAWT CLÁSICO TRIPALA (Tipo Iberdrola) ---
            blade_count = int(parameters.get("blade_count", 3))
            root_chord = float(parameters.get("root_chord", 150.0))
            tower_h = float(parameters.get("tower_height", 2500.0))
            rotor_radius = d_mm / 2.0
            hub_radius = rotor_radius * 0.12

            # 1. Torre soporte
            tower_mesh = trimesh.creation.cylinder(radius=hub_radius * 1.2, height=tower_h, sections=32)
            tower_mesh.apply_translation([0.0, 0.0, tower_h / 2.0])
            meshes.append(tower_mesh)

            # 2. Góndola (Nacelle)
            nacelle_length = hub_radius * 3.5
            nacelle_mesh = trimesh.creation.cylinder(radius=hub_radius * 1.1, height=nacelle_length, sections=24)
            rot_y = trimesh.transformations.rotation_matrix(math.pi / 2.0, [0, 1, 0])
            nacelle_mesh.apply_transform(rot_y)
            nacelle_mesh.apply_translation([nacelle_length * 0.3, 0.0, tower_h])
            meshes.append(nacelle_mesh)

            # 3. Buje cónico (Hub)
            hub_mesh = trimesh.creation.cone(radius=hub_radius, height=hub_radius * 1.5, sections=32)
            rot_hub = trimesh.transformations.rotation_matrix(-math.pi / 2.0, [0, 1, 0])
            hub_mesh.apply_transform(rot_hub)
            hub_mesh.apply_translation([nacelle_length * 0.8 + hub_radius * 0.75, 0.0, tower_h])
            meshes.append(hub_mesh)

            # 3.5 Timón / Veleta de cola (Tail Vane) para auto-orientación con el viento
            tail_boom_len = rotor_radius * 0.75
            tail_boom = trimesh.creation.cylinder(radius=hub_radius * 0.22, height=tail_boom_len, sections=16)
            rot_boom = trimesh.transformations.rotation_matrix(math.pi / 2.0, [0, 1, 0])
            tail_boom.apply_transform(rot_boom)
            tail_boom.apply_translation([-tail_boom_len / 2.0 - nacelle_length * 0.15, 0.0, tower_h])
            meshes.append(tail_boom)

            vane_h = rotor_radius * 0.45
            vane_w = rotor_radius * 0.35
            vane_th = hub_radius * 0.12
            tail_vane = trimesh.creation.box(extents=[vane_w, vane_th, vane_h])
            tail_vane.apply_translation([-tail_boom_len - nacelle_length * 0.15, 0.0, tower_h + vane_h * 0.25])
            meshes.append(tail_vane)

            # 4. Palas con perfil y cuerda ahusada
            blade_len = rotor_radius - hub_radius
            hub_center_x = nacelle_length * 0.8

            for i in range(blade_count):
                angle = (2.0 * math.pi / blade_count) * i

                # Aproximar la pala con secciones ahusadas tipo ala
                sections = 8
                blade_segs = []
                for s in range(sections):
                    frac = s / float(sections)
                    seg_r = hub_radius + frac * blade_len
                    chord = root_chord * (1.0 - 0.65 * frac)
                    thickness = chord * 0.16
                    seg_h = blade_len / float(sections)

                    seg = trimesh.creation.box(extents=[chord, thickness, seg_h])
                    # Pitch / torsión de la pala
                    twist = math.radians(12.0 * (1.0 - frac))
                    rot_pitch = trimesh.transformations.rotation_matrix(twist, [0, 0, 1])
                    seg.apply_transform(rot_pitch)
                    seg.apply_translation([0.0, 0.0, seg_r + seg_h / 2.0])
                    blade_segs.append(seg)

                one_blade = trimesh.util.concatenate(blade_segs)
                # Rotar al plano del rotor (YZ) y girar al ángulo correspondiente
                rot_blade_angle = trimesh.transformations.rotation_matrix(angle, [1, 0, 0])
                one_blade.apply_transform(rot_blade_angle)
                one_blade.apply_translation([hub_center_x, 0.0, tower_h])
                meshes.append(one_blade)

        elif family_id == "spherical_vawt":
            # --- TURBINA ESFÉRICA OMNIDIRECCIONAL ---
            blade_count = int(parameters.get("blade_count", 6))
            t_mm = float(parameters.get("blade_thickness", 3.5))
            radius = d_mm / 2.0

            # 1. Eje central
            shaft_mesh = trimesh.creation.cylinder(radius=radius * 0.05, height=d_mm * 1.2, sections=24)
            shaft_mesh.apply_translation([0.0, 0.0, d_mm * 0.6])
            meshes.append(shaft_mesh)

            # 2. Álabes curvados sobre la esfera
            for i in range(blade_count):
                meridian_angle = (2.0 * math.pi / blade_count) * i
                pts_count = 14
                blade_segs = []
                for p in range(pts_count):
                    phi = math.pi * (p / float(pts_count - 1))  # de 0 (polo norte) a pi (polo sur)
                    z = radius * math.cos(phi) + radius
                    r_slice = radius * math.sin(phi)
                    seg_len = (radius * math.pi / pts_count) * 1.1

                    seg = trimesh.creation.box(extents=[seg_len, t_mm, radius * 0.18])
                    rot_phi = trimesh.transformations.rotation_matrix(phi, [0, 1, 0])
                    seg.apply_transform(rot_phi)
                    seg.apply_translation([r_slice, 0.0, z])
                    blade_segs.append(seg)

                one_meridian = trimesh.util.concatenate(blade_segs)
                rot_meridian = trimesh.transformations.rotation_matrix(meridian_angle, [0, 0, 1])
                one_meridian.apply_transform(rot_meridian)
                meshes.append(one_meridian)

        elif family_id == "helical_gorlov":
            # --- TURBINA HELICOIDAL GORLOV (Eje vertical de torsión continua) ---
            h_mm = float(parameters.get("rotor_height", 1100.0))
            blade_count = int(parameters.get("blade_count", 3))
            twist_deg = float(parameters.get("curvature_twist", 120.0))
            radius = d_mm / 2.0
            chord = float(parameters.get("blade_chord", radius * 0.25))

            # 1. Eje central motriz
            shaft_mesh = trimesh.creation.cylinder(radius=radius * 0.05, height=h_mm * 1.15, sections=24)
            shaft_mesh.apply_translation([0.0, 0.0, h_mm / 2.0])
            meshes.append(shaft_mesh)

            # 2. Palas helicoidales y brazos de soporte radiales
            for b in range(blade_count):
                base_angle = (2.0 * math.pi / blade_count) * b
                n_segs = 14
                blade_segs = []
                for s in range(n_segs):
                    t = s / float(n_segs - 1)
                    z = t * h_mm
                    ang = base_angle + math.radians(twist_deg) * t
                    x = radius * math.cos(ang)
                    y = radius * math.sin(ang)
                    seg = trimesh.creation.box(extents=[chord, 4.0, (h_mm / n_segs) * 1.1])
                    rot_z = trimesh.transformations.rotation_matrix(ang + math.pi / 2.0, [0, 0, 1])
                    seg.apply_transform(rot_z)
                    seg.apply_translation([x, y, z])
                    blade_segs.append(seg)
                one_blade = trimesh.util.concatenate(blade_segs)
                meshes.append(one_blade)

                # Brazos de soporte en extremos y centro
                for arm_z in [15.0, h_mm / 2.0, h_mm - 15.0]:
                    arm_t = arm_z / h_mm
                    arm_ang = base_angle + math.radians(twist_deg) * arm_t
                    arm = trimesh.creation.box(extents=[radius, 14.0, 8.0])
                    arm.apply_translation([radius / 2.0, 0.0, 0.0])
                    rot_arm = trimesh.transformations.rotation_matrix(arm_ang, [0, 0, 1])
                    arm.apply_transform(rot_arm)
                    arm.apply_translation([0.0, 0.0, arm_z])
                    meshes.append(arm)

        elif family_id == "wind_lens_ducted":
            # --- TURBINA CON DIFUSOR VENTURI / WIND LENS ---
            tower_h = float(parameters.get("tower_height", 2200.0))
            rotor_radius = d_mm / 2.0
            blade_count = int(parameters.get("blade_count", 3))
            diff_len = float(parameters.get("diffuser_length", rotor_radius * 0.5))
            brim_h = float(parameters.get("brim_height", rotor_radius * 0.12))
            hub_radius = rotor_radius * 0.15

            # Torre y góndola
            tower = trimesh.creation.cylinder(radius=hub_radius * 0.9, height=tower_h, sections=24)
            tower.apply_translation([0.0, 0.0, tower_h / 2.0])
            meshes.append(tower)

            nacelle = trimesh.creation.cylinder(radius=hub_radius * 1.1, height=diff_len * 1.2, sections=24)
            rot_y = trimesh.transformations.rotation_matrix(math.pi / 2.0, [0, 1, 0])
            nacelle.apply_transform(rot_y)
            nacelle.apply_translation([0.0, 0.0, tower_h])
            meshes.append(nacelle)

            # Buje
            hub = trimesh.creation.cone(radius=hub_radius, height=hub_radius * 1.8, sections=24)
            rot_hub = trimesh.transformations.rotation_matrix(-math.pi / 2.0, [0, 1, 0])
            hub.apply_transform(rot_hub)
            hub.apply_translation([diff_len * 0.4, 0.0, tower_h])
            meshes.append(hub)

            # Palas
            for i in range(blade_count):
                ang = (2.0 * math.pi / blade_count) * i
                blade = trimesh.creation.box(extents=[rotor_radius * 0.14, rotor_radius, 4.0])
                blade.apply_translation([0.0, rotor_radius / 2.0, 0.0])
                rot_blade = trimesh.transformations.rotation_matrix(ang, [1, 0, 0])
                blade.apply_transform(rot_blade)
                blade.apply_translation([diff_len * 0.35, 0.0, tower_h])
                meshes.append(blade)

            # Anillo Difusor (Carenado Venturi)
            r_diff = rotor_radius * 1.15
            shroud = trimesh.creation.cylinder(radius=r_diff, height=diff_len, sections=36)
            shroud.apply_transform(rot_y)
            shroud.apply_translation([0.0, 0.0, tower_h])
            meshes.append(shroud)

            # Pestaña exterior (Brim) que genera vórtices posteriores
            brim = trimesh.creation.cylinder(radius=r_diff + brim_h, height=8.0, sections=36)
            brim.apply_transform(rot_y)
            brim.apply_translation([-diff_len / 2.0, 0.0, tower_h])
            meshes.append(brim)

        elif family_id == "hybrid_savonius_darrieus":
            # --- TURBINA HÍBRIDA DOBLE ETAPA ---
            h_mm = float(parameters.get("rotor_height", 1100.0))
            inner_d = float(parameters.get("inner_diameter", d_mm * 0.42))
            radius = d_mm / 2.0
            inner_r = inner_d / 2.0

            # Eje central
            shaft = trimesh.creation.cylinder(radius=radius * 0.06, height=h_mm * 1.15, sections=24)
            shaft.apply_translation([0.0, 0.0, h_mm / 2.0])
            meshes.append(shaft)

            # Núcleo interior Savonius (arranque)
            s_mesh1 = trimesh.creation.cylinder(radius=inner_r / 2.0, height=h_mm * 0.7, sections=24)
            s_mesh1.apply_translation([inner_r / 2.0, 0.0, h_mm / 2.0])
            meshes.append(s_mesh1)
            s_mesh2 = trimesh.creation.cylinder(radius=inner_r / 2.0, height=h_mm * 0.7, sections=24)
            s_mesh2.apply_translation([-inner_r / 2.0, 0.0, h_mm / 2.0])
            meshes.append(s_mesh2)

            # 3 Palas aerodinámicas Darrieus exteriores (alta velocidad)
            for i in range(3):
                ang = (2.0 * math.pi / 3.0) * i
                blade = trimesh.creation.box(extents=[radius * 0.16, 6.0, h_mm])
                rot_b = trimesh.transformations.rotation_matrix(ang + math.pi / 2.0, [0, 0, 1])
                blade.apply_transform(rot_b)
                blade.apply_translation([radius * math.cos(ang), radius * math.sin(ang), h_mm / 2.0])
                meshes.append(blade)

                # Brazos de conexión
                arm = trimesh.creation.box(extents=[radius, 12.0, 6.0])
                arm.apply_translation([radius / 2.0, 0.0, 0.0])
                rot_arm = trimesh.transformations.rotation_matrix(ang, [0, 0, 1])
                arm.apply_transform(rot_arm)
                arm.apply_translation([0.0, 0.0, h_mm - 20.0])
                meshes.append(arm)
                arm2 = arm.copy()
                arm2.apply_translation([0.0, 0.0, 40.0 - h_mm])
                meshes.append(arm2)

        elif family_id == "counter_rotating_crwt":
            # --- DOBLE ROTOR AXIAL CONTRARROTATIVO ---
            tower_h = float(parameters.get("tower_height", 2200.0))
            rotor_radius = d_mm / 2.0
            rotor_gap = float(parameters.get("rotor_spacing", rotor_radius * 0.4))
            hub_r = rotor_radius * 0.12

            # Torre y góndola tándem
            tower = trimesh.creation.cylinder(radius=hub_r * 0.9, height=tower_h, sections=24)
            tower.apply_translation([0.0, 0.0, tower_h / 2.0])
            meshes.append(tower)

            nacelle_len = rotor_gap * 2.2
            nacelle = trimesh.creation.cylinder(radius=hub_r * 1.1, height=nacelle_len, sections=24)
            rot_y = trimesh.transformations.rotation_matrix(math.pi / 2.0, [0, 1, 0])
            nacelle.apply_transform(rot_y)
            nacelle.apply_translation([0.0, 0.0, tower_h])
            meshes.append(nacelle)

            # Rotor 1 (Frontal)
            for i in range(3):
                ang = (2.0 * math.pi / 3.0) * i
                blade1 = trimesh.creation.box(extents=[rotor_radius * 0.12, rotor_radius, 4.0])
                blade1.apply_translation([0.0, rotor_radius / 2.0, 0.0])
                rot1 = trimesh.transformations.rotation_matrix(ang, [1, 0, 0])
                blade1.apply_transform(rot1)
                blade1.apply_translation([rotor_gap * 0.7, 0.0, tower_h])
                meshes.append(blade1)

            # Rotor 2 (Trasero en sentido inverso)
            for i in range(3):
                ang = (2.0 * math.pi / 3.0) * i + math.pi / 3.0
                blade2 = trimesh.creation.box(extents=[rotor_radius * 0.11, rotor_radius * 0.92, 4.0])
                blade2.apply_translation([0.0, (rotor_radius * 0.92) / 2.0, 0.0])
                rot2 = trimesh.transformations.rotation_matrix(ang, [1, 0, 0])
                blade2.apply_transform(rot2)
                blade2.apply_translation([-rotor_gap * 0.7, 0.0, tower_h])
                meshes.append(blade2)

        elif family_id == "bionic_whale_tubercle":
            # --- PALAS BIOINSPIRADAS CON TUBÉRCULOS ---
            tower_h = float(parameters.get("tower_height", 2200.0))
            rotor_radius = d_mm / 2.0
            hub_r = rotor_radius * 0.12
            tubercle_count = int(parameters.get("tubercle_count", 6))

            tower = trimesh.creation.cylinder(radius=hub_r * 0.9, height=tower_h, sections=24)
            tower.apply_translation([0.0, 0.0, tower_h / 2.0])
            meshes.append(tower)

            nacelle = trimesh.creation.cylinder(radius=hub_r * 1.1, height=rotor_radius * 0.6, sections=24)
            rot_y = trimesh.transformations.rotation_matrix(math.pi / 2.0, [0, 1, 0])
            nacelle.apply_transform(rot_y)
            nacelle.apply_translation([0.0, 0.0, tower_h])
            meshes.append(nacelle)

            # 3 Palas con tubérculos sinusoidales
            for i in range(3):
                ang = (2.0 * math.pi / 3.0) * i
                blade_base = trimesh.creation.box(extents=[rotor_radius * 0.14, rotor_radius, 4.0])
                blade_base.apply_translation([0.0, rotor_radius / 2.0, 0.0])
                
                # Nódulos en el borde de ataque
                nodules = []
                for n in range(tubercle_count):
                    y_pos = hub_r + (rotor_radius - hub_r) * (n / float(tubercle_count))
                    nodule = trimesh.creation.icosphere(radius=rotor_radius * 0.025, subdivisions=1)
                    nodule.apply_translation([rotor_radius * 0.07, y_pos, 0.0])
                    nodules.append(nodule)
                one_blade = trimesh.util.concatenate([blade_base] + nodules)
                rot_b = trimesh.transformations.rotation_matrix(ang, [1, 0, 0])
                one_blade.apply_transform(rot_b)
                one_blade.apply_translation([rotor_radius * 0.25, 0.0, tower_h])
                meshes.append(one_blade)

        elif family_id == "conical_drill_vane":
            # --- TURBINA CÓNICA TIPO TALADRO / BROCA CON VELETA ---
            tower_h = float(parameters.get("tower_height", 2200.0))
            rotor_radius = d_mm / 2.0
            cone_len = float(parameters.get("cone_length", rotor_radius * 2.2))
            cyl_len = rotor_radius * 0.9
            flute_count = int(parameters.get("blade_count", 4))
            twist_turns = float(parameters.get("twist_turns", 1.0))
            rot_y = trimesh.transformations.rotation_matrix(math.pi / 2.0, [0, 1, 0])

            # 1. Torre y rótula de giro (Yaw swivel tipo veleta)
            tower = trimesh.creation.cylinder(radius=rotor_radius * 0.12, height=tower_h, sections=24)
            tower.apply_translation([0.0, 0.0, tower_h / 2.0])
            meshes.append(tower)

            swivel = trimesh.creation.cylinder(radius=rotor_radius * 0.2, height=rotor_radius * 0.35, sections=24)
            swivel.apply_translation([0.0, 0.0, tower_h])
            meshes.append(swivel)

            # 2. Núcleo cónico frontal (la punta de broca taladro apuntando al viento en -X)
            cone_core = trimesh.creation.cone(radius=rotor_radius * 0.85, height=cone_len, sections=36)
            rot_cone = trimesh.transformations.rotation_matrix(-math.pi / 2.0, [0, 1, 0])
            cone_core.apply_transform(rot_cone)
            cone_core.apply_translation([-cone_len / 2.0, 0.0, tower_h])
            meshes.append(cone_core)

            # 3. Estrías y orificios helicoidales ranurados a lo largo del cono
            n_segs = 18
            for f in range(flute_count):
                base_ang = (2.0 * math.pi / flute_count) * f
                flute_segs = []
                for s in range(n_segs):
                    t = s / float(n_segs - 1)
                    x_pos = -cone_len + t * cone_len
                    r_at_t = max(rotor_radius * 0.15, rotor_radius * t)
                    ang = base_ang + (2.0 * math.pi * twist_turns) * t

                    y_pos = r_at_t * math.cos(ang)
                    z_pos = tower_h + r_at_t * math.sin(ang)

                    seg_len = (cone_len / n_segs) * 1.15
                    blade_h = rotor_radius * 0.28
                    seg = trimesh.creation.box(extents=[seg_len, blade_h, 5.0])
                    rot_blade = trimesh.transformations.rotation_matrix(ang, [1, 0, 0])
                    seg.apply_transform(rot_blade)
                    seg.apply_translation([x_pos, y_pos, z_pos])
                    flute_segs.append(seg)
                one_flute = trimesh.util.concatenate(flute_segs)
                meshes.append(one_flute)

            # 4. Tambor cilíndrico posterior con collarín de salida
            cyl_casing = trimesh.creation.cylinder(radius=rotor_radius, height=cyl_len, sections=36)
            cyl_casing.apply_transform(rot_y)
            cyl_casing.apply_translation([cyl_len / 2.0, 0.0, tower_h])
            meshes.append(cyl_casing)

            flange = trimesh.creation.cylinder(radius=rotor_radius * 1.08, height=8.0, sections=36)
            flange.apply_transform(rot_y)
            flange.apply_translation([cyl_len, 0.0, tower_h])
            meshes.append(flange)

            # 5. Veleta estabilizadora trasera
            tail_boom = trimesh.creation.cylinder(radius=rotor_radius * 0.06, height=rotor_radius * 1.4, sections=16)
            tail_boom.apply_transform(rot_y)
            tail_boom.apply_translation([cyl_len + rotor_radius * 0.7, 0.0, tower_h])
            meshes.append(tail_boom)

            tail_fin = trimesh.creation.box(extents=[rotor_radius * 0.5, 4.0, rotor_radius * 0.6])
            tail_fin.apply_translation([cyl_len + rotor_radius * 1.3, 0.0, tower_h + rotor_radius * 0.25])
            meshes.append(tail_fin)

        else:
            # --- SAVONIUS VAWT ---
            h_mm = float(parameters.get("rotor_height", 1300.0))
            blade_count = int(parameters.get("blade_count", 2))
            overlap = float(parameters.get("overlap_ratio", 0.18))
            t_mm = float(parameters.get("blade_thickness", 3.0))
            shaft_d_mm = float(parameters.get("shaft_diameter", 30.0))

            shaft_radius = shaft_d_mm / 2.0
            shaft_height = h_mm * 1.15
            shaft_mesh = trimesh.creation.cylinder(radius=shaft_radius, height=shaft_height, sections=32)
            shaft_mesh.apply_translation([0.0, 0.0, shaft_height / 2.0 - (shaft_height - h_mm) / 2.0])
            meshes.append(shaft_mesh)

            end_plate_radius = d_mm * 0.55
            plate_thickness = 4.0
            bottom_plate = trimesh.creation.cylinder(radius=end_plate_radius, height=plate_thickness, sections=36)
            bottom_plate.apply_translation([0.0, 0.0, plate_thickness / 2.0])
            meshes.append(bottom_plate)

            top_plate = trimesh.creation.cylinder(radius=end_plate_radius, height=plate_thickness, sections=36)
            top_plate.apply_translation([0.0, 0.0, h_mm - plate_thickness / 2.0])
            meshes.append(top_plate)

            s_mm = d_mm * overlap
            d_blade = (d_mm + s_mm) / 2.0
            r_blade = d_blade / 2.0

            for i in range(blade_count):
                angle = (2.0 * math.pi / blade_count) * i
                arc_sections = 12
                blade_parts = []
                for j in range(arc_sections):
                    th1 = math.pi * j / arc_sections
                    th2 = math.pi * (j + 1) / arc_sections
                    mid_th = (th1 + th2) / 2.0
                    seg_len = r_blade * (th2 - th1)

                    seg = trimesh.creation.box(extents=[seg_len, t_mm, h_mm - 2 * plate_thickness])
                    x = r_blade * math.cos(mid_th)
                    y = r_blade * math.sin(mid_th)
                    rot_matrix = trimesh.transformations.rotation_matrix(mid_th + math.pi / 2.0, [0, 0, 1])
                    seg.apply_transform(rot_matrix)
                    seg.apply_translation([x, y, h_mm / 2.0])
                    blade_parts.append(seg)

                one_blade = trimesh.util.concatenate(blade_parts)
                one_blade.apply_translation([r_blade - s_mm / 2.0, 0.0, 0.0])
                blade_rot_matrix = trimesh.transformations.rotation_matrix(angle, [0, 0, 1])
                one_blade.apply_transform(blade_rot_matrix)
                meshes.append(one_blade)

        # Unir y guardar en storage
        full_mesh = trimesh.util.concatenate(meshes)
        props = GeometryService.process_and_persist_mesh(full_mesh, geom_hash)

        return GeometryOutput(
            representation_type="mesh_trimesh",
            units="mm",
            generator_name=f"{family_id}_generator",
            parameters_used=parameters,
            mesh_vertices_count=props.vertex_count,
            mesh_faces_count=props.face_count,
            volume=props.volume,
            bounding_box=props.bounding_box_min + props.bounding_box_max,
            geometry_hash=geom_hash,
            is_valid=True,
            validation_messages=[],
        )

    def validate_geometry(self, geometry: GeometryOutput) -> tuple[bool, list[str]]:
        return geometry.is_valid, geometry.validation_messages

    def evaluate_fast(
        self, family_id: str, parameters: dict[str, Any], operating_conditions: dict[str, Any]
    ) -> EvaluationResult:
        v_wind = float(operating_conditions.get("wind_speed", 8.5))  # m/s
        rho_air = float(operating_conditions.get("air_density", 1.225))  # kg/m3
        d_mm = float(parameters.get("rotor_diameter", 1000.0))
        d_m = d_mm / 1000.0
        r_m = d_m / 2.0

        if family_id == "hawt_conventional":
            # --- FÍSICA HAWT DE SUSTENTACIÓN (Tipo Iberdrola) ---
            # Área barrida circular A = pi * R^2
            swept_area = math.pi * (r_m**2)
            p_wind = 0.5 * rho_air * swept_area * (v_wind**3)

            # HAWT moderno con perfil de sustentación alcanza Cp entre 0.42 y 0.48
            blade_count = int(parameters.get("blade_count", 3))
            base_cp = 0.46 if blade_count == 3 else 0.41
            pitch = float(parameters.get("pitch_angle", 5.0))
            pitch_factor = max(0.5, 1.0 - 0.02 * ((pitch - 4.5) ** 2))
            cp = round(base_cp * pitch_factor, 4)

            p_mech = round(p_wind * cp, 2)

            # TSR óptimo muy alto: lambda ~ 7.0
            tsr_opt = 7.0
            omega_rad_s = (tsr_opt * v_wind) / r_m
            rpm = round((omega_rad_s * 60.0) / (2.0 * math.pi), 1)
            torque_nominal = round(p_mech / omega_rad_s, 2) if omega_rad_s > 0 else 0.0

            # Par de arranque estático bajo (defecto clásico de sustentación pura: Cp alto pero poco par inicial)
            torque_starting = round(0.5 * rho_air * swept_area * r_m * (v_wind**2) * 0.04, 3)

            # Masa estimada: 3 palas fibra de vidrio/carbono + buje + torre
            blade_mass = blade_count * (r_m * 4.5)
            hub_tower_mass = 15.0 + (r_m * 10.0)
            rotor_mass = round(blade_mass + hub_tower_mass, 2)

            v_cut_in = 3.2  # m/s
            sigma_max = round(120.0 * (v_wind / 10.0), 2)

            assumptions = [
                "Teoría de Momento Elemental de Pala (BEM) para flujo axial",
                "Área barrida circular A = pi * R^2 con sustentación pura",
                "Tip Speed Ratio óptimo elevado (lambda = 7.0)",
                "Requiere alineación con la veleta de viento",
            ]

        elif family_id == "spherical_vawt":
            # --- FÍSICA TURBINA ESFÉRICA OMNIDIRECCIONAL ---
            swept_area = math.pi * (r_m**2) * 0.85
            p_wind = 0.5 * rho_air * swept_area * (v_wind**3)

            # Cp híbrido sustentación-arrastre para flujos 3D urbanos: Cp ~ 0.30 - 0.34
            cp = 0.31
            p_mech = round(p_wind * cp, 2)

            tsr_opt = 2.2
            omega_rad_s = (tsr_opt * v_wind) / r_m
            rpm = round((omega_rad_s * 60.0) / (2.0 * math.pi), 1)

            torque_starting = round(0.5 * rho_air * swept_area * r_m * (v_wind**2) * 0.18, 3)
            rotor_mass = round(math.pi * (d_m**2) * 4.2 + 8.0, 2)
            v_cut_in = 2.4

            assumptions = [
                "Rotor esférico omnidireccional con captura de vientos horizontales y ascendentes",
                "Régimen híbrido arrastre-sustentación con álabes meridianos",
                "TSR moderado (lambda = 2.2) y bajo nivel sonoro urbano",
            ]

        elif family_id == "helical_gorlov":
            # --- FÍSICA TURBINA HELICOIDAL GORLOV ---
            h_mm = float(parameters.get("rotor_height", 1100.0))
            h_m = h_mm / 1000.0
            swept_area = d_m * h_m
            p_wind = 0.5 * rho_air * swept_area * (v_wind**3)

            # Cp de perfil sustentador torsionado continuo: Cp ~ 0.35
            cp = 0.35
            p_mech = round(p_wind * cp, 2)

            tsr_opt = 2.6
            omega_rad_s = (tsr_opt * v_wind) / r_m
            rpm = round((omega_rad_s * 60.0) / (2.0 * math.pi), 1)

            # Par motor suave y uniforme sin pulsaciones cíclicas
            torque_starting = round(0.5 * rho_air * swept_area * r_m * (v_wind**2) * 0.14, 3)
            rotor_mass = round(math.pi * (d_m * h_m) * 2.8 + 6.0, 2)
            v_cut_in = 2.0

            assumptions = [
                "Turbina de eje vertical helicoidal Gorlov de 3 palas con torsión continua en 360°",
                "Par motor constante en cualquier acimut sin puntos muertos",
                "Emisión acústica ultra reducida (-8 dB respecto a HAWT)",
            ]

        elif family_id == "wind_lens_ducted":
            # --- FÍSICA TURBINA DIFUSOR VENTURI / WIND LENS ---
            swept_area = math.pi * (r_m**2)
            p_wind = 0.5 * rho_air * swept_area * (v_wind**3)

            # Aceleración local por baja presión posterior vórtice-brim: kv ~ 1.35 -> P proporcional a kv^3
            kv = 1.35
            cp = round(min(0.88, 0.44 * (kv**2.2)), 4)
            p_mech = round(p_wind * cp, 2)

            tsr_opt = 6.2
            omega_rad_s = (tsr_opt * v_wind) / r_m
            rpm = round((omega_rad_s * 60.0) / (2.0 * math.pi), 1)

            torque_starting = round(0.5 * rho_air * swept_area * r_m * (v_wind**2) * 0.08, 3)
            diff_mass = math.pi * (d_m * 1.15) * 0.4 * 4.5
            rotor_mass = round(3 * (r_m * 4.5) + diff_mass + 12.0, 2)
            v_cut_in = 1.8

            assumptions = [
                "Efecto Venturi y depresión por vórtices toroidales tras el labio exterior (Brim)",
                "Aceleración de masa de aire local a través del plano del rotor",
                "Multiplicación de densidad de potencia por unidad de área",
            ]

        elif family_id == "hybrid_savonius_darrieus":
            # --- FÍSICA HÍBRIDA DOBLE ETAPA ---
            h_mm = float(parameters.get("rotor_height", 1100.0))
            h_m = h_mm / 1000.0
            swept_area = d_m * h_m
            p_wind = 0.5 * rho_air * swept_area * (v_wind**3)

            cp = 0.37
            p_mech = round(p_wind * cp, 2)

            tsr_opt = 2.8
            omega_rad_s = (tsr_opt * v_wind) / r_m
            rpm = round((omega_rad_s * 60.0) / (2.0 * math.pi), 1)

            # Alto par de arranque gracias al núcleo Savonius
            torque_starting = round(0.5 * rho_air * swept_area * r_m * (v_wind**2) * 0.28, 3)
            rotor_mass = round(math.pi * (d_m * h_m) * 3.6 + 9.0, 2)
            v_cut_in = 1.9

            assumptions = [
                "Etapa interna Savonius para auto-arranque suave a baja velocidad",
                "Etapa externa Darrieus para alcanzar alta velocidad y máximo Cp en régimen continuo",
            ]

        elif family_id == "counter_rotating_crwt":
            # --- FÍSICA DOBLE ROTOR CONTRARROTATIVO ---
            swept_area = math.pi * (r_m**2)
            p_wind = 0.5 * rho_air * swept_area * (v_wind**3)

            # Recuperación del torbellino de estela: Cp hasta 0.51
            cp = 0.51
            p_mech = round(p_wind * cp, 2)

            tsr_opt = 5.6
            omega_rad_s = (tsr_opt * v_wind) / r_m
            rpm = round((omega_rad_s * 60.0) / (2.0 * math.pi), 1)

            torque_starting = round(0.5 * rho_air * swept_area * r_m * (v_wind**2) * 0.07, 3)
            rotor_mass = round((3 * (r_m * 4.5)) * 1.85 + 20.0, 2)
            v_cut_in = 2.8

            assumptions = [
                "Doble rotor en tándem con rotación opuesta en el mismo eje axial",
                "Recuperación de la energía cinética de rotación en la estela de salida",
            ]

        elif family_id == "bionic_whale_tubercle":
            # --- FÍSICA ROTOR BIOINSPIRADO ---
            swept_area = math.pi * (r_m**2)
            p_wind = 0.5 * rho_air * swept_area * (v_wind**3)

            cp = 0.44
            p_mech = round(p_wind * cp, 2)

            tsr_opt = 6.6
            omega_rad_s = (tsr_opt * v_wind) / r_m
            rpm = round((omega_rad_s * 60.0) / (2.0 * math.pi), 1)

            torque_starting = round(0.5 * rho_air * swept_area * r_m * (v_wind**2) * 0.05, 3)
            blade_mass = 3 * (r_m * 4.6)
            rotor_mass = round(blade_mass + 15.0 + (r_m * 10.0), 2)
            v_cut_in = 2.7

            assumptions = [
                "Nódulos en el borde de ataque inspirados en la aleta de ballena jorobada",
                "Retraso de la entrada en pérdida aerodinámica (Stall delay)",
                "Mayor tolerancia a turbulencias y rachas de viento cruzado",
            ]

        elif family_id == "conical_drill_vane":
            # --- FÍSICA TURBINA CÓNICA TIPO TALADRO / BROCA ---
            swept_area = math.pi * (r_m**2)
            p_wind = 0.5 * rho_air * swept_area * (v_wind**3)

            # Efecto reacción por confinamiento cónico helicoidal: Cp ~ 0.38
            cp = 0.38
            p_mech = round(p_wind * cp, 2)

            tsr_opt = 2.4
            omega_rad_s = (tsr_opt * v_wind) / r_m
            rpm = round((omega_rad_s * 60.0) / (2.0 * math.pi), 1)

            # Gran par de arranque debido al choque directo del flujo en el cono con estrías
            torque_starting = round(0.5 * rho_air * swept_area * r_m * (v_wind**2) * 0.28, 3)
            cone_mass = math.pi * (r_m**2) * 1.2 * 3.5
            rotor_mass = round(cone_mass + 14.0, 2)
            v_cut_in = 1.9

            assumptions = [
                "Cuerpo cónico aerodinámico alineado con el viento mediante veleta estabilizadora",
                "Efecto de desvío tangencial por estrías helicoidales ranuradas (principio de barrena de Arquímedes)",
                "Alto par estático inicial para auto-arranque suave con brisas leves",
            ]

        else:
            # --- FÍSICA SAVONIUS VAWT ---
            h_mm = float(parameters.get("rotor_height", 1300.0))
            h_m = h_mm / 1000.0
            swept_area = d_m * h_m
            p_wind = 0.5 * rho_air * swept_area * (v_wind**3)

            blade_count = int(parameters.get("blade_count", 2))
            overlap = float(parameters.get("overlap_ratio", 0.18))
            aspect_ratio = h_m / d_m
            ar_factor = min(1.15, max(0.85, 0.9 + 0.1 * aspect_ratio))
            overlap_factor = 1.0 - 1.5 * ((overlap - 0.18) ** 2)

            base_cp = 0.21 if blade_count == 2 else 0.18
            cp = round(max(0.08, min(0.26, base_cp * ar_factor * overlap_factor)), 4)
            p_mech = round(p_wind * cp, 2)

            tsr_opt = 0.95
            omega_rad_s = (tsr_opt * v_wind) / r_m
            rpm = round((omega_rad_s * 60.0) / (2.0 * math.pi), 1)

            c_ts = 0.36 if blade_count == 2 else 0.42
            torque_starting = round(0.5 * rho_air * swept_area * r_m * (v_wind**2) * c_ts, 3)

            t_mm = float(parameters.get("blade_thickness", 3.0))
            blade_developed_width = (math.pi * (d_m / 2.0))
            blade_vol = blade_developed_width * (t_mm / 1000.0) * h_m * blade_count
            blade_mass = blade_vol * 2700.0
            shaft_mass = math.pi * ((0.03 / 2.0) ** 2) * (h_m * 1.2) * 7850.0
            plates_mass = 2.0 * (math.pi * ((d_m * 0.55) ** 2) * 0.004 * 2700.0)
            rotor_mass = round(blade_mass + shaft_mass + plates_mass, 2)

            v_cut_in = max(1.8, round(1.5 + (rotor_mass / 50.0), 2))

            assumptions = [
                "Modelo aerodinámico de arrastre Savonius (Blackwell-Menet)",
                "Operación omnidireccional sin veleta de orientación",
                "Alto par de autoarranque a baja velocidad",
            ]

        return EvaluationResult(
            fidelity_level="LEVEL_1_ANALYTICAL",
            solver_name=f"{family_id}_aerodynamics_solver",
            convergence_status="CONVERGED",
            metrics={
                "power_output": p_mech,
                "power_coefficient": cp,
                "rotor_mass": rotor_mass,
                "starting_torque": torque_starting,
                "nominal_rpm": rpm,
                "cut_in_wind_speed": v_cut_in,
            },
            assumptions=assumptions,
            execution_time_seconds=0.001,
            is_valid=True,
        )

    def synthesize_from_prompt(
        self, prompt: str, scale: str = "domestic", operating_conditions: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Sintetiza una arquitectura eólica libre y validada a partir de lenguaje natural."""
        from modules.wind_turbines.synthesizer import (
            parse_prompt_intent,
            build_synthesized_parameters,
            generate_engineering_explanation,
            format_top_code,
        )
        conds = operating_conditions or {"wind_speed": 8.5, "air_density": 1.225, "scale": scale}
        family_id, detected_scale, overrides = parse_prompt_intent(prompt, default_scale=scale)
        params = build_synthesized_parameters(family_id, detected_scale, overrides)

        geom_output = self.generate_geometry(family_id, params)
        eval_result = self.evaluate_fast(family_id, params, conds)

        families_map = {f.id: f.name for f in self.get_design_families()}
        family_name = families_map.get(family_id, family_id)
        top_code = format_top_code(family_id, detected_scale, params)
        explanation = generate_engineering_explanation(family_id, params, eval_result.metrics, prompt)

        return {
            "family_id": family_id,
            "family_name": family_name,
            "title_code": top_code,
            "scale": detected_scale,
            "prompt": prompt,
            "explanation": explanation,
            "parameters": params,
            "metrics": eval_result.metrics,
            "geometry_hash": geom_output.geometry_hash,
            "assumptions": eval_result.assumptions,
        }

