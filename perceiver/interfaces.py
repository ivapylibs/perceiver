from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Any, TYPE_CHECKING


if TYPE_CHECKING:
    from .types import Detections, Tracks, Estimates, PerceptionResult

class Detector(ABC):
    """Pure per-frame detection. No temporal state/IDs"""

    @abstractmethod
    def detect(self, frame: Any, timestamp: Optional[float] = None) -> 'Detections':
        pass


class Trackpointer(ABC):
    """Assign persistent IDs / maintain temporal state"""
    @abstractmethod
    def update(self, detections: 'Detections', timestamp: Optional[float] = None) -> 'Tracks':
        pass

    @abstractmethod
    def reset(self) -> None:
        pass


class Filter(ABC):
    """Optional smoothing/denoising over time-series outputs"""
    @abstractmethod
    def apply(self, tracks_or_estimates: 'Tracks'| 'Estimates', timestamp: Optional[float] = None) -> 'Estimates':
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

class Perceiver(ABC):
    """Wires Detector → Trackpointer → (Filter). Single-frame step; returns normalized result."""
    @abstractmethod
    def process(self, frame: Any, timestamp: Optional[float]=None) -> 'PerceptionResult':
        pass

    @abstractmethod
    def reset(self) -> None:
        pass


__all__ = ['Detector', 'Trackpointer', 'Filter', 'Perceiver']