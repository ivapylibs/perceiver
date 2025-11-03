import numpy as np
import cv2

def _landmarks_to_px(pts_norm: np.ndarray, w: int, h: int, mirror: bool) -> np.ndarray:
    """Convert normalized (N,3) landmarks to pixel (N,2), respecting mirror flag."""
    pts = pts_norm.copy()
    if mirror:
        pts[:, 0] = 1.0 - pts[:, 0]     # flip x in normalized space
    return (pts[:, :2] * np.array([w, h])[None, :]).astype(np.int32)

def make_hand_mask_from_landmarks(frame_shape, hands, mirror=False,
                                  use_tips=True, dilate_iter=2, dilate_ks=7):
    """
    Build a binary uint8 mask (H,W) where hand regions are 255.
    - frame_shape: (H, W, 3) or (H, W)
    - hands: list of HandOutput or Tracks with `.present`, `.landmarks`
    - mirror: same logic as your preview overlay
    - use_tips: include fingertips to enlarge hull
    - dilate_iter/ks: grow mask (OK to be bigger than hand)
    """
    if len(frame_shape) == 3:
        H, W = frame_shape[:2]
    else:
        H, W = frame_shape

    mask = np.zeros((H, W), dtype=np.uint8)
    palm_idx = np.array([0, 1, 5, 9, 13, 17], dtype=np.int32)
    tip_idx  = np.array([4, 8, 12, 16, 20], dtype=np.int32)

    for h in hands:
        if not getattr(h, "present", False):
            continue
        pts = getattr(h, "landmarks", None)
        if not isinstance(pts, np.ndarray) or pts.shape != (21, 3) or not np.all(np.isfinite(pts)):
            continue

        idx = palm_idx
        if use_tips:
            idx = np.concatenate([palm_idx, tip_idx])

        px = _landmarks_to_px(pts[idx], W, H, mirror)  # (M,2) int
        if px.shape[0] < 3:
            continue

        # Convex hull
        hull = cv2.convexHull(px)
        cv2.fillPoly(mask, [hull], 255)

    if dilate_iter > 0 and dilate_ks > 1:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilate_ks, dilate_ks))
        mask = cv2.dilate(mask, kernel, iterations=dilate_iter)

    return mask
