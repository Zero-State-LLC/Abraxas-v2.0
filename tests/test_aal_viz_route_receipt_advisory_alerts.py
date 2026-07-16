from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from core.aal_viz_route_receipt_advisory_alerts import (
    ACKNOWLEDGEMENT_AUTHORITY,
    RouteReceiptAdvisoryAlertsError,
    canonical_json,
    evaluate_route_receipt_advisory_alerts,
    sha256_json,
    typed_id,
    validate_route_receipt_advisory_acknowledgements,
    validate_route_receipt_advisory_alerts,
)
from scripts.operator.run_route_receipt_advisory_alerts import main as runner_main


ROOT = Path(__file__).resolve().parents[1]
DELTA_PATH = (
    ROOT
    / "out/projections/aal_viz_yggdrasil_topology_delta_intelligence_v1.latest.json"
)
ALERT_SCHEMA = (
    ROOT / "contracts/canon/aal_viz_route_receipt_advisory_alerts.v1.schema.json"
)
ACK_SCHEMA = (
    ROOT
    / "contracts/canon/aal_viz_route_receipt_advisory_acknowledgements.v1.schema.json"
)


def _load(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def _evaluate(
    delta: dict[str, Any],
    *,
    prior: dict[str, Any] | None = None,
    acknowledgements: dict[str, Any] | None = None,
    generated_at: str = "2026-07-16T00:00:00Z",
) -> dict[str, Any]:
    return evaluate_route_receipt_advisory_alerts(
        delta,
        prior_alerts=prior,
        acknowledgements=acknowledgements,
        source_paths={
            "delta_intelligence": "out/projections/delta.json",
            "prior_alerts": "out/projections/prior-alerts.json",
            "acknowledgements": "out/projections/acknowledgements.json",
        },
        content_hashes={
            "delta_intelligence": "a" * 64,
            "prior_alerts": "b" * 64 if prior is not None else None,
            "acknowledgements": "c" * 64
            if acknowledgements is not None
            else None,
        },
        generated_at=generated_at,
    )


def _eligible_delta(
    *,
    score: int = 70,
    severity: str = "HIGH",
    confidence: str = "VERIFIED",
    state: str = "NEW",
    structural_class: str = "VALIDATOR_COVERAGE_LOSS",
    persistence: int | None = None,
) -> dict[str, Any]:
    delta, _ = _load(DELTA_PATH)
    priority = delta["sections"]["review_priorities"]["entries"][0]
    correlation = next(
        item
        for item in delta["sections"]["finding_correlation"]["entries"]
        if item["id"] == priority["source_ref"]["entity_id"]
    )
    priority["score"] = score
    priority["score_breakdown"] = {
        "severity": min(score, 35),
        "structural": max(0, score - min(score, 35)),
        "operational_surfaces": 0,
        "persistence": 0,
        "confidence": 0,
    }
    priority["severity"] = severity
    priority["confidence"] = confidence
    priority["structural_classes"] = [structural_class]
    priority["affected_surface_ids"] = ["system:production"]
    correlation["state"] = state
    correlation["current_severity"] = severity
    correlation["persistence_seconds_lower_bound"] = persistence
    correlation["severity_change"] = (
        "INCREASED" if state == "PERSISTENT" and severity == "HIGH" else "NOT_COMPUTABLE"
    )
    delta["sections"]["review_priorities"]["entries"] = [priority]
    delta["sections"]["finding_correlation"]["entries"] = [correlation]
    return delta


def _acknowledgements(alert_id: str) -> dict[str, Any]:
    record = {
        "id": "",
        "alert_id": alert_id,
        "acknowledged": True,
        "acknowledged_at": "2026-07-16T00:00:00Z",
        "operator_ref": "operator:test",
        "note": "Display only.",
        "non_authorizing": True,
    }
    record["id"] = typed_id(
        "ack", record["alert_id"], record["acknowledged_at"], record["operator_ref"]
    )
    artifact: dict[str, Any] = {
        "schema_version": "AALViz.RouteReceiptAdvisoryAcknowledgements.v1",
        "generation": {
            "generated_at": "2026-07-16T00:00:00Z",
            "acknowledgement_generation_id": "0" * 64,
        },
        "records": [record],
        "authority": copy.deepcopy(ACKNOWLEDGEMENT_AUTHORITY),
        "canonical_hash": "0" * 64,
    }
    semantic = copy.deepcopy(artifact)
    semantic.pop("canonical_hash")
    semantic["generation"].pop("generated_at")
    semantic["generation"].pop("acknowledgement_generation_id")
    artifact["generation"]["acknowledgement_generation_id"] = sha256_json(semantic)
    artifact["canonical_hash"] = sha256_json(
        {key: value for key, value in artifact.items() if key != "canonical_hash"}
    )
    return artifact


def test_v1_140_baseline_suppresses_all_162_candidates() -> None:
    delta, _ = _load(DELTA_PATH)
    first = _evaluate(delta)
    second = _evaluate(delta)
    assert first == second
    assert first["summary"] == {
        "candidate_count": 162,
        "active_count": 0,
        "resolved_count": 0,
        "suppressed_count": 162,
        "not_computable_count": 1,
        "published_receipt_count": 0,
        "highest_active_score": None,
    }
    reasons = {
        reason
        for item in first["sections"]["suppressed_candidates"]["entries"]
        for reason in item["suppression_reasons"]
    }
    assert "NO_ELIGIBLE_TRIGGER" in reasons
    assert "BELOW_SCORE_THRESHOLD" in reasons
    validate_route_receipt_advisory_alerts(first, ALERT_SCHEMA)


@pytest.mark.parametrize(
    ("structural_class", "score", "confidence", "expected_trigger"),
    [
        ("VALIDATOR_COVERAGE_LOSS", 60, "SUPPORTED", "VALIDATOR_COVERAGE_LOSS"),
        (
            "BROKEN_PRODUCER_CONSUMER_PATH",
            60,
            "VERIFIED",
            "BROKEN_PRODUCER_CONSUMER_PATH",
        ),
        ("OWNERSHIP_DRIFT", 60, "VERIFIED", "OWNERSHIP_DRIFT"),
        ("TOPOLOGY_FRAGMENTATION", 70, "VERIFIED", "TOPOLOGY_FRAGMENTATION"),
        (
            "UNEXPECTED_CLUSTER_FUSION",
            60,
            "INFERRED",
            "UNEXPECTED_CLUSTER_FUSION",
        ),
    ],
)
def test_structural_trigger_boundaries(
    structural_class: str, score: int, confidence: str, expected_trigger: str
) -> None:
    artifact = _evaluate(
        _eligible_delta(
            score=score,
            severity="MEDIUM",
            confidence=confidence,
            structural_class=structural_class,
        )
    )
    alert = artifact["sections"]["active_alerts"]["entries"][0]
    assert expected_trigger in alert["trigger_types"]
    assert alert["event_type"] == "FIRST_OBSERVED"
    assert alert["receipt_disposition"] == "PUBLISH"


def test_new_critical_and_persistent_damage_triggers() -> None:
    new = _evaluate(_eligible_delta(structural_class="ORPHANED_CONTRACT"))
    assert "NEW_CRITICAL_STRUCTURAL_FINDING" in new["sections"]["active_alerts"]["entries"][0]["trigger_types"]

    persistent = _evaluate(
        _eligible_delta(
            severity="MEDIUM",
            state="PERSISTENT",
            structural_class="STALE_EVIDENCE_CHAIN",
            persistence=86_400,
        )
    )
    assert "PERSISTENT_UNRESOLVED_DAMAGE" in persistent["sections"]["active_alerts"]["entries"][0]["trigger_types"]


def test_cooldown_update_and_refresh_lifecycle() -> None:
    delta = _eligible_delta()
    first = _evaluate(delta)
    inside = _evaluate(
        delta, prior=first, generated_at="2026-07-16T23:59:59Z"
    )
    alert = inside["sections"]["active_alerts"]["entries"][0]
    assert alert["event_type"] == "CARRIED_FORWARD"
    assert alert["receipt_disposition"] == "SUPPRESS"
    assert alert["suppression_reasons"] == ["UNCHANGED_WITHIN_COOLDOWN"]

    boundary = _evaluate(
        delta, prior=first, generated_at="2026-07-17T00:00:00Z"
    )
    alert = boundary["sections"]["active_alerts"]["entries"][0]
    assert alert["event_type"] == "REFRESHED"
    assert alert["receipt_disposition"] == "PUBLISH"

    changed = _eligible_delta(score=85)
    update = _evaluate(
        changed, prior=first, generated_at="2026-07-16T00:00:01Z"
    )
    assert update["sections"]["active_alerts"]["entries"][0]["event_type"] == "UPDATED"


def test_explicit_resolution_and_structural_carry_forward() -> None:
    delta = _eligible_delta()
    prior = _evaluate(delta)
    resolved_delta = copy.deepcopy(delta)
    resolved_delta["sections"]["finding_correlation"]["entries"][0]["state"] = "RESOLVED"
    resolved_delta["sections"]["review_priorities"]["entries"] = []
    resolved = _evaluate(resolved_delta, prior=prior)
    record = resolved["sections"]["resolved_alerts"]["entries"][0]
    assert record["event_type"] == "RESOLVED"
    assert record["resolution_evidence_refs"] == ["source:delta_intelligence"]

    structural_delta = _eligible_delta()
    structural_delta["sections"]["review_priorities"]["entries"][0]["source_ref"] = {
        "category": "STRUCTURAL_DELTA",
        "entity_id": structural_delta["sections"]["structural_deltas"]["entries"][0]["id"]
        if structural_delta["sections"]["structural_deltas"]["entries"]
        else "structural:" + "1" * 64,
    }
    if not structural_delta["sections"]["structural_deltas"]["entries"]:
        structural_delta["sections"]["structural_deltas"]["entries"] = [
            {
                "id": "structural:" + "1" * 64,
                "structural_class": "VALIDATOR_COVERAGE_LOSS",
            }
        ]
    structural_delta["sections"]["structural_deltas"]["status"] = "AVAILABLE"
    structural_prior = _evaluate(structural_delta)
    absent = copy.deepcopy(structural_delta)
    absent["sections"]["review_priorities"]["entries"] = []
    absent["sections"]["structural_deltas"]["entries"] = []
    carried = _evaluate(absent, prior=structural_prior)
    record = carried["sections"]["active_alerts"]["entries"][0]
    assert record["event_type"] == "CARRIED_FORWARD"
    assert record["receipt_disposition"] == "NOT_COMPUTABLE"


def test_acknowledgement_is_display_only() -> None:
    delta = _eligible_delta()
    without = _evaluate(delta)
    alert_id = without["sections"]["active_alerts"]["entries"][0]["alert_id"]
    acknowledgements = _acknowledgements(alert_id)
    validate_route_receipt_advisory_acknowledgements(acknowledgements, ACK_SCHEMA)
    with_ack = _evaluate(delta, acknowledgements=acknowledgements)
    before = without["sections"]["active_alerts"]["entries"][0]
    after = with_ack["sections"]["active_alerts"]["entries"][0]
    assert after["acknowledged"] is True
    assert after["acknowledgement_ref"] is not None
    for field in ("score", "score_tier", "severity", "trigger_types", "receipt_disposition", "lifecycle"):
        assert after[field] == before[field]


def test_generation_mismatch_suppresses_prior_history() -> None:
    delta = _eligible_delta()
    prior = _evaluate(delta)
    prior["generation"]["current_topology_generation_id"] = "f" * 64
    artifact = _evaluate(delta, prior=prior)
    assert artifact["generation"]["prior_alert_generation_id"] is None
    assert any("mismatch" in item.lower() for item in artifact["validation_findings"])
    assert artifact["sections"]["active_alerts"]["entries"][0]["event_type"] == "FIRST_OBSERVED"


def test_path_rejection_and_runner_requires_explicit_input() -> None:
    delta, _ = _load(DELTA_PATH)
    with pytest.raises(RouteReceiptAdvisoryAlertsError, match="repository-relative"):
        evaluate_route_receipt_advisory_alerts(
            delta,
            source_paths={
                "delta_intelligence": "/tmp/delta.json",
                "prior_alerts": "out/prior.json",
                "acknowledgements": "out/ack.json",
            },
            content_hashes={
                "delta_intelligence": "a" * 64,
                "prior_alerts": None,
                "acknowledgements": None,
            },
            generated_at="2026-07-16T00:00:00Z",
        )
    with pytest.raises(SystemExit):
        runner_main([])
    assert runner_main(["--delta-intelligence", "../delta.json"]) == 1


def test_fixed_epoch_is_byte_identical_across_hash_seeds(tmp_path: Path) -> None:
    script = """
import hashlib, json
from pathlib import Path
from core.aal_viz_route_receipt_advisory_alerts import evaluate_route_receipt_advisory_alerts
raw = Path('delta.json').read_bytes()
delta = json.loads(raw)
artifact = evaluate_route_receipt_advisory_alerts(
    delta,
    source_paths={'delta_intelligence':'delta.json','prior_alerts':'prior.json','acknowledgements':'ack.json'},
    content_hashes={'delta_intelligence':hashlib.sha256(raw).hexdigest(),'prior_alerts':None,'acknowledgements':None},
    generated_at='2026-07-16T00:00:00Z',
)
print(json.dumps(artifact, sort_keys=True, separators=(',', ':')))
"""
    outputs: list[bytes] = []
    for index, seed in enumerate(("1", "8675309")):
        worktree = tmp_path / f"root-{index}"
        worktree.mkdir()
        (worktree / "delta.json").write_bytes(DELTA_PATH.read_bytes())
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=worktree,
            env=os.environ | {"PYTHONHASHSEED": seed, "PYTHONPATH": str(ROOT)},
            check=True,
            capture_output=True,
        )
        outputs.append(result.stdout)
    assert outputs[0] == outputs[1]
    assert b"research_canary" not in outputs[0]
    assert hashlib.sha256(outputs[0]).hexdigest() == hashlib.sha256(outputs[1]).hexdigest()
    assert canonical_json(json.loads(outputs[0]))
