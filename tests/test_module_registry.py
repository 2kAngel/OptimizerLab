"""
Pruebas del registro de módulos de ingeniería.
"""

import pytest
from backend.core.module_registry.registry import ModuleRegistry
from modules.test_module.module import TestBeamModule


def test_register_and_retrieve_module():
    reg = ModuleRegistry()
    module = TestBeamModule()
    reg.register(module)

    meta = reg.get_module("structural_beam").get_metadata()
    assert meta.id == "structural_beam"
    assert meta.name == "Viga Estructural Paramétrica (Módulo de Prueba)"
    assert len(reg.list_modules()) == 1


def test_missing_module_raises_keyerror():
    reg = ModuleRegistry()
    with pytest.raises(KeyError):
        reg.get_module("non_existent_module")
