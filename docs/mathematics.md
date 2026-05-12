# Mathematical Notes

This document summarizes the mathematical structure implemented in the alpha prototype.

## Structured state

Each node carries a five-dimensional state vector constrained to the unit hypercube:

```text
S_i = (E_i, I_i, A_i, R_i, V_i)  in  [0, 1]^5
```

## Centering operator

The prototype defines the centering operator:

```text
P_- = I_5 - (1/5) * 11^T
```

where `I_5` is the 5×5 identity matrix and `11^T` is the 5×5 all-ones matrix.
`P_-` projects any vector onto the hyperplane orthogonal to the uniform direction,
measuring dimensional imbalance independently of the mean level.

## Internal incoherence

Internal incoherence of node `i` is defined as:

```text
O(S_i) = ||P_- S_i||^2  =  S_i^T P_- S_i
```

A perfectly balanced node (all components equal) has `O(S) = 0`.
High `O(S)` indicates that dimensions are severely out of balance —
for example, high Agency with very low Integrity.

## Admissible region K

The admissible coherence region is the set of states with bounded internal incoherence:

```text
K = { S in [0,1]^5  :  O(S) <= T_limit }
```

`T_limit` is configurable via `SupraNodeConfig.t_limit` (default: 0.30).
A node is considered coherent if and only if its state lies in K.

## External relational tension

For a network graph G = (N, E) with edge weights omega_{ij}:

```text
T_ext(X) = sum_{(i,j) in E}  omega_{ij} * ||S_i - S_j||^2
```

This measures aggregate state discrepancy across all relational edges.

## Internal network tension

```text
T_int(X) = lambda * sum_{i in N}  O(S_i)
          = lambda * sum_{i in N}  ||P_- S_i||^2
```

The scalar `lambda` (default: 1.0) controls the relative weight of internal
incoherence in the total objective.

## Total tension

```text
T(X) = T_ext(X) + T_int(X)
```

`T(X)` is the scalar objective that the projection-governed recovery protocol
drives toward zero.

## Local gradient

The gradient of T(X) with respect to node i's state is:

```text
grad_{S_i} T(X) = sum_{j: (i,j) in E} omega_{ij} * (S_i - S_j)  +  lambda * P_- S_i
```

The first term corrects relational discrepancy; the second corrects internal imbalance.

## Projection operator P_K

The projection onto K is the closest point in K to a candidate vector z:

```text
P_K(z) = argmin_{s in K} ||s - z||^2
```

If z is already in K, then `P_K(z) = z` (clipped to [0,1]^5).
Otherwise the prototype uses a 64-iteration binary search over a scaling
parameter mu to find the boundary point satisfying the constraint exactly.

## Projection-governed correction operator V_op

```text
V_op(S_i; X) = P_K( S_i - eta * grad_{S_i} T(X) )
```

`eta` is the gradient-descent step size (`SupraNodeConfig.eta`, default: 0.10).
V_op takes one projected gradient step and returns the corrected state.
It does not modify the node in place; the caller applies the relaxed update.

## Relaxed state update

To avoid hard jumps, the prototype uses a convex combination:

```text
S_i(t+1) = (1 - alpha) * S_i(t)  +  alpha * V_op(S_i(t); X)
```

where `alpha in (0, 1]` is the relaxation parameter (`SupraNodeConfig.alpha`,
default: 0.30). Smaller alpha gives slower but more stable convergence.

## Convergence criterion

A node is declared recovered when its state re-enters K:

```text
O(S_i(t+1)) <= T_limit
```

The network is declared fully recovered when every node satisfies this condition.
Non-convergent nodes (exceeding `SupraNodeConfig.replication_threshold` cycles)
trigger the twin-node recovery pattern described in `architecture.md`.
