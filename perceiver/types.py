from dataclasses import dataclass
from typing import Optional, Any
from enum import Enum

@dataclass
class Detections:
    items: list[dict[str, Any]]
    meta: dict[str, Any]


@dataclass
class Tracks:
    items: list[dict[str, Any]]
    meta: dict[str, Any]


@dataclass
class Estimates:
    items: dict[str | int, dict[str, Any]]
    meta: dict[str, Any]

@dataclass
class PerceptionResult:
    detections: Detections
    tracks: Tracks
    estimates: Optional[Estimates]
    meta: dict[str, Any]


class MaskMode(Enum):
    NONE = "none"
    PALM = "palm"
    HAND = "hand"


__all__ = ['Detections', 'Tracks', 'Estimates', 'PerceptionResult', 'MaskMode']