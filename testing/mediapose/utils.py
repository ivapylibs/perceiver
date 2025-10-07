"""!
@file utils.py
@brief Visualization + JSON helpers for MediaPipe demo.
"""

from __future__ import annotations
import json
import numpy as np
import cv2

# ---------- JSON helpers ----------

def _nan_to_none(x):
    """Convert scalars/arrays with NaNs to JSON-safe None values."""
    if x is None:
        return None
    arr = np.asarray(x)
    if arr.ndim == 0:
        return None if not np.isfinite(arr) else float(arr)
    out = arr.astype(object)
    out[~np.isfinite(arr)] = None
    return out.tolist()

def write_jsonl(fp, row: dict) -> None:
    """Append one JSON object per line and flush."""
    safe = {}
    for k, v in row.items():
        if isinstance(v, (float, int, str, bool)) or v is None:
            safe[k] = v
        elif isinstance(v, dict):
            # recursively clean nested dicts
            safe[k] = {kk: _nan_to_none(vv) for kk, vv in v.items()}
        else:
            safe[k] = _nan_to_none(v)
    json.dump(safe, fp)
    fp.write("\n")
    fp.flush()

# ---------- Drawing helpers ----------

def _norm_pts_to_px(pts_norm: np.ndarray, w: int, h: int, mirror: bool) -> np.ndarray:
    """
    pts_norm: (N,3) with x,y in [0,1]. Returns (N,2) int pixel coords.
    If mirror is True, flip x in normalized space to match preview mirroring.
    """
    if pts_norm is None:
        return None
    pts = np.asarray(pts_norm).copy()
    if pts.ndim != 2 or pts.shape[1] < 2:
        return None
    if mirror:
        pts[:, 0] = 1.0 - pts[:, 0]
    px = (pts[:, :2] * np.array([w, h])[None, :]).astype(int)
    return px

def draw_hand_overlay(frame_bgr, hand, color=(0, 255, 0), mirror=False):
    """
    Draw 21 landmarks, palm polygon (0,1,5,9,13,17), on-frame label, and centroid (if present).
    Assumes hand has fields: present(bool), label(str), score(float),
    landmarks(21,3), palm(6,3), centroid((2,) or (3,)).
    """
    if frame_bgr is None or not getattr(hand, "present", False):
        return frame_bgr

    h, w = frame_bgr.shape[:2]
    pts  = getattr(hand, "landmarks", None)     # (21,3) or NaN-filled
    palm = getattr(hand, "palm", None)          # (6,3)  or NaN-filled/None

    # 21 dots
    if isinstance(pts, np.ndarray) and pts.shape == (21, 3):
        pts_px = _norm_pts_to_px(pts, w, h, mirror)
        if pts_px is not None:
            for (cx, cy) in pts_px:
                cv2.circle(frame_bgr, (int(cx), int(cy)), 2, color, -1)

    # palm polygon (closed)
    if isinstance(palm, np.ndarray) and palm.shape == (6, 3):
        palm_px = _norm_pts_to_px(palm, w, h, mirror)
        if palm_px is not None:
            for i in range(len(palm_px)):
                p0 = tuple(palm_px[i])
                p1 = tuple(palm_px[(i + 1) % len(palm_px)])
                cv2.line(frame_bgr, p0, p1, color, 2)

    # label (swap for display if mirrored)
    base_label = getattr(hand, "label", "hand")
    score = getattr(hand, "score", np.nan)
    disp_label = {"left": "right", "right": "left"}.get(base_label, base_label) if mirror else base_label
    txt = f"{disp_label} ({score:.2f})" if np.isfinite(score) else disp_label

    # anchor near wrist if available
    if isinstance(pts, np.ndarray) and pts.shape == (21, 3):
        w0 = _norm_pts_to_px(pts[[0], :], w, h, mirror)
        anchor = (int(w0[0, 0]) + 6, int(w0[0, 1]) - 6) if w0 is not None else (10, 30)
    else:
        anchor = (10, 30 if base_label == "left" else 60)

    cv2.putText(frame_bgr, txt, anchor,
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

    # centroid (normalized → pixel; mirror-aware)
    cen = getattr(hand, "centroid", None)
    if isinstance(cen, np.ndarray) and cen.size >= 2 and np.all(np.isfinite(cen[:2])):
        cen2 = np.array(cen[:2], dtype=np.float32).reshape(1, 2)
        cen3 = np.hstack([cen2, np.zeros((1, 1), dtype=np.float32)])  # make (1,3) for converter
        (cx, cy) = _norm_pts_to_px(cen3, w, h, mirror)[0]
        cv2.circle(frame_bgr, (int(cx), int(cy)), 4, (255, 255, 0), -1)

    return frame_bgr

def draw_palm_overlay(frame_bgr, hand_like, color=(255,0,0), mirror=False):
    """hand_like must have .present and .palm (6,3) or NaNs."""
    if not getattr(hand_like, "present", False): return frame_bgr
    h, w = frame_bgr.shape[:2]
    palm = getattr(hand_like, "palm", None)
    if isinstance(palm, np.ndarray) and palm.shape == (6,3):
        pts_px = _norm_pts_to_px(palm, w, h, mirror)
        for i in range(len(pts_px)):
            cv2.line(frame_bgr, tuple(pts_px[i]), tuple(pts_px[(i+1)%len(pts_px)]), color, 2)
    return frame_bgr

def draw_centroid_overlay(frame_bgr, hand_like, color=(255,255,0), mirror=False):
    """hand_like must have .present and .centroid (2,) normalized."""
    if not getattr(hand_like, "present", False): return frame_bgr
    h, w = frame_bgr.shape[:2]
    cen = getattr(hand_like, "centroid", None)
    if isinstance(cen, np.ndarray) and np.all(np.isfinite(cen)):
        (cx, cy) = _norm_pts_to_px(np.c_[cen[None,:], [[0.0]]], w, h, mirror)[0]
        cv2.circle(frame_bgr, (cx, cy), 5, color, -1)
    return frame_bgr

