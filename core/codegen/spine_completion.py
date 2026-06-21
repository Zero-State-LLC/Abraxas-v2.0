from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineCompletionReceipt.v1"
RECEIPT_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_COMPLETION_RECEIPT_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_completion_receipt_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_completion_receipt_001.latest.md"

MERGE_REFS: dict[str, str] = {
    "PHASE_1_CONTRACTS_CODEGEN_SCHEMAS": "ee183d1d69539096f4cf1693966151b2b16d7835",
    "PHASE_2_CORE_CODEGEN_HARNESS": "c730750d2846200ea9e05e9cbdb3dd20295ca771",
    "PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY": "a69f87b08237da539e9dd09f02ed3ce7c64c58c1",
    "PHASE_4_META_GATE_OPERATOR_PROMOTION": "0cc01902ab06d4784755a6032d7bd292e2dcecc8",
    "PHASE_5_NOTION_RECONCILIATION_DRYRUN": "c8ba08fb6c772309b974fc87c5f29557c97d8d26",
}

REQUIRED_PATHS: tuple[str, ...] = (
    "contracts/codegen/__init__.py",
    "contracts/codegen/models.py",
    "contracts/codegen/validators.py",
    "contracts/codegen/schemas/PatchContract.json",
    "contracts/codegen/schemas/CodeDropEnvelope.json",
    "contracts/codegen/schemas/MetaGateSeal.json",
    "contracts/codegen/schemas/CodegenTaskPacket.json",
    "contracts/codegen/schemas/ShadowReplayFixture.json",
    "core/codegen/__init__.py",
    "core/codegen/builder.py",
    "core/codegen/runner.py",
    "core/codegen/shadow_replay_harness.py",
    "core/codegen/fixture_validation.py",
    "core/codegen/meta_gate.py",
    "core/codegen/notion_reconciliation.py",
    "tests/contracts/test_codegen_contracts.py",
    "tests/codegen/test_phase2_core_codegen_harness.py",
    "tests/codegen/test_phase3_fixture_validation.py",
    "tests/codegen/test_phase4_meta_gate.py",
    "tests/codegen/test_phase5_notion_reconciliation.py",
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _path_records(repo_root: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for rel_path in REQUIRED_PATHS:
        target = repo_root / rel_path
        records.append(
            {
                "path": rel_path,
                "status": "OBSERVED" if target.exists() else "MISSING",
                "source_hash": _sha256(target),
            }
        )
    return records


def _authority_locks() -> dict[str, bool]:
    return {
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


def build_codegen_spine_completion_receipt(
    *,
    repo_root: str | Path,
    timestamp: str = "2026-06-21T21:35:00Z",
    merge_refs: Mapping[str, str] = MERGE_REFS,
) -> dict[str, Any]:
    root = Path(repo_root)
    records = _path_records(root)
    all_observed = all(record["status"] == "OBSERVED" for record in records)
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "receipt_id": RECEIPT_ID,
        "timestamp": timestamp,
        "spine_status": (
            "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_COMPUTABLE"
            if all_observed
            else "ABX_CODEGEN_INTELLIGENCE_SPINE_INCOMPLETE"
        ),
        "phase_merge_refs": dict(merge_refs),
        "required_path_records": records,
        "required_path_count": len(records),
        "observed_path_count": sum(
            1 for record in records if record["status"] == "OBSERVED"
        ),
        "authority_locks": _authority_locks(),
        "validation_commands": [
            "python -m ruff check contracts/codegen core/codegen tests/codegen tests/contracts/test_codegen_contracts.py tests/test_codegen_shadow_replay_harness.py",
            "python -m pytest -q tests/codegen tests/contracts/test_codegen_contracts.py tests/test_codegen_shadow_replay_harness.py",
            "pyright contracts/codegen core/codegen",
        ],
        "residual_risks": [
            "Full repo fast CI has pre-existing Windows path/encoding baseline failures outside the codegen spine diff.",
            "The codegen spine remains advisory; runtime, canon, GitHub, and Notion authority locks remain false.",
            "Operator review is still required before any future activation or production lane.",
        ],
        "recommended_next": (
            "Operator may use the PHASE_5 dry-run text for manual Notion reconciliation."
        ),
        "advisory_only": True,
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_canon_promotion": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_codegen_spine_completion_receipt(
    *,
    repo_root: str | Path,
    out_json: str | Path = OUT_JSON,
    out_md: str | Path = OUT_MD,
    timestamp: str = "2026-06-21T21:35:00Z",
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = build_codegen_spine_completion_receipt(
        repo_root=root,
        timestamp=timestamp,
    )
    write_canonical_json(root / out_json, receipt)
    write_codegen_spine_completion_receipt_markdown(root / out_md, receipt)
    return receipt


def write_codegen_spine_completion_receipt_markdown(
    path: str | Path,
    receipt: Mapping[str, Any],
) -> None:
    lines = [
        "# ABX Codegen Intelligence Spine Completion Receipt",
        "",
        f"- receipt_id: {receipt['receipt_id']}",
        f"- spine_status: {receipt['spine_status']}",
        f"- observed_path_count: {receipt['observed_path_count']}",
        f"- required_path_count: {receipt['required_path_count']}",
        f"- valid_for_execution: {receipt['valid_for_execution']}",
        f"- valid_for_runtime_activation: {receipt['valid_for_runtime_activation']}",
        f"- valid_for_canon_promotion: {receipt['valid_for_canon_promotion']}",
        f"- Brier Score: {receipt['brier_score']:.2f}",
        "",
        "## Phase Merge Refs",
    ]
    for phase, sha in receipt["phase_merge_refs"].items():
        lines.append(f"- {phase}: {sha}")
    lines.extend(["", "## Required Paths"])
    for record in receipt["required_path_records"]:
        lines.append(f"- {record['path']}: {record['status']}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
