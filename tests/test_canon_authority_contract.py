import json
from dataclasses import asdict
from pathlib import Path

from core.canon.doctrine_hash import canonical_doctrine_hash
from core.canon.models import CanonDoctrineRef, CanonSource, CanonSyncPacket
from core.canon.runtime_sync import build_canon_audit_payload, build_canon_sync_packet, canon_sync_packet_json, validate_canon_sync_packet


def _assert_schema_required_fields(payload: dict) -> None:
    assert all(k in payload for k in ("canon_ref", "repo_ref", "attestation", "status"))
    for key in ("canon_ref", "repo_ref"):
        assert all(k in payload[key] for k in ("source_type", "source_id", "label"))
    assert all(k in payload["attestation"] for k in ("doctrine_hash", "repo_execution_hash", "sync_posture"))


def test_canon_sync_packet_json_stable() -> None:
    packet = build_canon_sync_packet("np-123", "core/canon/runtime_sync.py", "abc123")
    assert canon_sync_packet_json(packet) == canon_sync_packet_json(packet)


def test_doctrine_hash_stable() -> None:
    packet = build_canon_sync_packet("np-123", "core/canon/runtime_sync.py", "abc123")
    assert canonical_doctrine_hash(packet) == canonical_doctrine_hash(packet)


def test_missing_notion_page_id_not_computable() -> None:
    packet = build_canon_sync_packet(None, "core/canon/runtime_sync.py", "abc123")
    report = validate_canon_sync_packet(packet)
    assert report.status == "NOT_COMPUTABLE"


def test_repo_only_authority_flagged_as_drift_risk() -> None:
    packet = build_canon_sync_packet("np-123", "core/canon/runtime_sync.py", "abc123")
    packet = CanonSyncPacket(canon_ref=CanonDoctrineRef(source_type=CanonSource.REPO_FILE, source_id="core/canon/runtime_sync.py", label="repo-only"), repo_ref=packet.repo_ref, attestation=packet.attestation, status=packet.status)
    report = validate_canon_sync_packet(packet)
    assert any(f.code == "REPO_ONLY_AUTHORITY_DRIFT" for f in report.findings)


def test_schema_accepts_valid_rejects_missing_authority_fields() -> None:
    _ = json.loads(Path("contracts/canon/notion_runtime_sync.v1.schema.json").read_text(encoding="utf-8"))
    packet = build_canon_sync_packet("np-123", "core/canon/runtime_sync.py", "abc123")
    payload = asdict(packet)
    _assert_schema_required_fields(payload)

    bad_payload = asdict(packet)
    del bad_payload["attestation"]["doctrine_hash"]
    try:
        _assert_schema_required_fields(bad_payload)
        assert False, "Expected required-field failure"
    except AssertionError:
        assert True


def test_canon_audit_payload_includes_normalized_fields() -> None:
    packet = build_canon_sync_packet("np-123", "core/canon/runtime_sync.py", "abc123")
    payload = build_canon_audit_payload(packet)
    assert "status" in payload and "posture" in payload and "validation_status" in payload
    assert "audit_envelope" in payload
