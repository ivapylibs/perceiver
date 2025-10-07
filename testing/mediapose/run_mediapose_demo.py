"""!
@file run_mediapose_demo.py
@brief Demo runner: capture frames, run MediaPipe-Hands perceiver (detect+track), visualize, and log JSONL.
"""

from __future__ import annotations
import argparse, time, uuid, os
import numpy as np
import cv2

# perceiver wrapper
from perceiver.perceiver.mediapose_perceiver import MediaPosePerceiver
# just the minimal helpers we actually use:
from perceiver.testing.mediapose.utils import (
    draw_hand_overlay,     # draws 21 pts + palm poly + label (+centroid if present)
    draw_palm_overlay,     # (add this simple helper, see below)
    draw_centroid_overlay, # (add this simple helper, see below)
    write_jsonl,
)

# ---------- CLI ----------

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
    ap.add_argument("--ema_alpha", type=float, default=0.4,
                    help="EMA smoothing factor (0,1]; lower = smoother)")
    ap.add_argument(
        "--tracker",
        choices=["hand", "palm", "centroid"],
        default="hand",
        help="Which tracker to run: 21×3 landmarks (hand), 6×3 palm, or 2D centroid.",
    )
    return ap.parse_args()

# ---------- Video I/O ----------

def open_capture(src: str) -> cv2.VideoCapture:
    if src.isdigit():
        cap = cv2.VideoCapture(int(src))
    else:
        cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open source: {src}")
    return cap

# ---------- Main ----------

def main():
    args = parse_args()
    session_id = args.session_id or f"puzzle_{int(time.time())}_{uuid.uuid4().hex[:6]}"

    out_fp = None
    if args.write_jsonl:
        os.makedirs(os.path.dirname(args.write_jsonl) or ".", exist_ok=True)
        out_fp = open(args.write_jsonl, "w")

    cap = open_capture(args.source)
    perc = MediaPosePerceiver(tracker= args.tracker,ema_alpha=args.ema_alpha)

    prev_t = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

             # --- detect + track on the *raw* frame so JSON is in true coords ---
            hands = perc.track(perc.detect(frame))

            # preview (for mirror) and draw
            preview = cv2.flip(frame, 1) if args.mirror_view else frame

            if args.tracker == "hand":
                # hands[i] has: label, present, score, landmarks (21x3)
                preview = draw_hand_overlay(preview, hands[0], (0,255,0),  mirror=args.mirror_view)
                preview = draw_hand_overlay(preview, hands[1], (255,0,0),  mirror=args.mirror_view)

            elif args.tracker == "palm":
                # hands[i] has: label, present, score, palm (6x3)  (from PalmTracker)
                preview = draw_palm_overlay(preview, hands[0], (0,255,0),  mirror=args.mirror_view)
                preview = draw_palm_overlay(preview, hands[1], (255,0,0),  mirror=args.mirror_view)

            elif args.tracker == "centroid":
                # hands[i] has: label, present, score, centroid (2,)  (from CentroidTracker)
                preview = draw_centroid_overlay(preview, hands[0], (0,255,0),  mirror=args.mirror_view)
                preview = draw_centroid_overlay(preview, hands[1], (255,0,0),  mirror=args.mirror_view)


            # FPS overlay
            now = time.time()
            fps = 1.0 / max(1e-6, (now - prev_t))
            prev_t = now
            cv2.putText(preview, f"FPS: {fps:.1f}", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

            # logging (JSON-safe)
            def _maybe_list(a):
                if a is None: return None
                if isinstance(a, np.ndarray): return a.tolist()
                return a

            if out_fp:

                row = {
                    "ts": time.time(),
                    "tracker": args.tracker,
                    "left": {
                        "present": bool(hands[0].present),
                        "score": float(hands[0].score) if np.isfinite(getattr(hands[0], "score", np.nan)) else None,
                        "landmarks": _maybe_list(getattr(hands[0], "landmarks", None)),
                        "palm":      _maybe_list(getattr(hands[0], "palm", None)),
                        "centroid":  _maybe_list(getattr(hands[0], "centroid", None)),
                    },
                    "right": {
                        "present": bool(hands[1].present),
                        "score": float(hands[1].score) if np.isfinite(getattr(hands[1], "score", np.nan)) else None,
                        "landmarks": _maybe_list(getattr(hands[1], "landmarks", None)),
                        "palm":      _maybe_list(getattr(hands[1], "palm", None)),
                        "centroid":  _maybe_list(getattr(hands[1], "centroid", None)),
                    },
                }
                write_jsonl(out_fp, row)

            # --- FPS ---
            now = time.time()
            fps = 1.0 / max(1e-6, (now - prev_t))
            prev_t = now
            cv2.putText(preview, f"FPS: {fps:.1f}", (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
        
            if not args.no_view:
                # one window, draw the preview we just composed
                cv2.imshow("mediapose demo", preview)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC
                    break

    finally:
        cap.release()
        perc.close()
        if out_fp: out_fp.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
