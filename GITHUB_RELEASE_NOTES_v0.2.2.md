# VEHICLE-SUPRA v0.2.2 — Mathematical Correctness & Documentation Pass

This release strengthens the formal mathematical documentation and test coverage
of the VEHICLE-SUPRA alpha prototype. No changes to core algorithmic behavior;
the implementation in `node.py` and `network.py` is unchanged from v0.2.1.

## What changed

### Documentation

- `docs/mathematics.md` — fully rewritten. Now formally defines the admissible
  region K, the centering operator P_-, the projection operator P_K, the local
  gradient, the V_op correction operator, the relaxed update rule, and the
  convergence criterion. Previously these were stated informally or omitted.

- `docs/regimes.md` — fully rewritten. A4 (Isolated) is now precisely defined
  as degree = 0 in G. A6 (Cascade) documents the 3-node minimum threshold.
  Priority ordering of regime evaluation is now explicit.

- `docs/architecture.md` — updated with a formal reference to K and a precise
  description of the twin-node recovery pattern including spawn condition,
  reference state usage, and edge weight scaling.

- `docs/glossary.md` — new file. Formal one-entry-per-term glossary covering
  all mathematical symbols, operators, state dimensions, and regime terms.

- `README.md` — K is now defined inline in the Core Concept section. A4
  definition updated to match code. Rover hardware language clarified to
  distinguish software simulation from unvalidated physical hardware.

### Tests

- `tests/test_math_correctness.py` — new file with 9 tests validating the
  implementation against the formal mathematical definitions:
  - K boundary: balanced node in K; imbalanced node outside K.
  - P_K projection: result always lands inside K.
  - Gradient: zero for balanced isolated node; correct direction for neighbor term.
  - A4 isolation: requires degree = 0 exactly.
  - A6 cascade: requires >= 3 nodes above both warning thresholds.
  - Recovery monotonicity: T(X) does not increase under the recovery protocol.

### Version

- `setup.py` and `CITATION.cff` updated to `0.2.2`.

## Test status

17 passed / 0 failed / 0 warnings.

## Important disclaimer

This is an alpha research simulation. It is not a production uptime, robotics
safety, autonomous reliability, or self-healing AI guarantee.
