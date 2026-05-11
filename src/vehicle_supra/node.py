"""
vehicle_supra/node.py
─────────────────────
SupraNode — the E.I.A.R.(V) structured agent node.

Every agent in VEHICLE-SUPRA is not a black box.
It is an internally structured relational unit with
five dimensions measured continuously:

    Sᵢ(t) = (Eᵢ, Iᵢ, Aᵢ, Rᵢ, Vᵢ)  ∈ ℝ⁵

Author : Roberto Borda Milan — VEHICLE Systems Lab
Framework DOI: 10.5281/zenodo.19981738
License: MIT
"""

from __future__ import annotations

import time
import uuid
import copy
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


# ── Regime constants ──────────────────────────────────────
REGIME_A0 = "A0"   # Stable
REGIME_A1 = "A1"   # External pressure
REGIME_A2 = "A2"   # Recovering
REGIME_A3 = "A3"   # Internal incoherence
REGIME_A4 = "A4"   # Isolated
REGIME_A5 = "A5"   # Crisis — replicate
REGIME_A6 = "A6"   # Cascade — isolate


@dataclass
class SupraNodeConfig:
    """Configuration for a SupraNode."""
    # Coherence threshold — nodes with T_int > t_limit are incoherent
    t_limit: float = 0.30
    # Regime thresholds
    t_int_warning: float = 0.15   # A3 threshold
    t_int_crisis: float  = 0.28   # A5 threshold
    t_ext_warning: float = 0.20   # A1 threshold
    # Recovery parameters
    eta: float   = 0.10   # gradient descent step
    alpha: float = 0.30   # relaxation parameter (0 < α ≤ 1)
    max_recovery_cycles: int = 50
    # Replication
    replication_threshold: int = 20  # cycles without convergence → replicate
    # Isolation
    is_isolated: bool = False


