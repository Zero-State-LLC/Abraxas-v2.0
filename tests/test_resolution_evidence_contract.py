import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from core.resolution import (
    build_resolution_evidence_packet,
    canonical_resolution_evidence_json,
    resolution_evidence_hash,
    validate_resolution_evidence_packet,
    write_resolution_evidence_contract_audit,
)
from core.resolution.models import AuthorityRef, EvidenceConflict, EvidenceObservation, EvidenceStatus, ResolutionEvidenceItem, ResolutionEvidenceSourceRef


def _base(**kwargs):
    item = ResolutionEvidenceItem(
        item_id="item-1",
        observation=EvidenceObservation(
            observation_id="obs-1",
            observed_value="true",
            observation_type="BOOLEAN_EVENT",
            source_ref=ResolutionEvidenceSourceRef("REPO_FIXTURE", "fixtures/r.json", "fixture"),
            collection_policy="COLLECT_POLICY",
            confidence_policy="CONF_POLICY",
        ),
    )
    return build_resolution_evidence_packet(
        evidence_packet_id=kwargs.get("evidence_packet_id", "ep-1"),
        binding_id=kwargs.get("binding_id", "ob-1"),
        forecast_id=kwargs.get("forecast_id", "fc-1"),
        forecast_hash=kwargs.get("forecast_hash", "fhash"),
        binding_hash=kwargs.get("binding_hash", "bhash"),
        evidence_items=kwargs.get("evidence_items", (item,)),
        conflicts=kwargs.get("conflicts", ()),
        evidence_status=kwargs.get("evidence_status", EvidenceStatus.DRAFT),
        created_by_lane=kwargs.get("created_by_lane", "FORECAST"),
        authority_ref=kwargs.get("authority_ref", AuthorityRef("MANUAL_RECEIPT", "receipt://1", "op")),
        void_reason=kwargs.get("void_reason", None),
    )


def test_valid_draft_warn_or_pass_not_settlement_ready():
    assert validate_resolution_evidence_packet(_base(evidence_status=EvidenceStatus.DRAFT)).status in {"PASS", "WARN"}


def test_valid_collected_pass_with_at_least_one_item():
    assert validate_resolution_evidence_packet(_base(evidence_status=EvidenceStatus.EVIDENCE_COLLECTED)).status == "PASS"


def test_settlement_ready_without_items_blocked_or_not_computable():
    s = validate_resolution_evidence_packet(_base(evidence_status=EvidenceStatus.SETTLEMENT_READY, evidence_items=())).status
    assert s in {"BLOCKED", "NOT_COMPUTABLE"}


def test_settlement_ready_with_unresolved_conflicts_blocked_or_not_computable():
    c = EvidenceConflict("c1", ("s1",), "VALUE_MISMATCH", "HIGH", "MANUAL_REVIEW")
    s = validate_resolution_evidence_packet(_base(evidence_status=EvidenceStatus.SETTLEMENT_READY, conflicts=(c,))).status
    assert s in {"BLOCKED", "NOT_COMPUTABLE"}


def test_conflicting_without_conflict_blocked_or_not_computable():
    s = validate_resolution_evidence_packet(_base(evidence_status=EvidenceStatus.CONFLICTING, conflicts=())).status
    assert s in {"BLOCKED", "NOT_COMPUTABLE"}


def test_missing_binding_forecast_hashes_blocked_or_not_computable():
    s = validate_resolution_evidence_packet(_base(binding_id="", forecast_id="", forecast_hash="", binding_hash="")).status
    assert s in {"BLOCKED", "NOT_COMPUTABLE"}


def test_shadow_cannot_mark_settlement_ready():
    assert validate_resolution_evidence_packet(_base(created_by_lane="SHADOW", evidence_status=EvidenceStatus.SETTLEMENT_READY)).status == "BLOCKED"


def test_projection_cannot_create_authoritative_evidence_packet():
    assert validate_resolution_evidence_packet(_base(created_by_lane="PROJECTION", evidence_status=EvidenceStatus.EVIDENCE_COLLECTED)).status == "BLOCKED"


def test_evidence_hash_stable_excludes_evidence_hash_field():
    obj = _base(evidence_status=EvidenceStatus.EVIDENCE_COLLECTED)
    h1 = resolution_evidence_hash(obj)
    payload = asdict(obj)
    payload["evidence_hash"] = "mutated"
    h2 = resolution_evidence_hash(payload)
    assert h1 == h2


def test_canonical_json_byte_stable():
    obj = _base(evidence_status=EvidenceStatus.EVIDENCE_COLLECTED)
    assert canonical_resolution_evidence_json(obj) == canonical_resolution_evidence_json(obj)


def test_schema_accepts_shape_and_required_fields_present():
    schema = json.loads(Path("contracts/resolution/resolution_evidence.v1.schema.json").read_text(encoding="utf-8"))
    assert "required" in schema and "evidence_hash" in schema["required"]


def test_audit_artifact_stable_sha256_and_newline(tmp_path: Path):
    h1 = write_resolution_evidence_contract_audit(tmp_path)
    p = tmp_path / "out/audit/resolution_evidence_contract.latest.json"
    t1 = p.read_text(encoding="utf-8")
    h2 = write_resolution_evidence_contract_audit(tmp_path)
    t2 = p.read_text(encoding="utf-8")
    assert t1.endswith("\n")
    assert h1 == h2
    assert hashlib.sha256(t1.encode()).hexdigest() == hashlib.sha256(t2.encode()).hexdigest()
