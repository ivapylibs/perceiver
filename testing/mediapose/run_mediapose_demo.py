"""!
@file run_mediapose_demo.py
@brief Capture frames, run MediaPipe-Hands perceiver (legacy or API), visualize, and optionally log JSONL.
"""

from __future__ import annotations
import argparse, time, uuid, os
import numpy as np
import cv2

# Legacy perceiver (unchanged path)
from perceiver.perceiver.legacy.mediapose_perceiver import MediaPosePerceiver

# New API perceiver factory
from perceiver.perceiver.factory import load_config, build_mediapose_from_config

# Draw + logging helpers you already have
from perceiver.testing.mediapose.utils import (
    draw_hand_overlay,     # expects obj with .present and .landmarks (normalized)
    draw_palm_overlay,     # expects obj with .present and .palm (normalized)
    draw_centroid_overlay, # expects obj with .present and .centroid (normalized)
    write_jsonl,
)



# --------------------------- CLI ---------------------------

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0",
                    help="Webcam index (e.g., 0) or path to video")
    ap.add_argument("--camera_id", default="side")
    ap.add_argument("--session_id", default=None)
    ap.add_argument("--write_jsonl", default=None,
                    help="Path to JSONL file (directories will be created)")
    ap.add_argument("--no_view", action="store_true",
                    help="Disable GUI preview window")
    ap.add_argument("--mirror_view", action="store_true",
                    help="Flip the preview horizontally (labels swap on-screen only)")

    ap.add_argument("--tracker", choices=["hand", "palm", "centroid"],
                    default="hand",
                    help="What to visualize: 21×3 landmarks (hand), 6×3 palm, or 2D centroid.")

    # Perceiver selection + config
    ap.add_argument("--perceiver", choices=["legacy", "api"], default="api",
                    help="Use legacy demo perceiver or the new API-aligned perceiver.")
    ap.add_argument("--cfg", type=str, default=None,
                    help="Path to YAML config for API perceiver (overridden by CLI flags when present).")

    # Common knobs
    ap.add_argument("--mask_mode", choices=["none", "palm", "hand"], default=None,
                    help="Masking mode (owned by Detector). If unset, uses config or default.")
    ap.add_argument("--ema_alpha", type=float, default=None,
                    help="EMA smoothing factor (0,1]. If unset, uses config or default.")
    return ap.parse_args()


# --------------------------- Video I/O ---------------------------

def open_capture(src: str) -> cv2.VideoCapture:
    if src.isdigit():
        cap = cv2.VideoCapture(int(src))
    else:
        cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open source: {src}")
    return cap


# --------------------------- Helpers ---------------------------

def _maybe_list(a):
    if a is None:
        return None
    if isinstance(a, np.ndarray):
        return a.tolist()
    return a

def _temp_obj(**fields):
    """Tiny shim to satisfy draw_*_overlay helpers that expect attributes."""
    return type("Tmp", (), fields)()

def _normalize_cfg_shape(cfg: dict) -> dict:
    """
    Accept older configs like:
      perceiver: "mediapose"
      trackpointer: { name: "hand", params: {...} }
    and normalize to:
      perceiver:
        name: "mediapose"
        trackpointer: { name: "...", params: {...} }
    """
    # Perceiver as string -> expand to dict
    if isinstance(cfg.get("perceiver"), str):
        name = cfg["perceiver"]
        tp = cfg.pop("trackpointer", None)  # lift old top-level trackpointer if present
        cfg["perceiver"] = {"name": name}
        if tp is not None:
            cfg["perceiver"]["trackpointer"] = tp

    # Ensure nested trackpointer exists
    cfg.setdefault("perceiver", {}).setdefault("trackpointer", {"name": "hand", "params": {}})
    # Ensure detector/estimator nodes exist
    cfg.setdefault("detector", {}).setdefault("params", {})
    cfg.setdefault("estimator", {}).setdefault("filters", [])
    return cfg


# --------------------------- Main ---------------------------

