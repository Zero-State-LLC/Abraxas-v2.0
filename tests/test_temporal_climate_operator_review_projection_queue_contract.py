import hashlib
import json
from dataclasses import asdict, replace

from core.temporal_operator_review.queue import canonical_temporal_operator_review_projection_queue_json, derive_temporal_operator_review_projection_queue, temporal_operator_review_projection_queue_hash, write_temporal_operator_review_projection_queue_contract_audit
from core.temporal_operator_review.validator import validate_temporal_operator_review_projection_queue


def _binding(alerts=(), status="VIZ_STABLE", posture="STABLE"):
    return {"binding_status": status, "binding_posture": posture, "alert_surfaces": alerts}


def test_queue_derivation_rules():
    assert derive_temporal_operator_review_projection_queue([]).queue_status in {"NOT_COMPUTABLE", "INSUFFICIENT_BINDING_INPUTS"}
    stable = derive_temporal_operator_review_projection_queue([_binding()])
    assert stable.queue_status == "REVIEW_STABLE"
    pressure = derive_temporal_operator_review_projection_queue([_binding(({"alert_type": "PRESSURE_BUILDING", "severity": "WATCH", "source_ref_ids": ()},), "VIZ_PRESSURE", "PRESSURE")])
    assert pressure.queue_status in {"REVIEW_PRESSURE", "OPERATOR_REVIEW_REQUIRED"}
    regime = derive_temporal_operator_review_projection_queue([_binding(({"alert_type": "REGIME_TRANSITION_RISK", "severity": "WARN", "source_ref_ids": ()},), "VIZ_REGIME_RISK", "REGIME_RISK")])
    assert regime.queue_status in {"REVIEW_REGIME_RISK", "OPERATOR_REVIEW_REQUIRED"}
    fracture = derive_temporal_operator_review_projection_queue([_binding(({"alert_type": "FRACTURE_ESCALATION", "severity": "WARN", "source_ref_ids": ()},), "VIZ_FRACTURE_RISK", "FRACTURE_RISK")])
    assert fracture.queue_status in {"REVIEW_FRACTURE_RISK", "OPERATOR_REVIEW_REQUIRED"}
    unstable = derive_temporal_operator_review_projection_queue([_binding(({"alert_type": "BLOCKED_HISTORY_PRESENT", "severity": "BLOCKED", "source_ref_ids": ()},), "VIZ_UNSTABLE", "UNSTABLE")])
    assert unstable.queue_status in {"REVIEW_UNSTABLE", "BLOCKED_HISTORY_VISIBLE", "OPERATOR_REVIEW_REQUIRED"}
    blocked = derive_temporal_operator_review_projection_queue([_binding(({"alert_type": "BLOCKED_HISTORY_PRESENT", "severity": "BLOCKED", "source_ref_ids": ()},))])
    assert any(i.item_type == "BLOCKED_HISTORY" for i in blocked.queue_items)
    nondet = derive_temporal_operator_review_projection_queue([_binding(({"alert_type": "NONDETERMINISM_PRESENT", "severity": "BLOCKED", "source_ref_ids": ()},))])
    assert any(i.item_type == "NONDETERMINISM_CLUSTER" for i in nondet.queue_items)


def test_queue_validator_hash_schema_and_audit(tmp_path):
    base = derive_temporal_operator_review_projection_queue([_binding(({"alert_type": "PRESSURE_BUILDING", "severity": "WATCH", "source_ref_ids": ()},))])
    assert validate_temporal_operator_review_projection_queue(replace(base, projection_only=False)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_operator_review_projection_queue(replace(base, queue_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_operator_review_projection_queue(replace(base, action_authorization_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_operator_review_projection_queue(replace(base, execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_operator_review_projection_queue(replace(base, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_operator_review_projection_queue(replace(base, rollback_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_operator_review_projection_queue(replace(base, promotion_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_operator_review_projection_queue(replace(base, timeline_collapse_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_operator_review_projection_queue(replace(base, canonical_selection_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_operator_review_projection_queue(replace(base, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bqi = replace(base, queue_items=(replace(base.queue_items[0], action_authorization_allowed=True),) + base.queue_items[1:])
    assert validate_temporal_operator_review_projection_queue(bqi).status in {"BLOCKED", "NOT_COMPUTABLE"}
    brs = replace(base, risk_surfaces=(replace(base.risk_surfaces[0], action_authorization_allowed=True),) + base.risk_surfaces[1:])
    assert validate_temporal_operator_review_projection_queue(brs).status in {"BLOCKED", "NOT_COMPUTABLE"}
    brec = replace(base, recommendations=(replace(base.recommendations[0], execution_allowed=True),))
    assert validate_temporal_operator_review_projection_queue(brec).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_operator_review_projection_queue(replace(base, created_by_lane="PROJECTION", queue_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(base))
    alt["queue_hash"] = "x"
    assert temporal_operator_review_projection_queue_hash(base) == temporal_operator_review_projection_queue_hash(alt)
    assert canonical_temporal_operator_review_projection_queue_json(base) == canonical_temporal_operator_review_projection_queue_json(base)
    s = json.loads(open("contracts/temporal_operator_review/temporal_climate_operator_review_projection_queue.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(base).keys()))
    d = dict(asdict(base))
    d.pop("queue_id")
    assert "queue_id" in s["required"] and "queue_id" not in d

    h = write_temporal_operator_review_projection_queue_contract_audit(tmp_path)
    t = open(tmp_path / "out/audit/temporal_climate_operator_review_projection_queue_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
