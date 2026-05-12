from vehicle_supra import SupraNetwork


def build_network():
    net = SupraNetwork()
    net.add_node("a", E=0.2, I=0.9, A=0.8, R=0.7, V=0.6)
    net.add_node("b", E=0.3, I=0.8, A=0.7, R=0.6, V=0.5)
    net.add_node("c", E=0.1, I=0.95, A=0.9, R=0.8, V=0.4)
    net.add_edge("a", "b", weight=0.8)
    net.add_edge("b", "c", weight=0.6)
    return net


def test_network_total_tension_is_non_negative():
    net = build_network()
    assert net.external_tension() >= 0.0
    assert net.internal_tension() >= 0.0
    assert net.total_tension() >= 0.0


def test_regimes_returns_all_nodes():
    net = build_network()
    regimes = net.regimes()
    assert set(regimes.keys()) == {"a", "b", "c"}


def test_recover_returns_report():
    net = build_network()
    net.inject_stress("b", E=0.95, I=0.15)
    report = net.recover(max_cycles=10)
    assert report["status"] in {"recovered", "partial"}
    assert "t_initial" in report
    assert "t_final" in report
    assert "continuity_preserved" in report


def test_snapshot_contains_core_metrics():
    net = build_network()
    snap = net.snapshot()
    assert snap["node_count"] == 3
    assert snap["edge_count"] == 2
    assert "t_total" in snap
