from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "GrokAbxRunesReconciliationPlan.v1"
PLAN_ID = "grok_abx_runes_reconciliation_plan_001"
PLAN_JSON_PATH = Path("out/operator_review/grok_abx_runes_reconciliation_plan_001.latest.json")
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")

GROK_SHARE_URL = (
    "https://grok.com/share/"
    "c2hhcmQtMi1jb3B5_7ff7a1fd-d623-4aee-9adf-0447b43e5d05"
)
GROK_CONVERSATION_ID = "676ec4cf-a847-4e40-afa0-fbdfc1a92b30"
GROK_CONVERSATION_TITLE = "Dependabot PR Fixes and Cleanup"
GROK_CREATE_TIME_SOURCE_OBSERVED = "2026-06-15T18:42:35.252204Z"
GROK_MODIFY_TIME_SOURCE_OBSERVED = "2026-06-16T02:09:18.431Z"
GROK_RESPONSE_COUNT_SOURCE_OBSERVED = 646
GROK_MESSAGE_CHARACTER_COUNT_SOURCE_OBSERVED = 865838
GROK_ABX_TERM_COUNT_SOURCE_OBSERVED = 35
GROK_RUNE_TERM_COUNT_SOURCE_OBSERVED = 329
GROK_YGGDRASIL_TERM_COUNT_SOURCE_OBSERVED = 405
GROK_NOTION_TERM_COUNT_SOURCE_OBSERVED = 432

RUNE_CATALOG_PATH = "contracts/runes/catalog.v1.json"
V2_REGISTRATION_READINESS_PATH = "out/sync/v2_hygiene_registration_readiness_audit/latest.json"
V2_ALIGNMENT_PLAN_PATH = "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.json"
V2_OPERATOR_GATE_PATH = "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json"
RUNE_FORMALIZATION_PLAN_PATH = "out/audit/rune_registry_formalization_plan_001.latest.json"
YGGDRASIL_BINDING_MATRIX_PATH = "out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json"

GROK_NOTION_FAMILIES: tuple[dict[str, Any], ...] = (
    {"family_id": "ASTRA", "version": "v1.0", "description": "Astrological Rune Family", "response_index": 207},
    {"family_id": "DIVIN", "version": "v1.0", "description": "Divination Rune Family", "response_index": 233},
    {"family_id": "GEMATRIA", "version": "v1.0", "description": "Numerical & Symbolic Gematria Rune Family", "response_index": 243},
    {"family_id": "SIGIL", "version": "v1.0", "description": "Symbolic Sigil Rune Family", "response_index": 251},
    {"family_id": "CADENCE", "version": "v1.0", "description": "Rhythmic Pattern Rune Family", "response_index": 275},
    {"family_id": "ROLES", "version": "v1.0", "description": "Role & Actor Pattern Rune Family", "response_index": 295},
    {"family_id": "MYTHO", "version": "v1.0", "description": "Mythological Archetype Rune Family", "response_index": 321},
    {"family_id": "AFTER", "version": "v1.0", "description": "Post-Ritual Residue Rune Family", "response_index": 327},
    {"family_id": "ORACLE", "version": "v1.0", "description": "Oracular Pattern Rune Family", "response_index": 343},
    {"family_id": "LEGEND", "version": "v1.0", "description": "Legendary Narrative Rune Family", "response_index": 379},
    {"family_id": "VISION", "version": "v1.0", "description": "Visionary Pattern Rune Family", "response_index": 423},
    {"family_id": "ARCANA", "version": "v1.0", "description": "Arcane Symbolic System Rune Family", "response_index": 435},
    {"family_id": "THREAD", "version": "v1.0", "description": "Fate Thread & Destiny Pattern Rune Family", "response_index": 443},
    {"family_id": "ECHO", "version": "v1.0", "description": "Echo & Residue Pattern Rune Family", "response_index": 495},
    {"family_id": "FRACTAL", "version": "v1.0", "description": "Fractal Self-Similarity Rune Family", "response_index": 505},
    {"family_id": "PRISM", "version": "v1.0", "description": "Multi-Faceted Refraction Rune Family", "response_index": 531},
    {"family_id": "AETHYR", "version": "v1.0", "description": "Aethyric Realm Rune Family", "response_index": 575},
    {"family_id": "PATHS", "version": "v1.0", "description": "Pathways & Connections Rune Family", "response_index": 617},
    {"family_id": "VEIL", "version": "v1.0", "description": "Veils of Reality Rune Family", "response_index": 627},
)

