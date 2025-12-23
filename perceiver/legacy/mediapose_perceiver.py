# perceiver/perceiver/mediapose_perceiver.py
import numpy as np

from detector.detector.mediapipe_hands import MediaPipeHandsDetector
from trackpointer.trackpointer.hand_tracker import HandLandmarksTracker
from trackpointer.trackpointer.palm_tracker import PalmTracker
from trackpointer.trackpointer.centroid_tracker import CentroidTracker
from perceiver.perceiver.filters import MultiFeatureEMA  # NEW
from typing import Optional

_TRACKERS = {
    "hand": HandLandmarksTracker,
    "palm": PalmTracker,
    "centroid": CentroidTracker,
}

# Which field to smooth given the tracker type
_FEATURE_KEY = {
    "hand": "landmarks",
    "palm": "palm",
    "centroid": "centroid",
}

class MediaPosePerceiver:
    def __init__(self, tracker="hand", ema_alpha=None, mask_mode: str = "none", **mp_kwargs):
        if tracker not in _TRACKERS:
            raise ValueError(f"Unknown tracker '{tracker}'. Valid: {list(_TRACKERS.keys())}")

        self.det = MediaPipeHandsDetector(mask_mode = mask_mode, **mp_kwargs)
        # Keep passing alpha to trackers for API stability (they may ignore it internally)
        self.trk = _TRACKERS[tracker]()
        self._feat_key = _FEATURE_KEY[tracker]

        # Centralized smoothing lives here now
        self.ema_alpha = ema_alpha
        if ema_alpha is not None:
            self.ema = MultiFeatureEMA(alpha=ema_alpha)
        else:
            self.ema = None

        print(f"[MediaPosePerceiver] tracker={tracker} feat={self._feat_key} ema_alpha={self.ema_alpha}")

    def detect(self, frame):
        return self.det.detect(frame)

    def track(self, hands):
        tracks = self.trk.update(hands)

        if self.ema is not None:
            # Apply EMA to the selected feature per visible hand
            seen = set()
            for t in tracks:
                label = getattr(t, "label", None)
                if not label:
                    continue

                if getattr(t, "present", False):
                    raw_feat = getattr(t, self._feat_key, None)
                    feat2 = self._coerce_feature(raw_feat, self._feat_key)

                    if isinstance(feat2, np.ndarray) and feat2.size > 0 and np.isfinite(feat2).all():
                        feat2 = feat2.astype(np.float32, copy=False)
                        try:
                            sm = self.ema.smooth(label, self._feat_key, feat2)

                            # shape-preserving write-back
                            sm_out = None
                            if self._feat_key == "centroid":
                                if isinstance(raw_feat, np.ndarray):
                                    if raw_feat.shape == (2,):
                                        sm_out = sm.reshape(2,)             # (2,)
                                    elif raw_feat.shape == (1, 2):
                                        sm_out = sm                          # (1,2)
                                    elif raw_feat.shape == (3,):
                                        sm_out = raw_feat.copy()
                                        sm_out[0:2] = sm.reshape(2,)         # keep original z
                                    elif raw_feat.shape == (1, 3):
                                        sm_out = raw_feat.copy()
                                        sm_out[0, 0:2] = sm[0, 0:2]          # keep original z
                                    else:
                                        sm_out = sm                          # fallback (1,2)
                                else:
                                    sm_out = sm

                            elif self._feat_key == "hand":
                                if isinstance(raw_feat, np.ndarray):
                                    if raw_feat.shape == (21, 3):
                                        sm_out = raw_feat.copy()
                                        sm_out[:, :2] = sm                   # keep original z
                                    elif raw_feat.shape == (21, 2):
                                        sm_out = sm
                                    elif raw_feat.shape == (63,):
                                        tmp = raw_feat.reshape(21, 3).copy()
                                        tmp[:, :2] = sm
                                        sm_out = tmp.reshape(63,)
                                    elif raw_feat.shape == (42,):
                                        sm_out = sm.reshape(42,)
                                    else:
                                        sm_out = sm                          # fallback
                                else:
                                    sm_out = sm

                            elif self._feat_key == "palm":
                                if (isinstance(raw_feat, np.ndarray)
                                    and raw_feat.ndim == 2
                                    and raw_feat.shape[0] >= 4):
                                    if raw_feat.shape[1] == 3:
                                        sm_out = raw_feat.copy()
                                        sm_out[:, :2] = sm                   # keep original z
                                    elif raw_feat.shape[1] == 2:
                                        sm_out = sm
                                    else:
                                        sm_out = sm                          # fallback
                                else:
                                    sm_out = sm

                            else:
                                sm_out = sm

                            setattr(t, self._feat_key, sm_out)

                        except Exception:
                            # Don't kill the demo on a smoothing error; just skip this track
                            pass

                    # mark this label as seen this frame (only if present)
                    seen.add(label)

            # Reset EMA for tracks not seen this frame
            self.ema.reset_missing(seen)

        return tracks


    def close(self):
        self.det.close()


    def _coerce_feature(self, feat: np.ndarray, key: str) -> Optional[np.ndarray]:
        if not isinstance(feat, np.ndarray):
            return None
        
        if feat.size == 0:
            return None
        
        if not np.isfinite(feat).all():
            return None
        
        feat = feat.astype(np.float32, copy = False)

        if (key == "hand"):
            if feat.shape == (21, 3):
                feat = feat[:, 0:2]
                return feat
            if feat.shape == (21, 2):
                return feat
            if feat.shape == (63,):
                feat = np.reshape(feat, (21, 3))[:, 0:2]
                return feat
            if feat.shape == (42,):
                feat = np.reshape(feat, (21, 2))
                return feat
            return None
        
        if key == "palm":
            if feat.ndim == 2 and feat.shape[0] >= 4 and feat.shape[1] in {2,3}:
                if feat.shape[1] == 3:
                    feat = feat[:, 0:2] # drop z
                return feat             # shape (K,2)
            return None
        
        if key == "centroid":
        # Normalize to (1,2)
            if feat.shape == (2,):
                return feat.reshape(1,2)      # (1,2)
            if feat.shape == (3,):
                return feat[0:2].reshape(1, 2) # (1,2)
            if feat.shape == (1, 2):
                return feat
            if feat.shape == (1, 3):
                return feat[:, 0:2]            # (1,2)
            if feat.shape == (2, 1):
                return np.transpose(feat)         # (1,2)
            return None
        
        return None
    
    def set_mask_mode(self, mode: str) -> None:
        """Forward masking mode to the underlying detector (owned by detector)."""
        if hasattr(self, "det"):
            self.det.mask_mode = mode