from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityHistoricalRecoveryAudit.v1"
P102F_SOURCE_PATH = (
    "out/temporal_continuity_operator_authorization_record_decision_reconciliation_receipt/latest.json"
)
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
BADGES_PATH = "docs/status/badges.json"
NOTION_DIFF_PATH = "docs/audits/ABRAXAS_REPO_NOTION_DIFF_001.md"
TARGET_LANES: tuple[str, ...] = ("P103", "P104", "P105", "P106", "P107")
TARGET_SEARCH_TERMS: tuple[str, ...] = (
    "P103",
    "P104",
    "P105",
    "P106",
    "P107",
    "approval record",
    "seal finalization",
    "authorization record",
    "decision record",
    "segment closed",
    "record ready",
)
EXPECTED_P103_TEMPORAL_ROUTE = (
    "P103_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_REVIEW"
)

_DENIED_AUTHORITY: tuple[str, ...] = (
    "authorization_authority",
    "authorization_record_creation_authority",
    "canon_promotion",
    "execution_authority",
    "forecast_influence",
    "production_activation",
    "record_creation_authority",
    "runtime_authority",
    "scheduler_mutation",
    "token_minting_authority",
)

_RESEARCH_LANE_EXPECTATIONS: dict[str, dict[str, str]] = {
    "P103": {
        "core": "core/research_shadow_replay_audit.py",
        "script": "scripts/run_research_shadow_replay_audit.py",
        "schema": "contracts/canon/research_shadow_replay_audit.v1.schema.json",
        "test": "tests/test_research_shadow_replay_audit.py",
        "artifact": "out/research_shadow_replay_audit/latest.json",
        "semantic_branch": "research_shadow_replay_audit",
    },
    "P104": {
        "core": "core/research_boundary_decay_analysis.py",
        "script": "scripts/run_research_boundary_decay_analysis.py",
        "schema": "contracts/canon/research_boundary_decay_analysis.v1.schema.json",
        "test": "tests/test_research_boundary_decay_analysis.py",
        "artifact": "out/research_boundary_decay_analysis/latest.json",
        "semantic_branch": "research_boundary_decay_analysis",
    },
    "P105": {
        "core": "core/research_promotion_blocker_ledger.py",
        "script": "scripts/run_research_promotion_blocker_ledger.py",
        "schema": "contracts/canon/research_promotion_blocker_ledger.v1.schema.json",
        "test": "tests/test_research_promotion_blocker_ledger.py",
        "artifact": "out/research_promotion_blocker_ledger/latest.json",
        "semantic_branch": "research_promotion_blocker_ledger",
    },
    "P106": {
        "core": "core/research_canary_eligibility_dossier.py",
        "script": "scripts/run_research_canary_eligibility_dossier.py",
        "schema": "contracts/canon/research_canary_eligibility_dossier.v1.schema.json",
        "test": "tests/test_research_canary_eligibility_dossier.py",
        "artifact": "out/research_canary_eligibility_dossier/latest.json",
        "semantic_branch": "research_canary_eligibility_dossier",
    },
    "P107": {
        "core": "core/research_canary_review_packet.py",
        "script": "scripts/run_research_canary_review_packet.py",
        "schema": "contracts/canon/research_canary_review_packet.v1.schema.json",
        "test": "tests/test_research_canary_review_packet.py",
        "artifact": "out/research_canary_review_packet/latest.json",
        "semantic_branch": "research_canary_review_packet",
    },
}

_TEMPORAL_OPERATOR_APPROVAL_BRANCH_FILES: tuple[str, ...] = (
    "core/temporal_continuity_operator_authorization_record_approval_plan.py",
    "core/temporal_continuity_operator_authorization_record_approval_dry_run.py",
    "core/temporal_continuity_operator_authorization_record_approval_validation_plan.py",
    "core/temporal_continuity_operator_authorization_record_approval_validation_dry_run.py",
    "core/temporal_continuity_operator_authorization_record_approval_record_plan.py",
    "core/temporal_continuity_operator_authorization_record_approval_record_dry_run.py",
    "core/temporal_continuity_operator_authorization_record_approval_record_validation_plan.py",
    "core/temporal_continuity_operator_authorization_record_approval_record_validation_dry_run.py",
    "core/temporal_continuity_operator_authorization_record_approval_record_seal_plan.py",
    "core/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run.py",
    "core/temporal_continuity_operator_authorization_record_approval_record_seal_review.py",
)


def _read_bytes(path: Path) -> bytes | None:
    if not path.exists():
        return None
    try:
        return path.read_bytes()
    except OSError:
        return None


