# perceiver/perceiver/hand_pick_activity.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

import numpy as np

from detector.base import ActivityState  # <-- Monitor expects ActivityState style
from perceiver.types import PerceptionResult


class PickFSMState(str, Enum):
    OPEN = "open"
    PINCHING = "pinching"
    HOLD = "hold"
    RELEASE = "release"


@dataclass
class HandPickActivityParams:
    pinch_close_thresh: float = 0.25
    pinch_open_thresh: float = 0.32
    close_frames: int = 3
    open_frames: int = 3
    hold_min_frames: int = 3

    require_pnp_for_distance: bool = False
    min_distance_m: Optional[float] = None
    max_distance_m: Optional[float] = None


class HandPickActivity:
    """
    IVA-style Activity module (Monitor-compatible).

    Monitor will call:
      - process(perceiver.getState())
      - getState(), getEmptyState(), setState()
      - printState() when display='basic'
    """

    def __init__(self, params: Optional[HandPickActivityParams] = None) -> None:
        self.p = params or HandPickActivityParams()

        # Per-track FSM memory
        self._fsm: Dict[Any, PickFSMState] = {}
        self._close_ct: Dict[Any, int] = {}
        self._open_ct: Dict[Any, int] = {}
        self._hold_ct: Dict[Any, int] = {}

        # current activity state
        self.x: ActivityState = self.getEmptyState()

    def reset(self) -> None:
        self._fsm.clear()
        self._close_ct.clear()
        self._open_ct.clear()
        self._hold_ct.clear()
        self.x = self.getEmptyState()

    # ---------------- Monitor contract ----------------

    def getEmptyState(self) -> ActivityState:
        return ActivityState(
            xActivity={
                "activity": {},   # tid -> per-track activity dict
                "timestamp": None,
            },
            haveObs=False,
        )

    def getState(self) -> ActivityState:
        return self.x if self.x is not None else self.getEmptyState()

    def setState(self, nstate: ActivityState) -> None:
        self.x = nstate

    def printState(self, dState: Optional[ActivityState] = None) -> None:
        st = dState if dState is not None else self.getState()
        try:
            print("[HandPickActivity]", st.xActivity, "haveObs=", st.haveObs)
        except Exception:
            print("[HandPickActivity] (unprintable state)")

    # ---------------- Main entrypoint ----------------

    def process(self, result: Any) -> None:
        """
        Monitor passes perceiver.getState() here, which should be a PerceptionResult.
        We store our output into self.x as an ActivityState.
        """
        if not isinstance(result, PerceptionResult):
            self.x = self.getEmptyState()
            return

        # Safety: empty perception result
        if result.tracks is None:
            self.x = self.getEmptyState()
            return

        tracks = result.tracks.items or []
        estimates = result.estimates.items if (result.estimates is not None) else {}

        out: Dict[Any, Dict[str, Any]] = {}
        have_obs = False

        for trk in tracks:
            tid = trk.get("id", None)
            if tid is None:
                continue

            pick = self._get_pick_payload(tid, trk, estimates)
            pinch_ratio = self._safe_float(pick.get("pinch_ratio", None)) if pick else None
            distance = self._safe_float(pick.get("distance", None)) if pick else None
            frame = pick.get("frame", None) if pick else None

            # Initialize memory
            if tid not in self._fsm:
                self._fsm[tid] = PickFSMState.OPEN
                self._close_ct[tid] = 0
                self._open_ct[tid] = 0
                self._hold_ct[tid] = 0

            # If no evidence, decay to OPEN for this track
            if pinch_ratio is None:
                self._fsm[tid] = PickFSMState.OPEN
                self._close_ct[tid] = 0
                self._open_ct[tid] = 0
                self._hold_ct[tid] = 0
                out[tid] = self._emit_state(tid, pinch_ratio, distance)
                continue

            have_obs = True

            # Optional distance validity gating
            if not self._distance_ok(distance, frame) and self.p.require_pnp_for_distance:
                self._fsm[tid] = PickFSMState.OPEN
                self._close_ct[tid] = 0
                self._open_ct[tid] = 0
                self._hold_ct[tid] = 0
                out[tid] = self._emit_state(tid, pinch_ratio, distance)
                continue

            self._step_fsm(tid, pinch_ratio)
            out[tid] = self._emit_state(tid, pinch_ratio, distance)

        self.x = ActivityState(
            xActivity={
                "activity": out,
                "timestamp": result.meta.get("timestamp", None),
            },
            haveObs=have_obs,
        )

    # ---------------- Helpers ----------------

    def _get_pick_payload(
        self,
        tid: Any,
        track_item: Dict[str, Any],
        estimates_items: Dict[Any, Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        est = estimates_items.get(tid, None)
        if isinstance(est, dict) and isinstance(est.get("pick", None), dict):
            return est["pick"]

        pk = track_item.get("pick", None)
        if isinstance(pk, dict):
            return pk
        return None

    def _step_fsm(self, tid: Any, pinch_ratio: float) -> None:
        st = self._fsm[tid]
        close = pinch_ratio < self.p.pinch_close_thresh
        open_ = pinch_ratio > self.p.pinch_open_thresh

        if st == PickFSMState.OPEN:
            self._close_ct[tid] = self._close_ct[tid] + 1 if close else 0
            if self._close_ct[tid] >= self.p.close_frames:
                self._fsm[tid] = PickFSMState.PINCHING
                self._hold_ct[tid] = 0
                self._open_ct[tid] = 0

        elif st == PickFSMState.PINCHING:
            if close:
                self._hold_ct[tid] += 1
            else:
                self._fsm[tid] = PickFSMState.OPEN
                self._close_ct[tid] = 0
                self._hold_ct[tid] = 0
                self._open_ct[tid] = 0
                return
            if self._hold_ct[tid] >= self.p.hold_min_frames:
                self._fsm[tid] = PickFSMState.HOLD
                self._open_ct[tid] = 0

        elif st == PickFSMState.HOLD:
            self._open_ct[tid] = self._open_ct[tid] + 1 if open_ else 0
            if self._open_ct[tid] >= self.p.open_frames:
                self._fsm[tid] = PickFSMState.RELEASE

        elif st == PickFSMState.RELEASE:
            self._open_ct[tid] = self._open_ct[tid] + 1 if open_ else 0
            if self._open_ct[tid] >= self.p.open_frames:
                self._fsm[tid] = PickFSMState.OPEN
                self._close_ct[tid] = 0
                self._hold_ct[tid] = 0
                self._open_ct[tid] = 0

    def _emit_state(self, tid: Any, pinch_ratio: Optional[float], distance: Optional[float]) -> Dict[str, Any]:
        st = self._fsm.get(tid, PickFSMState.OPEN)
        is_picking = (st == PickFSMState.HOLD)

        hold_ct = self._hold_ct.get(tid, 0)
        conf = float(np.clip(hold_ct / max(1, self.p.hold_min_frames), 0.0, 1.0))

        return {
            "state": st.value,
            "is_picking": bool(is_picking),
            "pinch_ratio": pinch_ratio,
            "distance": distance,
            "confidence": conf,
            "counts": {
                "close": int(self._close_ct.get(tid, 0)),
                "open": int(self._open_ct.get(tid, 0)),
                "hold": int(self._hold_ct.get(tid, 0)),
            },
        }

    def _distance_ok(self, distance: Optional[float], frame: Optional[str]) -> bool:
        if distance is None:
            return not self.p.require_pnp_for_distance
        if frame is not None and frame != "camera":
            return not self.p.require_pnp_for_distance
        if self.p.min_distance_m is not None and distance < self.p.min_distance_m:
            return False
        if self.p.max_distance_m is not None and distance > self.p.max_distance_m:
            return False
        return True

    @staticmethod
    def _safe_float(x: Any) -> Optional[float]:
        try:
            if x is None:
                return None
            v = float(x)
            if not np.isfinite(v):
                return None
            return v
        except Exception:
            return None
