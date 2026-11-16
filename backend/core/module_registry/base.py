"""
Clase base abstracta para los módulos de ingeniería de DesignLab.
"""

from abc import ABC, abstractmethod
from typing import Any
from backend.core.module_registry.models import (
    ModuleMetadata,
    DesignFamily,
    ParameterDefinition,
    ObjectiveDefinition,
    ConstraintDefinition,
    EvaluationResult,
    GeometryOutput,
)


class EngineeringModule(ABC):
    """
    Contrato base estricto para cualquier disciplina de ingeniería en DesignLab.
    Todos los métodos deben ser implementados por módulos concretos.
    """

    @abstractmethod
    def get_metadata(self) -> ModuleMetadata:
        """Devuelve los metadatos globales del módulo."""
        pass

    @abstractmethod
    def get_design_families(self) -> list[DesignFamily]:
        """Devuelve las familias arquitectónicas soportadas por el módulo."""
        pass

    @abstractmethod
    def get_parameters(self, family_id: str) -> list[ParameterDefinition]:
        """Devuelve las definiciones de parámetros de diseño para una familia."""
        pass

    @abstractmethod
    def get_objectives(self, family_id: str) -> list[ObjectiveDefinition]:
        """Devuelve las métricas de rendimiento y objetivos de optimización."""
        pass

    @abstractmethod
    def get_constraints(self, family_id: str) -> list[ConstraintDefinition]:
        """Devuelve las restricciones físicas y de admisibilidad."""
        pass

    @abstractmethod
    def generate_geometry(self, family_id: str, parameters: dict[str, Any]) -> GeometryOutput:
        """Genera la geometría representativa a partir del vector de parámetros."""
        pass

    @abstractmethod
    def validate_geometry(self, geometry: GeometryOutput) -> tuple[bool, list[str]]:
        """Verifica la validez física y topológica de la geometría producida."""
        pass

    @abstractmethod
    def evaluate_fast(
        self, family_id: str, parameters: dict[str, Any], operating_conditions: dict[str, Any]
    ) -> EvaluationResult:
        """Evaluación rápida Nivel 1 (analítica / aproximación numérica de bajo coste)."""
        pass

    def synthesize_from_prompt(
        self, prompt: str, scale: str = "domestic", operating_conditions: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Sintetiza una arquitectura y parámetros a partir de una descripción en lenguaje natural."""
        raise NotImplementedError("Este módulo no soporta síntesis generativa por prompt.")

