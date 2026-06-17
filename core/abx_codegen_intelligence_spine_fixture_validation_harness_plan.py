from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_advisory_spec_plan import (
    AUTHORITY_LOCKS,
    BLOCKED_ACTIONS,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineFixtureValidationHarnessPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_FIXTURE_VALIDATION_HARNESS_PLAN_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_fixture_validation_harness_plan_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_fixture_validation_harness_plan_001.latest.md"
ADVISORY_SPEC_PLAN_JSON = (
    "out/audit/abx_codegen_intelligence_spine_advisory_spec_plan_001.latest.json"
)

NOTION_HARNESS_SOURCES: tuple[dict[str, str], ...] = (
    {
        "surface_id": "37d3e8ba-2f5c-8147-8aea-ccfd7be5d1e2",
        "title": "Harness Implementation Spec: core/codegen_shadow_replay_harness.py",
        "status": "DETAILED_IMPLEMENTATION_PLANNING_SPEC",
        "source_observed_at": "2026-06-12T20:03:11Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-8160-a6a4-e47bae761b2e",
        "title": "Harness Implementation Roadmap — Codegen Intelligence Spine",
        "status": "IMPLEMENTATION_PLANNING",
        "source_observed_at": "2026-06-12T20:18:46Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-8152-9f8c-d88593af42c1",
        "title": "Testing & Validation Strategy — Codegen Intelligence Spine",
        "status": "PLANNING_SPEC_ADVISORY",
        "source_observed_at": "2026-06-12T20:15:06Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-8140-963c-e1379a660411",
        "title": "Error & Failure Taxonomy — Codegen Intelligence Spine",
        "status": "PLANNING_SPEC_ADVISORY",
        "source_observed_at": "2026-06-12T20:14:38Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-8111-811f-e95fcdff4e64",
        "title": "Artifact Registry Integration — Codegen Intelligence Spine",
        "status": "PLANNING_SPEC_ADVISORY",
        "source_observed_at": "2026-06-12T20:14:50Z",
    },
)

PLANNED_INTERFACES: tuple[dict[str, Any], ...] = (
    {
        "name": "run_codegen_shadow_replay",
        "planned_module": "core/codegen_shadow_replay_harness.py",
        "input": "ImprovementProposal.v1 plus optional upstream GapDiagnosisPacket.v1",
        "output": "ShadowImprovementReceipt.v1",
        "implementation_status": "PLANNED_ONLY",
    },
    {
        "name": "_validate_proposal",
        "planned_module": "core/codegen_shadow_replay_harness.py",
        "input": "ImprovementProposal.v1",
        "output": "validation error list using Codegen failure taxonomy",
        "implementation_status": "PLANNED_ONLY",
    },
    {
        "name": "_build_replay_config",
        "planned_module": "core/codegen_shadow_replay_harness.py",
        "input": "shadow_validation_plan plus overrides",
        "output": "deterministic seed, constraints, run count, and invariant set",
        "implementation_status": "PLANNED_ONLY",
    },
    {
        "name": "_evaluate_proof_flags",
        "planned_module": "core/codegen_shadow_replay_harness.py",
        "input": "proposal plus replay result summaries",
        "output": "standard P103 flags plus codegen-specific flags",
        "implementation_status": "PLANNED_ONLY",
    },
    {
        "name": "_determine_recommendation",
        "planned_module": "core/codegen_shadow_replay_harness.py",
        "input": "status, proof flags, and self-modification flag",
        "output": "HOLD/BLOCK/PROMOTE recommendation with promotion blockers",
        "implementation_status": "PLANNED_ONLY",
    },
)

PLANNED_PROOF_FLAGS: tuple[dict[str, str], ...] = (
    {"flag": "authority_lock_invariance_observed", "source": "P103 standard"},
    {"flag": "not_computable_replay_observed", "source": "P103 standard"},
    {"flag": "operator_review_observed", "source": "P103 standard"},
    {"flag": "no_runtime_mutation_observed", "source": "P103 standard"},
    {"flag": "no_canon_promotion_observed", "source": "P103 standard"},
    {"flag": "codegen_deterministic_output_observed", "source": "Codegen extension"},
    {"flag": "contract_delta_replay_successful", "source": "Codegen extension"},
    {"flag": "self_modification_invariants_satisfied", "source": "Codegen extension"},
    {"flag": "meta_gate_extra_checks_passed", "source": "Meta-Gate extension"},
)

FAILURE_TAXONOMY: tuple[dict[str, str], ...] = (
    {"category": "Validation", "code_prefix": "VAL-", "default_recommendation": "REJECT"},
    {"category": "Replay", "code_prefix": "RPL-", "default_recommendation": "BLOCK_REPLAY_FAILURE"},
    {"category": "Governance", "code_prefix": "GOV-", "default_recommendation": "BLOCK_POLICY_VIOLATION"},
    {"category": "Meta-Gate", "code_prefix": "META-", "default_recommendation": "HOLD_FOR_META_GATE"},
    {"category": "Integration", "code_prefix": "INT-", "default_recommendation": "HOLD_FOR_OPERATOR"},
    {"category": "Internal", "code_prefix": "INTL-", "default_recommendation": "HOLD_FOR_OPERATOR"},
)

ARTIFACT_REGISTRY_REQUIREMENTS: tuple[dict[str, str], ...] = (
    {
        "artifact_type": "ImprovementProposal.v1",
        "lineage_requirement": "must link to source GapDiagnosisPacket",
    },
    {
        "artifact_type": "ShadowImprovementReceipt.v1",
        "lineage_requirement": "must link to originating ImprovementProposal",
    },
    {
        "artifact_type": "CodegenOperatorDecisionRecord.v1",
        "lineage_requirement": "must link to proposal and receipt",
    },
    {
        "artifact_type": "MetaGateAuthorizationRecord.v1",
        "lineage_requirement": "must link to operator decision record and receipt",
    },
    {
        "artifact_type": "MetaGateChainSeal.v1",
        "lineage_requirement": "must link to authorization record",
    },
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _status_for(path: Path) -> str:
    return "OBSERVED" if path.exists() else "MISSING"


def _source_records(records: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    for item in records:
        record = dict(item)
        record["source_hash"] = canonical_hash(item)
        enriched.append(record)
    return enriched


def _fixture_inventory(repo_root: Path) -> dict[str, Any]:
    fixture_root = repo_root / "tests/fixtures/codegen"
    fixtures: list[dict[str, str]] = []
    for target in sorted(fixture_root.glob("*.json")):
        fixtures.append(
            {
                "path": target.relative_to(repo_root).as_posix(),
                "fixture_class": "NEGATIVE" if target.name.startswith("invalid_") else "VALID",
                "source_hash": _sha256(target),
            }
        )
    return {
        "fixture_root": "tests/fixtures/codegen",
        "fixture_count": len(fixtures),
        "valid_fixture_count": sum(
            1 for fixture in fixtures if fixture["fixture_class"] == "VALID"
        ),
        "negative_fixture_count": sum(
            1 for fixture in fixtures if fixture["fixture_class"] == "NEGATIVE"
        ),
        "fixtures": fixtures,
    }


def build_abx_codegen_intelligence_spine_fixture_validation_harness_plan(
    *,
    repo_root: str | Path,
    advisory_spec_plan_path: str | Path = ADVISORY_SPEC_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_paths = {"advisory_spec_plan": Path(advisory_spec_plan_path).as_posix()}
    source_hashes = {key: _sha256(root / path) for key, path in source_paths.items()}
    required_source_statuses = {
        key: _status_for(root / path)
        for key, path in source_paths.items()
    }
    advisory_spec_plan = _read_json(root / advisory_spec_plan_path)
    upstream_ready = (
        advisory_spec_plan.get("recommended_next_lane")
        == "ABX_CODEGEN_INTELLIGENCE_SPINE_FIXTURE_VALIDATION_HARNESS_PLAN"
    )
    sources_observed = all(status == "OBSERVED" for status in required_source_statuses.values())
    fixture_inventory = _fixture_inventory(root)
    plan_status = (
        "ABX_CODEGEN_INTELLIGENCE_SPINE_FIXTURE_VALIDATION_HARNESS_PLAN_READY"
        if upstream_ready and sources_observed and fixture_inventory["fixture_count"] > 0
        else "NOT_COMPUTABLE"
    )

    authority_locks = dict(AUTHORITY_LOCKS)
    authority_locks.update(
        {
            "artifact_registry_mutation": False,
            "continuity_lane_creation": False,
            "harness_implementation": False,
        }
    )
    blocked_actions = sorted(
        set(BLOCKED_ACTIONS)
        | {
            "artifact_registry_mutation",
            "continuity_lane_creation",
            "harness_implementation",
            "receipt_creation",
        }
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": plan_status,
        "target_surface": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
        "target_surface_status": "FIXTURE_VALIDATION_HARNESS_PLANNED_ADVISORY_ONLY",
        "patch_id": "PATCH-ABX-CODEGEN-INTELLIGENCE-SPINE-FIXTURE-VALIDATION-HARNESS-PLAN-001",
        "source_paths": source_paths,
        "source_hashes": source_hashes,
        "required_source_statuses": required_source_statuses,
        "notion_harness_sources": _source_records(NOTION_HARNESS_SOURCES),
        "planned_interfaces": list(PLANNED_INTERFACES),
        "planned_proof_flags": list(PLANNED_PROOF_FLAGS),
        "failure_taxonomy": list(FAILURE_TAXONOMY),
        "test_strategy": {
            "unit_tests": [
                "proposal validation",
                "replay config building",
                "proof flag evaluation",
                "recommendation logic",
            ],
            "integration_tests": [
                "proposal to receipt flow",
                "meta-gate path",
                "error injection",
            ],
            "determinism_tests": [
                "12-run invariance",
                "24-run meta-gate invariance",
                "hash consistency for identical inputs and seed",
            ],
            "adversarial_tests": [
                "malformed proposals",
                "red-zone modification attempts",
                "missing fields",
                "governance lock violations",
            ],
            "test_files_planned": [
                "tests/codegen/test_harness.py",
                "tests/codegen/test_schemas.py",
                "tests/codegen/test_meta_gate.py",
                "tests/codegen/test_error_taxonomy.py",
            ],
        },
        "artifact_registry_requirements": list(ARTIFACT_REGISTRY_REQUIREMENTS),
        "fixture_inventory": fixture_inventory,
        "authority_locks": authority_locks,
        "blocked_actions": blocked_actions,
        "recommended_next_lane": (
            "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_GATE"
        ),
        "recommended_next_action": (
            "open a separate governed authorization gate before creating "
            "core/codegen_shadow_replay_harness.py or emitting live ShadowImprovementReceipt artifacts"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "harness_implementation_performed": False,
        "shadow_replay_execution_performed": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_fixture_validation_harness_plan(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_abx_codegen_intelligence_spine_fixture_validation_harness_plan_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    lines = [
        "# ABX Codegen Intelligence Spine Fixture Validation Harness Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- target_surface_status: {packet['target_surface_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- harness_implementation_performed: {packet['harness_implementation_performed']}",
        f"- shadow_replay_execution_performed: {packet['shadow_replay_execution_performed']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Planned Interfaces",
    ]
    for interface in packet.get("planned_interfaces", []):
        if isinstance(interface, dict):
            lines.append(f"- {interface['name']}: {interface['implementation_status']}")
    lines.extend(["", "## Planned Proof Flags"])
    for flag in packet.get("planned_proof_flags", []):
        if isinstance(flag, dict):
            lines.append(f"- {flag['flag']} ({flag['source']})")
    lines.extend(["", "## Failure Taxonomy"])
    for item in packet.get("failure_taxonomy", []):
        if isinstance(item, dict):
            lines.append(
                f"- {item['code_prefix']} {item['category']}: {item['default_recommendation']}"
            )
    fixture_inventory = packet.get("fixture_inventory", {})
    if isinstance(fixture_inventory, dict):
        lines.extend(
            [
                "",
                "## Fixture Inventory",
                f"- fixture_count: {fixture_inventory['fixture_count']}",
                f"- valid_fixture_count: {fixture_inventory['valid_fixture_count']}",
                f"- negative_fixture_count: {fixture_inventory['negative_fixture_count']}",
            ]
        )
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
