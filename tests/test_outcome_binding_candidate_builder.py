from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.generated_artifact_registry import build_generated_artifact_registry
from core.ingest.outcome_binding_candidate_builder import (
    AUTHORITY,
    PATCH_ID,
    build_brier_readiness_precheck,
    build_outcome_binding_candidate_packet,
    build_resolution_source_requirement_set,
    write_outcome_binding_candidate_outputs,
)
from core.ingest.runtime_handoff_executor import build_oracle_intake_queue, build_sample_manifest_and_config, build_source_pull_receipt_set, build_runtime_handoff_receipt_set


def _sample_cross_domain_queue() -> dict:
    return {
        "schema_version": "OracleIntakeQueue.v1",
        "patch_id": "PATCH-ABX-AUTO-INGEST-003",
        "scheduler_id": "abx_controlled_ingest_scheduler_v1",
        "run_id": "9f6509e3a2da1d7fb4e0c6d5dbbfa5f8895451dd543af7814a1715b089509bd7",
        "authority": "SHADOW_HANDOFF_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "queue_entries": [
            {
                "queue_entry_id": "5ce7cfd6c0fb0a5e69de9fbab7ee371fb4e0af0cee8e53d1f7fb30f014b45856",
                "handoff_receipt_id": "80a415ada51d62edc6ba7e858f5684a54108cadb3375dd88ed733ceb5b2a74ea",
                "source_pull_receipt_id": "5abd0bece41d801fe8454b2ea8b973d3fde96bcc20f7f4de27b9ad3147b92975",
                "adapter_id": "abx_market_feed_v1",
                "domain": "finance",
                "source_kind": "json",
                "source_uri": "input/finance/market_feed.shadow.json",
                "intake_mode": "SHADOW_PULL",
                "queue_status": "READY_FOR_ORACLE_INTAKE",
                "advisory_only": True,
                "projection_only": True,
                "non_authoritative": True,
                "forecast_authority": False,
                "canon_mutation": False,
                "runtime_mutation": False,
                "execution_authority": False,
            },
            {
                "queue_entry_id": "7f671dc1cbb341b2444d4fbfbd5b3c9e1e2df6c79b5bdccdb99f9d5f1eb53df4",
                "handoff_receipt_id": "29c053bd96f08ac04e0c12673fe3fc3dbc14d65df0a7a0c628872b362619dc2e",
                "source_pull_receipt_id": "8c94845529a8e78af6bf3a718cf4a06fbcf089f7fbbfd7666ead8d2c2b6158f0",
                "adapter_id": "abx_news_feed_v1",
                "domain": "news",
                "source_kind": "audit_artifact",
                "source_uri": "out/audit/repo_notion_diff_001.latest.json",
                "intake_mode": "SHADOW_PULL",
                "queue_status": "READY_FOR_ORACLE_INTAKE",
                "advisory_only": True,
                "projection_only": True,
                "non_authoritative": True,
                "forecast_authority": False,
                "canon_mutation": False,
                "runtime_mutation": False,
                "execution_authority": False,
            },
        ],
        "queue_hash": "c55eaec4bf719f068644ca9d7df421e12fddab4a31a347ab22a88677ef9bc8ea",
    }


def test_candidate_builder_is_deterministic_and_non_authoritative() -> None:
    queue = _sample_cross_domain_queue()
    candidate_a = build_outcome_binding_candidate_packet(queue)
    requirements_a = build_resolution_source_requirement_set(candidate_a)
    precheck_a = build_brier_readiness_precheck(candidate_a, requirement_set=requirements_a)

    candidate_b = build_outcome_binding_candidate_packet(queue)
    requirements_b = build_resolution_source_requirement_set(candidate_b)
    precheck_b = build_brier_readiness_precheck(candidate_b, requirement_set=requirements_b)

    assert candidate_a == candidate_b
    assert requirements_a == requirements_b
    assert precheck_a == precheck_b
    assert candidate_a["patch_id"] == PATCH_ID
    assert candidate_a["authority"] == AUTHORITY
    assert candidate_a["candidate_type"] == "news_market_coupling"
    assert candidate_a["candidate_status"] == "CANDIDATE_READY_ADVISORY_ONLY"
    assert candidate_a["activation_status"] == "OPERATOR_REQUIRED"
    assert candidate_a["brier_ready"] is False
    assert requirements_a["requirement_status"] == "REQUIREMENTS_DECLARED"
    assert precheck_a["missing_requirements"] == [
        "operator_approved_outcome_binding_contract",
    ]


