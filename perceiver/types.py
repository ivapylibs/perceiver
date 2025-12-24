from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any
from enum import Enum
from typing import Union
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
    # items maps track_id (str|int) -> arbitrary per-track estimate dict
    # For hand tracking, this may contain:
    # - 'landmarks_2d': np.ndarray of shape (N, 2)
    # - 'landmarks_3d': np.ndarray of shape (N, 3)
    # - 'mask': mask metadata
    # - 'pick': hand pick/axis info (pick_3d, axis_3d, distance), etc.
    items: dict[Union[str, int], dict[str, Any]]
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