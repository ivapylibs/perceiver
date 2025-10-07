# perceiver/testing/mediapose/utils_classic.py
import json
import numpy as np
import cv2

def _nan_to_none(x):
    if x is None: return None
    a = np.asarray(x)
    if a.ndim == 0:
        return None if not np.isfinite(a) else float(a)
    out = a.astype(object)
    out[~np.isfinite(a)] = None
    return out.tolist()

def write_jsonl(fp, row: dict):
    json.dump(row, fp)
    fp.write("\n")
    fp.flush()

def _norm_pts_to_px(pts_norm: np.ndarray, w: int, h: int, mirror: bool) -> np.ndarray:
    pts = pts_norm.copy()
    if mirror:
        pts[:, 0] = 1.0 - pts[:, 0]
    return (pts[:, :2] * np.array([w, h])[None, :]).astype(int)

def draw_hand_overlay(frame_bgr, hand, color=(0, 255, 0), mirror=False):
    if frame_bgr is None or not getattr(hand, "present", False):
        return frame_bgr

    h, w = frame_bgr.shape[:2]
    pts  = getattr(hand, "landmarks", None)      # (21,3)
    palm = getattr(hand, "palm", None)           # (6,3)

    # draw 21 dots
    if isinstance(pts, np.ndarray) and pts.shape == (21, 3):
        pts_px = _norm_pts_to_px(pts, w, h, mirror)
        for (cx, cy) in pts_px:
            cv2.circle(frame_bgr, (cx, cy), 2, color, -1)

    # draw palm polygon
    if isinstance(palm, np.ndarray) and palm.shape == (6, 3):
        palm_px = _norm_pts_to_px(palm, w, h, mirror)
        for i in range(len(palm_px)):
            p0 = tuple(palm_px[i]); p1 = tuple(palm_px[(i + 1) % len(palm_px)])
            cv2.line(frame_bgr, p0, p1, color, 2)

    # label (swap for display if mirrored)
    base = getattr(hand, "label", "hand")
    score = getattr(hand, "score", np.nan)
    disp = {"left":"right","right":"left"}.get(base, base) if mirror else base
    txt  = f"{disp} ({score:.2f})" if np.isfinite(score) else disp

    if isinstance(pts, np.ndarray) and pts.shape == (21, 3):
        wrist_px = _norm_pts_to_px(pts[[0], :], w, h, mirror)[0]
        anchor = (int(wrist_px[0]) + 6, int(wrist_px[1]) - 6)
    else:
        anchor = (10, 30 if base == "left" else 60)

    cv2.putText(frame_bgr, txt, anchor, cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2, cv2.LINE_AA)
    return frame_bgr

def draw_tracks(frame_bgr, hands, mirror=False):
    """
    Compat helper so the demo can call draw_tracks in either overlay mode.
    Draws each hand using draw_hand_overlay (left green, right blue).
    """
    for h in hands:
        color = (0, 255, 0) if getattr(h, "label", "left") == "left" else (255, 0, 0)
        draw_hand_overlay(frame_bgr, h, color=color, mirror=mirror)
    return frame_bgr
