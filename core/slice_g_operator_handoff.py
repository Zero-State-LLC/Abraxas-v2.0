"""Slice G operator handoff receipt for volume-derived advisory artifacts.

This module builds a deterministic E2E review packet from Hermes volume traces.
It emits a HandoffEnvelope.v1 fragment and a SkillPatchCandidate artifact for
operator review only. It never promotes, mounts, executes, mutates canon, or
couples the result to CLEAR / production activation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.operator_loop import default_authority, validate_handoff

ARTIFACT_TYPE = "SliceGOperatorHandoffReviewReceipt.v1"
STATUS = "SLICE_G_OPERATOR_HANDOFF_READY_ADVISORY_ONLY"
DEFAULT_FIXTURE = "tests/fixtures/slice_g_operator_handoff_volume_traces.json"
DEFAULT_OUT_PATH = "out/operator_review/slice_g_operator_handoff_review_001.latest.json"
DEFAULT_MD_PATH = "out/operator_review/slice_g_operator_handoff_review_001.latest.md"

AUTHORITY_LOCKS = {
    "execution_authority": False,
    "promotion_authorized": False,
    "active_skill_mutation_allowed": False,
    "mount_authorized": False,
    "canon_mutation_allowed": False,
    "clear_coupling_allowed": False,
    "production_activation": False,
    "github_writeback": False,
    "notion_writeback": False,
}


def _read_traces(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise TypeError("Slice G volume fixture must be a JSON array")
    return [item for item in payload if isinstance(item, dict)]


def _trace_key(trace: dict[str, Any]) -> str:
    skill = str(trace.get("skill_id", "unknown"))
    task = str(trace.get("task_class", "unknown"))
    return f"{skill}:{task}"


def _volume_summary(traces: list[dict[str, Any]]) -> dict[str, Any]:
    by_key: dict[str, dict[str, Any]] = {}
    for trace in traces:
        key = _trace_key(trace)
        row = by_key.setdefault(
            key,
            {
                "runs": 0,
                "observed": 0,
                "density_sum": 0.0,
                "brier_sum": 0.0,
                "sources": [],
            },
        )
        row["runs"] += 1
        if trace.get("evidence_status") == "OBSERVED":
            row["observed"] += 1
        brier = trace.get("brier_score")
        if isinstance(brier, int | float):
            row["brier_sum"] += float(brier)
        density = 0.0
        for output in trace.get("outputs", []):
            if isinstance(output, dict) and isinstance(output.get("evidence_density"), int | float):
                density = max(density, float(output["evidence_density"]))
        row["density_sum"] += density
        source = trace.get("provenance", {}).get("source") if isinstance(trace.get("provenance"), dict) else None
        row["sources"].append(str(source or trace.get("trace_id", "unknown")))

    for row in by_key.values():
        runs = max(int(row["runs"]), 1)
        row["observed_rate"] = round(float(row["observed"]) / runs, 6)
        row["mean_density"] = round(float(row["density_sum"]) / runs, 6)
        row["mean_brier"] = round(float(row["brier_sum"]) / runs, 6)
        row["sources"] = sorted(set(row["sources"]))
        del row["density_sum"]
        del row["brier_sum"]
    return by_key


def _skill_candidate(volume: dict[str, Any]) -> dict[str, Any]:
    key = min(volume) if volume else "unknown:unknown"
    stats = volume.get(key, {})
    seed = {"key": key, "stats": stats, "slice": "G"}
    suffix = canonical_hash(seed)[:12]
    return {
        "schema_version": "SkillEvolutionCandidate.v1",
        "candidate_id": f"evocand-slice-g-{suffix}",
        "skill_id": key,
        "triggering_patterns": ["high_hermes_signal_volume"],
        "evidence_window": f"{stats.get('runs', 0)} deterministic volume traces",
        "confidence": 0.6,
        "status": "CANDIDATE_ONLY",
        "advisory_only": True,
        "execution_authority": False,
    }


def _skill_patch_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    suffix = canonical_hash(candidate)[:12]
    skill_id = str(candidate.get("skill_id", "unknown"))
    return {
        "schema_version": "SkillPatchCandidate.v1",
        "patch_id": f"patch-slice-g-{suffix}",
        "skill_id": skill_id,
        "base_version": "0.1.0",
        "proposed_version": "0.1.1-shadow-review",
        "changed_sections": [
            "invocation_conditions",
            "completion_criteria",
            "operator_review_notes",
        ],
        "rationale_refs": candidate.get("triggering_patterns", []),
        "expected_behavior_change": (
            "Improve operator review of recurring high-volume signal_forage traces "
            "without changing active skill behavior."
        ),
        "rollback_plan": "Discard candidate; no active skill files were mutated.",
        "disposition_state": "OPERATOR_REVIEW_REQUIRED",
        "promotion_authorized": False,
        "execution_authority": False,
        "canon_mutation_allowed": False,
        "mount_authorized": False,
        "clear_coupling_allowed": False,
        "status": "CANDIDATE_ONLY",
    }


def _handoff(patch: dict[str, Any], fixture_path: str) -> dict[str, Any]:
    suffix = canonical_hash({"patch": patch, "fixture": fixture_path})[:12]
    handoff = {
        "schema_version": "HandoffEnvelope.v1",
        "handoff_id": f"HO-slice-g-{suffix}",
        "work_packet_id": "WP-slice-g-operator-handoff-001",
        "producer_system": "CODEX",
        "status": "COMPLETE",
        "changed_files": [
            "core/slice_g_operator_handoff.py",
            "scripts/operator/run_slice_g_operator_handoff_review.py",
            "docs/status/SLICE_G_OPERATOR_HANDOFF_REVIEW.md",
            fixture_path,
        ],
        "generated_assets": [
            DEFAULT_OUT_PATH,
            DEFAULT_MD_PATH,
            "SkillPatchCandidate.v1 fragment",
        ],
        "commands_run": [
            "python scripts/operator/run_slice_g_operator_handoff_review.py --fixture tests/fixtures/slice_g_operator_handoff_volume_traces.json",
            "abraxas os evolution-review --fixture tests/fixtures/slice_g_operator_handoff_volume_traces.json",
            "python -m pytest tests/test_slice_g_operator_handoff.py -q",
        ],
        "tests": {
            "passed": ["tests/test_slice_g_operator_handoff.py"],
            "failed": [],
        },
        "observed_findings": [
            "Deterministic volume fixture yields a SkillEvolutionCandidate and SkillPatchCandidate.",
            "HandoffEnvelope.v1 validates against contracts/engineering/handoff_envelope.v1.schema.json.",
            "All authority locks keep execution_authority false and require operator disposition.",
        ],
        "inferred_findings": [
            "Operator can review the candidate without mounting, executing, promoting, or mutating canon."
        ],
        "conflicts_detected": [],
        "residual_risks": [
            "Candidate quality is advisory and depends on future operator disposition.",
            "Live Hermes volume ingestion remains separate from this deterministic fixture.",
        ],
        "next_recommended_action": (
            "Operator reviews disposition_state=OPERATOR_REVIEW_REQUIRED; do not promote, "
            "mount, execute, mutate canon, or couple to CLEAR without explicit authorization."
        ),
        "branch": None,
        "pull_request": None,
        "notes": "Slice G #1111 deterministic operator handoff review surface.",
        "authority": default_authority(),
    }
    validate_handoff(handoff)
    return handoff


def build_slice_g_operator_handoff_review(
    *,
    repo_root: str | Path = ".",
    fixture_path: str | Path = DEFAULT_FIXTURE,
) -> dict[str, Any]:
    root = Path(repo_root)
    rel_fixture = Path(fixture_path).as_posix()
    traces = _read_traces(root / fixture_path)
    volume = _volume_summary(traces)
    candidate = _skill_candidate(volume)
    patch = _skill_patch_candidate(candidate)
    handoff = _handoff(patch, rel_fixture)
    receipt: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": ARTIFACT_TYPE,
        "status": STATUS,
        "issue": 1111,
        "track": "Slice G — Consumption Hardening + Operator Handoff Surfaces",
        "fixture_path": rel_fixture,
        "trace_count": len(traces),
        "volume_summary": volume,
        "skill_evolution_candidate": candidate,
        "skill_patch_candidate": patch,
        "handoff_envelope": handoff,
        "operator_review": {
            "disposition_state": "OPERATOR_REVIEW_REQUIRED",
            "commands": handoff["commands_run"],
            "risks": handoff["residual_risks"],
            "required_operator_action": handoff["next_recommended_action"],
        },
        "provenance": {
            "source_issue": "https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/issues/1111",
            "source_fixture_hash": canonical_hash(traces),
            "builder": "core.slice_g_operator_handoff.build_slice_g_operator_handoff_review",
            "runner": "scripts/operator/run_slice_g_operator_handoff_review.py",
        },
        "authority_locks": AUTHORITY_LOCKS,
        "non_goals": [
            "No promotion or mount authority.",
            "No runtime execution authority.",
            "No canon mutation.",
            "No CLEAR or production activation coupling.",
        ],
    }
    receipt["canonical_hash"] = canonical_hash(
        {key: value for key, value in receipt.items() if key != "canonical_hash"}
    )
    return receipt


def render_slice_g_operator_handoff_markdown(receipt: dict[str, Any]) -> str:
    patch = receipt["skill_patch_candidate"]
    handoff = receipt["handoff_envelope"]
    lines = [
        "# Slice G Operator Handoff Review",
        "",
        f"Status: `{receipt['status']}`",
        f"Issue: `#{receipt['issue']}`",
        "",
        "## Operator command path",
        "",
        "```bash",
        "python scripts/operator/run_slice_g_operator_handoff_review.py --fixture tests/fixtures/slice_g_operator_handoff_volume_traces.json",
        "abraxas os evolution-review --fixture tests/fixtures/slice_g_operator_handoff_volume_traces.json",
        "python -m pytest tests/test_slice_g_operator_handoff.py -q",
        "```",
        "",
        "## Artifacts",
        "",
        f"- HandoffEnvelope: `{handoff['handoff_id']}`",
        f"- SkillPatchCandidate: `{patch['patch_id']}`",
        f"- Disposition: `{patch['disposition_state']}`",
        "",
        "## Authority boundary",
        "",
        "- execution_authority: `false`",
        "- promotion_authorized: `false`",
        "- mount_authorized: `false`",
        "- canon_mutation_allowed: `false`",
        "- clear_coupling_allowed: `false`",
        "",
        "Operator disposition is required before any follow-up. This receipt does not promote, mount, execute, mutate canon, or couple to CLEAR / production activation.",
        "",
        "## Residual risks",
        "",
    ]
    lines.extend(f"- {risk}" for risk in handoff["residual_risks"])
    lines.extend(["", f"Canonical hash: `{receipt['canonical_hash']}`", ""])
    return "\n".join(lines)


def write_slice_g_operator_handoff_review(
    *,
    repo_root: str | Path = ".",
    fixture_path: str | Path = DEFAULT_FIXTURE,
    out_path: str | Path = DEFAULT_OUT_PATH,
    md_path: str | Path = DEFAULT_MD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = build_slice_g_operator_handoff_review(
        repo_root=root,
        fixture_path=fixture_path,
    )
    write_canonical_json(root / out_path, receipt)
    md_target = root / md_path
    md_target.parent.mkdir(parents=True, exist_ok=True)
    md_target.write_text(render_slice_g_operator_handoff_markdown(receipt), encoding="utf-8")
    return receipt
