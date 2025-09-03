"""!
@file mediapose_perceiver.py
@brief Perceiver instance using MediaPipe Hands (detector) plus a simple tracker and EMA smoothing.
@ingroup Perceiver

@details
This module prototypes a Perceiver consistent with the lab's definition:
a detector + tracker (+ optional filter). The detector is MediaPipe Hands,
the tracker assigns stable IDs via handedness, and an EMA filter smooths
landmark jitter frame-to-frame. Outputs are per-hand tracks with normalized
(21 x 3) landmarks (x,y in [0,1], z is a relative depth, not metric).
"""

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
    """!
    @brief Container for a single tracked hand at one frame.
    @ingroup Perceiver

    @details
    Represents one hand's smoothed landmarks and metadata after tracking.

    @note
    Landmarks are normalized: x,y ∈ [0,1] relative to image width/height;
    z is a relative depth (smaller values are closer), not metric units.
    """
    id: str                   # "left" or "right"
    score: float
    landmarks: np.ndarray     # (21, 3) normalized [0..1] for x,y; relative for z
    kind: str                 # "left_hand" or "right_hand"


class EMAFilter:
    """!
    @brief Exponential moving average (EMA) smoother for landmarks.
    @ingroup Perceiver

    @param alpha Smoothing factor in (0,1]. Lower values = more smoothing (more lag);
                 higher values = less smoothing (more responsive).
    """

    def __init__(self, alpha: float = 0.4):
        self.alpha = alpha
        self.prev: Optional[np.ndarray] = None

    def reset(self):
        """!
        @brief Reset internal state so the next call passes through the input.
        """
        self.prev = None

    def __call__(self, pts: np.ndarray) -> np.ndarray:
        """!
        @brief Apply EMA smoothing to a (21,3) landmark array.
        @param pts Landmark array for the current frame.
        @return Smoothed landmark array of the same shape.
        """
        if self.prev is None:
            self.prev = pts.copy()
            return pts
        self.prev = self.alpha * pts + (1 - self.alpha) * self.prev
        return self.prev


class MediaPosePerceiver:
    """!
    @ingroup Perceiver
    @brief Wraps MediaPipe Hands as a detector, adds handedness-based tracking and EMA smoothing.

    @param max_hands   Maximum number of hands to detect per frame.
    @param det_conf    Minimum detection confidence for initial hand detection.
    @param track_conf  Minimum tracking confidence for temporal landmark tracking.
    @param ema_alpha   EMA smoothing factor applied per-hand ID.

    @note
    - MediaPipe expects RGB input; frames from OpenCV are BGR, so conversion is applied before processing.
    - Landmarks are normalized (x,y ∈ [0,1]); z is a relative depth (not metric units).
    - This class prototypes the Perceiver interface: detector + tracker (+ filter).
      Use `detect(frame_bgr)` to get raw detections, and `track(detections)` to obtain
      stable IDs with smoothed landmarks.
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
        """!
        @brief Release MediaPipe resources.
        """
        self.hands.close()

    def detect(self, frame_bgr) -> List[Dict]:
        """!
        @brief Run the MediaPipe Hands detector on a single frame.
        @param frame_bgr Input image in BGR (OpenCV) format.
        @return A list of detections. Each detection is a dict with:
                - score: float confidence of handedness classification,
                - handedness: "left" or "right",
                - landmarks: np.ndarray shape (21,3) with normalized x,y and relative z.

        @details
        Converts the frame to RGB (as required by MediaPipe), runs `.process`,
        and zips the resulting `multi_hand_landmarks` with `multi_handedness`.
        """
        h, w = frame_bgr.shape[:2]  # kept for potential pixel conversion in overlays
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        res = self.hands.process(frame_rgb)
        out: List[Dict] = []

        if not res.multi_hand_landmarks:
            return out

        for lm, handed in zip(res.multi_hand_landmarks, res.multi_handedness):
            # Landmarks: 21 points; x,y normalized to [0,1]; z is relative depth (not metric)
            pts = np.array([[p.x, p.y, p.z] for p in lm.landmark], dtype=np.float32)  # (21,3)
            score = handed.classification[0].score
            label = handed.classification[0].label.lower()  # 'left' or 'right'
            out.append({
                "score": float(score),
                "handedness": label,
                "landmarks": pts,   # normalized coordinates
            })
        return out

    def track(self, detections: List[Dict]) -> List[Track]:
        """!
        @brief Assign stable hand IDs using handedness and apply EMA smoothing.
        @param detections List of detection dicts from `detect(...)`.
        @return List of `Track` objects with fields: id, kind, score, landmarks (21,3).

        @details
        Uses handedness ("left","right") as stable IDs when available; falls back to
        a free slot if handedness is missing. EMA smoothing is applied per ID using
        independent filters. Filters for IDs not observed in the current frame are reset.
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
        # Reset filters for hands not seen this frame (to avoid smearing across gaps)
        for k in ("left", "right"):
            if k not in seen:
                self.filters[k].reset()
        return tracks
