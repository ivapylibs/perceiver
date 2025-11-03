# perceiver/perceiver/mediapose_perceiver_api.py
from __future__ import annotations
from typing import Optional, Any, Dict

# API contracts + shared types
from perceiver.perceiver.interfaces import Perceiver
from perceiver.perceiver.types import Detections, Tracks, Estimates, PerceptionResult

# Concrete components we already built
from detector.detector.mediapipe_hands import MediaPipeHandsDetector
from trackpointer.trackpointer.api_adapter import APITrackpointerAdapter
from perceiver.perceiver.estimator import FilteringEstimator
from perceiver.filters.ema_filter import EMAFilter


class MediaPosePerceiverAPI(Perceiver):
    """
    API-aligned perceiver that wires:
        Detector.detect_struct -> Trackpointer.update -> Estimator.update
    and returns a single PerceptionResult.
    """

    def __init__(
        self,
        tracker: str = "hand",                     # {"hand","palm","centroid"}
        ema_alpha: Optional[float] = None,         # None = no smoothing
        mask_mode: str = "none",                   # {"none","palm","hand"}
        mirror: bool = False,
        **mp_kwargs: Any,                          # forwarded to MediaPipeHandsDetector
    ) -> None:
        # Detector owns masking + preprocessing
        self.det = MediaPipeHandsDetector(
            mask_mode=mask_mode,
            mirror=mirror,
            **mp_kwargs,
        )

        # Trackpointer adapter exposes new API over legacy trackers
        self.tpa = APITrackpointerAdapter(tracker_type=tracker)

        # Estimator chains Filters (EMA optional)
        self.ema_alpha = ema_alpha
        self.est = FilteringEstimator(
            filters=[EMAFilter(alpha=ema_alpha)] if ema_alpha is not None else []
        )

        # Metadata
        self._meta_static: Dict[str, Any] = {
            "tracker": tracker,
            "mask_mode": mask_mode,
            "mirror": mirror,
            "detector": "mediapipe_hands",
            "estimator": "filtering(EMA)" if ema_alpha is not None else "filtering(none)",
        }

    # --- Perceiver API ---------------------------------------------------
    def process(self, frame: Any, timestamp: Optional[float] = None) -> PerceptionResult:
        detections: Detections = self.det.detect_struct(frame, timestamp=timestamp)
        tracks: Tracks = self.tpa.update(detections, timestamp=timestamp)

        # DEBUG: show what keys reached the demo
        if tracks.items:
            print("TRK_CLASS:", type(self.tpa).__name__)
            print("DICT_KEYS_0:", list(tracks.items[0].keys()))

        estimates: Estimates = self.est.update(tracks, timestamp=timestamp)

        meta: Dict[str, Any] = {
            **self._meta_static,
            "timestamp": timestamp,
            "num_detections": len(detections.items),
            "num_tracks": len(tracks.items),
        }
        return PerceptionResult(
            detections=detections,
            tracks=tracks,
            estimates=estimates,
            meta=meta,
        )

    def reset(self) -> None:
        # Clear detector’s masking cache if present
        if hasattr(self.det, "_prev_hands"):
            self.det._prev_hands = []
        if hasattr(self.det, "_last_mask"):
            self.det._last_mask = None
        if hasattr(self.det, "_last_masked_input"):
            self.det._last_masked_input = None

        # Reset trackpointer + estimator
        self.tpa.reset()
        if hasattr(self.est, "reset"):
            self.est.reset()  # if you added a reset; otherwise Filters clear state individually

    def _handlike_to_dict(obj) -> dict:
        d = {}
        d["id"] = getattr(obj, "id", getattr(obj, "label", None))
        d["label"] = getattr(obj, "label", None)
        sc = getattr(obj, "score", None)
        if sc is not None:
            try:
                d["score"] = float(sc)
            except Exception:
                pass
        # Forward whichever payloads actually exist on this object
        for k in ("landmarks", "palm", "centroid", "fingers"):
            v = getattr(obj, k, None)
            if v is not None:
                d[k] = v
        return d

