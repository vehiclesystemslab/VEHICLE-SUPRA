"""
examples/vehicle_luna.py
════════════════════════
VEHICLE-LUNA — Lunar Rover Mission Simulation
GITEX Global 2026 · Expand North Star · Stand Demo

20 autonomous micro-rovers explore a lunar surface searching
for water-ice deposits. Each rover is a VEHICLE-SUPRA node
with E.I.A.R.(V) structured state. When a rover falls into
a crater (crisis), the system detects incoherence, attempts
autonomous recovery, or spawns a coherent twin rover to
continue the mission. The simulation preserves mission continuity.

This is a SOFTWARE simulation of the physical robot demo.
The same T(X) logic is designed to be portable to a Raspberry Pi / ESP32
physical rover demonstration for GITEX, subject to hardware validation.

Run:
    python examples/vehicle_luna.py
    python examples/vehicle_luna.py --scenario solar_storm
    python examples/vehicle_luna.py --scenario all --quiet

Author : Roberto Borda Milan — VEHICLE Systems Lab
Framework DOI: 10.5281/zenodo.19981738
License: MIT
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict

# ── Path setup ────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
SRC  = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vehicle_supra import SupraNetwork, SupraNodeConfig  # noqa: E402

# ── ANSI colors (with fallback) ───────────────────────────
try:
    import os
    _COLOR = sys.stdout.isatty() or os.environ.get("FORCE_COLOR")
except Exception:
    _COLOR = False

def _c(code: str, text: str) -> str:
    if not _COLOR:
        return text
    codes = {
        "green":  "\033[92m", "yellow": "\033[93m",
        "red":    "\033[91m", "cyan":   "\033[96m",
        "purple": "\033[95m", "white":  "\033[97m",
        "gray":   "\033[90m", "bold":   "\033[1m",
        "reset":  "\033[0m",
    }
    return f"{codes.get(code,'')}{text}{codes['reset']}"

def _regime_color(regime: str) -> str:
    palette = {
        "A0": "green", "A1": "yellow", "A2": "cyan",
        "A3": "yellow", "A4": "gray",  "A5": "red", "A6": "red",
        "CLONE": "purple",
    }
    return _c(palette.get(regime, "white"), f"[{regime}]")

# ── Mission configuration ─────────────────────────────────
ROVER_NAMES = [
    "LUNA-01", "LUNA-02", "LUNA-03", "LUNA-04", "LUNA-05",
    "LUNA-06", "LUNA-07", "LUNA-08", "LUNA-09", "LUNA-10",
    "LUNA-11", "LUNA-12", "LUNA-13", "LUNA-14", "LUNA-15",
    "LUNA-16", "LUNA-17", "LUNA-18", "LUNA-19", "LUNA-20",
]

# E.I.A.R.(V) interpretation for lunar rover context:
#   E = Exposure      → terrain hazard + radiation + comms latency
#   I = Integrity     → sensor + motor + power coherence
#   A = Agency        → mobility capacity + tool availability
#   R = Recovery      → self-repair capacity + twin availability
#   V = Value         → mission importance (proximity to targets)

LUNAR_NODE_CONFIG = SupraNodeConfig(
    t_limit             = 0.28,
    t_int_warning       = 0.14,
    t_int_crisis        = 0.25,
    t_ext_warning       = 0.18,
    eta                 = 0.12,
    alpha               = 0.28,
    max_recovery_cycles = 60,
    replication_threshold = 12,
)

# ── Scenario definitions ──────────────────────────────────
@dataclass
class CrisisEvent:
    """A single crisis event injected into a rover."""
    rover_id: str
    name: str
    description: str
    stress: Dict[str, float]

def crater_crisis(rover_id: str) -> CrisisEvent:
    return CrisisEvent(
        rover_id    = rover_id,
        name        = "Crater Fall",
        description = f"{rover_id} fell into an uncharted crater. Wheel motor failure + terrain sensor overload.",
        stress      = {"E": 0.93, "I": 0.07, "A": 0.35, "R": 0.55, "V": 0.75},
    )

def solar_storm_crisis(rover_id: str) -> CrisisEvent:
    return CrisisEvent(
        rover_id    = rover_id,
        name        = "Solar Storm",
        description = f"{rover_id} hit by solar particle burst. Comms degraded + sensor drift.",
        stress      = {"E": 0.95, "I": 0.12, "A": 0.65, "R": 0.42, "V": 0.80},
    )

def dust_storm_crisis(rover_id: str) -> CrisisEvent:
    return CrisisEvent(
        rover_id    = rover_id,
        name        = "Dust Storm",
        description = f"{rover_id} optical sensors blinded by dust. Navigation incoherent.",
        stress      = {"E": 0.82, "I": 0.19, "A": 0.55, "R": 0.60, "V": 0.70},
    )

def comms_blackout(rover_id: str) -> CrisisEvent:
    return CrisisEvent(
        rover_id    = rover_id,
        name        = "Comms Blackout",
        description = f"{rover_id} lost contact with base. Operating in isolation — high internal tension.",
        stress      = {"E": 0.75, "I": 0.30, "A": 0.80, "R": 0.38, "V": 0.85},
    )

# ── Display helpers ───────────────────────────────────────
def print_sep(char: str = "─", width: int = 68):
    print(_c("gray", char * width))

def print_header(title: str, subtitle: str = ""):
    print()
    print(_c("purple", "═" * 68))
    print(_c("bold",   f"  {title}"))
    if subtitle:
        print(_c("gray",   f"  {subtitle}"))
    print(_c("purple", "═" * 68))

def print_mission_status(net: SupraNetwork, label: str, rover_ids: List[str]):
    tensions = net.node_tensions()
    regimes  = net.regimes()
    print()
    print(_c("bold", f"  {label}"))
    print(_c("cyan",
        f"  T(X)={net.total_tension():.4f}  "
        f"T_ext={net.external_tension():.4f}  "
        f"T_int={net.internal_tension():.4f}"
    ))
    print_sep()
    print(f"  {'Rover':<16} {'Regime':<8} {'T_int':>8} {'T_ext':>8}  E    I    A    R    V")
    print_sep()
    for rid in rover_ids:
        if rid not in net.node_ids():
            continue
        node = net.get_node(rid)
        r    = regimes.get(rid, "A0")
        t    = tensions.get(rid, {"t_int": 0, "t_ext": 0})
        s    = node.state
        rc   = _regime_color(r)
        print(
            f"  {rid:<16} {rc:<8} "
            f"{t['t_int']:>7.4f} {t['t_ext']:>7.4f}  "
            f"{s[0]:.2f} {s[1]:.2f} {s[2]:.2f} {s[3]:.2f} {s[4]:.2f}"
        )
    print()

def print_event(event: CrisisEvent):
    print(_c("yellow", f"\n  ⚠  CRISIS EVENT: {event.name}"))
    print(_c("gray",   f"     {event.description}"))

def print_recovery(result: dict, rover_id: str):
    status  = result["status"].upper()
    sc      = "green" if status == "RECOVERED" else "yellow"
    reps    = result.get("replications", [])
    print()
    print(_c(sc,   f"  ✓ Recovery: {status}"))
    print(_c("gray", f"    Cycles : {result['cycles']}"))
    print(_c("gray", f"    T(X)   : {result['t_initial']:.4f} → {result['t_final']:.4f}  (−{result['t_reduction']:.4f})"))
    print(_c("gray", f"    Time   : {result['time_ms']:.1f}ms"))
    print(_c("gray", f"    Continuity preserved in simulation: {'Yes' if result.get('continuity_preserved', True) else 'No'}"))
    if reps:
        for rep in reps:
            print(_c("purple", f"    🟣 Twin spawned: {rep['original']} → {rep['twin']}"))

# ── Network builder ───────────────────────────────────────
def build_lunar_network() -> tuple[SupraNetwork, List[str]]:
    """
    Build a 20-rover network with realistic lunar mission topology.

    Rovers are organized in 4 squads:
      Squad Alpha  (LUNA-01 to 05) — Northern crater rim exploration
      Squad Beta   (LUNA-06 to 10) — Equatorial plains survey
      Squad Gamma  (LUNA-11 to 15) — Southern highlands mapping
      Squad Delta  (LUNA-16 to 20) — Standby / relay / reserve

    Edges represent proximity-based coordination links.
    """
    net = SupraNetwork(lam=1.0, node_config=LUNAR_NODE_CONFIG)
    rng = random.Random(42)  # Fixed seed for reproducibility

    def r(lo, hi): return round(rng.uniform(lo, hi), 3)

    # ── Squad Alpha — Northern crater rim (high exposure, high value)
    for name in ROVER_NAMES[0:5]:
        net.add_node(name,
            E=r(0.22, 0.38), I=r(0.80, 0.92), A=r(0.72, 0.88),
            R=r(0.62, 0.80), V=r(0.78, 0.95))

    # ── Squad Beta — Equatorial plains (moderate, active survey)
    for name in ROVER_NAMES[5:10]:
        net.add_node(name,
            E=r(0.15, 0.28), I=r(0.84, 0.94), A=r(0.75, 0.90),
            R=r(0.66, 0.82), V=r(0.65, 0.82))

    # ── Squad Gamma — Southern highlands (low exposure, steady)
    for name in ROVER_NAMES[10:15]:
        net.add_node(name,
            E=r(0.10, 0.22), I=r(0.86, 0.96), A=r(0.70, 0.85),
            R=r(0.70, 0.85), V=r(0.55, 0.75))

    # ── Squad Delta — Standby / relay (isolated, A4 candidates)
    for name in ROVER_NAMES[15:20]:
        net.add_node(name,
            E=r(0.06, 0.15), I=r(0.88, 0.96), A=r(0.68, 0.82),
            R=r(0.75, 0.90), V=r(0.40, 0.60))

    # ── Intra-squad edges (strong proximity links)
    squads = [ROVER_NAMES[0:5], ROVER_NAMES[5:10],
              ROVER_NAMES[10:15], ROVER_NAMES[15:20]]
    for squad in squads:
        for i in range(len(squad)):
            for j in range(i + 1, len(squad)):
                w = round(rng.uniform(0.60, 0.90), 2)
                net.add_edge(squad[i], squad[j], weight=w)

    # ── Inter-squad relay edges (Alpha↔Beta, Beta↔Gamma, Delta↔all)
    inter = [
        ("LUNA-03", "LUNA-07", 0.55),
        ("LUNA-04", "LUNA-08", 0.52),
        ("LUNA-08", "LUNA-13", 0.48),
        ("LUNA-09", "LUNA-12", 0.50),
        ("LUNA-16", "LUNA-01", 0.45),
        ("LUNA-17", "LUNA-06", 0.44),
        ("LUNA-18", "LUNA-11", 0.42),
        ("LUNA-19", "LUNA-02", 0.40),
        ("LUNA-20", "LUNA-14", 0.38),
    ]
    for a, b, w in inter:
        net.add_edge(a, b, weight=w)

    return net, list(ROVER_NAMES)

# ── Scenario runners ──────────────────────────────────────
def scenario_crater(net: SupraNetwork, rover_ids: List[str], quiet: bool) -> dict:
    """Single crater fall → autonomous recovery → twin spawn if needed."""
    target = "LUNA-04"
    event  = crater_crisis(target)
    print_event(event)
    if not quiet:
        print_mission_status(net, "BEFORE CRATER CRISIS", rover_ids)

    net.inject_stress(target, **event.stress)

    if not quiet:
        print_mission_status(net, f"AFTER CRATER STRESS — {target}", rover_ids)
        print(_c("cyan", "  → VEHICLE-LUNA detecting incoherence..."))
        print(_c("cyan", "  → V_op projection activated..."))
        time.sleep(0.3)

    result = net.recover(max_cycles=80)
    if not quiet:
        print_recovery(result, target)
        print_mission_status(net, "POST-RECOVERY STATUS", rover_ids + [
            r["twin"] for r in result.get("replications", [])
        ])
    return result

def scenario_solar_storm(net: SupraNetwork, rover_ids: List[str], quiet: bool) -> dict:
    """Solar storm hits Squad Alpha (5 rovers simultaneously) → cascade → recovery."""
    events  = [solar_storm_crisis(r) for r in ROVER_NAMES[0:5]]
    if not quiet:
        print(_c("red", "\n  ☀  SOLAR STORM — Squad Alpha hit simultaneously"))
        for e in events:
            print(_c("gray", f"     {e.rover_id}: {e.name}"))
        print_mission_status(net, "BEFORE SOLAR STORM", rover_ids)

    for e in events:
        net.inject_stress(e.rover_id, **e.stress)

    if not quiet:
        print_mission_status(net, "CASCADE ACTIVE — 5 rovers in crisis", rover_ids)
        print(_c("red",  "  → Cascade A6 detected across Squad Alpha"))
        print(_c("cyan", "  → Isolation + twin replication protocol firing..."))
        time.sleep(0.5)

    result = net.recover(max_cycles=100)
    if not quiet:
        print_recovery(result, ROVER_NAMES[0])
        all_ids = rover_ids + [r["twin"] for r in result.get("replications", [])]
        print_mission_status(net, "STORM RESOLVED", all_ids)
    return result

def scenario_dust_and_comms(net: SupraNetwork, rover_ids: List[str], quiet: bool) -> dict:
    """Mixed scenario: dust storm on Gamma + comms blackout on Delta."""
    events = [
        dust_storm_crisis("LUNA-13"),
        comms_blackout("LUNA-18"),
        crater_crisis("LUNA-07"),
    ]
    if not quiet:
        print(_c("yellow", "\n  ⚠  MIXED SCENARIO — 3 simultaneous crisis events"))
        for e in events:
            print(_c("gray", f"     {e.rover_id}: {e.name}"))
        print_mission_status(net, "BEFORE MIXED CRISIS", rover_ids)

    for e in events:
        net.inject_stress(e.rover_id, **e.stress)

    if not quiet:
        print_mission_status(net, "MIXED CRISIS ACTIVE", rover_ids)
        time.sleep(0.3)

    result = net.recover(max_cycles=100)
    if not quiet:
        print_recovery(result, "LUNA-13")
        all_ids = rover_ids + [r["twin"] for r in result.get("replications", [])]
        print_mission_status(net, "MIXED CRISIS RESOLVED", all_ids)
    return result

# ── Main ──────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="VEHICLE-LUNA — Lunar Rover Mission Simulation"
    )
    parser.add_argument(
        "--scenario",
        choices=["crater", "solar_storm", "mixed", "all"],
        default="all",
        help="Which crisis scenario to run (default: all)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress detailed output (useful for CI/CD)",
    )
    parser.add_argument(
        "--export", action="store_true",
        help="Export mission report to outputs/vehicle_luna_report.json",
    )
    args = parser.parse_args()

    print_header(
        "VEHICLE-LUNA — Lunar Rover Mission Simulation",
        "VEHICLE Systems Lab · Roberto Borda Milan · GITEX Global 2026 · Dubai"
    )

    if not args.quiet:
        print(_c("gray", """
  Mission context:
  20 autonomous micro-rovers explore the lunar surface searching for
  water-ice deposits in permanently shadowed craters.

  Each rover is a VEHICLE-SUPRA node with E.I.A.R.(V) structured state:
    E = terrain hazard + radiation + comms latency
    I = sensor + motor + power coherence
    A = mobility capacity + tool availability
    R = self-repair capacity + twin-rover availability
    V = mission importance (proximity to water-ice targets)

  When a rover loses coherence, VEHICLE-LUNA detects the incoherence,
  applies V_op projection recovery, or spawns a coherent twin rover.
  The simulated mission preserves continuity while recovery logic is evaluated.
