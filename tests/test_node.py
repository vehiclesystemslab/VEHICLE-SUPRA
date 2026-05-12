from vehicle_supra import SupraNode, SupraNodeConfig


def test_node_state_is_clamped():
    node = SupraNode(E=2.0, I=-1.0, A=0.5, R=0.5, V=0.5)
    state = node.state
    assert state.min() >= 0.0
    assert state.max() <= 1.0


def test_coherent_node_has_low_tension():
    node = SupraNode(E=0.7, I=0.7, A=0.7, R=0.7, V=0.7)
    assert node.internal_tension() < 1e-12
    assert node.is_coherent()


def test_recovery_step_does_not_increase_internal_tension_for_stressed_node():
    cfg = SupraNodeConfig(t_limit=0.30, alpha=0.5, eta=0.2)
    node = SupraNode(E=1.0, I=0.0, A=1.0, R=0.0, V=1.0, config=cfg)
    before = node.internal_tension()
    result = node.recovery_step(lam=1.0)
    after = node.internal_tension()
    assert after <= before
    assert result["t_int_after"] <= result["t_int_before"]


def test_spawn_twin_uses_reference_state():
    node = SupraNode(node_id="agent", E=0.2, I=0.9, A=0.8, R=0.7, V=0.6)
    node.inject_stress(E=0.95, I=0.1)
    twin = node.spawn_twin()
    assert twin.node_id.startswith("agent_twin_")
    assert twin.I > node.I
