from abraxas.v2.hygiene.contracts.schema_validator import validate_payload
from abraxas.v2.hygiene.loop_dynamics import LoopDynamics


def test_schema_validation_passes_for_loop_dynamics() -> None:
    payload = LoopDynamics().to_dict()
    assert validate_payload("loop_dynamics.v1.json", payload) == []


def test_schema_validation_fails_for_invalid_payload() -> None:
    errors = validate_payload("loop_dynamics.v1.json", {"schema_version": "LoopDynamics.v1"})
    assert errors
