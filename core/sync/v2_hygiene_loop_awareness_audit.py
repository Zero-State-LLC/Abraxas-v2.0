from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "V2HygieneLoopAwarenessAudit.v1"
AUDIT_ID = "V2_HYGIENE_LOOP_AWARENESS_AUDIT_001"
OUT_JSON = "out/sync/v2_hygiene_loop_awareness_audit/latest.json"
OUT_MD = "out/sync/v2_hygiene_loop_awareness_audit/latest.md"

EVIDENCE_PATHS = [
    "README.md",
    "PLANS.md",
    "STATUS.md",
    "docs/status/badges.json",
    "docs/status/continuity-spine.json",
    "docs/audits/ABRAXAS_REPO_NOTION_DIFF_001.md",
    "contracts/runes/catalog.v1.json",
    "core/pipelines/registry.py",
]

CHECKS = [
    {
        "check_id": "output_registers_present",
        "requirement": "high-signal outputs carry OBSERVED / INFERRED / SPECULATIVE registers",
        "required_terms": ["OBSERVED", "INFERRED", "SPECULATIVE"],
    },
    {
        "check_id": "loop_dynamics_assessment_present",
        "requirement": "forward-looking or mythic content includes loop_dynamics assessment",
        "required_terms": ["loop_dynamics", "loop_dynamics_assessment_complete"],
    },
    {
        "check_id": "hyperstitional_charge_tagged",
        "requirement": "hyperstitional charge has been evaluated and tagged where relevant",
        "required_terms": ["hyperstitional_charge", "hyperstitional_charge_evaluated"],
    },
    {
        "check_id": "provenance_blocks_present",
        "requirement": "provenance block is complete and non-empty on registered outputs",
        "required_terms": ["provenance"],
    },
    {
        "check_id": "v2_modules_registered",
        "requirement": "new v2.0 modules are registered in the Canon Spine",
        "required_terms": [
            "Retrocausal Hygiene",
            "Output Schema Enforcer",
            "Self-Adversarial Loop",
            "Hyperstition Evaluator",
        ],
    },
    {
        "check_id": "core_directive_linked",
        "requirement": "v2.0 Core Directive page is linked from repo projection surfaces",
        "required_terms": ["Abraxas v2.0 Core Directive"],
    },
    {
        "check_id": "v2_runes_documented",
        "requirement": "new v2.0 runes are documented in the ABX-Runes registry",
        "required_terms": [
            "LOOP_AWARENESS",
            "HYPERSTITION_TAG",
            "PROVENANCE_ENFORCE",
            "ADVERSARIAL_AUDIT",
            "OUTPUT_REGISTER_ENFORCE",
        ],
    },
    {
        "check_id": "projection_surfaces_have_v2_notes",
        "requirement": "projection surfaces include v2.0 compliance notes and freshness sync",
        "required_terms": ["v2.0 compliance", "freshness sync"],
    },
]


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _authority_locks() -> dict[str, bool]:
    return {
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_routing": False,
        "github_writeback": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "queue_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "token_minting": False,
    }


def _term_paths(term: str, evidence_text: dict[str, str]) -> list[str]:
    needle = term.casefold()
    return sorted(path for path, text in evidence_text.items() if needle in text.casefold())


def _evaluate_check(check: dict[str, Any], evidence_text: dict[str, str]) -> dict[str, Any]:
    terms = [str(term) for term in check["required_terms"]]
    observed_terms = [
        {"term": term, "paths": _term_paths(term, evidence_text)}
        for term in terms
    ]
    observed_count = sum(1 for item in observed_terms if item["paths"])
    if observed_count == len(terms):
        status = "PASSED"
    elif observed_count > 0:
        status = "PARTIAL"
    else:
        status = "MISSING"
    return {
        "check_id": str(check["check_id"]),
        "requirement": str(check["requirement"]),
        "status": status,
        "observed_term_count": observed_count,
        "required_term_count": len(terms),
        "observed_terms": observed_terms,
        "missing_terms": [item["term"] for item in observed_terms if not item["paths"]],
    }


