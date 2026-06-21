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


PHASE_SEQUENCE: tuple[PhaseId, ...] = (
    PhaseId.PHASE_0_EVIDENCE_BASELINE,
    PhaseId.PHASE_1_CONTRACTS_CODEGEN_SCHEMAS,
    PhaseId.PHASE_2_CORE_CODEGEN_HARNESS,
    PhaseId.PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY,
    PhaseId.PHASE_4_META_GATE_OPERATOR_PROMOTION,
    PhaseId.PHASE_5_NOTION_RECONCILIATION_DRYRUN,
)

EVIDENCE_PATHS: tuple[str, ...] = (
    "docs/workflows/cli-operator-layer.md",
    "AGENTS.md",
    "README.md",
    "ARCHITECTURE.md",
    "GOVERNANCE_V3.md",
    "PLANS.md",
    "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json",
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
    "Codegen spine remains advisory until the full operator chain is sealed.",
    "contracts/codegen/ and core/codegen/ remain future-phase deliverables.",
    "No Notion, GitHub, runtime, scheduler, queue, or canon mutation is granted.",
)

VALIDATION_COMMANDS: tuple[str, ...] = (
    "python -m pyright scripts/abraxas_v2.0_codex_governance_loop.py",
    "python -m ruff check scripts/abraxas_v2.0_codex_governance_loop.py",
    (
        "python scripts/abraxas_v2.0_codex_governance_loop.py "
        "--start-phase PHASE_0_EVIDENCE_BASELINE"
    ),
    "python scripts/run_fast_ci.py",
)


@dataclass(frozen=True, slots=True)
class PhaseSpec:
    phase: PhaseId
    task: str
    output: str
    validation: str
    recommended_next: str