def main():
    args = parse_args()
    session_id = args.session_id or f"puzzle_{int(time.time())}_{uuid.uuid4().hex[:6]}"

    out_fp = None
    if args.write_jsonl:
        os.makedirs(os.path.dirname(args.write_jsonl) or ".", exist_ok=True)
        out_fp = open(args.write_jsonl, "w")

    cap = open_capture(args.source)

    # Build perceiver (legacy or API)
    perc_legacy = None
    perc_api = None

    if args.perceiver == "legacy":
        # Legacy path: your existing class; pass mask_mode if provided, else "none"
        legacy_mask_mode = args.mask_mode if args.mask_mode is not None else "none"
        perc_legacy = MediaPosePerceiver(
            tracker=args.tracker,
            ema_alpha=args.ema_alpha,            # legacy will ignore if None
            mask_mode=legacy_mask_mode,
            mirror=args.mirror_view,
        )

    else:  # API path
        if args.cfg:
            cfg = load_config(args.cfg)
            cfg = _normalize_cfg_shape(cfg)

            # Apply CLI overrides to YAML (after normalization)
            if args.tracker is not None:
                cfg["perceiver"]["trackpointer"]["name"] = args.tracker

            if args.mask_mode is not None:
                cfg["detector"]["params"]["mask_mode"] = args.mask_mode

            if args.ema_alpha is not None:
                cfg["estimator"]["filters"] = [{"name": "ema", "params": {"alpha": float(args.ema_alpha)}}]

            #print("[EFFECTIVE] tracker=", cfg["perceiver"]["trackpointer"]["name"],
                #"mask_mode=", cfg["detector"]["params"].get("mask_mode"))
        else:
            # Minimal default config mirrors your YAML
            cfg = {
                "perceiver": "mediapose",
                "detector": {
                    "name": "mediapipe_hands",
                    "params": {
                        "mask_mode": "none",
                        "mirror": bool(args.mirror_view),
                        "det_conf": 0.4,
                        "track_conf": 0.4,
                        "max_hands": 2,
                    },
                },
                "trackpointer": {"name": args.tracker, "params": {}},
                "estimator": {"filters": [{"name": "ema", "params": {"alpha": 0.6}}]},
            }

        # CLI overrides (win over YAML)
        if args.mask_mode is not None:
            cfg.setdefault("detector", {}).setdefault("params", {})["mask_mode"] = args.mask_mode
        if args.ema_alpha is not None:
            cfg.setdefault("estimator", {})["filters"] = [{"name": "ema", "params": {"alpha": float(args.ema_alpha)}}]

        perc_api = build_mediapose_from_config(cfg)

    prev_t = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            # Choose path
            if args.perceiver == "api":
                # --- API pipeline ---
                result = perc_api.process(frame, timestamp=time.time())
                tracks = result.tracks.items  # list of dicts

                if tracks:
                    print("TRACK KEYS SAMPLE:", list(tracks[0].keys()))

                # --- New: visualize pick position and log distance from Tracks ---
                if args.tracker == "hand":
                    h_img, w_img = frame.shape[:2]

                    for t in tracks:
                        pick = t.get("pick", None)
                        if pick is None:
                            continue

                        pos = np.asarray(pick.get("pos", None))
                        if pos.size < 2:
                            continue

                        frame_name = pick.get("frame", "normalized")
                        distance   = pick.get("distance", None)
                        axis       = pick.get("axis", None)
                        pinch_dist = pick.get("pinch_dist", None)
                        pinch_ratio = pick.get("pinch_ratio", None)
                        is_picking  = pick.get("is_picking", None)

                        # ---- safe formatting helpers ----
                        def _fmt(val):
                            try:
                                if val is None:
                                    return "None"
                                return f"{float(val):.3f}"
                            except (TypeError, ValueError):
                                return "None"

                        dist_str  = _fmt(distance)
                        pinch_str = _fmt(pinch_dist)
                        ratio_str = _fmt(pinch_ratio)

                        print(
                            f"[Track {t.get('id')}] "
                            f"frame={frame_name} "
                            f"dist={dist_str} "
                            f"pinch={pinch_str} "
                            f"ratio={ratio_str} "
                            f"is_picking={is_picking} "
                            f"pos={pos} "
                            f"axis={axis}"
                        )

                        # --- drawing: ALWAYS use normalized landmarks for 2D overlay ---
                        lm = t.get("landmarks", None)
                        if lm is None:
                            continue

                        L = np.asarray(lm, dtype=np.float32)
                        if L.ndim != 2 or L.shape[0] <= 9:
                            continue

                        L_xy = L[:, :2]
                        thumb_xy = L_xy[4]
                        index_xy = L_xy[8]
                        wrist_xy = L_xy[0]
                        mid_xy   = L_xy[9]

                        pinch_center = 0.5 * (thumb_xy + index_xy)
                        u = int(pinch_center[0] * w_img)
                        v = int(pinch_center[1] * h_img)

                        cv2.circle(frame, (u, v), 6, (0, 255, 0), -1)

                        axis_2d = mid_xy - wrist_xy
                        axis_norm = np.linalg.norm(axis_2d)
                        if axis_norm > 1e-6:
                            axis_2d = axis_2d / axis_norm
                            end_point = (
                                int(u + 40 * axis_2d[0]),
                                int(v + 40 * axis_2d[1]),
                            )
                            cv2.line(frame, (u, v), end_point, (0, 255, 0), 2)




                # Optional: debug mask window (owned by detector)
                if not args.no_view:
                    mask = getattr(perc_api.det, "_last_mask", None)  # detector is public on API class
                    if mask is not None:
                        mask_vis = mask.astype(np.uint8) * 255
                        cv2.imshow("HAND MASK (debug)", mask_vis)

                preview = cv2.flip(frame, 1) if args.mirror_view else frame

                # Draw based on selected tracker type
                if args.tracker == "hand":
                    for t in tracks:
                        lm = t.get("landmarks")
                        if lm is None:
                            continue
                        color = (0, 255, 0) if t.get("label") == "left" else (255, 0, 0)
                        preview = draw_hand_overlay(
                            preview,
                            _temp_obj(present=True, landmarks=lm),
                            color,
                            mirror=args.mirror_view,
                        )

                elif args.tracker == "palm":
                    for t in tracks:
                        palm = t.get("palm")
                        if palm is None:
                            continue
                        color = (0, 255, 0) if t.get("label") == "left" else (255, 0, 0)
                        preview = draw_palm_overlay(
                            preview,
                            _temp_obj(present=True, palm=palm),
                            color,
                            mirror=args.mirror_view,
                        )

                elif args.tracker == "centroid":
                    for t in tracks:
                        cen = t.get("centroid")
                        if cen is None:
                            continue
                        color = (0, 255, 0) if t.get("label") == "left" else (255, 0, 0)
                        preview = draw_centroid_overlay(
                            preview,
                            _temp_obj(present=True, centroid=cen),
                            color,
                            mirror=args.mirror_view,
                        )

                # JSON logging (API)
                if out_fp:
                    row = {
                        "ts": time.time(),
                        "session_id": session_id,
                        "camera_id": args.camera_id,
                        "perceiver": "api",
                        "tracker": args.tracker,
                        "det_count": len(result.detections.items),
                        "trk_count": len(tracks),
                        "est_ids": list(result.estimates.items.keys()) if result.estimates is not None else [],
                        "tracks": [
                            {
                                "id": t.get("id"),
                                "label": t.get("label"),
                                "score": _maybe_list(t.get("score")),
                                "landmarks": _maybe_list(t.get("landmarks")),
                                "palm": _maybe_list(t.get("palm")),
                                "centroid": _maybe_list(t.get("centroid")),
                            }
                            for t in tracks
                        ],
                    }
                    write_jsonl(out_fp, row)

            else:
                # --- Legacy pipeline (unchanged behavior) ---
                hands = perc_legacy.track(perc_legacy.detect(frame))

                # Optional: debug mask window
                if not args.no_view:
                    mask = getattr(perc_legacy.det, "_last_mask", None)
                    if mask is not None:
                        mask_vis = mask.astype(np.uint8) * 255
                        cv2.imshow("HAND MASK (debug)", mask_vis)

                preview = cv2.flip(frame, 1) if args.mirror_view else frame

                if args.tracker == "hand":
                    preview = draw_hand_overlay(preview, hands[0], (0, 255, 0), mirror=args.mirror_view)
                    preview = draw_hand_overlay(preview, hands[1], (255, 0, 0), mirror=args.mirror_view)

                elif args.tracker == "palm":
                    preview = draw_palm_overlay(preview, hands[0], (0, 255, 0), mirror=args.mirror_view)
                    preview = draw_palm_overlay(preview, hands[1], (255, 0, 0), mirror=args.mirror_view)

                elif args.tracker == "centroid":
                    preview = draw_centroid_overlay(preview, hands[0], (0, 255, 0), mirror=args.mirror_view)
                    preview = draw_centroid_overlay(preview, hands[1], (255, 0, 0), mirror=args.mirror_view)

                # JSON logging (legacy)
                if out_fp:
                    row = {
                        "ts": time.time(),
                        "session_id": session_id,
                        "camera_id": args.camera_id,
                        "perceiver": "legacy",
                        "tracker": args.tracker,
                        "left": {
                            "present": bool(hands[0].present),
                            "score": float(hands[0].score) if np.isfinite(getattr(hands[0], "score", np.nan)) else None,
                            "landmarks": _maybe_list(getattr(hands[0], "landmarks", None)),
                            "palm": _maybe_list(getattr(hands[0], "palm", None)),
                            "centroid": _maybe_list(getattr(hands[0], "centroid", None)),
                        },
                        "right": {
                            "present": bool(hands[1].present),
                            "score": float(hands[1].score) if np.isfinite(getattr(hands[1], "score", np.nan)) else None,
                            "landmarks": _maybe_list(getattr(hands[1], "landmarks", None)),
                            "palm": _maybe_list(getattr(hands[1], "palm", None)),
                            "centroid": _maybe_list(getattr(hands[1], "centroid", None)),
                        },
                    }
                    write_jsonl(out_fp, row)

            # --- FPS overlay + display ---
            now = time.time()
            fps = 1.0 / max(1e-6, (now - prev_t))
            prev_t = now
            if not args.no_view:
                cv2.putText(preview, f"FPS: {fps:.1f}", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
                cv2.imshow("mediapose demo", preview)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC
                    break

    finally:
        cap.release()
        try:
            if args.perceiver == "legacy" and perc_legacy is not None:
                perc_legacy.close()
            elif args.perceiver == "api" and perc_api is not None:
                # Close underlying detector cleanly
                if hasattr(perc_api, "det") and hasattr(perc_api.det, "close"):
                    perc_api.det.close()
        except Exception:
            pass
        if out_fp:
            out_fp.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
