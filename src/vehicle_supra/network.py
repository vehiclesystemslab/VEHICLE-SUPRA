"""
vehicle_supra/network.py
────────────────────────
SupraNetwork — the relational graph of VEHICLE-SUPRA agents.

Models the global system as G = (N, E) where:
  - N = set of SupraNode agents
  - E = relational edges with weights ωᵢⱼ

Computes:
  T(X) = T_ext(X) + T_int(X)
  Regime classification for each node
  Autonomous recovery and replication protocols

Author : Roberto Borda Milan — VEHICLE Systems Lab
Framework DOI: 10.5281/zenodo.19981738
License: MIT
"""

from __future__ import annotations

import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

from .node import SupraNode, SupraNodeConfig, REGIME_A6


class SupraNetwork:
    """
    A network of VEHICLE-SUPRA agents modeled as a weighted undirected graph.

    The network computes:
      - T_ext(X) = Σ_{(i,j)∈E} ωᵢⱼ · ||Sᵢ - Sⱼ||²
      - T_int(X) = λ · Σᵢ∈N  ||P₋ Sᵢ||²
      - T(X) = T_ext + T_int
      - Per-node regime classification (A0–A6)
      - Autonomous recovery protocol across the network
      - Node replication when recovery fails

    Parameters
    ----------
    lam : float
        λ — weight of the internal coherence term in T(X).
    node_config : SupraNodeConfig
        Default configuration applied to all nodes.
    """

    def __init__(
        self,
        lam: float = 1.0,
        node_config: Optional[SupraNodeConfig] = None,
    ):
        self.lam = lam
        self._default_config = node_config or SupraNodeConfig()
        self._nodes: Dict[str, SupraNode] = {}
        self._edges: Dict[Tuple[str, str], float] = {}   # (id_i, id_j) → weight
        self._adjacency: Dict[str, List[str]] = {}
        self._step_count: int = 0
        self._recovery_log: List[Dict] = []

    # ── Graph construction ────────────────────────────────

    def add_node(
        self,
        node_id: str,
        E: float = 0.5,
        I: float = 0.8,
        A: float = 0.7,
        R: float = 0.6,
        V: float = 0.5,
        config: Optional[SupraNodeConfig] = None,
    ) -> SupraNode:
        """Add a new SupraNode agent to the network."""
        node = SupraNode(
            node_id=node_id,
            E=E, I=I, A=A, R=R, V=V,
            config=config or self._default_config,
        )
        self._nodes[node_id] = node
        self._adjacency[node_id] = []
        return node

    def add_edge(self, id_i: str, id_j: str, weight: float = 1.0):
        """
        Add a bidirectional relational edge between two agents.
        ωᵢⱼ controls how strongly their state discrepancy affects T_ext.
        """
        for a, b in [(id_i, id_j), (id_j, id_i)]:
            key = (min(a, b), max(a, b))
            self._edges[key] = float(weight)
        if id_j not in self._adjacency[id_i]:
            self._adjacency[id_i].append(id_j)
        if id_i not in self._adjacency[id_j]:
            self._adjacency[id_j].append(id_i)

    def get_node(self, node_id: str) -> SupraNode:
        """Retrieve a node by ID."""
        if node_id not in self._nodes:
            raise KeyError(f"Node '{node_id}' not found in network.")
        return self._nodes[node_id]

    def node_ids(self) -> List[str]:
        return list(self._nodes.keys())

    # ── Tension computation ───────────────────────────────

    def external_tension(self) -> float:
        """
        T_ext(X) = Σ_{(i,j)∈E} ωᵢⱼ · ||Sᵢ - Sⱼ||²

        Measures relational discrepancy between connected agents.
        """
        t_ext = 0.0
        for (id_i, id_j), weight in self._edges.items():
            s_i = self._nodes[id_i].state
            s_j = self._nodes[id_j].state
            diff = s_i - s_j
            t_ext += weight * float(np.dot(diff, diff))
        return t_ext

    def internal_tension(self) -> float:
        """
        T_int(X) = λ · Σᵢ∈N ||P₋ Sᵢ||²

        Sum of internal incoherence across all nodes.
        """
        t_int = 0.0
        for node in self._nodes.values():
            t_int += node.internal_incoherence()
        return self.lam * t_int

    def total_tension(self) -> float:
        """T(X) = T_ext(X) + T_int(X)"""
        return self.external_tension() + self.internal_tension()

    def node_tensions(self) -> Dict[str, Dict[str, float]]:
        """Per-node tension breakdown."""
        result = {}
        for node_id, node in self._nodes.items():
            # T_ext contribution of this node
            t_ext_i = 0.0
            for neighbor_id in self._adjacency.get(node_id, []):
                key = (min(node_id, neighbor_id), max(node_id, neighbor_id))
                w = self._edges.get(key, 1.0)
                diff = node.state - self._nodes[neighbor_id].state
                t_ext_i += w * float(np.dot(diff, diff))
            result[node_id] = {
                "t_ext": round(t_ext_i, 6),
                "t_int": round(node.internal_incoherence(), 6),
                "t_total": round(t_ext_i + node.internal_incoherence(), 6),
            }
        return result

    # ── Regime classification ─────────────────────────────

    def regimes(self) -> Dict[str, str]:
        """Classify all nodes into A0–A6 regimes."""
        tensions = self.node_tensions()
        cascade = self._detect_cascade()
        result = {}
        for node_id, node in self._nodes.items():
            is_isolated = len(self._adjacency.get(node_id, [])) == 0
            t_ext = tensions[node_id]["t_ext"]
            result[node_id] = node.classify_regime(
                t_ext=t_ext,
                is_isolated=is_isolated,
                cascade_detected=(node_id in cascade),
            )
        return result

    def regime(self, node_id: str) -> str:
        """Classify a single node."""
        return self.regimes()[node_id]

    def _detect_cascade(self) -> List[str]:
        """
        Detect A6 cascade: nodes where both T_ext and T_int are simultaneously high.
        Returns list of node_ids participating in the cascade.
        """
        tensions = self.node_tensions()
        cascade_nodes = []
        cascade_threshold = self._default_config.t_int_warning
        for node_id, t in tensions.items():
            if t["t_ext"] > cascade_threshold and t["t_int"] > cascade_threshold:
                cascade_nodes.append(node_id)
        # Only flag as cascade if 3+ nodes affected
        if len(cascade_nodes) >= 3:
            return cascade_nodes
        return []

    # ── Stress injection ──────────────────────────────────

    def inject_stress(self, node_id: str, **kwargs):
        """
        Inject stress into a node — simulates corrupt data or context drift.
        kwargs: any of E, I, A, R, V with values in [0, 1].

        Example
        -------
        net.inject_stress("agent_02", E=0.95, I=0.10)
        """
        self.get_node(node_id).inject_stress(**kwargs)

    # ── Network step ──────────────────────────────────────

    def step(self) -> Dict[str, Any]:
        """
        Execute one full network update cycle:
          1. Compute tensions for all nodes
          2. Update each node using V_op
          3. Check for replication requests
          4. Return step metrics

        Returns
        -------
        dict with step metrics: step number, T(X), regime map, replications
        """
        t_before = self.total_tension()
        regime_before = self.regimes()

        # Update all nodes
        for node_id, node in list(self._nodes.items()):
            neighbors = self._adjacency.get(node_id, [])
            neighbor_states = [self._nodes[n].state for n in neighbors]
            neighbor_weights = [
                self._edges.get(
                    (min(node_id, n), max(node_id, n)), 1.0
                )
                for n in neighbors
            ]
            node.recovery_step(neighbor_states, neighbor_weights, self.lam)

        # Handle replication requests
        replicated = []
        for node_id, node in list(self._nodes.items()):
            if node._replication_requested:
                twin = node.spawn_twin()
                self._nodes[twin.node_id] = twin
                self._adjacency[twin.node_id] = []
                # Connect twin to same neighbors
                for neighbor_id in self._adjacency.get(node_id, []):
                    key = (min(node_id, neighbor_id), max(node_id, neighbor_id))
                    w = self._edges.get(key, 1.0)
                    self.add_edge(twin.node_id, neighbor_id, weight=w * 0.5)
                node._replication_requested = False
                replicated.append({"original": node_id, "twin": twin.node_id})

        t_after = self.total_tension()
        self._step_count += 1

        return {
            "step":        self._step_count,
            "t_before":    round(t_before, 6),
            "t_after":     round(t_after, 6),
            "t_delta":     round(t_before - t_after, 6),
            "regimes":     self.regimes(),
            "replications": replicated,
        }

    # ── Full recovery protocol ────────────────────────────

    def recover(self, max_cycles: int = 100) -> Dict[str, Any]:
        """
        Run the full autonomous recovery protocol until:
          - All nodes reach coherent state, OR
          - max_cycles exceeded

        Returns a recovery report.
        """
        start_time = time.time()
        t_initial = self.total_tension()
        cycles_run = 0
        replications = []

        for cycle in range(max_cycles):
            # Check if all nodes are coherent
            all_coherent = all(
                node.is_coherent() for node in self._nodes.values()
            )
            if all_coherent:
                break

            # Mark nodes that need replication
            for node_id, node in self._nodes.items():
                if (
                    node._recovery_cycles > node.config.replication_threshold
                    and not node.is_coherent()
                ):
                    node.request_replication()

            step_result = self.step()
            replications.extend(step_result.get("replications", []))
            cycles_run += 1

        t_final = self.total_tension()
        elapsed_ms = (time.time() - start_time) * 1000
        all_coherent = all(n.is_coherent() for n in self._nodes.values())

        return {
            "status":       "recovered" if all_coherent else "partial",
            "cycles":       cycles_run,
            "t_initial":    round(t_initial, 6),
            "t_final":      round(t_final, 6),
            "t_reduction":  round(t_initial - t_final, 6),
            "time_ms":      round(elapsed_ms, 2),
            "continuity_preserved": True,
            "replications": replications,
            "regimes":      self.regimes(),
        }

    # ── Snapshot & summary ────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        """Full network state snapshot."""
        return {
            "step":          self._step_count,
            "node_count":    len(self._nodes),
            "edge_count":    len(self._edges),
            "t_ext":         round(self.external_tension(), 6),
            "t_int":         round(self.internal_tension(), 6),
            "t_total":       round(self.total_tension(), 6),
            "regimes":       self.regimes(),
            "nodes":         {nid: n.to_dict() for nid, n in self._nodes.items()},
        }

    def summary(self) -> str:
        """Human-readable network summary."""
        snap = self.snapshot()
        lines = [
            f"VEHICLE-SUPRA Network — step {snap['step']}",
            f"  Nodes : {snap['node_count']}",
            f"  Edges : {snap['edge_count']}",
            f"  T_ext : {snap['t_ext']:.4f}",
            f"  T_int : {snap['t_int']:.4f}",
            f"  T(X)  : {snap['t_total']:.4f}",
            f"  Regimes:",
        ]
        for nid, regime in snap["regimes"].items():
            t = self.node_tensions()[nid]
            lines.append(
                f"    [{regime}] {nid:20s} "
                f"T_int={t['t_int']:.4f} T_ext={t['t_ext']:.4f}"
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"SupraNetwork(nodes={len(self._nodes)}, "
            f"edges={len(self._edges)}, "
            f"T(X)={self.total_tension():.4f})"
        )
