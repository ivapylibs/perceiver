"""!
@file run_mediapose_demo.py
@brief Demo runner: capture frames, run MediaPipe-Hands perceiver (detect+track), visualize, and log JSONL.
@ingroup Perceiver

@details
Opens a video source (webcam index or file), converts frames to RGB for MediaPipe,
runs detection and tracking via the mediapose perceiver, overlays landmarks/FPS,
and optionally writes one JSON object per frame to a JSONL file. Designed as a
testing/validation script prior to integrating into the Perceiver package API.
"""

import argparse, time, uuid
import cv2
import numpy as np
from perceiver.mediapose_perceiver import MediaPosePerceiver
from perceiver.testing.mediapose.utils import write_jsonl, draw_hand_overlay

def parse_args():
    """!
    @brief Build command-line interface for the mediapose demo.

    @return argparse.Namespace with:
      - source: str; "0", "1", ... for webcam index or a file path.
      - camera_id: str; label for the camera/view (e.g., "side", "overhead").
      - session_id: str; optional run/session identifier (auto-generated if omitted).
      - write_jsonl: str; path to output JSONL file (created if missing directories).
      - no_view: bool; if true, no GUI window is displayed.
      - ema_alpha: float; EMA smoothing factor in (0,1].
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0",
                    help="Webcam index (e.g., 0) or path to video")
    ap.add_argument("--camera_id", default="side")
    ap.add_argument("--session_id", default=None)
    ap.add_argument("--write_jsonl", default=None)
    ap.add_argument("--no_view", action="store_true")
    ap.add_argument("--ema_alpha", type=float, default=0.4)
    ap.add_argument("--mirror_view", action = "store_true", help="Flip preview horizontally (mirror-like). Only affects display, not logs.")
    return ap.parse_args()

def open_capture(src: str):
    """!
    @brief Open an OpenCV video capture from webcam index or file path.

    @param src String "0", "1", ... for webcam index, or a filesystem path to a video file.
    @return cv2.VideoCapture opened for reading frames.

    @note On macOS, AVFoundation backend (cv2.CAP_AVFOUNDATION) is best for webcams.
    @warning If the source cannot be opened, this function raises a RuntimeError.
    """
    if src.isdigit():
        cap = cv2.VideoCapture(int(src))
    else:
        cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open source: {src}")
    return cap

def main():
    """!
    @brief Main capture loop: read frame -> detect -> track -> overlay -> log.

    @details
    - Reads frames from the capture source.
    - Converts BGR->RGB for MediaPipe and runs the perceiver's detect() and track().
    - If logging is enabled, writes one JSON object per frame with fields:
        t (float seconds), frame_idx (int), camera_id (str), session_id (str),
        tracks (list of {id, kind, score, landmarks(21x3)}).
    - If viewing is enabled, overlays landmarks/labels/FPS and displays a window.

    @note Landmarks are normalized (x,y ∈ [0,1]; z is a relative depth, not metric).
    @warning Press ESC to exit the windowed demo; proper cleanup releases camera and GUI.
    """
     
    args = parse_args()
    session_id = args.session_id or f"puzzle_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    out_fp = open(args.write_jsonl, "w") if args.write_jsonl else None

    cap = open_capture(args.source)
    perc = MediaPosePerceiver(ema_alpha=args.ema_alpha)
    prev_t = time.time(); frames = 0

    try:
        while True:
            
            ok, frame = cap.read()
            if not ok: break

            frames += 1

            hands = perc.track(perc.detect(frame))
            preview = cv2.flip(frame, 1) if args.mirror_view else frame
            preview = draw_hand_overlay(preview, hands[0], (0,255,0), mirror=args.mirror_view)
            preview = draw_hand_overlay(preview, hands[1], (255,0,0), mirror=args.mirror_view)
            if out_fp:
                row = {
                    "ts": time.time(),
                    "frame_idx": frames - 1,
                    "session_id": session_id,
                    "camera_id": args.camera_id,
                    "source": f"file:{args.source}" if not args.source.isdigit() else f"live:{args.source}",
                    "hands": {
                        "left": {
                            "present": bool(hands[0].present),
                            "score": float(hands[0].score) if np.isfinite(hands[0].score) else float("nan"),
                            "handedness": hands[0].label,
                            "landmarks": hands[0].landmarks,   # np.ndarray -> handled by sanitizer
                            "palm": hands[0].palm,
                            "fingers": hands[0].fingers,
                        },
                        "right": {
                            "present": bool(hands[1].present),
                            "score": float(hands[1].score) if np.isfinite(hands[1].score) else float("nan"),
                            "handedness": hands[1].label,
                            "landmarks": hands[1].landmarks,
                            "palm": hands[1].palm,
                            "fingers": hands[1].fingers,
                        }
                    }
                }
                write_jsonl(out_fp, row)

            now = time.time()
            fps = 1.0 / max(1e-6, (now - prev_t))
            prev_t = now
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2, cv2.LINE_AA)

            if not args.no_view:
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
