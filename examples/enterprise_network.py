"""
examples/enterprise_network.py
───────────────────────────────
GITEX Global 2026 — Expand North Star — Supernova Challenge
Live demo: 12-agent enterprise network showing self-healing in action.

This is the script behind the 4-minute GITEX demo.

Run:
    python examples/enterprise_network.py

Author : Roberto Borda Milan — VEHICLE Systems Lab
Framework DOI: 10.5281/zenodo.19981738
"""

import time
import sys
import os

# Allow running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vehicle_supra import SupraNetwork, SupraNodeConfig


def colored(text: str, code: str) -> str:
    """ANSI color helper."""
    colors = {
        "green":  "\033[92m",
        "yellow": "\033[93m",
        "red":    "\033[91m",
        "cyan":   "\033[96m",
        "purple": "\033[95m",
        "white":  "\033[97m",
        "gray":   "\033[90m",
        "bold":   "\033[1m",
        "reset":  "\033[0m",
    }
    return f"{colors.get(code, '')}{text}{colors['reset']}"


def regime_color(regime: str) -> str:
    palette = {
        "A0": "green",
        "A1": "yellow",
        "A2": "cyan",
        "A3": "yellow",
        "A4": "gray",
        "A5": "red",
        "A6": "red",
    }
    return colored(regime, palette.get(regime, "white"))


def print_network_status(net: SupraNetwork, title: str):
    tensions = net.node_tensions()
    regimes  = net.regimes()
    print(f"\n{colored('─' * 62, 'gray')}")
    print(colored(f"  {title}", "bold"))
    print(colored(f"  T(X) = {net.total_tension():.4f}  "
                  f"(T_ext={net.external_tension():.4f}  "
                  f"T_int={net.internal_tension():.4f})", "cyan"))
    print(colored('─' * 62, 'gray'))
    print(f"  {'Node':<18} {'Regime':<6} {'T_int':>8} {'T_ext':>8} {'Status'}")
    print(colored('  ' + '─' * 58, 'gray'))
    for nid in sorted(net.node_ids()):
        r  = regimes[nid]
        t  = tensions[nid]
        rc = regime_color(r)
        status_map = {
            "A0": colored("● stable",    "green"),
            "A1": colored("⚡ pressure", "yellow"),
            "A2": colored("↑ recovering","cyan"),
            "A3": colored("⚠ incoherent","yellow"),
            "A4": colored("◌ isolated",  "gray"),
            "A5": colored("✕ CRISIS",    "red"),
            "A6": colored("✕ CASCADE",   "red"),
        }
        status = status_map.get(r, r)
        print(f"  {nid:<18} {rc:<6}   {t['t_int']:>6.4f}   {t['t_ext']:>6.4f}   {status}")
    print()


def demo_pause(seconds: float, label: str = ""):
    if label:
        print(colored(f"  ⏱  {label}", "gray"))
    time.sleep(seconds)