PHASE_SPECS: dict[PhaseId, PhaseSpec] = {
    PhaseId.PHASE_0_EVIDENCE_BASELINE: PhaseSpec(
        phase=PhaseId.PHASE_0_EVIDENCE_BASELINE,
        task=(
            "Inventory the Codegen Intelligence Spine evidence baseline, confirm "
            "the gap plan remains GAP_ANALYSIS_PLAN_READY / NOT_COMPUTABLE, and "
            "record missing contracts/codegen and core/codegen surfaces without "
            "creating them."
        ),
        output=(
            "A baseline advisory receipt plus a compact evidence inventory for "
            "the next operator-gated implementation phase."
        ),
        validation=(
            "Confirm evidence paths resolve, authority locks remain false, and "
            "the receipt canonical_hash matches the canonical payload."
        ),
        recommended_next=(
            "Advance to PHASE_1_CONTRACTS_CODEGEN_SCHEMAS only after operator "
            "attestation."
        ),
    ),
    PhaseId.PHASE_1_CONTRACTS_CODEGEN_SCHEMAS: PhaseSpec(
        phase=PhaseId.PHASE_1_CONTRACTS_CODEGEN_SCHEMAS,
        task=(
            "Prepare the future contracts/codegen schema patch for PatchContract, "
            "CodeDropEnvelope, MetaGateSeal, lane signals, provenance, and "
            "authority locks while preserving advisory-only boundaries."
        ),
        output=(
            "A ready-to-paste Codex prompt for a future schema-only branch and a "
            "receipt that does not create schemas by itself."
        ),
        validation=(
            "Future schema work must use deterministic JSON schema patterns and "
            "must deny code mutation, runtime mutation, and auto-approval."
        ),
        recommended_next=(
            "Advance to PHASE_2_CORE_CODEGEN_HARNESS after schema prompt review."
        ),
    ),
    PhaseId.PHASE_2_CORE_CODEGEN_HARNESS: PhaseSpec(
        phase=PhaseId.PHASE_2_CORE_CODEGEN_HARNESS,
        task=(
            "Prepare the future core/codegen builder, runner, and "
            "shadow_replay_harness prompt. The harness must build deterministic "
            "plans and receipts, not execute generated code."
        ),
        output=(
            "A ready-to-paste Codex prompt for future core/codegen harness work "
            "with shadow-replay emphasis."
        ),
        validation=(
            "Future harness work must return deterministic dictionaries, validate "
            "against contracts, and keep generated code advisory."
        ),
        recommended_next=(
            "Advance to PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY after harness "
            "prompt review."
        ),
    ),
    PhaseId.PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY: PhaseSpec(
        phase=PhaseId.PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY,
        task=(
            "Prepare deterministic fixtures and shadow replay validation prompts "
            "for the future Codegen Intelligence Spine without mutating runtime "
            "state or applying generated patches."
        ),
        output=(
            "A ready-to-paste Codex prompt for fixture and replay validation plus "
            "an advisory receipt."
        ),
        validation=(
            "Future replay must validate structural JSON, expected denials, and "
            "canonical hash stability."
        ),
        recommended_next=(
            "Advance to PHASE_4_META_GATE_OPERATOR_PROMOTION after fixture plan "
            "review."
        ),
    ),
    PhaseId.PHASE_4_META_GATE_OPERATOR_PROMOTION: PhaseSpec(
        phase=PhaseId.PHASE_4_META_GATE_OPERATOR_PROMOTION,
        task=(
            "Prepare the advisory meta-gate prompt that summarizes phase receipts "
            "for operator promotion review without granting execution authority."
        ),
        output=(
            "A ready-to-paste Codex prompt for a meta-gate review packet and "
            "receipt."
        ),
        validation=(
            "Meta-gate output must preserve ADVISORY_ONLY, downstream "
            "NOT_COMPUTABLE until attested, and false authority locks."
        ),
        recommended_next=(
            "Advance to PHASE_5_NOTION_RECONCILIATION_DRYRUN after operator "
            "promotion review."
        ),
    ),
    PhaseId.PHASE_5_NOTION_RECONCILIATION_DRYRUN: PhaseSpec(
        phase=PhaseId.PHASE_5_NOTION_RECONCILIATION_DRYRUN,
        task=(
            "Prepare a Notion reconciliation dry-run prompt that reports observed "
            "GitHub state for manual operator copy-paste only."
        ),
        output=(
            "A dry-run reconciliation prompt and receipt with notion_writeback "
            "remaining false."
        ),
        validation=(
            "Dry-run text must not claim live Notion writeback or durable sync "
            "authority."
        ),
        recommended_next=(
            "Hold for operator review; no auto-continuation or writeback is "
            "authorized."
        ),
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
    records: list[dict[str, Any]] = []
    for rel_path in EVIDENCE_PATHS:
        path = repo_root / rel_path
        records.append(
            {
                "path": rel_path,
                "observed": path.exists(),
                "source_hash": _sha256_text(path),
            }
        )
    return records


def _gap_summary(repo_root: Path) -> dict[str, Any]:
    gap_packet = _read_json(
        repo_root
        / "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json"
    )
    return {
        "plan_status": gap_packet.get("plan_status", "NOT_COMPUTABLE"),
        "target_surface_status": gap_packet.get(
            "target_surface_status", "NOT_COMPUTABLE"
        ),
        "recommended_next_lane": gap_packet.get(
            "recommended_next_lane", "NOT_COMPUTABLE"
        ),
        "valid_for_execution": gap_packet.get("valid_for_execution", False),
        "valid_for_implementation": gap_packet.get("valid_for_implementation", False),
        "spine_required_path_records": gap_packet.get(
            "spine_required_path_records", []
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
    }


def _boundary_lines() -> list[str]:
    return [
        "Advisory-only, implementation-first, governance-compliant.",
        "No execution authority.",
        "ADVISORY_STACK_HELD_FOR_OPERATOR until operator gate.",
        "CANON_MUTATION=false; RUNTIME_MUTATION=false; EXECUTION_AUTHORITY=false.",
    ]


def _prompt_sections(phase: PhaseId, repo_root: Path) -> dict[str, list[str]]:
    spec = PHASE_SPECS[phase]
    evidence_lines = [
        (
            f"- {record['path']}: observed={record['observed']} "
            f"hash={record['source_hash']}"
        )
        for record in _evidence_records(repo_root)
    ]
    gap = _gap_summary(repo_root)
    evidence_lines.extend(
        [
            f"- gap_plan_status: {gap['plan_status']}",
            f"- target_surface_status: {gap['target_surface_status']}",
            f"- recommended_next_lane: {gap['recommended_next_lane']}",
            f"- valid_for_execution: {gap['valid_for_execution']}",
            f"- valid_for_implementation: {gap['valid_for_implementation']}",
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
    base: dict[str, Any] = {
        "artifact_type": "AbxCodexGovernanceLoopReceipt.v1",
        "receipt_id": f"ABX_CODEX_GOVERNANCE_LOOP_{phase.value}",
        "receipt_status": "ABX_CODEX_GOVERNANCE_LOOP_RECEIPT_EMITTED_ADVISORY_ONLY",
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
        "recommended_next": PHASE_SPECS[phase].recommended_next,
        "provenance": {
            "script": "scripts/abraxas_v2.0_codex_governance_loop.py",
            "repo_root": str(repo_root),
            "receipt_path": str(_receipt_path(repo_root, phase).relative_to(repo_root)),
            "canonical_hash_algorithm": (
                "sha256(canonical_json_without_canonical_hash)"
            ),
            "source_gap_plan": (
                "out/audit/"
                "abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json"
            ),
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
