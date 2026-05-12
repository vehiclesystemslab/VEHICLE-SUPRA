# A0-A6 Regime Taxonomy

VEHICLE-SUPRA classifies each node into one of seven regimes based on its internal
incoherence `O(S_i)`, its external tension contribution `T_ext_i`, and network-level
conditions (isolation, cascade). All thresholds are configurable via `SupraNodeConfig`.

## Classification logic

Regimes are evaluated in priority order (highest to lowest):

| Priority | Regime | Trigger condition |
|---|---|---|
| 1 | **A6** Cascade | 3 or more nodes simultaneously exceed both `t_int_warning` and `t_ext_warning` |
| 2 | **A5** Crisis | `O(S_i) >= t_int_crisis` **or** replication requested after non-convergence |
| 3 | **A3** Internal incoherence | `O(S_i) >= t_int_warning` |
| 4 | **A2** Recovering | Node is in recovery and `O(S_i) < t_int_warning` |
| 5 | **A4** Isolated | Node has zero relational edges (degree = 0 in G) |
| 6 | **A1** External pressure | `T_ext_i >= t_ext_warning` |
| 7 | **A0** Stable | None of the above |

## Default thresholds (`SupraNodeConfig`)

| Parameter | Default | Role |
|---|---|---|
| `t_limit` | 0.30 | Boundary of admissible region K |
| `t_int_warning` | 0.15 | A3 entry / A2 exit threshold |
| `t_int_crisis` | 0.28 | A5 entry threshold |
| `t_ext_warning` | 0.20 | A1 entry threshold |

## Regime reference table

| Regime | Name | Interpretation | Prototype response |
|---|---|---|---|
| A0 | Stable | `O(S_i)` and `T_ext_i` both below warning levels. Node is in K. | Normal operation. |
| A1 | External pressure | Relational discrepancy with neighbors is rising; internal coherence is still present. | Monitor, validate inputs, increase observation. |
| A2 | Recovering | Node is in active recovery and `O(S_i)` has returned below `t_int_warning`. | Continue verification and stabilize. |
| A3 | Internal incoherence | `O(S_i) >= t_int_warning`. Dimensions are out of balance. | Apply projection-governed recovery via V_op. |
| A4 | Isolated | Node has no active edges in G (degree = 0). | Standby, inspection, or controlled reintegration. |
| A5 | Crisis | `O(S_i) >= t_int_crisis` or recovery has not converged within `replication_threshold` cycles. | Escalate to twin-node recovery simulation. |
| A6 | Cascade | 3 or more nodes simultaneously exceed both `t_int_warning` and `t_ext_warning`. | Isolate propagation paths; rebuild from coherent nodes. |

All thresholds are adjustable per node via `SupraNodeConfig`. The classification
reflects the current simulated state and should not be interpreted as a production
safety certification.
