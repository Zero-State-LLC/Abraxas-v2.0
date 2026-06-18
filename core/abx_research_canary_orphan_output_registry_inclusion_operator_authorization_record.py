from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_orphan_output_registry_inclusion_constants import (
    AUTHORIZED_DECISION,
    INCLUSION_POLICY,
    ORPHAN_OUTPUT_JSON_PATHS,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryInclusionOperatorAuthorizationRecord.v1"
RECORD_ID = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_OPERATOR_AUTHORIZATION_RECORD_001"
CHAIN_CLOSURE_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_001.latest.json"
)
POLICY_REVIEW_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.json"
)
RECORD_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record_001.latest.json"
)
RECORD_MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record_001.latest.md"
)
SPEC_PLAN_LANE = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_SPEC_PLAN_001"
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


def build_abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    chain_closure = _read_json(root / CHAIN_CLOSURE_JSON_PATH)
    review = _read_json(root / POLICY_REVIEW_JSON_PATH)

    chain_sealed = (
        chain_closure.get("chain_closure_status") == "ORPHAN_POLICY_GOVERNANCE_SEALED"
        and chain_closure.get("status")
        == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_CHAIN_CLOSURE_RECEIPT_EMITTED"
    )
    review_ready = review.get("orphan_count") == len(ORPHAN_OUTPUT_JSON_PATHS)
    record_ready = chain_sealed and review_ready

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECORD_ID,
        "status": (
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_OPERATOR_AUTHORIZATION_RECORD_EMITTED"
            if record_ready
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_OPERATOR_AUTHORIZATION_RECORD_BLOCKED"
        ),
        "authorization_record_id": RECORD_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_OPERATOR_AUTHORIZATION_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authorization_scope": "ORPHAN_OUTPUT_REGISTRY_INCLUSION_BRANCH_A4B_ONLY",
        "selected_decision": AUTHORIZED_DECISION if record_ready else NOT_COMPUTABLE,
        "inclusion_policy": INCLUSION_POLICY if record_ready else NOT_COMPUTABLE,
        "operator_id": "thread_operator",
        "operator_name": "appliedalchemylabs",
        "operator_role": "governed_operator",
        "operator_instruction_observed": "AUTHORIZE_TRACK_A4B_ORPHAN_REGISTRY_INCLUSION",
        "operator_instruction_source": "governed_operator_thread_authorization_track_a4b_inclusion",
        "authorization_timestamp_utc": "2026-06-18T00:00:00Z",
        "orphan_count": len(ORPHAN_OUTPUT_JSON_PATHS),
        "authorized_orphan_paths": list(ORPHAN_OUTPUT_JSON_PATHS),
        "inclusion_spec_authoring_approved": record_ready,
        "execution_authority": False,
        "registry_mutation_performed": False,
        "implementation_authorized": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "p130_advisory_hold_preservation_acknowledged": True,
        "separate_orphan_registry_governance_acknowledged": True,
        "repair_chain_reopen_denied_acknowledged": True,
        "source_chain_closure": {
            "path": str(CHAIN_CLOSURE_JSON_PATH),
            "hash": str(chain_closure.get("receipt_hash", NOT_COMPUTABLE)),
            "chain_closure_status": str(chain_closure.get("chain_closure_status", NOT_COMPUTABLE)),
            "observed": chain_sealed,
        },
        "source_policy_review": {
            "path": str(POLICY_REVIEW_JSON_PATH),
            "hash": str(review.get("review_hash", NOT_COMPUTABLE)),
            "orphan_count": int(review.get("orphan_count", 0)),
        },
        "recommended_next_lane": SPEC_PLAN_LANE if record_ready else NOT_COMPUTABLE,
        "downstream_status": "READY_FOR_ORPHAN_INCLUSION_EXECUTION_SPEC_PLAN" if record_ready else NOT_COMPUTABLE,
        "blocked_actions": [
            "RESEARCH_CANARY_SPINE_REFRESH",
            "P130_ACTIVATION",
            "MERGE_ORPHAN_INCLUSION_INTO_REPAIR_CHAIN_CLOSURE",
            "REOPEN_EXCLUDE_CHAIN_WITHOUT_OPERATOR_REVIEW",
            "RUNTIME_MUTATION",
            "CANON_MUTATION",
        ],
    }
    return {**packet, "authorization_record_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    return [
        "# ABX Research Canary Orphan Output Registry Inclusion Operator Authorization Record 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `selected_decision`: `{packet['selected_decision']}`",
        f"- `inclusion_policy`: `{packet['inclusion_policy']}`",
        f"- `orphan_count`: `{packet['orphan_count']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
    ]


def write_abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    _write_markdown(target_root / RECORD_MD_PATH, render_markdown(packet))
    return packet
