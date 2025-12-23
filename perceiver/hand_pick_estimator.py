from __future__ import annotations

from typing import Optional, Dict, Any

import numpy as np

from .interfaces import Filter
from .types import Tracks, Estimates
from .types_hand import HandPickResult

class HandPickEstimator(Filter):
    """
    Computes per-hand pick position, axis, and distance from 3D landmarks.
    Assumes that each estimate dict contains 'landmarks_3d' (N, 3).
    """
    def __init__(
        self,
        pinch_indices: tuple[int, int] = (4, 8),
        axis_indices: tuple[int, int] = (0, 9),
    ):
        self.pinch_indices = pinch_indices   # e.g. (thumb_tip, index_tip)
        self.axis_indices = axis_indices     # e.g. (wrist, middle_mcp)

    def reset(self) -> None:
        # For now, HandPickEstimator is stateless per frame.
        # Later, we can add EMA or other temporal state here.
        pass


    def apply(
        self,
        tracks_or_estimates: Tracks | Estimates,
        timestamp: Optional[float] = None
    ) -> Estimates:
        # 1) Normalize to Estimates
        if isinstance(tracks_or_estimates, Tracks):
            # If your pipeline ever passes Tracks in, you might have a helper
            # that turns Tracks -> Estimates; if not, you can decide
            # that this filter only accepts Estimates.
            # For now, let's assume we always receive Estimates and
            # just assert:
            raise TypeError("HandPickEstimator expects Estimates, not Tracks")

        estimates = tracks_or_estimates

        # 2) Iterate over tracked hands and compute pick/axis/distance
        for track_id, est_dict in estimates.items.items():
            # est_dict is a dict[str, Any] for that hand
            self._compute_pick_for_track(est_dict)

        return estimates

    def _compute_pick_for_track(self, est_dict: Dict[str, Any]) -> None:
        """
        Mutates est_dict in-place, adding a 'pick' entry if landmarks are available.
        Prefers 3D ('landmarks_3d'), falls back to 2D ('landmarks') with z=0.
        """
        # Prefer explicit 3D landmarks if present
        landmarks_any = est_dict.get("landmarks_3d", None)
        if landmarks_any is None:
            # Fall back to 2D landmarks (typical MediaPipe output on webcam)
            landmarks_any = est_dict.get("landmarks", None)

        if landmarks_any is None:
            # No usable landmarks
            return

        L = np.asarray(landmarks_any)
        if L.ndim != 2:
            return

        # If we only have 2D (N,2), pad with zeros to make it (N,3)
        if L.shape[1] == 2:
            zeros = np.zeros((L.shape[0], 1), dtype=L.dtype)
            L = np.concatenate([L, zeros], axis=1)
        elif L.shape[1] != 3:
            # Unexpected shape; skip
            return

        # Pull indices from configuration
        i_thumb, i_index = self.pinch_indices
        i_wrist, i_mid = self.axis_indices

        # Basic bounds check
        if (
            i_thumb >= L.shape[0] or i_index >= L.shape[0]
            or i_wrist >= L.shape[0] or i_mid >= L.shape[0]
        ):
            return

        # --- Pick position: midpoint between thumb tip and index tip ---
        pick_3d = 0.5 * (L[i_thumb] + L[i_index])

        # --- Axis: wrist -> middle MCP ---
        axis_vec = L[i_mid] - L[i_wrist]
        axis_norm = np.linalg.norm(axis_vec)
        if axis_norm > 1e-6:
            axis_3d = axis_vec / axis_norm
        else:
            axis_3d = np.zeros(3, dtype=float)

        # --- Distance: norm of pick position ---
        distance = float(np.linalg.norm(pick_3d))

        # Store as HandPickResult (or dict)
        est_dict["pick"] = HandPickResult(
            pick_3d=pick_3d,
            axis_3d=axis_3d,
            distance=distance,
        )

