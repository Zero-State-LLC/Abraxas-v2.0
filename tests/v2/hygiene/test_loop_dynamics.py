from abraxas.v2.hygiene.loop_dynamics import LoopDynamics


def test_loop_dynamics_defaults_and_to_dict() -> None:
    dynamics = LoopDynamics()
    assert dynamics.retrocausal_risk == 0.0
    payload = dynamics.to_dict()
    assert payload["schema_version"] == "LoopDynamics.v1"


def test_loop_dynamics_validation_bounds() -> None:
    dynamics = LoopDynamics(retrocausal_risk=0.5, hyperstitional_charge=0.25)
    assert dynamics.mitigation == "none"
