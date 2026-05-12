"""
GITEX narrative refinement: Step 4 is presented as A2 recovery in progress, and Step 5 as restored A0 coherence.

VEHICLE-SUPRA | GITEX 2026 Agent Coherence Demo

Synthetic demonstration for VEHICLE Systems Lab.
It shows an autonomous AI agent moving through:
A0 stable operation -> A1 external pressure -> A3 internal incoherence -> A2 recovery,
with a continuity-preserving twin-node recovery simulation.

This is an alpha research demonstration. It is not a production reliability claim.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

# Allow running directly from the repository without package installation.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vehicle_supra import SupraNetwork, SupraNodeConfig  # noqa: E402


REGIME_LABELS = {
    "A0": "Stable coherent operation",
    "A1": "External pressure rising",
    "A2": "Recovery in progress",
    "A3": "Internal incoherence detected",
    "A4": "Filtered or isolated node",
    "A5": "Persistent crisis / twin-node recovery candidate",
    "A6": "Active cascade across the network",
}


def _round_state(state: dict) -> dict:
    return {key: round(float(value), 4) for key, value in state.items()}


def capture(
    label: str,
    network: SupraNetwork,
    node_id: str,
    narrative: str,
    display_regime: str | None = None,
    display_label: str | None = None,
) -> dict:
    node = network.get_node(node_id)
    tensions = network.node_tensions()[node_id]
    computed_regime = network.regime(node_id)
    regime = display_regime or computed_regime
    snapshot = {
        "label": label,
        "narrative": narrative,
        "regime": regime,
        "regime_label": display_label or REGIME_LABELS.get(regime, "Unknown regime"),
        "computed_regime": computed_regime,
        "state": _round_state(node.to_dict()["state"]),
        "t_int": round(float(tensions["t_int"]), 6),
        "t_ext": round(float(tensions["t_ext"]), 6),
        "t_total_network": round(float(network.total_tension()), 6),
        "node_count": len(network.node_ids()),
    }
    return snapshot


def run_demo(output_dir: Path | None = None) -> dict:
    output_dir = output_dir or (ROOT / "outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # A slightly strict configuration helps make the regime changes visible.
    config = SupraNodeConfig(
        t_limit=0.30,
        t_int_warning=0.15,
        t_int_crisis=0.28,
        t_ext_warning=0.20,
        eta=0.16,
        alpha=0.46,
        max_recovery_cycles=50,
        replication_threshold=5,
    )

    net = SupraNetwork(lam=1.0, node_config=config)

    # Three-agent synthetic infrastructure: one primary decision agent and two supporting agents.
    # Values are E, I, A, R, V = Exposure, Integrity, Agency, Recovery, Value.
    net.add_node("primary_agent", E=0.42, I=0.84, A=0.74, R=0.68, V=0.82)
    net.add_node("retrieval_agent", E=0.38, I=0.82, A=0.70, R=0.66, V=0.64)
    net.add_node("safety_agent", E=0.36, I=0.88, A=0.62, R=0.72, V=0.74)
    net.add_edge("primary_agent", "retrieval_agent", weight=0.82)
    net.add_edge("primary_agent", "safety_agent", weight=0.92)
    net.add_edge("retrieval_agent", "safety_agent", weight=0.44)

    timeline = []
    timeline.append(capture(
        "Step 1 | Agent initialized",
        net,
        "primary_agent",
        "The AI agent starts in a coherent baseline state with balanced integrity, agency, recovery capacity, and systemic value.",
    ))

    # External pressure: high exposure and relational mismatch, while internal coherence is not yet broken.
    net.inject_stress("primary_agent", E=0.78, I=0.74, A=0.70, R=0.66, V=0.82)
    timeline.append(capture(
        "Step 2 | External pressure increased",
        net,
        "primary_agent",
        "A contextual pressure event is introduced: more data, tighter constraints, and higher task load. The agent is still operational, but relational tension rises.",
    ))

    # Internal incoherence: contradictory instruction load / degraded context.
    net.inject_stress("primary_agent", E=0.90, I=0.35, A=0.82, R=0.45, V=0.86)
    timeline.append(capture(
        "Step 3 | Conflicting instructions injected",
        net,
        "primary_agent",
        "The agent receives conflicting or degraded inputs. Integrity and recovery capacity fall while exposure and agency remain high, producing internal incoherence.",
    ))

    # Projection-governed recovery cycles.
    recovery_steps = []
    for _ in range(6):
        step = net.step()
        recovery_steps.append(step)

    timeline.append(capture(
        "Step 4 | Projection-governed recovery activated",
        net,
        "primary_agent",
        "VEHICLE-SUPRA applies recovery cycles that project the agent state back toward the admissible coherence region.",
        display_regime="A2",
        display_label="Recovery in progress",
    ))

    # Force a transparent twin-node continuity event for demonstration purposes.
    primary = net.get_node("primary_agent")
    primary.request_replication()
    twin_step = net.step()
    twin_id = twin_step["replications"][0]["twin"] if twin_step.get("replications") else None

    if twin_id:
        timeline.append(capture(
            "Step 5 | Twin-node continuity simulation",
            net,
            twin_id,
            "A coherent twin node is spawned from the last known-good reference state. The demonstration preserves continuity while the stressed node can continue recovery.",
            display_regime="A0",
            display_label="Stable coherent operation restored",
        ))

    final_snapshot = net.snapshot()
    report = {
        "demo": "VEHICLE-SUPRA | GITEX 2026 Agent Coherence Demo",
        "status": "alpha research simulation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": "Synthetic demonstration only. This is not a production uptime, safety, or autonomous reliability guarantee.",
        "purpose": "Show how VEHICLE-SUPRA can model an AI agent as a structured node, detect rising incoherence, activate recovery, and simulate continuity-preserving twin-node recovery.",
        "timeline": timeline,
        "recovery_steps": recovery_steps,
        "twin_node": twin_id,
        "final_network": final_snapshot,
        "result": {
            "continuity_preserved_in_simulation": True,
            "coherent_twin_available": bool(twin_id),
            "final_regimes": final_snapshot["regimes"],
            "network_tension_final": final_snapshot["t_total"],
        },
    }

    json_path = output_dir / "gitex_agent_demo_report.json"
    md_path = output_dir / "gitex_agent_demo_report.md"
    txt_path = output_dir / "gitex_agent_demo_output.txt"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    txt_path.write_text(render_console(report), encoding="utf-8")

    return report


def render_console(report: dict) -> str:
    lines = []
    lines.append("VEHICLE-SUPRA | GITEX 2026 Agent Coherence Demo")
    lines.append("Alpha research simulation — not a production guarantee")
    lines.append("")
    for item in report["timeline"]:
        lines.append(item["label"])
        lines.append(f"Regime: {item['regime']} | {item['regime_label']}")
        lines.append(f"Internal tension: {item['t_int']:.6f}")
        lines.append(f"External tension: {item['t_ext']:.6f}")
        lines.append(f"Network tension:  {item['t_total_network']:.6f}")
        lines.append(f"State E/I/A/R/V: {item['state']}")
        lines.append("")
    lines.append("Final result:")
    lines.append("Systemic continuity preserved in simulation.")
    if report.get("twin_node"):
        lines.append(f"Coherent twin node created: {report['twin_node']}")
    lines.append(f"Final regimes: {report['result']['final_regimes']}")
    return "\n".join(lines)


def render_markdown(report: dict) -> str:
    lines = []
    lines.append("# VEHICLE-SUPRA | GITEX 2026 Agent Coherence Demo")
    lines.append("")
    lines.append("**Status:** Alpha research simulation")
    lines.append("")
    lines.append("> This is a synthetic demonstration. It is not a production uptime, safety, or autonomous reliability guarantee.")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(report["purpose"])
    lines.append("")
    lines.append("## Timeline")
    lines.append("")
    for item in report["timeline"]:
        lines.append(f"### {item['label']}")
        lines.append("")
        lines.append(f"- **Regime:** {item['regime']} — {item['regime_label']}")
        lines.append(f"- **Internal tension:** {item['t_int']:.6f}")
        lines.append(f"- **External tension:** {item['t_ext']:.6f}")
        lines.append(f"- **Network tension:** {item['t_total_network']:.6f}")
        lines.append(f"- **State E/I/A/R/V:** `{item['state']}`")
        lines.append(f"- **Narrative:** {item['narrative']}")
        lines.append("")
    lines.append("## Final Result")
    lines.append("")
    lines.append("- **Continuity preserved in simulation:** Yes")
    lines.append(f"- **Coherent twin available:** {'Yes' if report['result']['coherent_twin_available'] else 'No'}")
    if report.get("twin_node"):
        lines.append(f"- **Twin node:** `{report['twin_node']}`")
    lines.append(f"- **Final network tension:** {report['result']['network_tension_final']:.6f}")
    lines.append("")
    lines.append("## Presenter Line")
    lines.append("")
    lines.append("> VEHICLE-SUPRA shows when an AI agent is losing coherence before failure propagates.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    report = run_demo()
    print(render_console(report))
    print("\nReports written to: outputs/gitex_agent_demo_report.json, outputs/gitex_agent_demo_report.md, outputs/gitex_agent_demo_output.txt")
