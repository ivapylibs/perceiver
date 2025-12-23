# perceiver/perceiver/factory.py
from __future__ import annotations
from typing import Any, Dict, Optional

# External (ensure PyYAML is installed in your venv)
import yaml

# Our API-aligned perceiver
from perceiver.perceiver.mediapose_perceiver_api import MediaPosePerceiverAPI

# Allowed tokens (keep in sync with detector + adapter)
_ALLOWED_MASK_MODES = {"none", "palm", "hand"}
_ALLOWED_TRACKERS   = {"hand", "palm", "centroid"}


def load_config(path: str) -> Dict[str, Any]:
    """
    Load a YAML config file into a Python dict.
    """
    with open(path, "r") as f:
        cfg = yaml.safe_load(f) or {}
    if not isinstance(cfg, dict):
        raise ValueError(f"Config at {path} must be a mapping.")
    return cfg


def _validate_detector_section(det: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the detector section and return detector params dict for constructor.
    Expected shape:
      detector:
        name: mediapipe_hands
        params:
          mask_mode: none|palm|hand
          mirror: bool
          det_conf: float
          track_conf: float
          max_hands: int
    """
    name = (det or {}).get("name", "")
    if name != "mediapipe_hands":
        raise ValueError(
            f"Unsupported detector.name='{name}'. Only 'mediapipe_hands' is supported."
        )

    params = (det or {}).get("params", {}) or {}
    if not isinstance(params, dict):
        raise ValueError("detector.params must be a mapping.")

    # Defaults (safe dev defaults)
    mask_mode  = params.get("mask_mode", "none")
    mirror     = bool(params.get("mirror", False))
    det_conf   = float(params.get("det_conf", 0.4))
    track_conf = float(params.get("track_conf", 0.4))
    max_hands  = int(params.get("max_hands", 2))

    if mask_mode not in _ALLOWED_MASK_MODES:
        raise ValueError(
            f"detector.params.mask_mode='{mask_mode}' invalid. "
            f"Allowed: {sorted(_ALLOWED_MASK_MODES)}"
        )

    # Return kwargs exactly as MediaPipeHandsDetector expects
    return {
        "mask_mode":  mask_mode,
        "mirror":     mirror,
        "det_conf":   det_conf,
        "track_conf": track_conf,
        "max_hands":  max_hands,
    }


def _validate_trackpointer_section(tp: Dict[str, Any]) -> str:
    """
    Validate the trackpointer section and return the tracker token ('hand'|'palm'|'centroid').
    Expected shape:
      trackpointer:
        name: hand|palm|centroid
        params: {...}  # currently unused by the adapter; reserved for future
    """
    tp_name = (tp or {}).get("name", "hand")
    if tp_name not in _ALLOWED_TRACKERS:
        raise ValueError(
            f"trackpointer.name='{tp_name}' invalid. Allowed: {sorted(_ALLOWED_TRACKERS)}"
        )
    return tp_name


def _extract_ema_alpha(cfg: Dict[str, Any]) -> Optional[float]:
    """
    Find the first EMA filter in estimator.filters and return its alpha.
    If no EMA configured, return None (means no smoothing).
    Expected shape:
      estimator:
        filters:
          - name: ema
            params: { alpha: 0.6 }
    """
    est = (cfg or {}).get("estimator", {})
    filters = (est or {}).get("filters", [])
    if not isinstance(filters, list):
        return None

    for f in filters:
        if not isinstance(f, dict):
            continue
        if f.get("name", "") != "ema":
            continue
        p = f.get("params", {}) or {}
        try:
            alpha = float(p.get("alpha"))
        except (TypeError, ValueError):
            alpha = None
        if alpha is not None:
            # Basic safety clamp to (0,1]
            if not (0.0 < alpha <= 1.0):
                raise ValueError("EMA alpha must be in (0, 1].")
            return alpha
    return None


def build_mediapose_from_config(cfg: Dict[str, Any]) -> MediaPosePerceiverAPI:
    """
    Build a MediaPosePerceiverAPI instance from a (possibly legacy) config dict.
    Supports:
      - legacy: {"perceiver":"mediapose", "trackpointer":{...}, "detector":{...}, "estimator":{...}}
      - new:    {"perceiver":{"name":"mediapose","trackpointer":{...}}, "detector":{...}, "estimator":{...}}
    """

    # ---- perceiver name + choose the correct trackpointer node ----
    pnode = cfg.get("perceiver", None)
    if isinstance(pnode, str):
        perceiver_name = pnode
        tp_cfg = (cfg.get("trackpointer", {}) or {})
    elif isinstance(pnode, dict):
        perceiver_name = pnode.get("name", None)
        tp_cfg = (pnode.get("trackpointer", {}) or {})
    else:
        perceiver_name = None
        tp_cfg = {}

    if perceiver_name != "mediapose":
        raise ValueError(f"perceiver='{pnode}' not supported by this factory. Use 'mediapose'.")

    # ---- detector / estimator nodes (same for both shapes) ----
    det_cfg = (cfg.get("detector", {}) or {})
    # estimator is only needed for EMA alpha extraction
    # filters format expected: [{"name":"ema","params":{"alpha":0.6}}, ...]
    ema_alpha = _extract_ema_alpha(cfg)  # returns Optional[float]

    # ---- validate / normalize sections ----
    detector_kwargs = _validate_detector_section(det_cfg)   # -> kwargs for MediaPipeHandsDetector
    tracker_name    = _validate_trackpointer_section(tp_cfg)  # -> "hand" | "palm" | "centroid"
    print("[FACTORY] perceiver=mediapose tracker=", tracker_name, "det.kw=", detector_kwargs.get("mask_mode"))


    # ---- construct API-aligned perceiver ----
    # MediaPosePerceiverAPI signature:
    #   (tracker: str="hand", ema_alpha: Optional[float]=None,
    #    mask_mode: str="none", mirror: bool=False, **mp_kwargs)
    # detector_kwargs should carry: mask_mode, mirror, det_conf, track_conf, max_hands
    return MediaPosePerceiverAPI(
        tracker=tracker_name,
        ema_alpha=ema_alpha,
        cfg = cfg,
        **detector_kwargs,
    )


# Convenience helper if you want to build directly from a YAML path:
def build_mediapose_from_yaml(path: str) -> MediaPosePerceiverAPI:
    """
    Load YAML at 'path' and build a MediaPosePerceiverAPI.
    """
    cfg = load_config(path)
    return build_mediapose_from_config(cfg)
