# GUÍA DE DESARROLLO DE MÓDULOS DE INGENIERÍA

DesignLab está diseñado para que cualquier disciplina física (aerodinámica, mecánica de fluidos, estructuras, intercambio de calor) pueda integrarse de forma limpia y tipada mediante el contrato `EngineeringModule`.

---

## 1. Contrato de un Módulo de Ingeniería

Todo módulo de ingeniería debe heredar de la clase base abstracta `EngineeringModule` y registrarse en el `ModuleRegistry`.

```python
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
    """Contrato base obligatorio para cualquier disciplina de ingeniería en DesignLab."""

    @abstractmethod
    def get_metadata(self) -> ModuleMetadata:
        """Devuelve identificador único, nombre, versión, autor y descripción del módulo."""
        pass

    @abstractmethod
    def get_design_families(self) -> list[DesignFamily]:
        """Devuelve las familias arquitectónicas soportadas (ej. Savonius, Darrieus, HAWT)."""
        pass

    @abstractmethod
    def get_parameters(self, family_id: str) -> list[ParameterDefinition]:
        """Devuelve la especificación de parámetros válidos, tipos, rangos y valores por defecto."""
        pass

    @abstractmethod
    def get_objectives(self, family_id: str) -> list[ObjectiveDefinition]:
        """Devuelve los objetivos a optimizar (ej. Maximizar Potencia, Minimizar Masa)."""
        pass

    @abstractmethod
    def get_constraints(self, family_id: str) -> list[ConstraintDefinition]:
        """Devuelve las restricciones físicas y geométricas admisibles."""
        pass

    @abstractmethod
    def generate_geometry(self, family_id: str, parameters: dict[str, Any]) -> GeometryOutput:
        """Genera el modelo geométrico (B-Rep o Malla) a partir del vector de parámetros."""
        pass

    @abstractmethod
    def validate_geometry(self, geometry: GeometryOutput) -> tuple[bool, list[str]]:
        """Valida que la geometría sea físicamente realizable, estanca y sin degeneraciones."""
        pass

    @abstractmethod
    def evaluate_fast(
        self, family_id: str, parameters: dict[str, Any], operating_conditions: dict[str, Any]
    ) -> EvaluationResult:
        """Evaluación rápida Nivel 1 (analítica / numérica barata)."""
        pass
```

---

## 2. Buenas Prácticas en el Desarrollo de Módulos

1. **Aislamiento Físico:** El módulo no debe depender de bases de datos ni de rutas absolutas del host. Todas las funciones de generación y evaluación deben ser funciones puras o con efectos secundarios acotados al objeto de salida.
2. **Explicitud de Supuestos:** Si una fórmula asume flujo potencial, incompresible o condiciones de régimen laminar, debe declararse en los metadatos de la evaluación (`assumptions: list[str]`).
3. **Manejo de Errores Defensivo:** Si un juego de parámetros genera una autointersección geométrica o una singularidad matemática (ej. división por cero en un ángulo de ataque crítico), el evaluador debe capturar la excepción y retornar un resultado marcado como inválido con explicación detallada, en lugar de provocar la caída del proceso.
