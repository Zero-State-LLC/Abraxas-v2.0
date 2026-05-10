from core.audit.status import build_audit_status_envelope, canonical_json, normalize_audit_status


def test_normalizer_detects_status() -> None:
    assert normalize_audit_status({"status": "PASS"})["status"] == "PASS"


def test_normalizer_detects_posture() -> None:
    assert normalize_audit_status({"posture": "WARN"})["status"] == "WARN"


def test_normalizer_detects_chain_posture() -> None:
    assert normalize_audit_status({"chain_posture": "BLOCKED"})["status"] == "BLOCKED"


def test_normalizer_detects_runtime_posture() -> None:
    assert normalize_audit_status({"runtime_posture": "PASS"})["status"] == "PASS"


def test_normalizer_detects_validation_status() -> None:
    assert normalize_audit_status({"validation_status": "NOT_COMPUTABLE"})["status"] == "NOT_COMPUTABLE"


def test_missing_status_returns_not_computable() -> None:
    assert normalize_audit_status({"foo": "bar"})["status"] == "NOT_COMPUTABLE"


def test_envelope_canonical_json_deterministic() -> None:
    env = build_audit_status_envelope("a", "t", "PASS", artifact_hash="h")
    assert canonical_json(env) == canonical_json(env)
