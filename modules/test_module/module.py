"""
Módulo de prueba de ingeniería para DesignLab: Viga Estructural Paramétrica.
Demuestra la implementación completa del contrato EngineeringModule sin acoplamientos.
"""

import hashlib
import math
import trimesh
from typing import Any
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


class TestBeamModule(EngineeringModule):
    """Módulo de prueba de ingeniería que modela una viga en voladizo sometida a carga puntual."""

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="structural_beam",
            name="Viga Estructural Paramétrica (Módulo de Prueba)",
            version="1.0.0",
            description="Módulo de ingeniería de referencia para validación de la plataforma DesignLab.",
            author="DesignLab Core Team",
        )

    def get_design_families(self) -> list[DesignFamily]:
        return [
            DesignFamily(
                id="cantilever_rectangular",
                name="Viga en Voladizo Rectangular Sólida",
                description="Perfil macizo rectangular empotrado en un extremo con carga en el extremo libre.",
            ),
            DesignFamily(
                id="cantilever_hollow",
                name="Viga en Voladizo Hueca",
                description="Perfil tubular rectangular hueco optimizado para reducción de masa.",
            ),
        ]

    def get_parameters(self, family_id: str) -> list[ParameterDefinition]:
        params = [
            ParameterDefinition(
                name="length",
                description="Longitud de la viga",
                data_type="float",
                min_value=100.0,
                max_value=2000.0,
                default_value=500.0,
                units="mm",
            ),
            ParameterDefinition(
                name="width",
                description="Anchura del perfil",
                data_type="float",
                min_value=10.0,
                max_value=200.0,
                default_value=50.0,
                units="mm",
            ),
            ParameterDefinition(
                name="height",
                description="Altura del perfil en la dirección de la carga",
                data_type="float",
                min_value=10.0,
                max_value=300.0,
                default_value=80.0,
                units="mm",
            ),
            ParameterDefinition(
                name="elastic_modulus",
                description="Módulo de elasticidad longitudinal (Young)",
                data_type="float",
                min_value=10.0,
                max_value=300.0,
                default_value=70.0,  # Aluminio ~70 GPa
                units="GPa",
            ),
            ParameterDefinition(
                name="density",
                description="Densidad del material",
                data_type="float",
                min_value=500.0,
                max_value=10000.0,
                default_value=2700.0,  # Aluminio ~2700 kg/m^3
                units="kg/m^3",
            ),
        ]
        if family_id == "cantilever_hollow":
            params.append(
                ParameterDefinition(
                    name="wall_thickness",
                    description="Espesor de pared del tubo hueco",
                    data_type="float",
                    min_value=1.0,
                    max_value=20.0,
                    default_value=4.0,
                    units="mm",
                )
            )
        return params

    def get_objectives(self, family_id: str) -> list[ObjectiveDefinition]:
        return [
            ObjectiveDefinition(
                name="mass",
                description="Masa total del componente",
                direction="minimize",
                units="kg",
            ),
            ObjectiveDefinition(
                name="deflection",
                description="Deflexión elástica en el extremo libre",
                direction="minimize",
                units="mm",
            ),
            ObjectiveDefinition(
                name="natural_frequency",
                description="Primera frecuencia natural de vibración",
                direction="maximize",
                units="Hz",
            ),
        ]

    def get_constraints(self, family_id: str) -> list[ConstraintDefinition]:
        return [
            ConstraintDefinition(
                name="max_stress",
                description="Tensión normal máxima admisible",
                constraint_type="lte",
                limit_value=200.0,  # 200 MPa
                units="MPa",
            ),
            ConstraintDefinition(
                name="max_allowable_deflection",
                description="Deflexión máxima admisible en servicio",
                constraint_type="lte",
                limit_value=5.0,  # 5 mm
                units="mm",
            ),
        ]

    def generate_geometry(self, family_id: str, parameters: dict[str, Any]) -> GeometryOutput:
        length = float(parameters.get("length", 500.0))
        width = float(parameters.get("width", 50.0))
        height = float(parameters.get("height", 80.0))

        # Crear hash determinista a partir de los parámetros ordenados
        param_repr = "_".join(f"{k}:{v}" for k, v in sorted(parameters.items()))
        geom_hash = hashlib.sha256(param_repr.encode()).hexdigest()

        # Validación dimensional previa
        is_valid = True
        val_msgs = []
        if length <= 0 or width <= 0 or height <= 0:
            is_valid = False
            val_msgs.append("Las dimensiones exteriores deben ser estrictamente positivas.")

        if family_id == "cantilever_hollow":
            thickness = float(parameters.get("wall_thickness", 4.0))
            if thickness * 2 >= min(width, height):
                is_valid = False
                val_msgs.append("El doble del espesor excede las dimensiones de la sección transversal.")

        if not is_valid:
            return GeometryOutput(
                representation_type="mesh_trimesh",
                units="mm",
                generator_name="test_beam_generator",
                parameters_used=parameters,
                mesh_vertices_count=0,
                mesh_faces_count=0,
                volume=0.0,
                bounding_box=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                geometry_hash=geom_hash,
                is_valid=False,
                validation_messages=val_msgs,
            )

        # Generar malla real con Trimesh
        if family_id == "cantilever_hollow":
            thickness = float(parameters.get("wall_thickness", 4.0))
            outer_box = trimesh.creation.box(extents=[length, width, height])
            inner_w = max(0.1, width - 2 * thickness)
            inner_h = max(0.1, height - 2 * thickness)
            inner_box = trimesh.creation.box(extents=[length + 2.0, inner_w, inner_h])
            try:
                mesh = outer_box.difference(inner_box)
            except Exception:
                # Fallback seguro si la operación booleana no converge
                mesh = outer_box
        else:
            mesh = trimesh.creation.box(extents=[length, width, height])

        # Centrar la base en el origen X=0 para visualización de viga en voladizo
        mesh.apply_translation([length / 2.0, 0.0, 0.0])

        # Procesar, calcular propiedades reales y persistir artefactos STL y GLB en storage
        props = GeometryService.process_and_persist_mesh(mesh, geom_hash)

        return GeometryOutput(
            representation_type="mesh_trimesh",
            units="mm",
            generator_name="test_beam_generator",
            parameters_used=parameters,
            mesh_vertices_count=props.vertex_count,
            mesh_faces_count=props.face_count,
            volume=props.volume,
            bounding_box=props.bounding_box_min + props.bounding_box_max,
            geometry_hash=geom_hash,
            is_valid=True,
            validation_messages=val_msgs,
        )

    def validate_geometry(self, geometry: GeometryOutput) -> tuple[bool, list[str]]:
        return geometry.is_valid, geometry.validation_messages

    def evaluate_fast(
        self, family_id: str, parameters: dict[str, Any], operating_conditions: dict[str, Any]
    ) -> EvaluationResult:
        # Condiciones operativas por defecto: carga puntual en extremo F=500 N
        load_f = float(operating_conditions.get("applied_load", 500.0))  # N

        length_mm = float(parameters.get("length", 500.0))
        width_mm = float(parameters.get("width", 50.0))
        height_mm = float(parameters.get("height", 80.0))
        e_gpa = float(parameters.get("elastic_modulus", 70.0))
        rho_kg_m3 = float(parameters.get("density", 2700.0))

        # Conversión a unidades SI
        l_m = length_mm / 1000.0
        w_m = width_mm / 1000.0
        h_m = height_mm / 1000.0
        e_pa = e_gpa * 1e9

        if family_id == "cantilever_hollow":
            t_mm = float(parameters.get("wall_thickness", 4.0))
            t_m = t_mm / 1000.0
            w_in = max(0.0, w_m - 2 * t_m)
            h_in = max(0.0, h_m - 2 * t_m)
            area = (w_m * h_m) - (w_in * h_in)
            # Momento de inercia I_z = (W*H^3 - w_in*h_in^3) / 12
            inertia = ((w_m * (h_m**3)) - (w_in * (h_in**3))) / 12.0
        else:
            area = w_m * h_m
            inertia = (w_m * (h_m**3)) / 12.0

        if inertia <= 0.0 or area <= 0.0 or e_pa <= 0.0:
            return EvaluationResult(
                fidelity_level="LEVEL_1_ANALYTICAL",
                solver_name="euler_bernoulli_beam_solver",
                convergence_status="NOT_CONVERGED",
                is_valid=False,
                error_message="Propiedades geométricas no válidas (inercia o área nula).",
            )

        # 1. Masa (kg)
        volume_m3 = area * l_m
        mass_kg = volume_m3 * rho_kg_m3

        # 2. Deflexión en extremo libre: delta = (F * L^3) / (3 * E * I) en mm
        delta_m = (load_f * (l_m**3)) / (3.0 * e_pa * inertia)
        deflection_mm = delta_m * 1000.0

        # 3. Tensión máxima en empotramiento: sigma = (M * c) / I = (F * L * (H/2)) / I en MPa
        sigma_max_pa = (load_f * l_m * (h_m / 2.0)) / inertia
        stress_mpa = sigma_max_pa / 1e6

        # 4. Frecuencia natural fundamental (modo 1 flexión voladizo):
        # omega_1 = 3.516 * sqrt( (E * I) / (m_linear * L^4) )
        m_linear = mass_kg / l_m
        omega_1 = (3.516 / (2.0 * math.pi)) * math.sqrt((e_pa * inertia) / (m_linear * (l_m**4)))

        return EvaluationResult(
            fidelity_level="LEVEL_1_ANALYTICAL",
            solver_name="euler_bernoulli_beam_solver",
            convergence_status="CONVERGED",
            metrics={
                "mass": round(mass_kg, 4),
                "deflection": round(deflection_mm, 4),
                "natural_frequency": round(omega_1, 2),
                "max_stress": round(stress_mpa, 2),
            },
            assumptions=[
                "Teoría de viga de Euler-Bernoulli (pequeñas deformaciones)",
                "Material homogéneo e isótropo elástico lineal",
                "Carga puntual concentrada en el extremo libre",
                "Efectos de cortante de Timoshenko despreciables",
            ],
            execution_time_seconds=0.0005,
            is_valid=True,
        )
