# perceiver/perceiver/mediapose_perceiver.py
from detector.detector.legacy.mediapipe_hands import MediaPipeHandsDetector
from trackpointer.trackpointer.hand_tracker import HandLandmarksTracker
from trackpointer.trackpointer.palm_tracker import PalmTracker
from trackpointer.trackpointer.centroid_tracker import CentroidTracker

_TRACKERS = {
    "hand": HandLandmarksTracker,
    "palm": PalmTracker,
    "centroid": CentroidTracker,
}

class MediaPosePerceiver:
    def __init__(self, tracker="hand", ema_alpha=0.4, **mp_kwargs):
        self.det = MediaPipeHandsDetector(**mp_kwargs)
        self.trk = _TRACKERS[tracker](alpha=ema_alpha)
    def detect(self, frame): return self.det.detect(frame)
    def track(self, hands):  return self.trk.update(hands)
    def close(self):         self.det.close()