def _read_json(root: Path, rel_path: str) -> dict[str, Any] | None:
    raw = _read_bytes(root / rel_path)
    if raw is None:
        return None
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _file_hash(root: Path, rel_path: str) -> str:
    raw = _read_bytes(root / rel_path)
    if raw is None:
        return "NOT_COMPUTABLE"
    return hashlib.sha256(raw).hexdigest()


def _git_lines(root: Path, args: list[str]) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return []
    return [line for line in completed.stdout.splitlines() if line]


def _tracked_files(root: Path) -> list[str]:
    git_files = _git_lines(root, ["ls-files"])
    if git_files:
        return sorted(git_files)
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    )


def _merge_history(root: Path) -> list[dict[str, str]]:
    lines = _git_lines(root, ["log", "--merges", "--format=%H%x09%s", "--max-count=120"])
    return [
        {"commit": line.split("\t", 1)[0], "subject": line.split("\t", 1)[1]}
        for line in lines
        if "\t" in line
    ]


def _history_hits(root: Path) -> list[dict[str, str]]:
    pattern = "P103|P104|P105|P106|P107|approval record|seal finalization|authorization record|decision record|segment closed|record ready"
    lines = _git_lines(
        root,
        [
            "log",
            "--all",
            "--regexp-ignore-case",
            "--extended-regexp",
            f"--grep={pattern}",
            "--format=%H%x09%s",
            "--max-count=200",
        ],
    )
    return [
        {"commit": line.split("\t", 1)[0], "subject": line.split("\t", 1)[1]}
        for line in lines
        if "\t" in line
    ]


