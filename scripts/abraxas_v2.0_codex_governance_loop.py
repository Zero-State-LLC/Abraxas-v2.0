from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canonical.json import canonical_hash, write_canonical_json  # noqa: E402


class PhaseId(StrEnum):
    PHASE_0_EVIDENCE_BASELINE = "PHASE_0_EVIDENCE_BASELINE"
    PHASE_1_CONTRACTS_CODEGEN_SCHEMAS = "PHASE_1_CONTRACTS_CODEGEN_SCHEMAS"
    PHASE_2_CORE_CODEGEN_HARNESS = "PHASE_2_CORE_CODEGEN_HARNESS"
    PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY = (
        "PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY"
    )
    PHASE_4_META_GATE_OPERATOR_PROMOTION = "PHASE_4_META_GATE_OPERATOR_PROMOTION"
    PHASE_5_NOTION_RECONCILIATION_DRYRUN = "PHASE_5_NOTION_RECONCILIATION_DRYRUN"
    PHASE_6_POST_MERGE_RECONCILIATION = "PHASE_6_POST_MERGE_RECONCILIATION"
    PHASE_7_SHADOW_RUNTIME_ACTIVATION_PREP = (
        "PHASE_7_SHADOW_RUNTIME_ACTIVATION_PREP"
    )
    PHASE_8_GLOBAL_INGEST_WIRING_STUB = "PHASE_8_GLOBAL_INGEST_WIRING_STUB"
    PHASE_9_NOTION_PROJECTION_DRYRUN = "PHASE_9_NOTION_PROJECTION_DRYRUN"


PHASE_SEQUENCE: tuple[PhaseId, ...] = tuple(PhaseId)

EVIDENCE_PATHS: tuple[str, ...] = (
    "docs/workflows/cli-operator-layer.md",
    "AGENTS.md",
    "README.md",
    "ARCHITECTURE.md",
    "GOVERNANCE_V3.md",
    "PLANS.md",
    "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json",
    "out/audit/abx_codegen_intelligence_spine_completion_receipt_001.latest.json",
    "contracts/codegen/models.py",
    "core/codegen/builder.py",
    "core/codegen/runner.py",
    "core/codegen/shadow_replay_harness.py",
    "core/codegen/meta_gate.py",
    "core/codegen/notion_reconciliation.py",
)

CODEGEN_COMPLETION_RECEIPT = (
    "out/audit/abx_codegen_intelligence_spine_completion_receipt_001.latest.json"
)

REQUIRED_RECEIPT_FIELDS: tuple[str, ...] = (
    "artifact_type",
    "receipt_id",
    "receipt_status",
    "phase",
    "timestamp",
    "authority_locks",
    "lane_signals",
    "evidence",
    "prompt",
    "operator_attestation",
    "validation",
    "residual_risks",
    "recommended_next",
    "provenance",
    "canonical_hash",
)

AUTHORITY_LOCKS: dict[str, bool] = {
    "advisory_only": True,
    "canon_mutation": False,
    "runtime_mutation": False,
    "execution_authority": False,
    "code_generation": False,
    "code_mutation": False,
    "file_writeback": False,
    "github_writeback": False,
    "notion_writeback": False,
    "queue_mutation": False,
    "scheduler_mutation": False,
    "auto_approval": False,
    "production_activation": False,
}

RESIDUAL_RISKS: tuple[str, ...] = (
    "Operator must review and attest each phase before advancing.",
    "Codegen spine remains advisory until a separate operator chain is sealed.",
    "No Notion, GitHub, runtime, scheduler, queue, or canon mutation is granted.",
    "Full repo fast CI may retain unrelated Windows/path/encoding baselines.",
)

VALIDATION_COMMANDS: tuple[str, ...] = (
    "python -m pyright scripts/abraxas_v2.0_codex_governance_loop.py",
    "python -m ruff check scripts/abraxas_v2.0_codex_governance_loop.py",
    (
        "python scripts/abraxas_v2.0_codex_governance_loop.py "
        "--start-phase PHASE_6_POST_MERGE_RECONCILIATION"
    ),
    "python scripts/run_fast_ci.py",
)

