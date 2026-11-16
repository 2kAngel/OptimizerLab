"""
Modelos Pydantic v2 fuertemente tipados para los módulos de ingeniería de DesignLab.
"""

from typing import Any, Literal
from pydantic import BaseModel, Field


class ModuleMetadata(BaseModel):
    id: str = Field(..., description="Identificador único del módulo (ej. wind_turbines, test_beam)")
    name: str = Field(..., description="Nombre amigable del módulo")
    version: str = Field("0.1.0", description="Versión semántica del módulo")
    description: str = Field(..., description="Descripción detallada de la física y dominio del módulo")
    author: str = Field("DesignLab Team", description="Autor o equipo responsable")


class DesignFamily(BaseModel):
    id: str = Field(..., description="Identificador de la familia arquitectónica")
    name: str = Field(..., description="Nombre descriptivo de la familia")
    description: str = Field(..., description="Explicación de la arquitectura física y campo de aplicación")


class ParameterDefinition(BaseModel):
    name: str = Field(..., description="Nombre del parámetro (clave)")
    description: str = Field(..., description="Significado físico")
    data_type: Literal["float", "int", "str", "bool"] = "float"
    min_value: float | None = None
    max_value: float | None = None
    default_value: Any = None
    units: str = Field("", description="Unidad de medida física (ej. m, mm, rad, kg/m3)")
    step: float | None = None


class ObjectiveDefinition(BaseModel):
    name: str = Field(..., description="Nombre de la métrica objetivo")
    description: str = Field(..., description="Descripción del objetivo")
    direction: Literal["minimize", "maximize"] = "maximize"
    units: str = Field("", description="Unidad de medida (ej. W, N, kg, USD)")


class ConstraintDefinition(BaseModel):
    name: str = Field(..., description="Identificador de la restricción")
    description: str = Field(..., description="Descripción de la condición de admisibilidad")
    constraint_type: Literal["lte", "gte", "range", "boolean"] = "lte"
    limit_value: float | None = None
    units: str = Field("", description="Unidades físicas")


class GeometryOutput(BaseModel):
    representation_type: Literal["brep_solid", "mesh_trimesh", "analytic_surfaces"] = "mesh_trimesh"
    units: str = "mm"
    generator_name: str
    parameters_used: dict[str, Any]
    mesh_vertices_count: int = 0
    mesh_faces_count: int = 0
    volume: float = 0.0
    bounding_box: list[float] = Field(default_factory=list, description="[min_x, min_y, min_z, max_x, max_y, max_z]")
    geometry_hash: str = ""
    is_valid: bool = True
    validation_messages: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    fidelity_level: Literal["LEVEL_1_ANALYTICAL", "LEVEL_2_CFD", "LEVEL_3_SURROGATE"]
    solver_name: str
    solver_version: str = "1.0.0"
    convergence_status: Literal["CONVERGED", "NOT_CONVERGED", "ESTIMATED"] = "CONVERGED"
    metrics: dict[str, float] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)
    uncertainty_estimate: float | None = None
    execution_time_seconds: float = 0.0
    is_valid: bool = True
    error_message: str | None = None