def _classify_research_lanes(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for lane_id in TARGET_LANES:
        expected = _RESEARCH_LANE_EXPECTATIONS[lane_id]
        evidence_paths = [expected[key] for key in ("core", "script", "schema", "test", "artifact")]
        observed_paths = [path for path in evidence_paths if (root / path).exists()]
        all_present = len(observed_paths) == len(evidence_paths)
        findings.append(
            {
                "lane_id": lane_id,
                "branch": "research_canary_continuity",
                "semantic_branch": expected["semantic_branch"],
                "classification": "IMPLEMENTED" if all_present else "UNKNOWN",
                "merge_classification": "MERGED" if all_present else "UNKNOWN",
                "continuity_relation": "SUPERSEDED_FOR_TEMPORAL_OPERATOR_DECISION_PATH",
                "observed_paths": observed_paths,
                "missing_paths": [path for path in evidence_paths if path not in observed_paths],
            }
        )
    return findings


def _classify_temporal_target(root: Path, tracked: list[str]) -> dict[str, Any]:
    exact_hits = [path for path in tracked if EXPECTED_P103_TEMPORAL_ROUTE.lower() in path.lower()]
    exact_text_hits: list[str] = []
    for rel_path in tracked:
        if not rel_path.endswith((".md", ".py", ".json", ".yaml", ".yml", ".txt")):
            continue
        raw = _read_bytes(root / rel_path)
        if raw is None:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if EXPECTED_P103_TEMPORAL_ROUTE in text:
            exact_text_hits.append(rel_path)

    branch_paths = [path for path in _TEMPORAL_OPERATOR_APPROVAL_BRANCH_FILES if (root / path).exists()]
    return {
        "target_route": EXPECTED_P103_TEMPORAL_ROUTE,
        "exact_path_hits": sorted(exact_hits),
        "exact_text_hits": sorted(exact_text_hits),
        "classification": "NOT_COMPUTABLE" if not exact_hits and not exact_text_hits else "DOCUMENTATION_ONLY",
        "branch_evidence_classification": "SUPERSEDED" if branch_paths else "UNKNOWN",
        "branch_evidence_paths": branch_paths,
        "reason": (
            "No exact repo evidence authorizes the P103 temporal operator approval-record seal finalization review route; older operator authorization approval/seal planning surfaces exist below P103 and are superseded by the P102E/P102F operator-decision threshold."
        ),
    }


def _term_hits(tracked: list[str]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for term in TARGET_SEARCH_TERMS:
        lowered = term.lower().replace(" ", "_")
        path_hits = [path for path in tracked if lowered in path.lower() or term.lower() in path.lower()]
        hits.append({"term": term, "path_hits": sorted(path_hits)[:80], "hit_count": len(path_hits)})
    return hits


def build_temporal_continuity_historical_recovery_audit(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    tracked = _tracked_files(root)
    p102f = _read_json(root, P102F_SOURCE_PATH) or {}
    spine = _read_json(root, CONTINUITY_SPINE_PATH) or {}
    badges = _read_json(root, BADGES_PATH) or {}
    signals = badges.get("signals") if isinstance(badges.get("signals"), dict) else {}

    research_findings = _classify_research_lanes(root)
    temporal_target = _classify_temporal_target(root, tracked)
    merge_history = _merge_history(root)
    history_hits = _history_hits(root)

    p103_to_p107_ever_existed = all(
        finding["classification"] == "IMPLEMENTED" for finding in research_findings
    )
    p103_to_p107_temporal_operator_route_existed = bool(
        temporal_target["exact_path_hits"] or temporal_target["exact_text_hits"]
    )

    missing_transitions = [
        "operator_authorization_record_decision_evidence",
        EXPECTED_P103_TEMPORAL_ROUTE,
    ]

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "historical_recovery_audit_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "record_creation_authority": False,
        "token_minting_authority": False,
        "token_minting_allowed": False,
        "authorization_granted": False,
        "authorization_record_created": False,
        "valid_for_execution": False,
        "observed_current_highest_lane": str(spine.get("highest_lane", "NOT_COMPUTABLE")),
        "observed_current_handoff": str(p102f.get("handoff", "NOT_COMPUTABLE")),
        "observed_current_downstream": str(p102f.get("recommended_next_lane", "NOT_COMPUTABLE")),
        "governance_status": str(signals.get("governance_status", "NOT_COMPUTABLE")),
        "canon_status": str(signals.get("canon_status", "NOT_COMPUTABLE")),
        "source_p102f_path": P102F_SOURCE_PATH,
        "source_p102f_observed": bool((root / P102F_SOURCE_PATH).exists()),
        "source_p102f_hash": _file_hash(root, P102F_SOURCE_PATH),
        "source_continuity_spine_path": CONTINUITY_SPINE_PATH,
        "source_continuity_spine_hash": _file_hash(root, CONTINUITY_SPINE_PATH),
        "source_badges_path": BADGES_PATH,
        "source_badges_hash": _file_hash(root, BADGES_PATH),
        "source_notion_diff_path": NOTION_DIFF_PATH,
        "source_notion_diff_observed": bool((root / NOTION_DIFF_PATH).exists()),
        "source_notion_diff_hash": _file_hash(root, NOTION_DIFF_PATH),
        "target_lanes": list(TARGET_LANES),
        "observed_continuity_history": {
            "current_repo_lane": "P102F_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_DECISION_RECONCILIATION_RECEIPT",
            "current_handoff": "OPERATOR_AUTHORIZATION_RECORD_DECISION_REQUIRED",
            "current_downstream": "NOT_COMPUTABLE",
            "research_p103_to_p107_present": p103_to_p107_ever_existed,
            "temporal_operator_p103_to_p107_present": p103_to_p107_temporal_operator_route_existed,
        },
        "recovered_lane_lineage": research_findings,
        "temporal_operator_target_route_audit": temporal_target,
        "repo_notion_divergence_map": [
            {
                "divergence_id": "P103_TEMPORAL_OPERATOR_ROUTE_NOT_REPO_AUTHORIZED",
                "notion_or_prompt_expected": EXPECTED_P103_TEMPORAL_ROUTE,
                "repo_observed": "P102F blocks downstream routing as NOT_COMPUTABLE until explicit operator decision evidence exists.",
                "classification": "DOCUMENTATION_DRIFT_OR_EXTERNAL_NOTION_ONLY",
            },
            {
                "divergence_id": "P103_TO_P107_RESEARCH_BRANCH_NAME_COLLISION",
                "notion_or_prompt_expected": "P103-P107 temporal continuity operator authorization sequence",
                "repo_observed": "P103-P107 are implemented and merged as research-canary continuity lanes, not as temporal operator authorization-record finalization lanes.",
                "classification": "SUPERSEDED_CONTINUITY_BRANCH",
            },
        ],
        "missing_transitions": missing_transitions,
        "search_term_hits": _term_hits(tracked),
        "git_merge_history_hits": merge_history[:80],
        "git_keyword_history_hits": history_hits[:80],
        "historical_recovery_status": "HISTORICAL_RECOVERY_AUDIT_COMPLETE_WITH_BLOCKERS",
        "p103_to_p107_existence_answer": {
            "implemented_repo_history": p103_to_p107_ever_existed,
            "generated_but_unmerged_work": "NOT_COMPUTABLE_FROM_LOCAL_GIT_HISTORY",
            "simulated_planning_artifacts_only": False,
            "superseded_continuity_branches": True,
            "documentation_drift": not p103_to_p107_temporal_operator_route_existed,
        },
        "recommended_next_action": "KEEP_DOWNSTREAM_NOT_COMPUTABLE_AND_REQUEST_OPERATOR_DECISION_EVIDENCE_OR_HOLD",
        "recommended_next_lane": "NOT_COMPUTABLE",
        "authority_locks": {authority: False for authority in sorted(_DENIED_AUTHORITY)},
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }

    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_historical_recovery_audit(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