NEXT_RECOMMENDED_LANES: tuple[str, ...] = (
    "continuity_reconciliation",
    "runtime_shadow_activation_prep",
    "global_ingest_wiring_stub",
    "notion_projection_dryrun",
    "aal_hollersports_cross_pollination_stubs",
    "v2_1_roadmap_selector",
    "p88_stabilization_advisory",
    "phase10_sovereign_expansion",
    "phase10_self_healing_hooks",
    "holler_pipeline_v2.1",
)


@dataclass(frozen=True, slots=True)
class PhaseSpec:
    phase: PhaseId
    task: str
    output: str
    validation: str
    recommended_next: str
    receipt_status: str


PHASE_SPECS: dict[PhaseId, PhaseSpec] = {
    PhaseId.PHASE_0_EVIDENCE_BASELINE: PhaseSpec(
        PhaseId.PHASE_0_EVIDENCE_BASELINE,
        "Inventory the historical Codegen Spine evidence baseline.",
        "A baseline advisory receipt plus compact evidence inventory.",
        "Confirm evidence paths resolve and authority locks remain false.",
        "Advance to PHASE_1 only after operator attestation.",
        "ABX_CODEX_GOVERNANCE_LOOP_RECEIPT_EMITTED_ADVISORY_ONLY",
    ),
    PhaseId.PHASE_1_CONTRACTS_CODEGEN_SCHEMAS: PhaseSpec(
        PhaseId.PHASE_1_CONTRACTS_CODEGEN_SCHEMAS,
        "Prepare future contracts/codegen schema work.",
        "A ready-to-paste Codex prompt for schema-only implementation.",
        "Future schema work must deny runtime and auto-approval.",
        "Advance to PHASE_2 after schema prompt review.",
        "ABX_CODEX_GOVERNANCE_LOOP_RECEIPT_EMITTED_ADVISORY_ONLY",
    ),
    PhaseId.PHASE_2_CORE_CODEGEN_HARNESS: PhaseSpec(
        PhaseId.PHASE_2_CORE_CODEGEN_HARNESS,
        "Prepare future core/codegen builder, runner, and replay harness work.",
        "A ready-to-paste Codex prompt for shadow-replay harness work.",
        "Future harness work must not execute generated code.",
        "Advance to PHASE_3 after harness prompt review.",
        "ABX_CODEX_GOVERNANCE_LOOP_RECEIPT_EMITTED_ADVISORY_ONLY",
    ),
    PhaseId.PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY: PhaseSpec(
        PhaseId.PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY,
        "Prepare deterministic fixture validation and replay-only checks.",
        "A ready-to-paste Codex prompt for fixture validation.",
        "Future replay must validate structural JSON and denials.",
        "Advance to PHASE_4 after fixture plan review.",
        "ABX_CODEX_GOVERNANCE_LOOP_RECEIPT_EMITTED_ADVISORY_ONLY",
    ),
    PhaseId.PHASE_4_META_GATE_OPERATOR_PROMOTION: PhaseSpec(
        PhaseId.PHASE_4_META_GATE_OPERATOR_PROMOTION,
        "Prepare advisory meta-gate operator promotion review.",
        "A ready-to-paste Codex prompt for meta-gate review.",
        "Meta-gate output must preserve ADVISORY_ONLY.",
        "Advance to PHASE_5 after operator promotion review.",
        "ABX_CODEX_GOVERNANCE_LOOP_RECEIPT_EMITTED_ADVISORY_ONLY",
    ),
    PhaseId.PHASE_5_NOTION_RECONCILIATION_DRYRUN: PhaseSpec(
        PhaseId.PHASE_5_NOTION_RECONCILIATION_DRYRUN,
        "Prepare a Notion reconciliation dry-run prompt.",
        "A dry-run reconciliation prompt and receipt.",
        "Dry-run text must not claim live Notion writeback.",
        "Hold for operator review; no auto-continuation.",
        "ABX_CODEX_GOVERNANCE_LOOP_RECEIPT_EMITTED_ADVISORY_ONLY",
    ),
    PhaseId.PHASE_6_POST_MERGE_RECONCILIATION: PhaseSpec(
        PhaseId.PHASE_6_POST_MERGE_RECONCILIATION,
        (
            "Reconcile post-merge Codegen Spine state, update status/plans, "
            "emit completion receipt, and compute continuity signals."
        ),
        "README/PLANS routing, completion receipt, and phase receipt.",
        "Confirm 20/20 observed paths and all authority locks false.",
        "Advance to PHASE_7 shadow runtime prep after review.",
        "ABX_PHASE_6_POST_MERGE_RECONCILIATION_READY",
    ),
    PhaseId.PHASE_7_SHADOW_RUNTIME_ACTIVATION_PREP: PhaseSpec(
        PhaseId.PHASE_7_SHADOW_RUNTIME_ACTIVATION_PREP,
        (
            "Prepare advisory shadow runtime activation surfaces that remain "
            "valid_for_execution=false and fixture/replay-only."
        ),
        "Shadow activation prep prompt and oracle signal intake hooks.",
        "Confirm no runtime execution, scheduler, or queue mutation.",
        "Advance to PHASE_8 global ingest wiring stub.",
        "ABX_PHASE_7_SHADOW_RUNTIME_ACTIVATION_PREP_READY",
    ),
    PhaseId.PHASE_8_GLOBAL_INGEST_WIRING_STUB: PhaseSpec(
        PhaseId.PHASE_8_GLOBAL_INGEST_WIRING_STUB,
        (
            "Prepare connector stubs between Codegen surfaces, "
            "ABX-GLOBAL-INGEST, and oracle intake."
        ),
        "Global ingest wiring stub plan and governance-loop receipt.",
        "Confirm connectors are static planning records only.",
        "Advance to PHASE_9 Notion projection dry run.",
        "ABX_PHASE_8_GLOBAL_INGEST_WIRING_STUB_READY",
    ),
    PhaseId.PHASE_9_NOTION_PROJECTION_DRYRUN: PhaseSpec(
        PhaseId.PHASE_9_NOTION_PROJECTION_DRYRUN,
        (
            "Prepare safe Notion projection templates and consolidate "
            "operator-selectable PHASE_10+ forward paths. "
            "v2.1 scripts available (advisory): p88_stabilization_advisory, "
            "phase10_sovereign_expansion + self_healing_hooks, holler_pipeline_v2.1."
        ),
        "Notion projection + v2.1 forward paths. New scripts in lanes.",
        "No writeback/execution. New scripts advisory receipts only.",
        "Review stabilized v2.1 scripts as PHASE_10+ forward paths.",
        "ABX_PHASE_9_NOTION_PROJECTION_DRYRUN_READY",
    ),
}