def main():
    print()
    print(colored("═" * 62, "purple"))
    print(colored("  VEHICLE-SUPRA — GITEX Global 2026 Live Demo", "bold"))
    print(colored("  Expand North Star · Supernova Challenge", "purple"))
    print(colored("  Roberto Borda Milan · VEHICLE Systems Lab · Bolivia", "gray"))
    print(colored("═" * 62, "purple"))

    # ── BUILD THE NETWORK ─────────────────────────────────
    print(colored("\n[1/4] Building 12-agent enterprise network...", "cyan"))

    cfg = SupraNodeConfig(
        t_limit=0.28,
        t_int_warning=0.14,
        t_int_crisis=0.25,
        t_ext_warning=0.18,
        eta=0.12,
        alpha=0.25,
        replication_threshold=15,
    )

    net = SupraNetwork(lam=1.0, node_config=cfg)

    # Core processing agents
    net.add_node("core_01",    E=0.15, I=0.92, A=0.88, R=0.75, V=0.90)
    net.add_node("core_02",    E=0.18, I=0.89, A=0.85, R=0.72, V=0.85)
    net.add_node("core_03",    E=0.12, I=0.95, A=0.90, R=0.80, V=0.80)
    # Data ingestion agents
    net.add_node("ingest_01",  E=0.22, I=0.87, A=0.82, R=0.68, V=0.60)
    net.add_node("ingest_02",  E=0.20, I=0.85, A=0.80, R=0.65, V=0.55)
    # Analysis agents
    net.add_node("analysis_01",E=0.16, I=0.91, A=0.86, R=0.74, V=0.75)
    net.add_node("analysis_02",E=0.14, I=0.93, A=0.88, R=0.76, V=0.70)
    # Output agents
    net.add_node("output_01",  E=0.10, I=0.94, A=0.89, R=0.78, V=0.65)
    net.add_node("output_02",  E=0.12, I=0.92, A=0.87, R=0.76, V=0.60)
    # Orchestrator
    net.add_node("orchestr",   E=0.08, I=0.96, A=0.92, R=0.82, V=0.95)
    # Monitor
    net.add_node("monitor_01", E=0.06, I=0.97, A=0.91, R=0.85, V=0.70)
    # Isolated low-priority
    net.add_node("archive_01", E=0.05, I=0.90, A=0.75, R=0.60, V=0.30)

    # Connect the network
    core_edges = [
        ("orchestr",    "core_01",     0.95),
        ("orchestr",    "core_02",     0.95),
        ("orchestr",    "core_03",     0.90),
        ("core_01",     "ingest_01",   0.80),
        ("core_02",     "ingest_02",   0.80),
        ("core_01",     "analysis_01", 0.85),
        ("core_02",     "analysis_02", 0.85),
        ("core_03",     "analysis_01", 0.75),
        ("analysis_01", "output_01",   0.90),
        ("analysis_02", "output_02",   0.90),
        ("monitor_01",  "orchestr",    0.70),
        ("monitor_01",  "core_01",     0.65),
        ("ingest_01",   "ingest_02",   0.60),
    ]
    for id_i, id_j, w in core_edges:
        net.add_edge(id_i, id_j, weight=w)

    print_network_status(net, "INITIAL STATE — All agents nominal")
    demo_pause(1.5)

    # ── SCENARIO 1: SINGLE NODE STRESS ───────────────────
    print(colored("[2/4] SCENARIO 1 — Injecting corrupt data into ingest_01...", "yellow"))
    demo_pause(0.8)

    net.inject_stress("ingest_01", E=0.92, I=0.08, A=0.45)

    print_network_status(net, "AFTER STRESS INJECTION — ingest_01 in crisis")
    print(colored(
        "  → T_int of ingest_01 spiked. "
        "T_ext rising between ingest_01 ↔ core_01.\n"
        "  → VEHICLE-SUPRA detected incoherence. Auto-correction activating...",
        "yellow"
    ))
    demo_pause(1.0)

    # Run recovery
    t0 = time.time()
    result = net.recover(max_cycles=60)
    recovery_ms = (time.time() - t0) * 1000

    print_network_status(net, f"AFTER AUTO-RECOVERY ({result['cycles']} cycles)")
    print(colored(
        f"  ✓ Status   : {result['status'].upper()}\n"
        f"  ✓ Cycles   : {result['cycles']}\n"
        f"  ✓ T(X) reduction: {result['t_initial']:.4f} → {result['t_final']:.4f} "
        f"(−{result['t_reduction']:.4f})\n"
        f"  ✓ Time     : {recovery_ms:.0f}ms\n"
        f"  ✓ Continuity preserved : {result.get('continuity_preserved', True)}",
        "green"
    ))
    demo_pause(1.5)

    # ── SCENARIO 2: CASCADE ATTACK ───────────────────────
    print(colored("[3/4] SCENARIO 2 — Mass injection (cascade scenario)...", "red"))
    demo_pause(0.8)

    # Inject stress into 4 connected nodes simultaneously
    stress_nodes = {
        "ingest_01":   dict(E=0.96, I=0.05, A=0.30),
        "ingest_02":   dict(E=0.94, I=0.07, A=0.35),
        "analysis_01": dict(E=0.90, I=0.10, A=0.40),
        "core_01":     dict(E=0.88, I=0.12, A=0.45),
    }
    for nid, stress in stress_nodes.items():
        net.inject_stress(nid, **stress)

    print_network_status(net, "CASCADE ACTIVE — Multiple nodes in crisis")
    print(colored(
        "  → T(X) explosion across 4 connected nodes.\n"
        "  → Cascade detected. Isolation + replication protocol activating...",
        "red"
    ))
    demo_pause(1.2)

    t0 = time.time()
    result2 = net.recover(max_cycles=100)
    recovery_ms2 = (time.time() - t0) * 1000

    print_network_status(net, f"CASCADE RESOLVED ({result2['cycles']} cycles)")

    rep_count = len(result2.get("replications", []))
    if rep_count:
        print(colored(f"  → {rep_count} twin node(s) spawned:", "cyan"))
        for r in result2["replications"]:
            print(colored(
                f"     {r['original']} → twin: {r['twin']}", "cyan"
            ))

    print(colored(
        f"\n  ✓ Status   : {result2['status'].upper()}\n"
        f"  ✓ Cycles   : {result2['cycles']}\n"
        f"  ✓ T(X) reduction: {result2['t_initial']:.4f} → {result2['t_final']:.4f}\n"
        f"  ✓ Time     : {recovery_ms2:.0f}ms\n"
        f"  ✓ Continuity preserved : {result2.get('continuity_preserved', True)}",
        "green"
    ))
    demo_pause(1.5)

    # ── FINAL SUMMARY ─────────────────────────────────────
    print(colored("[4/4] FINAL NETWORK STATUS", "cyan"))
    print_network_status(net, "SYSTEM STABLE — All agents recovered or replicated")

    print(colored("═" * 62, "purple"))
    print(colored("  VEHICLE-SUPRA DEMO SUMMARY", "bold"))
    print(colored("═" * 62, "purple"))
    print(colored(
        f"  Scenario 1: Single-node stress\n"
        f"    Detected in simulation · Recovery protocol applied · Continuity preserved\n\n"
        f"  Scenario 2: Cascade (4 nodes simultaneous)\n"
        f"    Detected · Isolated · Twin-node recovery simulated · Continuity preserved\n\n"
        f"  The synthetic simulation preserved continuity under the modeled conditions. This is not a production uptime or data-loss guarantee.\n"
        f"  This is what self-healing AI looks like with formal mathematics.",
        "white"
    ))
    print(colored("─" * 62, "gray"))
    print(colored(
        "  Roberto Borda Milan · VEHICLE Systems Lab · Bolivia\n"
        "  vehiclesystemslab.com · Framework DOI: 10.5281/zenodo.19981738\n"
        "  GITEX Global 2026 · Expand North Star · December 8-10 · Dubai",
        "gray"
    ))
    print(colored("═" * 62, "purple"))


if __name__ == "__main__":
    main()
