"""
Abstracción de geometrías en DesignLab (B-Rep y Mallas poligonales).
"""

from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class GeometryKind(str, Enum):
    BREP_SOLID = "BREP_SOLID"
    POLYGONAL_MESH = "POLYGONAL_MESH"


class GeometryProperties(BaseModel):
    kind: GeometryKind = GeometryKind.POLYGONAL_MESH
    units: str = "mm"
    volume: float = 0.0
    surface_area: float = 0.0
    vertex_count: int = 0
    face_count: int = 0
    is_watertight: bool = True
    bounding_box_min: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    bounding_box_max: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    center_of_mass: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    geometry_hash: str = ""