def _utc_timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _sha256_text(path: Path) -> str:
    try:
        content = path.read_bytes()
    except OSError:
        return "NOT_COMPUTABLE"
    return hashlib.sha256(content).hexdigest()


def _evidence_records(repo_root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": rel_path,
            "observed": (repo_root / rel_path).exists(),
            "source_hash": _sha256_text(repo_root / rel_path),
        }
        for rel_path in EVIDENCE_PATHS
    ]


def _gap_summary(repo_root: Path) -> dict[str, Any]:
    gap_packet = _read_json(
        repo_root
        / "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json"
    )
    completion = _read_json(repo_root / CODEGEN_COMPLETION_RECEIPT)
    return {
        "historical_gap_plan_status": gap_packet.get(
            "plan_status", "NOT_COMPUTABLE"
        ),
        "historical_target_surface_status": gap_packet.get(
            "target_surface_status", "NOT_COMPUTABLE"
        ),
        "spine_status": completion.get(
            "spine_status", "ABX_CODEGEN_INTELLIGENCE_SPINE_NOT_COMPUTABLE"
        ),
        "observed_path_count": completion.get("observed_path_count", 0),
        "required_path_count": completion.get("required_path_count", 0),
        "completion_canonical_hash": completion.get(
            "canonical_hash", "NOT_COMPUTABLE"
        ),
        "valid_for_execution": completion.get("valid_for_execution", False),
        "valid_for_runtime_activation": completion.get(
            "valid_for_runtime_activation", False
        ),
        "valid_for_canon_promotion": completion.get(
            "valid_for_canon_promotion", False
        ),
    }