REPRESENTATIVE_GROK_RUNE_IDS: tuple[str, ...] = (
    "RUNE.SYMBOLIC.TEMPORAL_RESONANCE",
    "RUNE.SYMBOLIC.ATTENTION_WEATHER",
    "RUNE.SYMBOLIC.MEMETIC_COMPRESSION",
    "RUNE.SYMBOLIC.FRACTAL_CORE",
    "RUNE.SYMBOLIC.HYPERSTITION_BIND",
    "RUNE.ASTRA.v1.0",
    "RUNE.DIVIN.v1.0",
    "RUNE.GEMATRIA.v1.0",
    "RUNE.SIGIL.v1.0",
    "RUNE.CADENCE.v1.0",
    "RUNE.ORACLE.v1.0",
    "RUNE.LEGEND.v1.0",
    "RUNE.VISION.v1.0",
    "RUNE.ARCANA.v1.0",
    "RUNE.THREAD.v1.0",
    "RUNE.ECHO.v1.0",
    "RUNE.FRACTAL.v1.0",
    "RUNE.PRISM.v1.0",
    "RUNE.AETHYR.v1.0",
    "RUNE.PATHS.v1.0",
    "RUNE.VEIL.v1.0",
)

CONFLICTING_GROK_CLAIM_CLASSES: tuple[str, ...] = (
    "catalog_updated",
    "binding_matrix_regenerated",
    "full_system_audit_passed",
    "pr_posted_and_merged",
    "canon_promotion_authorized",
    "canary_authorization_granted",
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _catalog_rune_ids(root: Path) -> set[str]:
    packet = _read_json(root / RUNE_CATALOG_PATH)
    runes = packet.get("runes", [])
    if not isinstance(runes, list):
        return set()
    return {
        str(rune.get("rune_id"))
        for rune in runes
        if isinstance(rune, Mapping) and isinstance(rune.get("rune_id"), str)
    }


def _hash_or_not_computable(root: Path, rel_path: str) -> str:
    packet = _read_json(root / rel_path)
    return canonical_hash(packet) if packet else NOT_COMPUTABLE


def _authority_locks() -> dict[str, bool]:
    return {
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "catalog_mutation": False,
        "code_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "notion_writeback": False,
        "operator_authorization_record_creation": False,
        "operator_attestation": False,
        "pr_merge_authority": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "yggdrasil_binding_mutation": False,
    }


def _repo_evidence(root: Path) -> dict[str, Any]:
    catalog_ids = _catalog_rune_ids(root)
    missing_representative = [
        rune_id for rune_id in REPRESENTATIVE_GROK_RUNE_IDS if rune_id not in catalog_ids
    ]
    observed_representative = [
        rune_id for rune_id in REPRESENTATIVE_GROK_RUNE_IDS if rune_id in catalog_ids
    ]
    registration_readiness = _read_json(root / V2_REGISTRATION_READINESS_PATH)
    alignment_plan = _read_json(root / V2_ALIGNMENT_PLAN_PATH)
    operator_gate = _read_json(root / V2_OPERATOR_GATE_PATH)
    formalization_plan = _read_json(root / RUNE_FORMALIZATION_PLAN_PATH)
    binding_matrix = _read_json(root / YGGDRASIL_BINDING_MATRIX_PATH)

    return {
        "rune_catalog_path": RUNE_CATALOG_PATH,
        "catalog_observed": bool(catalog_ids),
        "catalog_rune_count": len(catalog_ids),
        "representative_grok_rune_ids_observed_in_catalog": observed_representative,
        "representative_grok_rune_ids_missing_from_catalog": missing_representative,
        "all_representative_grok_runes_registered": not missing_representative,
        "registration_readiness_status": str(
            registration_readiness.get("audit_status", NOT_COMPUTABLE)
        ),
        "registration_safe_to_register_runes": bool(
            registration_readiness.get("registration_readiness", {}).get(
                "safe_to_register_runes", False
            )
        ),
        "alignment_plan_status": str(alignment_plan.get("plan_status", NOT_COMPUTABLE)),
        "operator_gate_status": str(operator_gate.get("gate_status", NOT_COMPUTABLE)),
        "operator_authorization_observed": bool(
            registration_readiness.get("operator_authorization_observed", False)
            or alignment_plan.get("operator_authorization_observed", False)
            or operator_gate.get("operator_authorization_observed", False)
        ),
        "rune_formalization_plan_status": str(
            formalization_plan.get("plan_status", NOT_COMPUTABLE)
        ),
        "rune_formalization_registration_performed": bool(
            formalization_plan.get("rune_registration_performed", False)
        ),
        "yggdrasil_binding_matrix_status": str(
            binding_matrix.get("final_status", NOT_COMPUTABLE)
        ),
        "yggdrasil_binding_mutation_authorized": False,
    }


def build_grok_abx_runes_reconciliation_plan(repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root)
    evidence = _repo_evidence(root)
    source_ready = evidence["catalog_observed"] and len(GROK_NOTION_FAMILIES) == 19
    safe_to_register = (
        evidence["all_representative_grok_runes_registered"] is False
        and evidence["registration_safe_to_register_runes"] is True
        and evidence["operator_authorization_observed"] is True
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "reconciliation_status": (
            "GROK_ABX_RUNES_RECONCILIATION_HELD_FOR_OPERATOR"
            if source_ready
            else "GROK_ABX_RUNES_RECONCILIATION_BLOCKED"
        ),
        "source_conversation": {
            "source_type": "external_grok_share",
            "source_url": GROK_SHARE_URL,
            "conversation_id": GROK_CONVERSATION_ID,
            "title": GROK_CONVERSATION_TITLE,
            "create_time_source_observed": GROK_CREATE_TIME_SOURCE_OBSERVED,
            "modify_time_source_observed": GROK_MODIFY_TIME_SOURCE_OBSERVED,
            "response_count_source_observed": GROK_RESPONSE_COUNT_SOURCE_OBSERVED,
            "message_character_count_source_observed": GROK_MESSAGE_CHARACTER_COUNT_SOURCE_OBSERVED,
            "abx_term_count_source_observed": GROK_ABX_TERM_COUNT_SOURCE_OBSERVED,
            "rune_term_count_source_observed": GROK_RUNE_TERM_COUNT_SOURCE_OBSERVED,
            "yggdrasil_term_count_source_observed": GROK_YGGDRASIL_TERM_COUNT_SOURCE_OBSERVED,
            "notion_term_count_source_observed": GROK_NOTION_TERM_COUNT_SOURCE_OBSERVED,
            "source_is_repo_authoritative": False,
            "source_grants_authority": False,
        },
        "grok_claim_digest": {
            "notion_rune_family_count": len(GROK_NOTION_FAMILIES),
            "notion_rune_families": list(GROK_NOTION_FAMILIES),
            "representative_rune_ids": list(REPRESENTATIVE_GROK_RUNE_IDS),
            "representative_rune_id_count": len(REPRESENTATIVE_GROK_RUNE_IDS),
            "conflicting_claim_classes": list(CONFLICTING_GROK_CLAIM_CLASSES),
        },
        "repo_evidence": evidence,
        "source_artifact_hashes": {
            RUNE_CATALOG_PATH: _hash_or_not_computable(root, RUNE_CATALOG_PATH),
            V2_REGISTRATION_READINESS_PATH: _hash_or_not_computable(
                root, V2_REGISTRATION_READINESS_PATH
            ),
            V2_ALIGNMENT_PLAN_PATH: _hash_or_not_computable(root, V2_ALIGNMENT_PLAN_PATH),
            V2_OPERATOR_GATE_PATH: _hash_or_not_computable(root, V2_OPERATOR_GATE_PATH),
            RUNE_FORMALIZATION_PLAN_PATH: _hash_or_not_computable(
                root, RUNE_FORMALIZATION_PLAN_PATH
            ),
            YGGDRASIL_BINDING_MATRIX_PATH: _hash_or_not_computable(
                root, YGGDRASIL_BINDING_MATRIX_PATH
            ),
        },
        "reconciliation_findings": [
            {
                "finding_id": "grok_share_contains_abx_runes_work",
                "finding_status": "OBSERVED" if source_ready else "NOT_OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "grok_execution_claims_not_repo_authoritative",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "representative_runes_missing_from_catalog",
                "finding_status": (
                    "OBSERVED"
                    if evidence["representative_grok_rune_ids_missing_from_catalog"]
                    else "CLEAR"
                ),
                "authority_granted": False,
            },
            {
                "finding_id": "operator_gate_blocks_registration",
                "finding_status": "ENFORCED" if not safe_to_register else "READY_FOR_SEPARATE_REVIEW",
                "authority_granted": False,
            },
        ],
        "recommended_next_lane": (
            "GROK_ABX_RUNES_OPERATOR_REVIEW_DECISION_RECORD_PLAN"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "recommended_next_action": (
            "prepare an operator decision-record plan that can classify the Grok "
            "ABX-Runes digest as backlog, reject it, or authorize a separate "
            "advisory-only registration planning lane without mutating the rune catalog"
            if source_ready
            else "restore repo-visible rune evidence before reconciling external Grok claims"
        ),
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authorization_granted": False,
        "operator_authorization_observed": evidence["operator_authorization_observed"],
        "operator_authorization_record_created": False,
        "operator_attestation_created": False,
        "rune_registration_authorized": False,
        "yggdrasil_binding_mutation_authorized": False,
        "catalog_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "pr_merge_authority": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "reconciliation_hash": canonical_hash(packet)}


def render_grok_abx_runes_reconciliation_plan_markdown(packet: Mapping[str, Any]) -> list[str]:
    source = packet["source_conversation"]
    digest = packet["grok_claim_digest"]
    evidence = packet["repo_evidence"]
    lines = [
        "# Grok ABX-Runes Reconciliation Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- reconciliation_status: {packet['reconciliation_status']}",
        f"- source_url: {source['source_url']}",
        f"- source_modify_time_observed: {source['modify_time_source_observed']}",
        f"- notion_rune_family_count: {digest['notion_rune_family_count']}",
        f"- catalog_rune_count: {evidence['catalog_rune_count']}",
        f"- missing_representative_rune_count: {len(evidence['representative_grok_rune_ids_missing_from_catalog'])}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Observed Grok Rune Families",
    ]
    for family in digest["notion_rune_families"]:
        lines.append(
            f"- {family['family_id']} {family['version']}: {family['description']}"
        )
    lines.extend(["", "## Findings"])
    for finding in packet["reconciliation_findings"]:
        lines.append(
            f"- {finding['finding_id']}: {finding['finding_status']} "
            f"(authority_granted={finding['authority_granted']})"
        )
    return lines


def write_grok_abx_runes_reconciliation_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_grok_abx_runes_reconciliation_plan(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLAN_JSON_PATH, packet)
    md_path = root / PLAN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_grok_abx_runes_reconciliation_plan_markdown(packet)) + "\n",
        encoding="utf-8",
    )
    return packet
