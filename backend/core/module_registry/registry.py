"""
Registro dinámico y desacoplado de módulos de ingeniería en DesignLab.
"""

from typing import Dict, List
from backend.core.module_registry.base import EngineeringModule
from backend.core.module_registry.models import ModuleMetadata


class ModuleRegistry:
    """Registro central singleton para módulos de ingeniería."""

    def __init__(self):
        self._modules: Dict[str, EngineeringModule] = {}

    def register(self, module: EngineeringModule) -> None:
        """Registra un nuevo módulo en el sistema validando sus metadatos."""
        meta = module.get_metadata()
        if not meta.id:
            raise ValueError("El módulo debe tener un 'id' no vacío.")
        self._modules[meta.id] = module

    def get_module(self, module_id: str) -> EngineeringModule:
        """Obtiene un módulo por su ID o lanza KeyError si no está registrado."""
        if module_id not in self._modules:
            raise KeyError(f"Módulo de ingeniería '{module_id}' no encontrado en el registro.")
        return self._modules[module_id]

    def list_modules(self) -> List[ModuleMetadata]:
        """Lista los metadatos de todos los módulos registrados."""
        return [mod.get_metadata() for mod in self._modules.values()]

    def clear(self) -> None:
        """Limpia el registro (útil para pruebas unitarias)."""
        self._modules.clear()


# Instancia global del registro
registry = ModuleRegistry()
