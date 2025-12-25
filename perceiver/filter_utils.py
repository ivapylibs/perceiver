# perceiver/perceiver/filters.py
from __future__ import annotations
from typing import Optional, Dict
import numpy as np

class EMA:
    def __init__(self, alpha: float = 0.4):
        self.alpha = float(alpha)
        self.prev: Optional[np.ndarray] = None

    def reset(self):
        self.prev = None

    def __call__(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x)
        if self.prev is None or self.prev.shape != x.shape or not np.all(np.isfinite(self.prev)):
            self.prev = x
        else:
            self.prev = self.alpha * x + (1.0 - self.alpha) * self.prev
        return self.prev

class MultiFeatureEMA:
    """
    Keeps independent EMA states per hand label ('left'/'right')
    and per feature key ('landmarks' | 'palm' | 'centroid').
    """
    def __init__(self, alpha: float = 0.4):
        self.alpha = float(alpha)
        self.filters: Dict[str, Dict[str, EMA]] = {"left": {}, "right": {}}

    def _f(self, label: str, key: str) -> EMA:
        d = self.filters[label]
        if key not in d:
            d[key] = EMA(self.alpha)
        return d[key]

    def smooth(self, label: str, key: str, x: np.ndarray) -> np.ndarray:
        return self._f(label, key)(x)

    def reset_missing(self, seen_labels):
        for k in ("left", "right"):
            if k not in seen_labels:
                for f in self.filters[k].values():
                    f.reset()
