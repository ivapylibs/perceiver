import argparse, time, uuid
import cv2
from mediapose_perceiver import MediaPosePerceiver
from utils import draw_tracks, write_jsonl

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0",
                    help="Webcam index (e.g., 0) or path to video")
    ap.add_argument("--camera_id", default="side")
    ap.add_argument("--session_id", default=None)
    ap.add_argument("--write_jsonl", default=None)
    ap.add_argument("--no_view", action="store_true")
    ap.add_argument("--ema_alpha", type=float, default=0.4)
    return ap.parse_args()

def open_capture(src: str):
    if src.isdigit():
        cap = cv2.VideoCapture(int(src))
    else:
        cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open source: {src}")
    return cap

def main():
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
            t = time.time(); frames += 1

            dets = perc.detect(frame)
            tracks = perc.track(dets)

            if out_fp:
                write_jsonl(out_fp, {
                    "t": t,
                    "frame_idx": frames,
                    "camera_id": args.camera_id,
                    "session_id": session_id,
                    "tracks": [
                        {
                          "id": tr.id,
                          "kind": tr.kind,
                          "score": tr.score,
                          "landmarks": tr.landmarks.tolist()
                        } for tr in tracks
                    ]
                })

            if not args.no_view:
                draw_tracks(frame, tracks)
                # FPS
                now = time.time()
                fps = 1.0 / max(1e-6, (now - prev_t))
                prev_t = now
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2, cv2.LINE_AA)
                cv2.imshow("mediapose demo", frame)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
                    break
    finally:
        cap.release()
        perc.close()
        if out_fp: out_fp.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
