# perceiver/testing/mediapose/run_mediapose_offline_monitor.py
from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any, Dict, Optional, Tuple, List

import cv2
import numpy as np

from perceiver.factory import load_config, build_mediapose_from_config
from perceiver.monitor2 import Monitor, CfgMonitor
from perceiver.hand_pick_activity import HandPickActivity

# Visualization + capture helpers live here (per your note)
from .utils import (
    open_capture,
    draw_hand_overlay,
    draw_palm_overlay,
    draw_centroid_overlay,
)


def _temp_obj(**fields):
    """Tiny shim to satisfy draw_*_overlay helpers that expect attributes."""
    return type("Tmp", (), fields)()


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser("run_mediapose_offline_monitor")

    p.add_argument("--source", required=True, help="Camera index (e.g. 0) or video path.")
    p.add_argument("--cfg", default=None, help="Path to YAML config. If omitted, uses defaults.")

    p.add_argument("--tracker", choices=["hand", "palm", "centroid"], default=None, help="Override tracker.")
    p.add_argument("--mask_mode", choices=["none", "palm", "hand"], default=None, help="Override mask mode.")
    p.add_argument("--ema_alpha", default=None, help="Override EMA alpha (float). Use 'None' to disable.")
    p.add_argument("--mirror_view", action="store_true", help="Mirror input view (passed to detector config).")

    p.add_argument("--write_jsonl", default=None, help="Write results to JSONL file.")
    p.add_argument("--max_frames", type=int, default=0, help="Stop after N frames (0 = unlimited).")

    p.add_argument("--no_view", action="store_true", help="Disable OpenCV preview window.")
    p.add_argument("--print_every", type=int, default=60, help="Print a short status line every N frames.")

    # Visual debugging knobs
    p.add_argument("--show_mask", action="store_true", help="Show detector mask debug window if available.")
    p.add_argument("--show_pick", action="store_true", help="Overlay pinch center/axis and distance (hand tracker only).")
    p.add_argument("--show_activity", action="store_true", help="Overlay activity FSM state text.")
    p.add_argument("--window_name", default="offline_monitor", help="OpenCV window name.")
    return p.parse_args()


def _coerce_source(src: str) -> Any:
    s = str(src).strip()
    if s.isdigit():
        return int(s)
    return src


def _default_cfg(args: argparse.Namespace) -> Dict[str, Any]:
    # Mirrors your API-branch minimal default dict
    # NOTE: pick/pnp settings live in calibration cfg (MediaPoseCalibration / HandPickFilter)
    return {
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
        "trackpointer": {"name": "hand", "params": {}},
        "estimator": {"filters": []},
    }


def _normalize_cfg(cfg: Dict[str, Any]) -> Dict[str, Any]:
    # Minimal normalization matching your demo intent
    out = cfg if isinstance(cfg, dict) else {}
    out.setdefault("perceiver", "mediapose")
    out.setdefault("detector", {"name": "mediapipe_hands", "params": {}})
    if "trackpointer" not in out and not (
        isinstance(out.get("perceiver"), dict) and "trackpointer" in out["perceiver"]
    ):
        out["trackpointer"] = {"name": "hand", "params": {}}
    out.setdefault("estimator", {"filters": []})
    return out


def _apply_cli_overrides(cfg: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    cfg = _normalize_cfg(cfg)

    # tracker override (works for both legacy and nested perceiver shapes)
    if args.tracker is not None:
        if isinstance(cfg.get("perceiver"), dict):
            cfg["perceiver"].setdefault("trackpointer", {})
            cfg["perceiver"]["trackpointer"]["name"] = args.tracker
        else:
            cfg.setdefault("trackpointer", {})
            cfg["trackpointer"]["name"] = args.tracker

    # detector overrides
    if args.mask_mode is not None:
        cfg.setdefault("detector", {}).setdefault("params", {})
        cfg["detector"]["params"]["mask_mode"] = args.mask_mode

    if args.mirror_view:
        cfg.setdefault("detector", {}).setdefault("params", {})
        cfg["detector"]["params"]["mirror"] = True

    # estimator EMA override
    if args.ema_alpha is not None:
        if str(args.ema_alpha).strip().lower() in ("none", "null", ""):
            cfg.setdefault("estimator", {}).setdefault("filters", [])
            cfg["estimator"]["filters"] = [
                f for f in cfg["estimator"]["filters"]
                if not (isinstance(f, dict) and f.get("name") == "ema")
            ]
        else:
            alpha = float(args.ema_alpha)
            cfg.setdefault("estimator", {}).setdefault("filters", [])
            filters = cfg["estimator"]["filters"]
            replaced = False
            for f in filters:
                if isinstance(f, dict) and f.get("name") == "ema":
                    f["params"] = {"alpha": alpha}
                    replaced = True
                    break
            if not replaced:
                filters.insert(0, {"name": "ema", "params": {"alpha": alpha}})
            cfg["estimator"]["filters"] = filters

    return cfg


def _get_tracker_name_from_cfg(cfg: Dict[str, Any]) -> str:
    # supports both shapes:
    # legacy: cfg["trackpointer"]["name"]
    # nested: cfg["perceiver"]["trackpointer"]["name"]
    pnode = cfg.get("perceiver", None)
    if isinstance(pnode, dict):
        tp = pnode.get("trackpointer", {}) or {}
        name = tp.get("name", "hand")
    else:
        tp = cfg.get("trackpointer", {}) or {}
        name = tp.get("name", "hand")
    name = str(name)
    if name not in ("hand", "palm", "centroid"):
        return "hand"
    return name


def _jsonify(obj: Any) -> Any:
    # Numpy
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)

    # dataclasses / objects with __dict__
    if hasattr(obj, "__dict__") and not isinstance(obj, type):
        return {k: _jsonify(v) for k, v in obj.__dict__.items()}

    # dict/list/tuple
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]

    return obj


