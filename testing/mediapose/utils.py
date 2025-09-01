import json, time
from typing import List
import numpy as np
import cv2

def draw_tracks(frame_bgr, tracks) -> None:
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

def write_jsonl(fp, obj):
    fp.write(json.dumps(obj) + "\n")
    fp.flush()