def _phase_slug(phase: PhaseId) -> str:
    return phase.value.lower()


def _receipt_path(repo_root: Path, phase: PhaseId) -> Path:
    return (
        repo_root
        / "out"
        / "audit"
        / f"abx_codex_governance_loop_{_phase_slug(phase)}.latest.json"
    )


def _lane_signals(phase: PhaseId) -> dict[str, Any]:
    return {
        "phase": phase.value,
        "lane": "ADVISORY_STACK_HELD_FOR_OPERATOR",
        "downstream": "NOT_COMPUTABLE",
        "advisory_only": True,
        "projection_only": True,
        "shadow_replay_emphasis": True,
        "safe_to_auto_continue": False,
        "valid_for_execution": False,
        "recommended_lanes": list(NEXT_RECOMMENDED_LANES),
    }


def _boundary_lines() -> list[str]:
    return [
        "Advisory-only, governance-first, post-spine-completion layer.",
        "All authority locks remain explicitly false.",
        "ADVISORY_STACK_HELD_FOR_OPERATOR until operator gate.",
        "CANON_MUTATION=false; RUNTIME_MUTATION=false; EXECUTION_AUTHORITY=false.",
        "GITHUB_WRITEBACK=false; NOTION_WRITEBACK=false; FILE_WRITEBACK=false.",
    ]


def _prompt_sections(phase: PhaseId, repo_root: Path) -> dict[str, list[str]]:
    spec = PHASE_SPECS[phase]
    gap = _gap_summary(repo_root)
    evidence_lines = [
        (
            f"- {record['path']}: observed={record['observed']} "
            f"hash={record['source_hash']}"
        )
        for record in _evidence_records(repo_root)
    ]
    evidence_lines.extend(
        [
            f"- spine_status: {gap['spine_status']}",
            (
                "- path_coverage: "
                f"{gap['observed_path_count']}/{gap['required_path_count']}"
            ),
            f"- completion_canonical_hash: {gap['completion_canonical_hash']}",
            f"- valid_for_execution: {gap['valid_for_execution']}",
            (
                "- valid_for_runtime_activation: "
                f"{gap['valid_for_runtime_activation']}"
            ),
            f"- valid_for_canon_promotion: {gap['valid_for_canon_promotion']}",
        ]
    )
    return {
        "BOUNDARY": [f"- {line}" for line in _boundary_lines()],
        "EVIDENCE PACKET": evidence_lines,
        "TASK": [f"- {spec.task}"],
        "OUTPUT": [f"- {spec.output}"],
        "VALIDATION": [
            f"- {spec.validation}",
            *[f"- {command}" for command in VALIDATION_COMMANDS],
        ],
        "RESIDUAL RISKS": [f"- {risk}" for risk in RESIDUAL_RISKS],
        "RECOMMENDED NEXT ADVISORY ACTION": [f"- {spec.recommended_next}"],
    }


def _render_prompt(phase: PhaseId, repo_root: Path) -> str:
    sections = _prompt_sections(phase, repo_root)
    lines: list[str] = []
    for header in (
        "BOUNDARY",
        "EVIDENCE PACKET",
        "TASK",
        "OUTPUT",
        "VALIDATION",
        "RESIDUAL RISKS",
        "RECOMMENDED NEXT ADVISORY ACTION",
    ):
        lines.append(header)
        lines.extend(sections[header])
        lines.append("")
    return "\n".join(lines).rstrip()


def _attestation() -> dict[str, str] | None:
    gate = input('Operator gate: type exact "yes" to emit receipt: ').strip()
    if gate != "yes":
        print("Gate declined; no receipt written.", flush=True)
        return None
    note = input("Operator attestation note: ").strip()
    if not note:
        print("Missing attestation note; no receipt written.", flush=True)
        return None
    return {"gate": gate, "note": note}


