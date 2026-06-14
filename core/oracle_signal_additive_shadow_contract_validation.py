from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OracleSignalAdditiveShadowContractValidation.v1"
OUT_JSON = Path("out/oracle/oracle_signal_additive_shadow_contract_validation.latest.json")
OUT_MD = Path("out/oracle/oracle_signal_additive_shadow_contract_validation.latest.md")

IMPLEMENTATION_SPEC_PATH = Path("out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json")
INTAKE_RECEIPT_PATH = Path("out/oracle/oracle_signal_intake_receipt.latest.json")
CONTRACT_PATHS = (
    "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
    "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
    "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
)
CANDIDATE_RUNNER_PATH = "scripts/run_oracle_signal_intake_boundary.py"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_weight": False,
        "github_writeback": False,
        "implementation_authority": False,
        "ingest_runner_mutation": False,
        "notion_writeback": False,
        "pipeline_or_route_mutation": False,
        "queue_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "token_minting": False,
    }


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_oracle_signal_additive_shadow_contract_validation(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    spec = _read_json(root / IMPLEMENTATION_SPEC_PATH)
    receipt = _read_json(root / INTAKE_RECEIPT_PATH)
    contract_paths = [path for path in CONTRACT_PATHS if (root / path).exists()]
    missing_contract_paths = sorted(set(CONTRACT_PATHS) - set(contract_paths))
    runner_observed = (root / CANDIDATE_RUNNER_PATH).exists()

    spec_ready = (
        spec.get("status")
        in {
            "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_READY",
            "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_CONSUMED_ADVISORY_ONLY",
        }
        and (
            spec.get("recommended_next_patch")
            == "PATCH-ABX-GLOBAL-INGEST-ADDITIVE-SHADOW-CONTRACTS-001"
            or (
                spec.get("recommended_next_patch") == "NOT_COMPUTABLE"
                and spec.get("implementation_pr_consumed") is True
                and spec.get("additive_shadow_surfaces_observed") is True
            )
        )
        and spec.get("implementation_authorized") is False
        and spec.get("execution_authority") is False
    )
    receipt_ready = (
        receipt.get("receipt_status") == "ORACLE_SIGNAL_INTAKE_RECEIPT_EMITTED_ADVISORY_ONLY"
        and receipt.get("authority") == "SHADOW_INTAKE_BOUNDARY_ONLY"
        and receipt.get("valid_for_execution") is False
        and receipt.get("execution_authority") is False
        and receipt.get("runtime_mutation") is False
        and receipt.get("pipeline_or_route_mutation") is False
    )
    validation_ready = spec_ready and receipt_ready and not missing_contract_paths and runner_observed

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "validation_id": "",
        "status": (
            "ORACLE_SIGNAL_ADDITIVE_SHADOW_CONTRACT_VALIDATION_READY"
            if validation_ready
            else "ORACLE_SIGNAL_ADDITIVE_SHADOW_CONTRACT_VALIDATION_BLOCKED"
        ),
        "target_pipeline_id": "oracle_signal",
        "target_contract_status": "additive_shadow_contracts_observed",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_spec_path": IMPLEMENTATION_SPEC_PATH.as_posix(),
        "source_spec_hash": str(spec.get("spec_hash", "NOT_COMPUTABLE")),
        "source_receipt_path": INTAKE_RECEIPT_PATH.as_posix(),
        "source_receipt_hash": str(receipt.get("receipt_hash", "NOT_COMPUTABLE")),
        "observed_contract_paths": sorted(contract_paths),
        "missing_contract_paths": missing_contract_paths,
        "candidate_runner_path": CANDIDATE_RUNNER_PATH,
        "candidate_runner_observed": runner_observed,
        "contract_path_hashes": {path: _sha256(root / path) for path in sorted(contract_paths)},
        "validation_ready": validation_ready,
        "validation_scope": "SCHEMA_AND_SHADOW_RECEIPT_ONLY",
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "pipeline_or_route_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "token_minting_allowed": False,
        "authority_locks": _authority_locks(),
        "blocked_actions": [
            "CORE_ORACLE_SIGNAL_IMPLEMENTATION",
            "INGEST_RUNNER_BEHAVIOR_MUTATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "QUEUE_MUTATION",
            "FORECAST_WEIGHTING",
            "CANON_PROMOTION",
            "EXECUTION_AUTHORITY_GRANT",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
            "TOKEN_MINTING",
        ],
        "recommended_next_action": (
            "carry Oracle Signal additive shadow validation as coverage evidence; keep implementation and execution denied"
            if validation_ready
            else "repair Oracle Signal additive shadow validation evidence before using it as coverage"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
    }
    packet["validation_id"] = canonical_hash({k: v for k, v in packet.items() if k != "validation_id"})
    return packet


def render_oracle_signal_additive_shadow_contract_validation_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Oracle Signal Additive Shadow Contract Validation",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `validation_ready`: `{packet['validation_ready']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        "",
        "## Observed Contracts",
    ]
    for path in packet["observed_contract_paths"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## Blocked Actions"])
    for action in packet["blocked_actions"]:
        lines.append(f"- `{action}`")
    return lines


def write_oracle_signal_additive_shadow_contract_validation(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_oracle_signal_additive_shadow_contract_validation(root)
    write_canonical_json(target_root / OUT_JSON, packet)
    _write_markdown(target_root / OUT_MD, render_oracle_signal_additive_shadow_contract_validation_markdown(packet))
    return packet