def build_v2_hygiene_loop_awareness_audit(repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root)
    observed_paths = [path for path in EVIDENCE_PATHS if (root / path).exists()]
    evidence_text = {path: _read_text(root / path) for path in observed_paths}
    check_results = [_evaluate_check(check, evidence_text) for check in CHECKS]
    missing_checks = [
        result["check_id"]
        for result in check_results
        if result["status"] in {"MISSING", "PARTIAL"}
    ]
    status = (
        "V2_HYGIENE_LOOP_AWARENESS_AUDIT_DEGRADED"
        if observed_paths
        else NOT_COMPUTABLE
    )
    if observed_paths and not missing_checks:
        status = "V2_HYGIENE_LOOP_AWARENESS_AUDIT_READY"

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "audit_id": AUDIT_ID,
        "audit_status": status,
        "notion_source": (
            "ABRAXAS v2.0 Repo Notion Sync Receipt 2026-06-12 "
            "v2.0 Hygiene and Loop-Awareness Checks"
        ),
        "source_mode": "repo_visible_evidence_only",
        "evidence_paths": EVIDENCE_PATHS,
        "observed_evidence_paths": observed_paths,
        "missing_evidence_paths": sorted(set(EVIDENCE_PATHS) - set(observed_paths)),
        "source_artifact_hashes": {path: _sha256(root / path) for path in EVIDENCE_PATHS},
        "check_results": check_results,
        "passed_checks": [
            result["check_id"] for result in check_results if result["status"] == "PASSED"
        ],
        "partial_checks": [
            result["check_id"] for result in check_results if result["status"] == "PARTIAL"
        ],
        "missing_checks": [
            result["check_id"] for result in check_results if result["status"] == "MISSING"
        ],
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_action": (
            "prepare a separate advisory v2.0 hygiene alignment plan before any "
            "module, rune, projection, or schema mutation; keep all authority denied"
        ),
        "safe_to_auto_continue": False,
        "safe_to_prepare_patch": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "blocked_actions": [
            "V2_MODULE_IMPLEMENTATION",
            "RUNE_REGISTRATION",
            "CANON_SPINE_MUTATION",
            "PROJECTION_SURFACE_MUTATION",
            "OUTPUT_SCHEMA_ENFORCEMENT_ACTIVATION",
            "NOTION_WRITEBACK",
            "GITHUB_WRITEBACK",
            "AUTO_CONTINUATION",
            "EXECUTION",
        ],
        "authority_locks": _authority_locks(),
    }
    return {**base, "audit_hash": canonical_hash(base)}


def write_v2_hygiene_loop_awareness_audit(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def render_v2_hygiene_loop_awareness_audit_markdown(packet: dict[str, Any]) -> list[str]:
    lines = [
        "# v2.0 Hygiene Loop-Awareness Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- audit_status: {packet['audit_status']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- safe_to_prepare_patch: {packet['safe_to_prepare_patch']}",
        "",
        "## Check Results",
    ]
    for result in packet["check_results"]:
        lines.append(
            "- "
            f"{result['check_id']}: {result['status']} "
            f"({result['observed_term_count']}/{result['required_term_count']} terms)"
        )
        if result["missing_terms"]:
            lines.append(f"  missing: {', '.join(result['missing_terms'])}")
    lines.extend(["", "## Authority"])
    lines.append("- advisory_only: True")
    lines.append("- valid_for_execution: False")
    lines.append("- notion_writeback_allowed: False")
    lines.append("- github_writeback_allowed: False")
    return lines


def write_v2_hygiene_loop_awareness_audit_markdown(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_v2_hygiene_loop_awareness_audit_markdown(packet)) + "\n",
        encoding="utf-8",
    )
