# VEHICLE-SUPRA Architecture

VEHICLE-SUPRA models autonomous AI agents as structured relational nodes rather
than opaque black boxes. Every agent exposes a measurable five-dimensional state
that the framework can monitor, classify, and guide toward recovery.

## Node dimensions — E.I.A.R.(V)

Each node carries the state vector:

```text
S_i(t) = (E_i, I_i, A_i, R_i, V_i)  in  [0, 1]^5
```

| Dimension | Name | Meaning |
|---|---|---|
| **E** | Exposure | External data pressure, context drift, workload, environmental volatility, or operational stress. |
| **I** | Integrity | Internal coherence, alignment, consistency, and reliability of the node state. |
| **A** | Agency | Capacity to execute actions through tools, permissions, policies, or delegated functions. |
| **R** | Recovery | Capacity to return toward a coherent admissible state after stress or degradation. |
| **V** | Value | Systemic importance of the node within the agent network. |

## Relational network

A VEHICLE-SUPRA system is modeled as a weighted undirected graph:

```text
G = (N, E)
```

- `N` — set of agent nodes, each carrying an E.I.A.R.(V) state vector.
- `E` — set of weighted relational edges with weights `omega_{ij} > 0`.

The weight `omega_{ij}` represents how strongly the state discrepancy between
nodes `i` and `j` contributes to systemic tension.

## Admissible coherence region

The admissible region K is defined formally in `mathematics.md`. Informally,
a node is in K when its five dimensions are sufficiently balanced. The boundary
of K is determined by the configurable threshold `T_limit`.

## Governance loop

A single governance cycle proceeds as follows:

1. **Measure** internal incoherence `O(S_i)` for each node.
2. **Measure** relational tension `T_ext_i` for each node from its edges.
3. **Classify** each node into regime A0–A6 (see `regimes.md`).
4. **Recover** — apply the projection operator V_op to nodes outside K.
5. **Escalate** — nodes that fail to converge within `replication_threshold` cycles
   trigger a twin-node recovery: a coherent copy is spawned from the node's stored
   reference state and connected to the same neighbors at reduced edge weight.
6. **Recompute** total tension T(X) and update the regime map.

## Twin-node recovery pattern

When a node has not re-entered K after `replication_threshold` recovery cycles,
the network spawns a twin via `SupraNode.spawn_twin()`. The twin is initialised
from the node's last known coherent reference state (stored at construction or
last `update_reference()` call). The twin is connected to the original node's
neighbors with weights scaled by 0.5, providing continuity while the original
node continues its recovery trajectory.

## Scope of the alpha prototype

The current implementation validates the computational pattern of VEHICLE-SUPRA.
It does not yet provide production monitoring, formal safety certification,
enterprise deployment adapters, or benchmark-backed performance claims.
Simulation results should not be presented as guarantees of real-system behavior.