def _color_for_label(label: Optional[str]) -> Tuple[int, int, int]:
    # BGR like your demo (left=green, right=blue-ish)
    if label == "left":
        return (0, 255, 0)
    return (255, 0, 0)


def _overlay_pick_from_estimates(
    img: np.ndarray,
    track_item: Dict[str, Any],
    pick: Dict[str, Any],
    mirror: bool,
) -> None:
    """
    Draw pinch center + 2D axis line in image coordinates.
    We intentionally ALWAYS use normalized landmark XY for 2D overlay,
    even when pick.frame == camera (PnP).
    """
    lm = track_item.get("landmarks", None)
    if lm is None:
        return

    L = np.asarray(lm, dtype=np.float32)
    if L.ndim != 2 or L.shape[0] <= 9:
        return

    h_img, w_img = img.shape[:2]

    L_xy = L[:, :2]
    thumb_xy = L_xy[4]
    index_xy = L_xy[8]
    wrist_xy = L_xy[0]
    mid_xy = L_xy[9]

    if not (np.isfinite(thumb_xy).all() and np.isfinite(index_xy).all()
            and np.isfinite(wrist_xy).all() and np.isfinite(mid_xy).all()):
        return

    pinch_center = 0.5 * (thumb_xy + index_xy)

    # Convert to pixel
    u = int(pinch_center[0] * w_img)
    v = int(pinch_center[1] * h_img)

    # If the DISPLAY is mirrored, flip the drawn x-coordinate accordingly.
    # (We mirror the final preview image, so we should also mirror overlay coords.)
    if mirror:
        u = (w_img - 1) - u

    cv2.circle(img, (u, v), 6, (0, 255, 0), -1)

    axis_2d = mid_xy - wrist_xy
    axis_norm = float(np.linalg.norm(axis_2d))
    if axis_norm > 1e-6:
        axis_2d = axis_2d / axis_norm
        # If mirrored display, flip axis x-direction
        if mirror:
            axis_2d[0] *= -1.0

        end_point = (
            int(u + 40 * axis_2d[0]),
            int(v + 40 * axis_2d[1]),
        )
        cv2.line(img, (u, v), end_point, (0, 255, 0), 2)

    # text: distance/pinch ratio near pinch center
    dist = pick.get("distance", None)
    ratio = pick.get("pinch_ratio", None)
    frame_name = pick.get("frame", "normalized")

    def _fmt(val):
        try:
            if val is None:
                return "None"
            return f"{float(val):.3f}"
        except Exception:
            return "None"

    txt = f"{frame_name} dist={_fmt(dist)} ratio={_fmt(ratio)}"
    cv2.putText(img, txt, (u + 10, v - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)


def main() -> None:
    args = _parse_args()
    src = _coerce_source(args.source)

    # ---- config ----
    if args.cfg:
        cfg = load_config(args.cfg)
    else:
        cfg = _default_cfg(args)

    cfg = _apply_cli_overrides(cfg, args)
    tracker_mode = _get_tracker_name_from_cfg(cfg)

    # ---- build perceiver ----
    perc = build_mediapose_from_config(cfg)

    # ---- build activity + monitor ----
    activity = HandPickActivity()
    mcfg = CfgMonitor({"external": False, "display": "none", "displayDebug": "none"})
    mon = Monitor(mcfg, perc, activity, theReporter=None)

    # ---- capture ----
    cap = open_capture(src)

    out_fp = None
    if args.write_jsonl:
        os.makedirs(os.path.dirname(args.write_jsonl) or ".", exist_ok=True)
        out_fp = open(args.write_jsonl, "w")

    frame_idx = 0
    t0 = time.time()
    prev_t = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                break

            ts = time.time()

            # Core pipeline: Monitor will call perceiver.process(frame) and activity.process(perceiver.getState())
            mon.process(frame)

            # Grab states for logging + display
            pstate = perc.getState()
            astate = mon.getState()

            # JSONL
            if out_fp is not None:
                row = {
                    "frame_idx": frame_idx,
                    "timestamp": ts,
                    "perception": _jsonify(pstate),
                    "activity_state": _jsonify(astate),
                }
                out_fp.write(json.dumps(row) + "\n")

            # ---- VIEW PATH (API-aligned visuals) ----
            if not args.no_view:
                preview = frame.copy()

                # If you want the preview mirrored, we will mirror the final image.
                # For overlays that depend on pixel coordinates, we adjust in helper where needed.
                mirror_disp = bool(args.mirror_view)

                # 1) Draw tracker geometry from Tracks (API dicts)
                tracks_items = []
                try:
                    tracks_items = list(pstate.tracks.items) if pstate.tracks is not None else []
                except Exception:
                    tracks_items = []

                if tracker_mode == "hand":
                    for t in tracks_items:
                        lm = t.get("landmarks", None)
                        if lm is None:
                            continue
                        color = _color_for_label(t.get("label", None))
                        preview = draw_hand_overlay(
                            preview,
                            _temp_obj(present=True, landmarks=lm),
                            color,
                            mirror= False,
                        )

                elif tracker_mode == "palm":
                    for t in tracks_items:
                        palm = t.get("palm", None)
                        if palm is None:
                            continue
                        color = _color_for_label(t.get("label", None))
                        preview = draw_palm_overlay(
                            preview,
                            _temp_obj(present=True, palm=palm),
                            color,
                            mirror=False,
                        )

                elif tracker_mode == "centroid":
                    for t in tracks_items:
                        cen = t.get("centroid", None)
                        if cen is None:
                            continue
                        color = _color_for_label(t.get("label", None))
                        preview = draw_centroid_overlay(
                            preview,
                            _temp_obj(present=True, centroid=cen),
                            color,
                            mirror=False,
                        )

                # 2) Draw pick overlay from Estimates (API-aligned), only for hand tracker
                if args.show_pick and tracker_mode == "hand":
                    est_items = {}
                    try:
                        est_items = pstate.estimates.items if (pstate.estimates is not None) else {}
                    except Exception:
                        est_items = {}

                    for t in tracks_items:
                        tid = t.get("id", None)
                        if tid is None:
                            continue
                        est = est_items.get(tid, {})
                        if not isinstance(est, dict):
                            continue
                        pick = est.get("pick", None)
                        if not isinstance(pick, dict):
                            continue
                        _overlay_pick_from_estimates(preview, t, pick, mirror=False)

                # 3) Activity overlay (FSM state) from Monitor state
                if args.show_activity:
                    try:
                        act = astate.xActivity.get("activity", {})
                    except Exception:
                        act = {}
                    y = 30
                    for tid, st in (act or {}).items():
                        if not isinstance(st, dict):
                            continue
                        txt = f"{tid}: {st.get('state')} picking={st.get('is_picking')} conf={st.get('confidence')}"
                        cv2.putText(preview, txt, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
                        y += 22

                # 4) FPS overlay
                now = time.time()
                fps = 1.0 / max(1e-6, (now - prev_t))
                prev_t = now
                cv2.putText(preview, f"FPS: {fps:.1f}", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

                # 5) Optional mask debug window (detector-owned)
                if args.show_mask:
                    mask = getattr(getattr(perc, "det", None), "_last_mask", None)
                    if mask is not None:
                        mask_vis = (mask.astype(np.uint8) * 255)
                        if mirror_disp:
                            mask_vis = cv2.flip(mask_vis, 1)
                        cv2.imshow("HAND MASK (debug)", mask_vis)

                # Final mirror (visual preference)
                if mirror_disp:
                    preview = cv2.flip(preview, 1)

                cv2.imshow(args.window_name, preview)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC
                    break

            # ---- status print ----
            if args.print_every > 0 and (frame_idx % args.print_every == 0):
                dt = time.time() - t0
                fps = (frame_idx + 1) / max(dt, 1e-6)
                print(f"[offline_monitor] frame={frame_idx} fps={fps:.1f}")

            frame_idx += 1
            if args.max_frames and frame_idx >= args.max_frames:
                break

    finally:
        if out_fp is not None:
            out_fp.close()
        try:
            cap.release()
        except Exception:
            pass
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass


if __name__ == "__main__":
    main()