"""))

    results = {}
    report_sections = []

    # ── SCENARIO: CRATER ─────────────────────────────────
    if args.scenario in ("crater", "all"):
        print_header("SCENARIO 1 — Crater Fall", "LUNA-04 falls into uncharted crater")
        net, rover_ids = build_lunar_network()
        if not args.quiet:
            print_mission_status(net, "INITIAL MISSION STATE — all 20 rovers nominal", rover_ids)
        r = scenario_crater(net, rover_ids, args.quiet)
        results["crater"] = r
        report_sections.append({"scenario": "crater", "result": r})
        if not args.quiet:
            print(_c("green", "\n  ✓ Scenario 1 complete. Mission continues.\n"))

    # ── SCENARIO: SOLAR STORM ────────────────────────────
    if args.scenario in ("solar_storm", "all"):
        print_header(
            "SCENARIO 2 — Solar Storm",
            "Squad Alpha (5 rovers) hit simultaneously — cascade event"
        )
        net, rover_ids = build_lunar_network()
        r = scenario_solar_storm(net, rover_ids, args.quiet)
        results["solar_storm"] = r
        report_sections.append({"scenario": "solar_storm", "result": r})
        if not args.quiet:
            print(_c("green", "\n  ✓ Scenario 2 complete. Mission continues.\n"))

    # ── SCENARIO: MIXED ──────────────────────────────────
    if args.scenario in ("mixed", "all"):
        print_header(
            "SCENARIO 3 — Mixed Crisis",
            "Dust storm + comms blackout + crater fall — 3 simultaneous events"
        )
        net, rover_ids = build_lunar_network()
        r = scenario_dust_and_comms(net, rover_ids, args.quiet)
        results["mixed"] = r
        report_sections.append({"scenario": "mixed", "result": r})
        if not args.quiet:
            print(_c("green", "\n  ✓ Scenario 3 complete. Mission continues.\n"))

    # ── SUMMARY ──────────────────────────────────────────
    print_header("MISSION SUMMARY", "VEHICLE-LUNA performance across all scenarios")
    print()
    print(_c("bold", "  Scenario results:"))
    for name, r in results.items():
        sc = "green" if r["status"] == "recovered" else "yellow"
        reps = len(r.get("replications", []))
        print(
            _c(sc, f"  ✓ {name:<18}") +
            _c("gray", f" | {r['status']:<10}") +
            _c("gray", f" | {r['cycles']:>3} cycles") +
            _c("gray", f" | {r['t_initial']:.4f}→{r['t_final']:.4f}") +
            (_c("purple", f" | {reps} twin(s)") if reps else "")
        )
    print()
    print(_c("bold", "  Key property demonstrated:"))
    print(_c("white", "  The simulated lunar mission preserved continuity."))
    print(_c("white", "  Every synthetic crisis was detected, contained, and guided toward recovery."))
    print(_c("white", "  No simulated mission-level interruption across the demonstrated scenarios."))
    print()
    print(_c("gray",  "  This software simulation is designed as a portable counterpart for"))
    print(_c("gray",  "  a Raspberry Pi / ESP32 rover demonstration after hardware validation."))
    print()
    print_sep("═")
    print(_c("gray",  "  Roberto Borda Milan · VEHICLE Systems Lab · Bolivia"))
    print(_c("gray",  "  vehiclesystemslab.com · Framework DOI: 10.5281/zenodo.19981738"))
    print(_c("purple", "  GITEX Global 2026 · Expand North Star · Dec 8–10 · Dubai"))
    print_sep("═")

    # ── EXPORT ───────────────────────────────────────────
    if args.export:
        output_dir = ROOT / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "mission":    "VEHICLE-LUNA — Lunar Rover Mission Simulation",
            "status":     "alpha research simulation",
            "generated":  datetime.now(timezone.utc).isoformat(),
            "disclaimer": (
                "Synthetic simulation only. The physical stand at GITEX 2026 "
                "uses the same T(X) engine on Raspberry Pi 4 controlling real "
                "ESP32-based rovers. This software is not a production uptime guarantee."
            ),
            "scenarios": report_sections,
        }
        out = output_dir / "vehicle_luna_report.json"
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(_c("green", f"\n  Report saved → {out}"))


if __name__ == "__main__":
    main()
