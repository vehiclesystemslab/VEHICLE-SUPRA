# VEHICLE-SUPRA

**Coherence-Governed Architecture for Autonomous AI Agents**  
*Alpha research prototype by VEHICLE Systems Lab*

[![License: MIT](https://img.shields.io/badge/License-MIT-violet.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Development Status](https://img.shields.io/badge/status-alpha%20research%20prototype-orange.svg)](#project-status)
[![VEHICLE Systems Lab](https://img.shields.io/badge/VEHICLE%20Systems%20Lab-Santa%20Cruz%2C%20Bolivia-green.svg)](https://vehiclesystemslab.com)

---

## What is VEHICLE-SUPRA?

VEHICLE-SUPRA is a projection-governed architecture for autonomous AI agents. It models each agent as a structured relational node with measurable coherence, tension, recovery capacity, and systemic value.

The purpose of VEHICLE-SUPRA is to help AI systems detect incoherence before failure propagates, recover toward admissible states, and operate more resiliently within multi-agent networks.

This repository contains an alpha research prototype of the core engine. It is intended for simulation, research, and architectural validation. It should not yet be interpreted as a production-ready safety system.

---

## Core Concept

Each VEHICLE-SUPRA agent carries a five-dimensional structured state:

```text
S_i(t) = (E_i, I_i, A_i, R_i, V_i)
```

| Component | Name | Meaning in the agent context |
|---|---|---|
| **E** | Exposure | External pressure, input volatility, context drift, or operational load. |
| **I** | Integrity | Internal coherence, alignment, consistency, and state reliability. |
| **A** | Agency | Capacity to act through tools, policies, execution, and available permissions. |
| **R** | Recovery | Capacity to return toward a coherent state after instability. |
| **V** | Value | Systemic importance of the node within the agent network. |

The system estimates structural tension as:

```text
T(X) = T_ext(X) + T_int(X)
```

Where:

- `T_ext` measures relational discrepancy between connected agents.
- `T_int` measures internal incoherence inside each structured node.

When tension exceeds defined thresholds, the projection operator `V_op` guides the node back toward the admissible coherence region `K`, defined as the set of states whose internal incoherence `O(S_i) = ||P_- S_i||²` does not exceed a configurable threshold `T_limit`. If recovery does not converge in simulation, the framework initiates a twin-node recovery pattern — spawning a coherent copy from the node's last known good state — to preserve continuity in the modeled network.

---

## Current Implementation

The current alpha prototype includes:

- `SupraNode`: an E.I.A.R.(V) structured agent node.
- `SupraNetwork`: a weighted relational graph of agent nodes.
- Internal tension measurement.
- External relational tension measurement.
- Total system tension `T(X)`.
- A0-A6 regime classification.
- Projection-governed recovery steps.
- Twin-node recovery simulation for non-convergent nodes.
- Enterprise network simulation example.
- GITEX AI-agent coherence demo.
- VEHICLE-LUNA lunar rover mission simulation.

---

## Repository Structure

```text
vehicle-supra/
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── setup.py
├── src/
│   └── vehicle_supra/
│       ├── __init__.py
│       ├── node.py
│       └── network.py
├── examples/
│   ├── enterprise_network.py
│   ├── gitex_agent_demo.py
│   ├── vehicle_luna.py
│   └── README_GITEX_DEMO.md
├── docs/
│   ├── architecture.md
│   ├── mathematics.md
│   ├── regimes.md
│   ├── glossary.md
│   ├── roadmap.md
│   ├── gitex_demo_explanation.md
│   └── demo_script_for_presenter.md
├── sample_outputs/
│   ├── gitex_agent_demo_output.txt
│   ├── gitex_agent_demo_report.json
│   └── gitex_agent_demo_report.md
├── outputs/
│   └── .gitkeep
└── tests/
    ├── conftest.py
    ├── test_node.py
    └── test_network.py
```

---

## Installation

```bash
git clone https://github.com/vehiclesystemslab/VEHICLE-SUPRA.git
cd vehicle-supra
pip install -r requirements.txt
pip install -e .
```

For local validation:

```bash
pip install pytest
pytest
```

---

## Quick Start

### Single structured node

```python
from vehicle_supra import SupraNode

node = SupraNode(
    node_id="agent_01",
    E=0.2,
    I=0.9,
    A=0.8,
    R=0.7,
    V=0.6,
)

print(node.internal_tension())
print(node.is_coherent())
```

### Network of agents

```python
from vehicle_supra import SupraNetwork

net = SupraNetwork()
net.add_node("agent_01", E=0.2, I=0.9, A=0.8, R=0.7, V=0.6)
net.add_node("agent_02", E=0.3, I=0.8, A=0.7, R=0.6, V=0.5)
net.add_node("agent_03", E=0.1, I=0.95, A=0.9, R=0.8, V=0.4)

net.add_edge("agent_01", "agent_02", weight=0.8)
net.add_edge("agent_02", "agent_03", weight=0.6)

print(net.total_tension())
print(net.regimes())
```

### Stress and recovery simulation

```python
net.inject_stress("agent_02", E=0.95, I=0.15)

print(net.total_tension())
print(net.regime("agent_02"))

result = net.recover(max_cycles=50)
print(result)
```

---

## A0-A6 Regime Taxonomy

| Regime | Name | Interpretation | Prototype response |
|---|---|---|---|
| **A0** | Stable | Low tension and coherent state. | Normal operation. |
| **A1** | External pressure | Relational pressure is rising while internal coherence remains present. | Monitor and validate inputs. |
| **A2** | Recovering | Tension is decreasing after correction. | Continue verification. |
| **A3** | Internal incoherence | Internal dimensions are unbalanced. | Apply projection-governed recovery. |
| **A4** | Isolated | Node has no active relational edges (degree = 0 in G). | Standby or inspection. |
| **A5** | Crisis | High internal tension or non-convergent behavior. | Trigger recovery escalation in simulation. |
| **A6** | Cascade | Multi-node instability is detected. | Isolate, reduce propagation, and rebuild from coherent nodes. |

---

## Project Status

**Status:** Alpha research prototype.

This repository demonstrates the core mathematical and computational pattern of VEHICLE-SUPRA. The current code is suitable for research simulations and early demonstrations. It does not yet include production-grade monitoring, formal benchmarks, security hardening, dashboard visualization, or deployment integrations.

### Implemented

- Structured node model.
- Agent network model.
- Internal and external tension metrics.
- Projection-governed recovery steps.
- A0-A6 classification.
- Basic twin-node recovery simulation.
- Example enterprise scenario.
- Initial test coverage.

### In development

- Formal benchmark scenarios.
- Dashboard visualization.
- Expanded tests.
- API reference.
- Documentation for deployment patterns.
- Integration examples for real agent frameworks.

---

## Scientific Foundation

VEHICLE-SUPRA is a technological instance of the VEHICLE Formula-as-Architecture, a projection-governed framework for complex relational systems developed at VEHICLE Systems Lab.

**Reference framework:**

> Borda Milan, R. (2026). *The Borda Milan Pyramid and the VEHICLE Formula-as-Architecture*. VEHICLE Systems Lab / Zenodo. DOI: 10.5281/zenodo.19981738

---

## Citation

If you use this repository in research, prototypes, or derivative work, please cite the project using `CITATION.cff`.

A project-specific Zenodo DOI should be added after the GitHub release is archived in Zenodo.

---

## License

This project is released under the MIT License. See `LICENSE`.

---

## Contact

**VEHICLE Systems Lab**  
Santa Cruz de la Sierra, Bolivia  
Website: https://vehiclesystemslab.com  
Email: contact@vehiclesystemslab.com


## GITEX 2026 Simulation Demo

Version **v0.2.1** includes a synthetic demonstration prepared for GITEX 2026:

```bash
python examples/gitex_agent_demo.py
```

The demo shows an autonomous AI agent moving through:

1. **A0** stable coherent operation
2. **A1** external pressure
3. **A3** internal incoherence
4. **A2** projection-governed recovery in progress
5. **A0** stable coherent operation restored through twin-node continuity simulation

Generated reports are written to `outputs/` as JSON, Markdown, and console text.

This is an alpha research simulation and must not be presented as a production reliability guarantee.

---

## VEHICLE-LUNA — Lunar Rover Mission Simulation

The most visible application of VEHICLE-SUPRA is **VEHICLE-LUNA**:
20 autonomous micro-rovers exploring a lunar surface, each a structured
E.I.A.R.(V) node governed by T(X).

```bash
python examples/vehicle_luna.py                      # all 3 scenarios
python examples/vehicle_luna.py --scenario crater    # single crater fall
python examples/vehicle_luna.py --scenario solar_storm  # cascade event
python examples/vehicle_luna.py --quiet --export     # CI mode + JSON report
```

**E.I.A.R.(V) in the lunar context:**

| Component | Lunar meaning |
|-----------|--------------|
| E | Terrain hazard + radiation + comms latency |
| I | Sensor + motor + power coherence |
| A | Mobility capacity + tool availability |
| R | Self-repair capacity + twin-rover availability |
| V | Mission importance (proximity to water-ice targets) |

The software simulation is designed as a portable counterpart for a future hardware rover demonstration. Any physical Raspberry Pi / ESP32 rover stand at GITEX Global 2026 is a planned exhibit and should only be described as validated after physical hardware testing is complete and independently confirmed.
