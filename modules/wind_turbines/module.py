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
        ]

    def get_parameters(self, family_id: str) -> list[ParameterDefinition]:
        if family_id == "savonius_vawt":
            return [
                ParameterDefinition(name="rotor_diameter", description="Diámetro exterior total del rotor D", data_type="float", min_value=300.0, max_value=3000.0, default_value=900.0, units="mm"),
                ParameterDefinition(name="rotor_height", description="Altura total del rotor H", data_type="float", min_value=300.0, max_value=3500.0, default_value=1300.0, units="mm"),
                ParameterDefinition(name="blade_count", description="Número de palas (2 o 3 palas)", data_type="int", min_value=2, max_value=3, default_value=2, units=""),
                ParameterDefinition(name="overlap_ratio", description="Relación de solapamiento entre palas (s/d)", data_type="float", min_value=0.08, max_value=0.30, default_value=0.18, units=""),
                ParameterDefinition(name="blade_thickness", description="Espesor del material de las palas", data_type="float", min_value=1.5, max_value=8.0, default_value=3.0, units="mm"),
                ParameterDefinition(name="shaft_diameter", description="Diámetro del eje motriz central", data_type="float", min_value=20.0, max_value=60.0, default_value=30.0, units="mm"),
            ]
        elif family_id == "hawt_conventional":
            return [
                ParameterDefinition(name="rotor_diameter", description="Diámetro del disco rotor D", data_type="float", min_value=500.0, max_value=5000.0, default_value=2000.0, units="mm"),
                ParameterDefinition(name="blade_count", description="Número de palas (típico 3 palas)", data_type="int", min_value=2, max_value=4, default_value=3, units=""),
                ParameterDefinition(name="root_chord", description="Cuerda de la pala en la raíz", data_type="float", min_value=60.0, max_value=350.0, default_value=150.0, units="mm"),
                ParameterDefinition(name="pitch_angle", description="Ángulo de calado / pitch de la pala", data_type="float", min_value=0.0, max_value=25.0, default_value=5.0, units="deg"),
                ParameterDefinition(name="tower_height", description="Altura de la torre soporte", data_type="float", min_value=1000.0, max_value=6000.0, default_value=2500.0, units="mm"),
            ]
        else:
            # spherical_vawt
            return [
                ParameterDefinition(name="rotor_diameter", description="Diámetro esférico D", data_type="float", min_value=400.0, max_value=2500.0, default_value=1000.0, units="mm"),
                ParameterDefinition(name="blade_count", description="Número de álabes meridianos esféricos", data_type="int", min_value=4, max_value=8, default_value=6, units=""),
                ParameterDefinition(name="blade_thickness", description="Espesor de los álabes", data_type="float", min_value=2.0, max_value=8.0, default_value=3.5, units="mm"),
                ParameterDefinition(name="curvature_twist", description="Ángulo de torsión helicoidal sobre la esfera", data_type="float", min_value=10.0, max_value=90.0, default_value=45.0, units="deg"),
            ]

    def get_objectives(self, family_id: str) -> list[ObjectiveDefinition]:
        return [
            ObjectiveDefinition(name="power_output", description="Potencia mecánica generada a velocidad de diseño", direction="maximize", units="W"),
            ObjectiveDefinition(name="power_coefficient", description="Coeficiente de rendimiento aerodinámico (Cp)", direction="maximize", units=""),
            ObjectiveDefinition(name="rotor_mass", description="Masa total del conjunto (palas, buje, eje)", direction="minimize", units="kg"),
            ObjectiveDefinition(name="starting_torque", description="Par disponible para autoarranque a baja velocidad", direction="maximize", units="N·m"),
        ]

    def get_constraints(self, family_id: str) -> list[ConstraintDefinition]:
        return [
            ConstraintDefinition(name="max_stress", description="Tensión máxima admisible", constraint_type="lte", limit_value=200.0, units="MPa"),
            ConstraintDefinition(name="cut_in_wind_speed", description="Velocidad de viento de arranque", constraint_type="lte", limit_value=4.0, units="m/s"),
        ]

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
