from __future__ import annotations
from typing import Optional, List, Any


from .interfaces import Filter
from .types import Tracks, Estimates


class Estimator:
    """
    Minimal Estimator abstraction.
    Takes Tracks and produces Estimates (e.g., smoothed landmarks/bboxes).
    """

    def update(self, tracks: Tracks, timestamp: Optional[float] = None) -> Estimates:
        """
        Default no-op: return an empty Estimates. Concrete estimators should override.
        """
        return Estimates(items={}, meta={"timestamp": timestamp})
    
    def reset(self) -> None:
        """Reset any internal state in the estimator (default is no-op)"""
        return
    

class FilteringEstimator(Estimator):
    """
    An Estimator that chains one or more Filters.
    - The first filter is expected to accept Tracks.
    - Subsequent filters may accept either Tracks or Estimates. For simplicity,
      we currently pass the Estimates forward (common smoothing chain).
    """
    def __init__(self, filters: List[Filter]) -> None:
        self._filters = list(filters)
    
    
    def update(self, tracks: Tracks, timestamp: Optional[float] = None) -> Estimates:
        if not self._filters:
            # No filters configured -> return empty Estimates (identity).
            return Estimates(items={}, meta={"timestamp": timestamp})
        
        # First filter consumes Tracks → Estimates
        current: Any = self._filters[0].apply(tracks, timestamp=timestamp)

        # Chain any remaining filters on the Estimates
        for f in self._filters[1:]:
            current = f.apply(current, timestamp=timestamp)

        # `current` should be an Estimates instance by interface contract.
        return current
    
    def reset(self) -> None:
        for f in self._filters:
            f.reset()