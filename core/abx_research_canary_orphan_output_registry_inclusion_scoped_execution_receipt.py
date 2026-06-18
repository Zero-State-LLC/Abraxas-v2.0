from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_artifact_registry_coverage_audit import (
    build_abx_research_canary_artifact_registry_coverage_audit,
)
from core.abx_research_canary_orphan_output_registry_inclusion_constants import ORPHAN_OUTPUT_JSON_PATHS
from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryInclusionScopedExecutionReceipt.v1"
RECEIPT_ID = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_SCOPED_EXECUTION_RECEIPT_001"
AUTHORIZATION_RECORD_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_execution_authorization_record_001.latest.json"
)
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt_001.latest.md"
)
AUDIT_REGENERATION_LANE = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_AUDIT_REGENERATION_RECEIPT_001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _post_inclusion_verification(root: Path) -> dict[str, Any]:
    derived_optional_paths = set(_DERIVED_OPTIONAL_ARTIFACTS)
    registered = [path for path in ORPHAN_OUTPUT_JSON_PATHS if path in derived_optional_paths]
    audit = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=root)
    coverage = audit.get("coverage_summary", {})
    return {
        "orphan_paths_registered_count": len(registered),
        "orphan_paths_registered": registered,
        "orphan_research_output_count": int(coverage.get("orphan_research_output_count", -1)),
        "all_orphan_paths_registered": len(registered) == len(ORPHAN_OUTPUT_JSON_PATHS),
        "orphan_exclusion_cleared": coverage.get("orphan_research_output_count") == 0,
    }


def build_abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    authorization = _read_json(root / AUTHORIZATION_RECORD_JSON_PATH)
    authorization_status = authorization.get("status")
    authorization_ready = (
        authorization.get("schema_version")
        == "AbxResearchCanaryOrphanOutputRegistryInclusionExecutionAuthorizationRecord.v1"
        and authorization_status
        in {
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR",
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_RECORD_CONSUMED_BY_SCOPED_EXECUTION_RECEIPT",
        }
        and authorization.get("authorization_granted") is True
        and authorization.get("execution_authority") is True
        and (
            authorization.get("safe_to_prepare_execution_pr") is True
            or authorization_status
            == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_RECORD_CONSUMED_BY_SCOPED_EXECUTION_RECEIPT"
        )
    )
    verification = _post_inclusion_verification(root) if authorization_ready else {}
    inclusion_verified = (
        authorization_ready
        and verification.get("all_orphan_paths_registered") is True
        and verification.get("orphan_exclusion_cleared") is True
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECEIPT_ID,
        "status": (
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_SCOPED_EXECUTION_RECEIPT_EMITTED"
            if inclusion_verified
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_SCOPED_EXECUTION_RECEIPT_BLOCKED"
        ),
        "receipt_id": "abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt_001",
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_SCOPED_EXECUTION_RECEIPT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_authorization_record": {
            "path": str(AUTHORIZATION_RECORD_JSON_PATH),
            "hash": str(authorization.get("authorization_record_hash", NOT_COMPUTABLE)),
            "status": str(authorization.get("status", NOT_COMPUTABLE)),
            "observed": authorization_ready,
        },
        "authorization_scope": "SCOPED_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_PR_ONLY",
        "registry_mutation_performed": inclusion_verified,
        "inclusion_execution_performed": inclusion_verified,
        "execution_authority": authorization_ready,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "orphan_inclusion_repair": {
            "repair_status": "REPAIRED_BY_DERIVED_OPTIONAL_ORPHAN_INCLUSION" if inclusion_verified else "BLOCKED",
            "target_path_count": len(ORPHAN_OUTPUT_JSON_PATHS),
            "repaired_count": verification.get("orphan_paths_registered_count", 0),
            "repaired_paths": verification.get("orphan_paths_registered", []),
            "repair_policy": "REGISTER_AS_DERIVED_OPTIONAL",
        },
        "post_inclusion_verification": verification,
        "governance_preservation": {
            "p130_hold_preserved": True,
            "research_canary_spine_refresh_performed": False,
            "repair_chain_remains_sealed": True,
        },
        "downstream_status": "READY_FOR_ORPHAN_INCLUSION_AUDIT_REGENERATION" if inclusion_verified else NOT_COMPUTABLE,
        "recommended_next_lane": AUDIT_REGENERATION_LANE if inclusion_verified else NOT_COMPUTABLE,
    }
    return {**packet, "receipt_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    return [
        "# ABX Research Canary Orphan Output Registry Inclusion Scoped Execution Receipt 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `registry_mutation_performed`: `{packet['registry_mutation_performed']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
    ]


def write_abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(target_root / RECEIPT_MD_PATH, render_markdown(packet))
    return packet
