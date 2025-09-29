# perceiver/perceiver/mediapose_perceiver.py
from detector.detector.mediapipe_hands import MediaPipeHandsDetector
from trackpointer.trackpointer.ema_tracker import EMAHandTracker

class MediaPosePerceiver:
    def __init__(self, ema_alpha=0.4, **mp_kwargs):
        self.det = MediaPipeHandsDetector(**mp_kwargs)
        self.trk = EMAHandTracker(alpha=ema_alpha)
    def detect(self, frame): return self.det.detect(frame)
    def track(self, hands):  return self.trk.update(hands)
    def close(self):         self.det.close()
