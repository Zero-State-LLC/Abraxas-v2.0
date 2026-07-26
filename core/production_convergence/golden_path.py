"""Supported product golden-path trace (Phase 1.4) with Alembic placement."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash


def build_golden_path_trace() -> dict[str, Any]:
    stages = [
        {
            "stage_id": "input_envelope",
            "name": "InputEnvelope",
            "source": "operator/API/CLI input or ingest adapter payload",
            "canonical_impl": "ingest / Oracle candidate signal envelopes",
            "validation": "schema contracts under contracts/ + validation_service",
            "transformation": "normalize to evidence-bearing envelope",
            "persistence": "none at this stage (pure)",
            "side_effects": "none",
            "authority_checks": "activation_policy LOCAL_DEV/SANDBOX; no auth packet",
            "output": "InputEnvelope",
            "failure_behavior": "typed validation error; no partial artifact",
            "replay_behavior": "deterministic for fixed input bytes",
            "test_coverage": "Partial — validation_service tests; full envelope contract TBD",
            "status": "PARTIAL",
        },
        {
            "stage_id": "ingest",
            "name": "IngestService",
            "source": "InputEnvelope",
            "canonical_impl": "scripts/ingest/* + core oracle/ingest builders",
            "validation": "ingest schemas / shadow handoff contracts",
            "transformation": "source pull → candidate evidence objects",
            "persistence": "out/ingest/* via runners (not core)",
            "side_effects": "disk writes through runners only",
            "authority_checks": "SHADOW default; no live external production",
            "output": "EvidenceObject / intake queue items",
            "failure_behavior": "fail-closed receipts / NOT_COMPUTABLE where evidence missing",
            "replay_behavior": "fixture-backed replay for sealed packets",
            "test_coverage": "Partial — ingest/oracle tests present; not one facade yet",
            "status": "PARTIAL",
        },
        {
            "stage_id": "belief_graph",
            "name": "BeliefGraphService",
            "source": "EvidenceObject",
            "canonical_impl": "core/belief_graph/ + belief runners",
            "validation": "SignalGraph.v1 frozen contracts",
            "transformation": "evidence → belief/graph structure",
            "persistence": "out/belief_graph/* via runners",
            "side_effects": "disk via runners",
            "authority_checks": "advisory; no forecast authority from graph alone",
            "output": "BeliefGraph snapshot / signals",
            "failure_behavior": "schema/validation failure",
            "replay_behavior": "deterministic builders",
            "test_coverage": "Partial — belief_graph fixture tests",
            "status": "PARTIAL",
        },
        {
            "stage_id": "alembic_optional",
            "name": "AlembicSpine (optional specialist)",
            "source": "Evidence/Belief context or Oracle candidate metadata",
            "canonical_impl": "core/alembic/pipeline.py + oracle_bridge.py",
            "validation": "contracts/alembic/*; eligibility before ranking",
            "transformation": (
                "route/fuse multi-architecture contributions; shadow compare; "
                "emit advisory fusion — does not mutate Oracle receipts"
            ),
            "persistence": "local out/alembic via scripts/alembic/run_alembic_spine.py",
            "side_effects": "advisory artifacts only; ADVISORY_ONLY",
            "authority_checks": (
                "no canon mutation; stubs NOT_IMPLEMENTED/UNAVAILABLE; "
                "SHADOW results cannot become FORECAST"
            ),
            "output": "ArchitectureContribution[] + FusionResult + run receipt",
            "failure_behavior": "abstain / operator-review route; fail-closed on escalation",
            "replay_behavior": "replay manifest + content hashes",
            "test_coverage": "Present — tests/test_alembic_spine.py and binding tests",
            "status": "ADVISORY_COMPLETE_WITH_RESIDUALS",
            "spine_role": (
                "Optional stage after ingest/evidence and before/alongside Oracle advisory "
                "fusion. Not a parallel product kernel."
            ),
        },
        {
            "stage_id": "oracle_analysis",
            "name": "OracleAnalysisService",
            "source": "Evidence + optional Alembic fusion metadata",
            "canonical_impl": "core/oracle_signal*.py + ingest oracle runners",
            "validation": "oracle intake schemas; conflict detect-only",
            "transformation": "signal analysis → advisory result",
            "persistence": "out/oracle/* / intake receipts via runners",
            "side_effects": "SHADOW handoff only unless separately authorized",
            "authority_checks": "SHADOW/FORECAST separation; adapters cannot assign truth",
            "output": "AdvisoryResult",
            "failure_behavior": "blocked intake / advisory denial; no silent promotion",
            "replay_behavior": "receipt hashes",
            "test_coverage": "Partial",
            "status": "PARTIAL",
        },
        {
            "stage_id": "artifact_repository",
            "name": "ArtifactRepository",
            "source": "AdvisoryResult / governed packets",
            "canonical_impl": "core/canonical/json.py + artifact_provenance_service",
            "validation": "schema validation + canonical hash",
            "transformation": "envelope + classify + atomic write (runners/services)",
            "persistence": "out/** via sole-writer doctrine",
            "side_effects": "filesystem publish",
            "authority_checks": "path policy; activation lane for external publish",
            "output": "durable artifact + hash",
            "failure_behavior": "WRITE_FAILED / PATH_DENIED typed errors",
            "replay_behavior": "hash verify",
            "test_coverage": "Present for canonical_json + artifact_provenance_service",
            "status": "PARTIAL",
        },
        {
            "stage_id": "cli_response",
            "name": "CLI response",
            "source": "AdvisoryResult / validation result",
            "canonical_impl": "NOT_COMPUTABLE as single CLI — many runners; target abraxas CLI",
            "validation": "per-runner",
            "transformation": "print/normalize",
            "persistence": "optional",
            "side_effects": "stdout",
            "authority_checks": "activation_policy",
            "output": "operator-visible result",
            "failure_behavior": "non-zero exit",
            "replay_behavior": "NOT_COMPUTABLE globally",
            "test_coverage": "Partial per runner",
            "status": "NOT_COMPUTABLE",
        },
        {
            "stage_id": "service_response",
            "name": "Service/API response",
            "source": "request models",
            "canonical_impl": "apps/api/main.py routers (health/registry/validation/metrics)",
            "validation": "FastAPI + validation router",
            "transformation": "HTTP JSON",
            "persistence": "none for health/validation",
            "side_effects": "none for current supported routers",
            "authority_checks": "no production activation",
            "output": "HTTP response",
            "failure_behavior": "HTTP errors",
            "replay_behavior": "N/A for health; validation deterministic for fixed schemas",
            "test_coverage": "tests/test_api.py",
            "status": "PARTIAL",
        },
        {
            "stage_id": "validation_request",
            "name": "Validation request → result",
            "source": "schema_ref + instance",
            "canonical_impl": "core/services/validation_service.py",
            "validation": "contracts/-only schema_ref policy",
            "transformation": "jsonschema validate",
            "persistence": "none",
            "side_effects": "none",
            "authority_checks": "none beyond path policy",
            "output": "OK/ERROR typed response",
            "failure_behavior": "typed error_class",
            "replay_behavior": "deterministic",
            "test_coverage": "tests/test_validation_service.py",
            "status": "SUPPORTED_FRAGMENT",
        },
        {
            "stage_id": "current_state_projection",
            "name": "Canonical state load → current-state projection",
            "source": "out/ + STATUS/Notion",
            "canonical_impl": "NOT_COMPUTABLE — out/ mixes domain, audit, workflow, history",
            "validation": "per-artifact",
            "transformation": "ad hoc readers / STATUS.md",
            "persistence": "read-only projection",
            "side_effects": "none",
            "authority_checks": "historical receipts must not authorize runtime",
            "output": "STATUS / readiness projections",
            "failure_behavior": "stale or contradictory docs",
            "replay_behavior": "NOT_COMPUTABLE as one projection",
            "test_coverage": "Partial readiness baselines",
            "status": "NOT_COMPUTABLE",
        },
    ]

    payload = {
        "artifact_type": "golden_path_trace",
        "schema_version": "golden_path_trace.v1",
        "evidence_state": "Partial",
        "supported_spine_target": {
            "shape": [
                "InputEnvelope",
                "IngestService",
                "EvidenceObject",
                "BeliefGraphService",
                "AlembicSpine?",
                "OracleAnalysisService",
                "AdvisoryResult",
                "ArtifactRepository",
                "CLI/API response",
            ],
            "alembic_fit": (
                "Optional specialist after evidence/belief context and before or alongside "
                "Oracle advisory fusion. Reuses contracts/alembic and core/alembic; "
                "does not become a second OS or ingest pipeline."
            ),
            "application_module": "core/application/advisory_spine.py",
        },
        "stages": stages,
        "coverage_summary": {
            "stage_count": len(stages),
            "supported_fragments": sum(1 for s in stages if s["status"] == "SUPPORTED_FRAGMENT"),
            "partial": sum(1 for s in stages if s["status"] == "PARTIAL"),
            "advisory_complete": sum(
                1 for s in stages if s["status"] == "ADVISORY_COMPLETE_WITH_RESIDUALS"
            ),
            "not_computable": sum(1 for s in stages if s["status"] == "NOT_COMPUTABLE"),
        },
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