def _build_receipt(
    *,
    phase: PhaseId,
    repo_root: Path,
    timestamp: str,
    prompt: str,
    operator_attestation: Mapping[str, str],
) -> dict[str, Any]:
    spec = PHASE_SPECS[phase]
    base: dict[str, Any] = {
        "artifact_type": "AbxCodexGovernanceLoopReceipt.v2",
        "receipt_id": f"ABX_CODEX_GOVERNANCE_LOOP_{phase.value}",
        "receipt_status": spec.receipt_status,
        "phase": phase.value,
        "timestamp": timestamp,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "lane_signals": _lane_signals(phase),
        "evidence": {
            "paths": _evidence_records(repo_root),
            "gap_summary": _gap_summary(repo_root),
        },
        "prompt": prompt,
        "operator_attestation": dict(operator_attestation),
        "validation": {
            "commands": list(VALIDATION_COMMANDS),
            "structural_json_validation": "PASSED_BEFORE_WRITE",
            "shadow_replay_emphasis": True,
        },
        "residual_risks": list(RESIDUAL_RISKS),
        "recommended_next": spec.recommended_next,
        "provenance": {
            "script": "scripts/abraxas_v2.0_codex_governance_loop.py",
            "repo_root": str(repo_root),
            "receipt_path": str(_receipt_path(repo_root, phase).relative_to(repo_root)),
            "canonical_hash_algorithm": (
                "sha256(canonical_json_without_canonical_hash)"
            ),
            "source_completion_receipt": CODEGEN_COMPLETION_RECEIPT,
            "phase_6_plus_extension": True,
        },
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _validate_receipt(receipt: Mapping[str, Any]) -> None:
    missing = [field for field in REQUIRED_RECEIPT_FIELDS if field not in receipt]
    if missing:
        raise ValueError(f"receipt missing required fields: {', '.join(missing)}")

    authority_locks = receipt.get("authority_locks")
    if not isinstance(authority_locks, dict):
        raise TypeError("receipt authority_locks must be an object")
    for lock_name, lock_value in authority_locks.items():
        if lock_name == "advisory_only":
            if lock_value is not True:
                raise ValueError("advisory_only must remain true")
            continue
        if lock_value is not False:
            raise ValueError(f"authority lock must remain false: {lock_name}")

    expected_hash_payload = dict(receipt)
    observed_hash = expected_hash_payload.pop("canonical_hash")
    if observed_hash != canonical_hash(expected_hash_payload):
        raise ValueError("receipt canonical_hash mismatch")


def _write_receipt(receipt: Mapping[str, Any], path: Path) -> None:
    _validate_receipt(receipt)
    write_canonical_json(path, receipt)


def _phase_window(start_phase: PhaseId, max_iterations: int) -> tuple[PhaseId, ...]:
    start_index = PHASE_SEQUENCE.index(start_phase)
    end_index = min(start_index + max_iterations, len(PHASE_SEQUENCE))
    return PHASE_SEQUENCE[start_index:end_index]


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the advisory ABX Codex governance loop."
    )
    parser.add_argument(
        "--start-phase",
        choices=[phase.value for phase in PHASE_SEQUENCE],
        default=PhaseId.PHASE_0_EVIDENCE_BASELINE.value,
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=1,
        help="Maximum phases to process; each phase still requires attestation.",
    )
    parser.add_argument(
        "--timestamp",
        default=None,
        help="Optional deterministic ISO-8601 timestamp for replayable receipts.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.max_iterations < 1:
        print("--max-iterations must be >= 1", file=sys.stderr, flush=True)
        return 2

    repo_root = ROOT
    start_phase = PhaseId(args.start_phase)
    timestamp = str(args.timestamp) if args.timestamp is not None else _utc_timestamp()

    for phase in _phase_window(start_phase, args.max_iterations):
        prompt = _render_prompt(phase, repo_root)
        print("\n" + "=" * 80, flush=True)
        print(f"ABX CODEX GOVERNANCE LOOP :: {phase.value}", flush=True)
        print("=" * 80, flush=True)
        print(prompt, flush=True)
        print("=" * 80, flush=True)

        attestation = _attestation()
        if attestation is None:
            return 1

        receipt = _build_receipt(
            phase=phase,
            repo_root=repo_root,
            timestamp=timestamp,
            prompt=prompt,
            operator_attestation=attestation,
        )
        target = _receipt_path(repo_root, phase)
        _write_receipt(receipt, target)
        print(f"Receipt emitted: {target.relative_to(repo_root)}", flush=True)
        print(f"canonical_hash: {receipt['canonical_hash']}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
