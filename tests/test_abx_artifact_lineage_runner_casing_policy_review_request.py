from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_runner_casing_policy_review_request import (
    build_abx_artifact_lineage_runner_casing_policy_review_request,
    render_abx_artifact_lineage_runner_casing_policy_review_request_markdown,
    write_abx_artifact_lineage_runner_casing_policy_review_request,
)


def test_request_is_deterministic_and_fail_closed() -> None:
    first = build_abx_artifact_lineage_runner_casing_policy_review_request()
    second = build_abx_artifact_lineage_runner_casing_policy_review_request()

    assert first["request_hash"] == second["request_hash"]
    assert first["schema_version"] == "AbxArtifactLineageRunnerCasingPolicyReviewRequest.v1"
    assert first["status"] == "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_REVIEW_REQUEST_HELD"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["runner_casing_policy_override_allowed"] is False
    assert first["runner_path_normalization_allowed"] is False
    assert first["execution_authority"] is False
    assert first["safe_to_auto_continue"] is False


def test_request_targets_current_runner_casing_gap() -> None:
    packet = build_abx_artifact_lineage_runner_casing_policy_review_request()

    assert packet["review_scope"] == "RUNNER_CASING_POLICY_DECISION_ONLY"
    assert packet["target_finding_id"] == "detect_uppercase_Scripts_runner_discovery_gaps"
    assert packet["target_status"] == "NOT_COMPUTABLE"
    assert packet["impacted_runner_count"] == 478
    assert "run_aal_viz_geometric_renderer.py" in packet["sample_impacted_runners"]
    assert packet["source_traceability_audit"]["source_audit_ready"] is True


def test_request_preserves_policy_review_boundaries() -> None:
    packet = build_abx_artifact_lineage_runner_casing_policy_review_request()

    assert "KEEP_CASE_SENSITIVE_RUNNER_DISCOVERY" in packet["decision_options"]
    assert "AUTHORIZE_REPO_WIDE_RUNNER_PATH_NORMALIZATION_PLAN" in packet["decision_options"]
    assert packet["recommended_decision"] == "REQUEST_ADDITIONAL_RUNNER_CASE_EVIDENCE"
    assert "RUNNER_CASING_POLICY_OVERRIDE" in packet["blocked_actions"]
    assert "RUNNER_PATH_NORMALIZATION" in packet["blocked_actions"]
    assert packet["recommended_next_lane"] == "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_DECISION_PLAN"
    assert packet["downstream_status"] == "HELD_FOR_OPERATOR_POLICY_DECISION"


def test_writer_emits_json_and_markdown() -> None:
    packet = write_abx_artifact_lineage_runner_casing_policy_review_request()

    json_path = Path("out/operator_review/abx_artifact_lineage_runner_casing_policy_review_request_001.latest.json")
    md_path = Path("out/operator_review/abx_artifact_lineage_runner_casing_policy_review_request_001.latest.md")
    assert json_path.exists()
    assert md_path.exists()
    assert packet["impacted_runner_count"] == 478


def test_schema_and_markdown_render() -> None:
    packet = build_abx_artifact_lineage_runner_casing_policy_review_request()
    schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_runner_casing_policy_review_request.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_runner_casing_policy_review_request_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Runner Casing Policy Review Request"
    assert any("RUNNER_CASING_POLICY_OVERRIDE" in line for line in markdown)
