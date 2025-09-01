import time
from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
import cv2

try:
    import mediapipe as mp
except ImportError as e:
    raise ImportError("Install mediapipe: pip install mediapipe") from e


@dataclass
class Track:
    id: str              # "left" or "right"
    score: float
    landmarks: np.ndarray  # (21,3), normalized [0..1]
    kind: str            # "left_hand" or "right_hand"


class EMAFilter:
    def __init__(self, alpha: float = 0.4):
        self.alpha = alpha
        self.prev: Optional[np.ndarray] = None

    def reset(self):
        self.prev = None

    def __call__(self, pts: np.ndarray) -> np.ndarray:
        if self.prev is None:
            self.prev = pts.copy()
            return pts
        self.prev = self.alpha * pts + (1 - self.alpha) * self.prev
        return self.prev


class MediaPosePerceiver:
    """
    Perceiver instance = Detector (MediaPipe Hands) + Tracker (handedness/EMA).
    - detect(frame_bgr) -> raw detections
    - track(dets) -> stable IDs + smoothed landmarks
    """
    def __init__(self, max_hands=2, det_conf=0.5, track_conf=0.5, ema_alpha=0.4):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=det_conf,
            min_tracking_confidence=track_conf,
            model_complexity=1,
        )
        # Simple per-ID filters
        self.filters = {"left": EMAFilter(ema_alpha), "right": EMAFilter(ema_alpha)}

    def close(self):
        self.hands.close()

    def detect(self, frame_bgr) -> List[Dict]:
        h, w = frame_bgr.shape[:2]
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        res = self.hands.process(frame_rgb)
        out = []

        if not res.multi_hand_landmarks:
            return out

        for lm, handed in zip(res.multi_hand_landmarks, res.multi_handedness):
            # landmarks normalized to [0,1] by MediaPipe (x,y), z in roughly meters normalized by image width
            pts = np.array([[p.x, p.y, p.z] for p in lm.landmark], dtype=np.float32)  # (21,3)
            score = handed.classification[0].score
            label = handed.classification[0].label.lower()  # 'left' or 'right'
            out.append({
                "score": float(score),
                "handedness": label,
                "landmarks": pts,   # normalized
            })
        return out

    def track(self, detections: List[Dict]) -> List[Track]:
        """
        Assign stable IDs by handedness; smooth with EMA.
        """
        tracks: List[Track] = []
        seen = set()
        for det in detections:
            hid = det["handedness"] if det["handedness"] in ("left", "right") else None
            if hid is None:
                # Fallback: nearest slot not used yet
                hid = "left" if "left" not in seen else "right"
            seen.add(hid)
            filt = self.filters[hid]
            smoothed = filt(det["landmarks"])
            kind = f"{hid}_hand"
            tracks.append(Track(id=hid, score=det["score"], landmarks=smoothed, kind=kind))
        # reset filters for hands not seen this frame (optional)
        for k in ("left", "right"):
            if k not in seen:
                self.filters[k].reset()
        return tracks
