# Mathematical Notes

This document summarizes the mathematical structure implemented in the alpha prototype.

## Structured state

Each node has a state vector:

```text
S_i = (E_i, I_i, A_i, R_i, V_i) in [0, 1]^5
```

## Internal incoherence

The prototype uses a centering operator:

```text
P_- = I_5 - (1/5) 11^T
```

Internal incoherence is measured as:

```text
O(S_i) = ||P_- S_i||^2
```

This captures imbalance across the five dimensions of a node.

## External relational tension

For connected nodes `i` and `j`, external tension is computed as:

```text
T_ext = sum_{(i,j)} w_ij ||S_i - S_j||^2
```

This measures state discrepancy across the relational network.

## Internal network tension

```text
T_int = lambda * sum_i ||P_- S_i||^2
```

## Total tension

```text
T(X) = T_ext(X) + T_int(X)
```

## Projection-governed correction

The recovery operator computes a gradient-guided candidate state and projects it toward the admissible region `K`:

```text
V_op(S_i; X) = P_K(S_i - eta * grad T(X))
```

Where `K` is defined by the configured internal tension limit.

## Relaxed update

The prototype uses a relaxed update:

```text
S_i(t+1) = (1 - alpha) S_i(t) + alpha V_op(S_i(t); X)
```

This avoids hard jumps in state and allows gradual convergence in simulation.
