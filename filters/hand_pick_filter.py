# perceiver/filters/hand_pick_filter.py
from __future__ import annotations

from typing import Optional, Any, Dict, Union

import numpy as np

from perceiver.interfaces import Filter
from perceiver.types import Tracks, Estimates

from trackpointer.calibration import MediaPoseCalibration
from trackpointer.hand_model import compute_pick_pose_camera


TrackId = Union[int, str]


class HandPickFilter(Filter):
    """
    Filter that computes per-track "pick" evidence from hand landmarks.

    Input:  Tracks (expects each track item to have: {"id": ..., "landmarks": np.ndarray (N,2|3)})
            and tracks.meta to include image_height/image_width when camera-frame PnP is desired.

    Output: Estimates with:
        estimates.items[track_id]["pick"] = {
            "frame": "camera" | "normalized",
            "pos":   (3,) or (2,),
            "axis":  (3,) or (2,),
            "distance": float | None,
            "pinch_dist": float,
            "pinch_ratio": float,
            "pick_candidate": bool,
        }
    """

    def __init__(self, cfg: dict | None = None) -> None:
        self._calib = MediaPoseCalibration.from_cfg(cfg or {})

    def reset(self) -> None:
        # stateless filter (for now)
        return

    def apply(self, tracks_or_estimates: Any, timestamp: Optional[float] = None) -> Estimates:
        # This filter is intended to be first in the chain: Tracks -> Estimates
        if not isinstance(tracks_or_estimates, Tracks):
            return Estimates(items={}, meta={"timestamp": timestamp, "note": "HandPickFilter expects Tracks input"})

        tracks: Tracks = tracks_or_estimates
        if not self._calib.pick_enabled:
            return Estimates(items={}, meta={"timestamp": timestamp, "pick_enabled": False})

        H = tracks.meta.get("image_height", None)
        W = tracks.meta.get("image_width", None)
        image_shape = (int(H), int(W)) if (H is not None and W is not None) else None

        out_items: Dict[TrackId, Dict[str, Any]] = {}

        for item in tracks.items:
            if "id" not in item:
                continue
            tid: TrackId = item["id"]

            landmarks = item.get("landmarks", None)
            if landmarks is None:
                continue

            L = np.asarray(landmarks, dtype=np.float32)
            if L.ndim != 2 or L.shape[0] < 9:
                continue

            # normalized XY view
            if L.shape[1] == 2:
                L_xy = L
            elif L.shape[1] >= 2:
                L_xy = L[:, :2]
            else:
                continue

            i_thumb, i_index = self._calib.pinch_landmarks
            i_wrist, i_mid = self._calib.axis_pair

            if (
                i_thumb >= L_xy.shape[0] or i_index >= L_xy.shape[0]
                or i_wrist >= L_xy.shape[0] or i_mid >= L_xy.shape[0]
            ):
                continue

            thumb_xy = L_xy[i_thumb]
            index_xy = L_xy[i_index]
            wrist_xy = L_xy[i_wrist]
            mid_xy = L_xy[i_mid]

            # finite guard
            if not (np.isfinite(thumb_xy).all() and np.isfinite(index_xy).all()
                    and np.isfinite(wrist_xy).all() and np.isfinite(mid_xy).all()):
                continue

            pinch_vec = thumb_xy - index_xy
            pinch_dist = float(np.linalg.norm(pinch_vec))

            hand_axis_xy = mid_xy - wrist_xy
            hand_scale = float(np.linalg.norm(hand_axis_xy))
            pinch_ratio = (pinch_dist / hand_scale) if hand_scale > 1e-6 else 1.0

            pick_candidate = bool(pinch_ratio < self._calib.pinch_ratio_thresh)

            # default (normalized)
            frame_name = "normalized"
            pos = 0.5 * (thumb_xy + index_xy)  # (2,)
            axis = (hand_axis_xy / hand_scale) if hand_scale > 1e-6 else np.array([0.0, 1.0], dtype=np.float32)
            distance = None

            # optional PnP
            if image_shape is not None and self._calib.pnp_enabled:
                K = self._calib.get_K(image_shape)
                success, pick_cam, axis_cam = compute_pick_pose_camera(
                    landmarks_norm=L,     # normalized; function uses xy internally
                    image_shape=image_shape,
                    K=K,
                )
                if success and pick_cam is not None and axis_cam is not None:
                    frame_name = "camera"
                    pos = np.asarray(pick_cam, dtype=np.float32)   # (3,)
                    axis = np.asarray(axis_cam, dtype=np.float32)  # (3,)
                    distance = float(np.linalg.norm(pos))

            out_items[tid] = {
                "pick": {
                    "frame": frame_name,
                    "pos": pos,
                    "axis": axis,
                    "distance": distance,
                    "pinch_dist": pinch_dist,
                    "pinch_ratio": pinch_ratio,
                    "pick_candidate": pick_candidate,
                }
            }

        return Estimates(
            items=out_items,
            meta={
                "timestamp": timestamp,
                "pick_enabled": self._calib.pick_enabled,
                "pnp_enabled": self._calib.pnp_enabled,
            },
        )
