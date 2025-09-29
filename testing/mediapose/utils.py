"""!
@file utils.py
@brief Utility helpers for the mediapose demo: drawing overlays and JSONL logging.
@ingroup Perceiver

@details
Provides visualization utilities to draw normalized (21x3) hand landmarks onto
BGR frames and a small writer to append one JSON object per line (JSONL format).
"""

import json, time
from typing import List
import numpy as np
import cv2
from dataclasses import dataclass
from typing import Optional
import math

def draw_tracks(frame_bgr, tracks) -> None:
    """!
    @brief Draw 21-keypoint hand landmarks and labels onto a BGR frame.

    @param frame_bgr numpy array (H,W,3) in OpenCV BGR format (modified in-place for display).
    @param tracks List of track objects or dicts with:
                  - id: "left" or "right"
                  - score: float confidence
                  - landmarks: np.ndarray (21,3) with normalized x,y and relative z
                  - kind: label string (e.g., "left_hand")

    @details
    Converts normalized x,y to pixel coordinates using the frame width/height and
    draws small circles for landmarks plus a text label near the wrist (index 0).
    May optionally draw simple connections between landmarks if provided.

    @return The same frame_bgr reference
    @note This function does not convert color spaces; pass BGR frames for display.
    """

    h, w = frame_bgr.shape[:2]
    for tr in tracks:
        pts = tr.landmarks
        # draw connections (simple: draw all points + a few key edges)
        for (x, y, _z) in pts:
            cx, cy = int(x * w), int(y * h)
            cv2.circle(frame_bgr, (cx, cy), 2, (0, 255, 0), -1)
        # label
        wrist = pts[0]
        cv2.putText(frame_bgr, f"{tr.id} ({tr.score:.2f})",
                    (int(wrist[0]*w)+5, int(wrist[1]*h)-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

def _nan_to_none(obj):
    """Recursively convert NaN/Inf to None for strict JSON."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, np.ndarray):
        return _nan_to_none(obj.tolist())
    if isinstance(obj, (list, tuple)):
        return [_nan_to_none(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _nan_to_none(v) for k, v in obj.items()}
    return obj

def write_jsonl(fp, row: dict):
    json.dump(_nan_to_none(row), fp)
    fp.write("\n")
    fp.flush()


@dataclass
class HandOutput:
    label: str    #left or right
    score: float    #detection confidence
    landmarks: np.ndarray   #(21, 3) array representing landmarks and x,y,z or filled with NaN
    present: bool   #true if detected, false otherwise
    palm: Optional[np.ndarray] = None
    fingers: Optional[np.ndarray] = None

def make_nan_hand(label: str) -> HandOutput:
    return HandOutput(
        label = label,
        score = np.nan,
        landmarks = np.full((21, 3), np.nan, dtype = np.float32),
        palm=np.full((6, 3), np.nan, dtype=np.float32),
        fingers=np.full((15, 3), np.nan, dtype=np.float32),
        present = False
    )



def draw_hand_overlay(frame_bgr, hand, color=(0, 255, 0), mirror=False):
    """
    Draw all 21 landmarks as dots, draw the palm as a closed polyline,
    and write a small label. Always returns the (possibly modified) frame.
    """
    if frame_bgr is None:
        return frame_bgr
    if not getattr(hand, "present", False):
        return frame_bgr

    h, w = frame_bgr.shape[:2]

    # helpers to convert normalized -> pixel with optional mirroring on x
    def x_px(x_norm: float) -> int:
        x = int(x_norm * w)
        return (w - 1 - x) if mirror else x

    def y_px(y_norm: float) -> int:
        return int(y_norm * h)

    # ---------- Draw all 21 landmarks ----------
    pts = getattr(hand, "landmarks", None)
    if isinstance(pts, np.ndarray) and pts.shape == (21, 3):
        for (x, y, _z) in pts:
            cv2.circle(frame_bgr, (x_px(x), y_px(y)), 2, color, -1)

    # ---------- Draw palm outline (closed loop over 6 points) ----------
    palm = getattr(hand, "palm", None)
    if isinstance(palm, np.ndarray) and palm.shape == (6, 3) and np.isfinite(palm).all():
        palm_xy = [(x_px(x), y_px(y)) for (x, y, _z) in palm]
        n = len(palm_xy)
        for i in range(n):
            cv2.line(frame_bgr, palm_xy[i], palm_xy[(i + 1) % n], color, 2)

    # ---------- Label (swap for display if mirrored) ----------
    base_label = getattr(hand, "label", "hand")
    score = getattr(hand, "score", np.nan)
    disp_label = {"left": "right", "right": "left"}.get(base_label, base_label) if mirror else base_label
    txt = f"{disp_label} ({score:.2f})" if np.isfinite(score) else disp_label

    # Anchor near wrist (0)
    if isinstance(pts, np.ndarray) and pts.shape == (21, 3):
        wx, wy, _ = pts[0]
        anchor = (x_px(wx) + 6, y_px(wy) - 6)
    else:
        anchor = (10, 30 if base_label == "left" else 60)

    cv2.putText(frame_bgr, txt, anchor,
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    return frame_bgr