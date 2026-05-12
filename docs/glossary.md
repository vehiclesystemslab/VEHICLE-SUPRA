# Glossary — VEHICLE-SUPRA

**Admissible region K** — The set of node states `S in [0,1]^5` satisfying
`O(S) <= T_limit`. A node inside K is considered coherent. See `mathematics.md`.

**Agency (A)** — The second-to-last component of the E.I.A.R.(V) state vector.
Represents the node's effective capacity to act: tool access, permission scope,
execution bandwidth.

**Cascade (A6)** — Network regime where 3 or more nodes simultaneously exceed
both `t_int_warning` and `t_ext_warning`. Signals systemic instability requiring
isolation of propagation paths.

**Centering operator P_-** — The 5×5 matrix `I_5 - (1/5)*11^T` used to measure
dimensional imbalance in a state vector. Eigenvalue 0 on the uniform direction,
eigenvalue 1 on all orthogonal directions.

**Coherence** — Condition where a node's state lies inside K. Formally:
`O(S_i) = ||P_- S_i||^2 <= T_limit`.

**E.I.A.R.(V)** — The five-dimensional structured state model: Exposure,
Integrity, Agency, Recovery, Value.

**Exposure (E)** — First component of the state vector. Represents external
pressure, environmental volatility, input noise, or operational load.

**Gradient (local)** — `grad_{S_i} T(X) = sum_j omega_{ij}*(S_i - S_j) + lambda*P_- S_i`.
Combines relational discrepancy correction with internal coherence correction.

**Integrity (I)** — Second component of the state vector. Represents internal
alignment, consistency, and reliability of the node's state.

**Internal incoherence O(S_i)** — `||P_- S_i||^2`. Zero for perfectly balanced
nodes; increases as dimensional imbalance grows.

**Lambda (λ)** — Scalar weight applied to the internal tension term in T(X).
Default: 1.0. Controls the relative importance of internal coherence versus
relational agreement in the total objective.

**Recovery (R)** — Fourth component of the state vector. Represents the node's
self-repair capacity and its access to twin-node resources.

**Regime** — One of seven operational states (A0–A6) assigned to each node
based on its tension metrics and network context. See `regimes.md`.

**Relaxed update** — `S_i(t+1) = (1-alpha)*S_i(t) + alpha*V_op(S_i(t); X)`.
Convex combination preventing abrupt state jumps.

**T(X)** — Total system tension: `T_ext(X) + T_int(X)`. The scalar objective
the recovery protocol drives toward zero.

**T_ext** — External relational tension: `sum_{(i,j)} omega_{ij} * ||S_i - S_j||^2`.

**T_int** — Internal network tension: `lambda * sum_i O(S_i)`.

**T_limit** — Configurable threshold defining the boundary of K. Default: 0.30.

**Twin-node recovery** — When a node exceeds `replication_threshold` recovery
cycles without re-entering K, a coherent twin is spawned from the node's stored
reference state. The twin connects to the original neighbors at 0.5x edge weight.

**Value (V)** — Fifth component of the state vector. Represents the node's
systemic importance in the network — e.g. proximity to mission-critical targets.

**V_op** — Projection-governed correction operator: `P_K(S_i - eta * grad T(X))`.
Takes one projected gradient step toward K.

**omega_{ij}** — Edge weight between nodes i and j. Controls how strongly their
state discrepancy contributes to T_ext.
