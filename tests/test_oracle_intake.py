from core.oracle.intake import OracleIntakeEnvelope


def test_deterministic_intake_hashing() -> None:
    assert OracleIntakeEnvelope.hash_payload("abc") == OracleIntakeEnvelope.hash_payload("abc")
