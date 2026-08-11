"""Track B contract closure receipt builder.

Closes the AI OS Kernel Unification Track B leaf slices at the full
``contracts/pipelines/*.v1_1.json`` tier while preserving SHADOW/advisory-only
authority. The receipt is evidence only. It does not grant runtime, canon,
forecast-weight, packaging, mint, queue-write, or production authority.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.governance.authority import locked_authority
from core.pipelines.registry import PIPELINE_INVENTORY, load_pipeline_contract

ARTIFACT_TYPE = "TrackBContractClosureReceipt.v1"
STATUS = "TRACK_B_CONTRACT_CLOSURE_ALIGNED_ADVISORY_ONLY"
DEFAULT_OUT_PATH = "out/ai_os/track_b_contract_closure/latest.json"
RUNNER_PATH = "scripts/operator/run_track_b_contract_closure.py"
AUTHORITY_LOCKS = {
    "canon_mutation": False,
    "runtime_mutation": False,
    "execution_authority": False,
    "writeback": False,
    "github_writeback": False,
    "notion_writeback": False,
    "production_activation": False,
    "forecast_weight": False,
    "operator_queue_write": False,
    "artifact_mint": False,
    "packaging_runtime_authority": False,
}

TRACK_B_PIPELINE_IDS = [
    "neon_genie_ideation",
    "familiar_ingestion",
    "noctis_dream",
    "hollersports_ticket",
    "memetic_futurecast",
    "level99_content",
    "beatoven_psyfi_integration",
    "phonomicon_artifact",
]

ISSUE_BY_PIPELINE = {
    "neon_genie_ideation": 1125,
    "familiar_ingestion": 1126,
    "noctis_dream": 1127,
    "hollersports_ticket": 1128,
    "memetic_futurecast": 1129,
    "level99_content": 1130,
    "beatoven_psyfi_integration": 1131,
    "phonomicon_artifact": 1132,
}

SCOPE_BY_PIPELINE = {
    "neon_genie_ideation": "novelty validation + operator packet",
    "familiar_ingestion": "receipt + proof + review chain",
    "noctis_dream": "dream analysis -> receipt + IR + review",
    "hollersports_ticket": "forecast proof + outcome binding",
    "memetic_futurecast": "horizon policy + validation gates + Brier bridge",
    "level99_content": "virality scoring boundaries + operator review",
    "beatoven_psyfi_integration": "shared runic core pipeline contract",
    "phonomicon_artifact": "provenance / artifact proof chain",
}


def _inventory_by_pipeline() -> dict[str, dict[str, Any]]:
    return {str(item["pipeline_id"]): item for item in PIPELINE_INVENTORY}


def _module_path(module_name: str) -> Path:
    return Path(*module_name.split(".")).with_suffix(".py")


def _path_status(root: Path, relative: str | Path | None) -> dict[str, Any]:
    if relative is None:
        return {"path": None, "status": "NOT_APPLICABLE"}
    path = Path(relative)
    target = root / path
    observed = target.is_file()
    return {
        "path": path.as_posix(),
        "status": "OBSERVED" if observed else "MISSING",
        "authority_granted": False,
    }


def _module_importable(root: Path, module_name: str | None) -> dict[str, Any]:
    if not module_name:
        return {"module": None, "status": "NOT_APPLICABLE"}
    path = root / _module_path(module_name)
    spec = importlib.util.spec_from_file_location(module_name, path)
    importable = path.is_file() and spec is not None
    return {
        "module": module_name,
        "path": _module_path(module_name).as_posix(),
        "status": "OBSERVED" if importable else "MISSING",
        "authority_granted": False,
    }


def _contract_row(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    pipeline_id = str(spec["pipeline_id"])
    contract_path = Path("contracts/pipelines") / f"{pipeline_id}.v1_1.json"
    contract = load_pipeline_contract(root / contract_path)
    contract_authority = contract.authority.model_dump()
    contract_authority_locked = all(value is False for value in contract_authority.values())
    evidence_paths = [
        _path_status(root, contract_path),
        _path_status(root, spec.get("contract_path")),
        _path_status(root, spec.get("bridge_contract_path")),
        _path_status(root, spec.get("review_contract_path")),
        _path_status(root, spec.get("dry_run_contract_path")),
        _path_status(root, RUNNER_PATH),
    ]
    module_evidence = [
        _module_importable(root, spec.get("builder_module")),
        _module_importable(root, spec.get("bridge_module")),
        _module_importable(root, spec.get("review_module")),
        _module_importable(root, spec.get("dry_run_module")),
    ]
    missing_required = [
        item["path"]
        for item in evidence_paths
        if item["status"] == "MISSING" and item["path"] == contract_path.as_posix()
    ]
    missing_required.extend(
        item["path"]
        for item in module_evidence
        if item["status"] == "MISSING" and item.get("module") == spec.get("builder_module")
    )
    owner_matches = contract.owner_subsystem == spec["owner_subsystem"]
    aligned = (
        contract.schema_version == "AbraxasPipelineAutomationContract.v1.1"
        and contract.pipeline_id == pipeline_id
        and owner_matches
        and contract_authority_locked
        and not missing_required
    )
    return {
        "pipeline_id": pipeline_id,
        "issue": ISSUE_BY_PIPELINE[pipeline_id],
        "subsystem": spec["owner_subsystem"],
        "scope": SCOPE_BY_PIPELINE[pipeline_id],
        "alignment": "ALIGNED" if aligned else "NOT_ALIGNED",
        "contract_path": contract_path.as_posix(),
        "contract_lane": contract.lane.value,
        "typed_ir_schema": contract.typed_ir_schema,
        "final_state_policy": [item.value for item in contract.final_state_policy],
        "authority_locked": contract_authority_locked,
        "authority": contract_authority,
        "owner_matches": owner_matches,
        "evidence_paths": evidence_paths,
        "module_evidence": module_evidence,
        "runner_path": RUNNER_PATH,
        "missing_required": missing_required,
        "operator_posture": "SHADOW/advisory-only; operator disposition required",
    }


def build_track_b_contract_closure_receipt(repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root)
    inventory = _inventory_by_pipeline()
    rows = [_contract_row(root, inventory[pipeline_id]) for pipeline_id in TRACK_B_PIPELINE_IDS]
    aligned_count = sum(1 for row in rows if row["alignment"] == "ALIGNED")
    payload: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": "TrackBContractClosureReceipt.v1",
        "status": STATUS if aligned_count == len(rows) else "TRACK_B_CONTRACT_CLOSURE_INCOMPLETE",
        "track": "ABRAXAS_UNIFICATION_PLAN_002 Track B",
        "coordination": {
            "issue_author": "prabu-openclaw",
            "source_comment": "https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/issues/1118#issuecomment-5248164045",
            "coordination_posture": "preserve Prabu's priority-ordered 8-slice Track B decomposition; close via the mandatory contract->builder->script->receipt->tests->ALIGNED pattern",
            "writeback_performed": False,
        },
        "parent_issues": [1086, 1118],
        "leaf_issues": [ISSUE_BY_PIPELINE[pipeline_id] for pipeline_id in TRACK_B_PIPELINE_IDS],
        "summary": {
            "target_count": len(rows),
            "aligned_count": aligned_count,
            "not_aligned_count": len(rows) - aligned_count,
            "matrix_expected_alignment": "ALIGNED" if aligned_count == len(rows) else "PARTIAL",
        },
        "authority_locks": AUTHORITY_LOCKS,
        "authority": locked_authority(),
        "contract_closures": rows,
        "validation_commands": [
            "python3 scripts/operator/run_track_b_contract_closure.py",
            "python3 scripts/readiness/run_subsystem_ownership_matrix_refresh_receipt.py",
            "python3 -m pytest tests/test_pipeline_contracts.py tests/test_track_b_contract_closure.py tests/test_subsystem_ownership_matrix_refresh.py",
        ],
        "non_goals": [
            "No runtime/canon/execution authority granted.",
            "No live forecast weight, artifact mint, operator queue write, packaging runtime authority, or production activation granted.",
            "No GitHub/Notion writeback is performed by this receipt builder.",
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {key: value for key, value in payload.items() if key != "canonical_hash"}
    )
    return payload


def write_track_b_contract_closure_receipt(
    repo_root: str | Path = ".",
    out_path: str | Path = DEFAULT_OUT_PATH,
) -> dict[str, Any]:
    payload = build_track_b_contract_closure_receipt(repo_root)
    write_canonical_json(Path(repo_root) / out_path, payload)
    return payload
