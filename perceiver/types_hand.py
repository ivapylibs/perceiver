from dataclasses import dataclass
import numpy as np

@dataclass
class HandPickResult:
    pick_3d: np.ndarray      # shape (3,)
    axis_3d: np.ndarray      # shape (3,)
    distance: float
