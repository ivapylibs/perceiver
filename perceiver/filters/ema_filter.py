from __future__ import annotations
from typing import Optional, Any, Dict, Union

# Interfaces & result types (lightweight; no heavy deps)
from perceiver.interfaces import Filter
from perceiver.types import Tracks, Estimates


Number = Union[int, float]

class EMAFilter(Filter):
    """
    Exponential Moving Average (EMA) Filter.
    - Owns per-track smoothing state.
    - Expects a Tracks object with items that include:
        { "id": <int|str>, ... , "<payload_key>": <numeric or nested list of numerics> }
      By default, we look for "landmarks" first; if not found, we fall back to "bbox".
    - Produces an Estimates mapping track_id -> {"<payload_key>_smoothed": value}

    Notes:
    • This module is intentionally numpy-free. It recursively smooths lists of lists.
    • You can change `payload_key_order` to prefer a different key.
    """

    def __init__(
        self,
        alpha: float,
        payload_key_order: tuple[str, ...] = ("landmarks", "bbox"),
        output_suffix: str = "_smoothed",
    ) -> None:
        if not (0.0 < alpha <= 1.0):
            raise ValueError("EMAFilter: alpha must be in (0, 1].")
        self.alpha = alpha
        self.payload_key_order = payload_key_order
        self.output_suffix = output_suffix

        # Per-track memory: track_id -> previous value (same structure as payload)
        self._prev: Dict[Union[int, str], Any] = {}

    # ---- Filter interface ----------------------------------------------------
    def reset(self) -> None:
        self._prev.clear()

    def apply(self, tracks_or_estimates: Any, timestamp: Optional[float] = None) -> Estimates:
        """
        Apply EMA smoothing. For Phase 2A, we expect a Tracks input.
        If an Estimates is passed, we attempt to smooth its values again (chaining).
        """
        # If input is Tracks, extract raw payloads, smooth, and return Estimates.
        if isinstance(tracks_or_estimates, Tracks):
            return self._apply_to_tracks(tracks_or_estimates, timestamp)
        # If input is already Estimates, smooth the existing estimated values again.
        if isinstance(tracks_or_estimates, Estimates):
            return self._apply_to_estimates(tracks_or_estimates, timestamp)
        # Fallback: treat unknown input as empty
        return Estimates(items={}, meta={"timestamp": timestamp, "alpha": self.alpha, "note": "unsupported input"})
        
        # ---- Internals -----------------------------------------------------------
    def _apply_to_tracks(self, tracks: Tracks, timestamp: Optional[float]) -> Estimates:
        out_items: Dict[Union[int, str], Dict[str, Any]] = {}
        for item in tracks.items:
            if "id" not in item:
                # Skip items without an ID; estimator assumes tracked entities
                continue
            tid = item["id"]
            # Choose which payload to smooth
            key = self._select_payload_key(item)
            if key is None:
                # Nothing to smooth for this track
                continue
            curr = item.get(key, None)
            if curr is None:
                continue
            prev = self._prev.get(tid, None)
            smoothed = self._ema(prev, curr, self.alpha)
            self._prev[tid] = smoothed  # update memory
            out_items[tid] = {f"{key}{self.output_suffix}": smoothed}
        return Estimates(
            items=out_items,
            meta={"timestamp": timestamp, "alpha": self.alpha, "source": "tracks"},
        )
        
    def _apply_to_estimates(self, estimates: Estimates, timestamp: Optional[float]) -> Estimates:
        out_items: Dict[Union[int, str], Dict[str, Any]] = {}
        for tid, payload in estimates.items.items():
            # Smooth all numeric entries in the payload dict
            sm_payload: Dict[str, Any] = {}
            prev_payload = self._prev.get(tid, {})
            for k, v in payload.items():
                prev_v = prev_payload.get(k, None) if isinstance(prev_payload, dict) else None
                sm_payload[k] = self._ema(prev_v, v, self.alpha)
            self._prev[tid] = sm_payload
            out_items[tid] = sm_payload
        return Estimates(
            items=out_items,
            meta={"timestamp": timestamp, "alpha": self.alpha, "source": "estimates"},
        )
        
    def _select_payload_key(self, item: Dict[str, Any]) -> Optional[str]:
        for k in self.payload_key_order:
            if k in item and item[k] is not None:
                return k
        return None
        
    def _ema(self, prev: Any, curr: Any, alpha: float) -> Any:
         """
         Recursive EMA for scalars or (nested) lists/tuples of numbers.
         """
         if prev is None:
             return curr
         # Scalar numbers
         if isinstance(curr, (int, float)) and isinstance(prev, (int, float)):
             return alpha * curr + (1.0 - alpha) * prev
         # Lists/tuples: smooth elementwise with matching shapes
         if isinstance(curr, (list, tuple)) and isinstance(prev, (list, tuple)) and len(curr) == len(prev):
             result = []
             for c, p in zip(curr, prev):
                 result.append(self._ema(p, c, alpha))
             # Keep same container type as input
             return type(curr)(result)
         # Dicts: smooth matching keys if both are dicts
         if isinstance(curr, dict) and isinstance(prev, dict):
             keys = set(curr.keys()) | set(prev.keys())
             out: Dict[str, Any] = {}
             for k in keys:
                 out[k] = self._ema(prev.get(k), curr.get(k), alpha)
             return out
         # Fallback: if structures mismatch, return curr (don’t crash)
         return curr
