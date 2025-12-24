# perceiver/perceiver/mediapose_perceiver.py
"""!
@file mediapose_perceiver.py
@brief Perceiver = detector (MediaPipe Hands) + tracker (EMA smoothing).
@ingroup Perceiver

Detector returns fixed-size per-hand outputs (left, right) including:
- landmarks (21x3, normalized x,y and relative z),
- palm (6x3),
- fingers (15x3),
- centroid (3,),
- present flag and score.

Tracker smooths landmarks with EMA, then recomputes palm/fingers/centroid
from the smoothed landmarks for consistent geometry.
"""

from __future__ import annotations
from typing import List

# Prefer the centroid-capable copies if you created them; otherwise fall back.
try:
    from detector.legacy.mediapipe_hands_centroid import MediaPipeHandsDetector, HandOutput
except ImportError:
    # fallback if you didn’t make the centroid copy
    from detector.mediapipe_hands import MediaPipeHandsDetector, HandOutput  # type: ignore

try:
    from trackpointer.legacy.ema_tracker_centroid import EMAHandTracker
except ImportError:
    from trackpointer.ema_tracker import EMAHandTracker  # type: ignore


class MediaPosePerceiver:
    """Wraps detector + tracker with a simple, unified interface."""

    def __init__(self, ema_alpha: float = 0.4, **mp_detector_kwargs) -> None:
        """
        Args:
            ema_alpha: EMA smoothing factor (0,1]; lower = smoother.
            **mp_detector_kwargs: forwarded to MediaPipeHandsDetector (e.g., max_hands, det_conf, track_conf).
        """
        self.det = MediaPipeHandsDetector(**mp_detector_kwargs)
        self.trk = EMAHandTracker(alpha=ema_alpha)

    def detect(self, frame_bgr) -> List[HandOutput]:
        """Run the detector on a BGR frame and return [left, right] HandOutput."""
        return self.det.detect(frame_bgr)

    def track(self, hands: List[HandOutput]) -> List[HandOutput]:
        """Apply tracking/smoothing and return the same [left, right] structure."""
        return self.trk.update(hands)

    def close(self) -> None:
        """Release detector resources (MediaPipe)."""
        self.det.close()