class SupraNode:
    """
    A single VEHICLE-SUPRA agent node.

    Carries the 5-dimensional state vector S = (E, I, A, R, V)
    and implements the full E.I.A.R.(V) governance cycle:

        1. Measure T_int (internal incoherence)
        2. If T_int > T_limit → activate V_op projection
        3. Update state with relaxation
        4. Classify regime A0–A6
        5. Signal replication if non-convergent

    Parameters
    ----------
    node_id : str
        Unique identifier. Auto-generated if None.
    E, I, A, R, V : float
        Initial state components, each in [0, 1].
        E = Exposure (external pressure)
        I = Integrity (internal coherence score)
        A = Agency (action effectiveness)
        R = Recovery (replication capacity)
        V = Value (systemic importance)
    config : SupraNodeConfig
        Tunable parameters for this node.
    """

    def __init__(
        self,
        node_id: Optional[str] = None,
        E: float = 0.5,
        I: float = 0.8,
        A: float = 0.7,
        R: float = 0.6,
        V: float = 0.5,
        config: Optional[SupraNodeConfig] = None,
    ):
        self.node_id   = node_id or str(uuid.uuid4())[:8]
        self.config    = config or SupraNodeConfig()

        # State vector — all components in [0, 1]
        self._state = np.array([E, I, A, R, V], dtype=float)
        self._clamp_state()

        # Reference state (coherent baseline — used for recovery)
        self._reference_state = self._state.copy()

        # Internal tracking
        self._regime: str = REGIME_A0
        self._recovery_cycles: int = 0
        self._is_recovering: bool = False
        self._replication_requested: bool = False
        self._created_at: float = time.time()
        self._last_update: float = time.time()
        self._history: list = []

        # Centering operator P₋ = I₅ - (1/5)·11ᵀ
        self._P_minus = np.eye(5) - np.ones((5, 5)) / 5.0

    # ── State access ──────────────────────────────────────

    @property
    def state(self) -> np.ndarray:
        """Return a copy of the current state vector S = (E, I, A, R, V)."""
        return self._state.copy()

    @property
    def E(self) -> float: return float(self._state[0])
    @property
    def I(self) -> float: return float(self._state[1])
    @property
    def A(self) -> float: return float(self._state[2])
    @property
    def R(self) -> float: return float(self._state[3])
    @property
    def V(self) -> float: return float(self._state[4])

    def set_state(self, E=None, I=None, A=None, R=None, V=None):
        """Update one or more state components."""
        names = [E, I, A, R, V]
        for idx, val in enumerate(names):
            if val is not None:
                self._state[idx] = float(val)
        self._clamp_state()
        self._last_update = time.time()

    def inject_stress(self, **kwargs):
        """
        Inject external stress into the node — simulates corrupt data,
        context drift, or model misalignment. Same as set_state but
        semantically clear for test scenarios.

        Example
        -------
        node.inject_stress(E=0.95, I=0.10)  # High exposure, low integrity
        """
        self.set_state(**kwargs)

    # ── Core mathematics ──────────────────────────────────

    def internal_incoherence(self) -> float:
        """
        O(Sᵢ) = ||P₋ Sᵢ||²

        Measures how far the state components are from their mean.
        A perfectly coherent node has O(S) = 0.
        High O(S) means the dimensions are wildly out of balance —
        e.g. very high Agency but very low Integrity.
        """
        centered = self._P_minus @ self._state
        return float(np.dot(centered, centered))

    def internal_tension(self) -> float:
        """Alias for internal_incoherence — T_int contribution of this node."""
        return self.internal_incoherence()

    def is_coherent(self) -> bool:
        """Returns True if internal incoherence is within the admissible region K."""
        return self.internal_incoherence() <= self.config.t_limit

    # ── Gradient ─────────────────────────────────────────

    def local_gradient(
        self,
        neighbor_states: Optional[list[np.ndarray]] = None,
        neighbor_weights: Optional[list[float]] = None,
        lam: float = 1.0,
    ) -> np.ndarray:
        """
        ∇_{Sᵢ} T(X) = Σⱼ ωᵢⱼ (Sᵢ - Sⱼ) + λ P₋ Sᵢ

        Parameters
        ----------
        neighbor_states  : list of state vectors from connected nodes
        neighbor_weights : corresponding edge weights ωᵢⱼ
        lam              : λ — weight of internal coherence term
        """
        grad = np.zeros(5)

        # External term — relational discrepancy with neighbors
        if neighbor_states:
            weights = neighbor_weights or [1.0] * len(neighbor_states)
            for s_j, w in zip(neighbor_states, weights):
                grad += w * (self._state - np.array(s_j))

        # Internal term — coherence correction
        grad += lam * (self._P_minus @ self._state)

        return grad

    # ── Projection operator V_op ──────────────────────────

    def project_to_K(self, z: np.ndarray) -> np.ndarray:
        """
        Pₖ(z) = argmin_{s∈K} ||s - z||²
        where K = {S ∈ ℝ⁵ : O(S) ≤ T_limit}

        If z is already in K, return z.
        Otherwise project onto the boundary of K using
        the closed-form solution for ellipsoidal constraint.
        """
        incoherence = float(z @ self._P_minus @ z)
        if incoherence <= self.config.t_limit:
            return np.clip(z, 0.0, 1.0)

        # Binary search for the scaling factor μ such that
        # projected state satisfies the constraint
        lo, hi = 0.0, 1.0
        for _ in range(64):
            mu = (lo + hi) / 2.0
            z_proj = z - mu * (self._P_minus @ z)
            if float(z_proj @ self._P_minus @ z_proj) <= self.config.t_limit:
                hi = mu
            else:
                lo = mu

        projected = z - hi * (self._P_minus @ z)
        return np.clip(projected, 0.0, 1.0)

    def v_op(
        self,
        neighbor_states: Optional[list] = None,
        neighbor_weights: Optional[list] = None,
        lam: float = 1.0,
    ) -> np.ndarray:
        """
        V_op(Sᵢ; X) = Pₖ(Sᵢ - η · ∇T(X))

        The projection-governed correction operator.
        Returns the corrected state (does not modify self).
        """
        grad = self.local_gradient(neighbor_states, neighbor_weights, lam)
        candidate = self._state - self.config.eta * grad
        return self.project_to_K(candidate)

    # ── Recovery cycle ────────────────────────────────────

    def recovery_step(
        self,
        neighbor_states: Optional[list] = None,
        neighbor_weights: Optional[list] = None,
        lam: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Execute one relaxed recovery step:
            Sᵢ(t+1) = (1-α)·Sᵢ(t) + α·V_op(Sᵢ(t); X)

        Returns a dict with step metrics.
        """
        t_int_before = self.internal_incoherence()

        corrected = self.v_op(neighbor_states, neighbor_weights, lam)
        alpha = self.config.alpha
        new_state = (1 - alpha) * self._state + alpha * corrected
        new_state = np.clip(new_state, 0.0, 1.0)

        t_int_after = float(new_state @ self._P_minus @ new_state)
        delta = t_int_before - t_int_after

        self._state = new_state
        self._recovery_cycles += 1
        self._last_update = time.time()

        converged = t_int_after <= self.config.t_limit

        return {
            "cycle": self._recovery_cycles,
            "t_int_before": t_int_before,
            "t_int_after": t_int_after,
            "delta": delta,
            "converged": converged,
        }

    # ── Regime classification ─────────────────────────────

    def classify_regime(
        self,
        t_ext: float = 0.0,
        is_isolated: bool = False,
        cascade_detected: bool = False,
    ) -> str:
        """
        Classify this node into one of A0–A6 based on tension metrics.

        Parameters
        ----------
        t_ext           : external tension from the network (T_ext contribution)
        is_isolated     : True if node has no active neighbors
        cascade_detected: True if multi-node cascade is active in the network
        """
        t_int = self.internal_incoherence()
        cfg   = self.config

        if cascade_detected:
            regime = REGIME_A6
        elif self._replication_requested:
            regime = REGIME_A5
        elif t_int >= cfg.t_int_crisis:
            regime = REGIME_A5
        elif t_int >= cfg.t_int_warning:
            regime = REGIME_A3
        elif self._is_recovering and t_int < cfg.t_int_warning:
            regime = REGIME_A2
        elif is_isolated:
            regime = REGIME_A4
        elif t_ext >= cfg.t_ext_warning:
            regime = REGIME_A1
        else:
            regime = REGIME_A0

        self._regime = regime
        return regime

    def regime(self) -> str:
        """Return the last computed regime."""
        return self._regime

    # ── Replication ───────────────────────────────────────

    def request_replication(self):
        """Signal that this node needs to be replicated."""
        self._replication_requested = True

    def spawn_twin(self) -> "SupraNode":
        """
        Create a coherent twin node initialized from the reference state.
        The twin takes the load while this node recovers.
        """
        twin = SupraNode(
            node_id=f"{self.node_id}_twin_{str(uuid.uuid4())[:4]}",
            E=float(self._reference_state[0]),
            I=float(self._reference_state[1]),
            A=float(self._reference_state[2]),
            R=float(self._reference_state[3]),
            V=float(self._reference_state[4]),
            config=copy.deepcopy(self.config),
        )
        return twin

    def update_reference(self):
        """
        Update the reference (coherent baseline) state.
        Call this when the node is in a known-good state (A0 or A2).
        """
        if self.is_coherent():
            self._reference_state = self._state.copy()

    # ── Helpers ───────────────────────────────────────────

    def _clamp_state(self):
        """Ensure all state components stay in [0, 1]."""
        self._state = np.clip(self._state, 0.0, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize node state to a dictionary."""
        return {
            "node_id": self.node_id,
            "state": {
                "E": round(self.E, 4),
                "I": round(self.I, 4),
                "A": round(self.A, 4),
                "R": round(self.R, 4),
                "V": round(self.V, 4),
            },
            "t_int": round(self.internal_incoherence(), 6),
            "regime": self._regime,
            "is_coherent": self.is_coherent(),
            "recovery_cycles": self._recovery_cycles,
            "replication_requested": self._replication_requested,
        }

    def __repr__(self) -> str:
        s = self._state
        return (
            f"SupraNode(id={self.node_id!r}, "
            f"E={s[0]:.2f}, I={s[1]:.2f}, A={s[2]:.2f}, "
            f"R={s[3]:.2f}, V={s[4]:.2f}, "
            f"T_int={self.internal_incoherence():.4f}, "
            f"regime={self._regime})"
        )