def test_candidate_builder_fails_closed_when_cross_domain_evidence_is_missing() -> None:
    manifest, config = build_sample_manifest_and_config()
    pull = build_source_pull_receipt_set(manifest, config)
    handoff = build_runtime_handoff_receipt_set(manifest, config, source_pull_receipt_set=pull)
    queue = build_oracle_intake_queue(manifest, config, runtime_handoff_receipt_set=handoff)

    candidate = build_outcome_binding_candidate_packet(queue)
    requirements = build_resolution_source_requirement_set(candidate)
    precheck = build_brier_readiness_precheck(candidate, requirement_set=requirements)

    assert candidate["candidate_status"] == "NOT_COMPUTABLE_CROSS_DOMAIN_EVIDENCE_REQUIRED"
    assert candidate["candidate_type"] == "NOT_COMPUTABLE"
    assert candidate["required_resolution_sources"] == []
    assert candidate["activation_status"] == "BLOCKED_PENDING_CROSS_DOMAIN_EVIDENCE"
    assert requirements["requirement_status"] == "NOT_COMPUTABLE_CANDIDATE_NOT_READY"
    assert precheck["brier_ready"] is False
    assert "cross_domain_candidate_evidence" in precheck["missing_requirements"]


def test_candidate_builder_contracts_outputs_and_registry() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    queue = _sample_cross_domain_queue()
    candidate = build_outcome_binding_candidate_packet(queue)
    requirements = build_resolution_source_requirement_set(candidate)
    precheck = build_brier_readiness_precheck(candidate, requirement_set=requirements)

    contract_dir = Path("contracts/ingest")
    jsonschema.validate(
        candidate,
        json.loads((contract_dir / "outcome_binding_candidate_packet.v1.schema.json").read_text(encoding="utf-8")),
    )
    jsonschema.validate(
        requirements,
        json.loads((contract_dir / "resolution_source_requirement_set.v1.schema.json").read_text(encoding="utf-8")),
    )
    jsonschema.validate(
        precheck,
        json.loads((contract_dir / "brier_readiness_precheck.v1.schema.json").read_text(encoding="utf-8")),
    )

    out_dir = Path("out/ingest/_tmp_outcome_binding_candidate")
    write_outcome_binding_candidate_outputs(
        out_dir,
        candidate_packet=candidate,
        requirement_set=requirements,
        precheck=precheck,
    )
    assert (out_dir / "outcome_binding_candidate_packet_001.latest.md").read_text(encoding="utf-8").endswith("\n")
    assert (out_dir / "resolution_source_requirement_set_001.latest.md").read_text(encoding="utf-8").endswith("\n")
    assert (out_dir / "brier_readiness_precheck_001.latest.md").read_text(encoding="utf-8").endswith("\n")

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {entry.artifact_path: entry for entry in registry.entries}
    assert emap["out/ingest/outcome_binding_candidate_packet_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/ingest/resolution_source_requirement_set_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/ingest/brier_readiness_precheck_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"

    for path in (
        out_dir / "outcome_binding_candidate_packet_001.latest.json",
        out_dir / "outcome_binding_candidate_packet_001.latest.md",
        out_dir / "resolution_source_requirement_set_001.latest.json",
        out_dir / "resolution_source_requirement_set_001.latest.md",
        out_dir / "brier_readiness_precheck_001.latest.json",
        out_dir / "brier_readiness_precheck_001.latest.md",
    ):
        path.unlink(missing_ok=True)
    out_dir.rmdir()
