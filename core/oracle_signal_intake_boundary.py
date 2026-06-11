from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

PATCH_ID = "PATCH-ABX-GLOBAL-INGEST-ADDITIVE-SHADOW-CONTRACTS-001"
SCHEMA_VERSION = "OracleSignalIntakeReceipt.v1"
AUTHORITY = "SHADOW_INTAKE_BOUNDARY_ONLY"

SPEC_JSON_PATH = Path("out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json")
QUEUE_JSON_PATH = Path("out/ingest/oracle_intake_queue_001.latest.json")
RECEIPT_JSON_PATH = Path("out/oracle/oracle_signal_intake_receipt.latest.json")
RECEIPT_MD_PATH = Path("out/oracle/oracle_signal_intake_receipt.latest.md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def _assert_shadow_queue(queue: Mapping[str, Any]) -> None:
    required_true = ("advisory_only", "projection_only", "non_authoritative")
    required_false = ("forecast_authority", "canon_mutation", "runtime_mutation", "execution_authority")
    if queue.get("schema_version") != "OracleIntakeQueue.v1":
        raise ValueError("expected OracleIntakeQueue.v1")
    if queue.get("authority") != "SHADOW_HANDOFF_ONLY":
        raise ValueError("oracle intake queue authority must remain SHADOW_HANDOFF_ONLY")
    for key in required_true:
        if queue.get(key) is not True:
            raise ValueError(f"oracle intake queue must set {key}=true")
    for key in required_false:
        if queue.get(key) is not False:
            raise ValueError(f"oracle intake queue must set {key}=false")


def _assert_spec_ready(spec: Mapping[str, Any]) -> None:
    if spec.get("status") != "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_READY":
        raise ValueError("global ingest implementation spec must be ready")
    if spec.get("recommended_next_patch") != PATCH_ID:
        raise ValueError(f"global ingest implementation spec must route to {PATCH_ID}")
    if spec.get("implementation_authorized") is not False or spec.get("execution_authority") is not False:
        raise ValueError("global ingest implementation spec must not authorize implementation or execution")


def _candidate_signal(entry: Mapping[str, Any]) -> dict[str, Any]:
    source_ref = {
        "queue_entry_id": str(entry["queue_entry_id"]),
        "source_pull_receipt_id": str(entry["source_pull_receipt_id"]),
        "source_uri": str(entry["source_uri"]),
    }
    signal_base = {
        "adapter_id": str(entry["adapter_id"]),
        "domain": str(entry["domain"]),
        "source_ref": source_ref,
    }
    return {
        "schema_version": "OracleCandidateSignalPacket.v1",
        "signal_id": canonical_hash({"record": "oracle_candidate_signal", **signal_base}),
        "signal_status": "CANDIDATE_SHADOW_ONLY",
        "payload_ref": "SOURCE_URI_ONLY_NO_FETCH",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "source_ref": source_ref,
        "signal_hash": canonical_hash(signal_base),
    }


def _input_envelope_ref(candidate: Mapping[str, Any]) -> dict[str, Any]:
    base = {
        "candidate_signal_id": str(candidate["signal_id"]),
        "candidate_signal_hash": str(candidate["signal_hash"]),
    }
    return {
        "schema_version": "OracleSignalInputEnvelopeRef.v1",
        "envelope_ref_id": canonical_hash({"record": "oracle_signal_input_envelope_ref", **base}),
        "envelope_status": "REFERENCE_ONLY_NOT_BOUND",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        **base,
    }


def build_oracle_signal_intake_receipt(
    *,
    source_root: str | Path = ".",
    queue_path: str | Path = QUEUE_JSON_PATH,
    spec_path: str | Path = SPEC_JSON_PATH,
) -> dict[str, Any]:
    root = Path(source_root)
    queue = _read_json(root / queue_path)
    spec = _read_json(root / spec_path)
    _assert_shadow_queue(queue)
    _assert_spec_ready(spec)

    entries = queue.get("queue_entries", [])
    if not isinstance(entries, list):
        raise ValueError("oracle intake queue entries must be a list")
    candidate_signals = [_candidate_signal(entry) for entry in entries]
    input_envelope_refs = [_input_envelope_ref(candidate) for candidate in candidate_signals]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_status": "ORACLE_SIGNAL_INTAKE_RECEIPT_EMITTED_ADVISORY_ONLY",
        "patch_id": PATCH_ID,
        "authority": AUTHORITY,
        "source_spec_path": str(spec_path),
        "source_spec_hash": str(spec.get("spec_hash", "NOT_COMPUTABLE")),
        "source_queue_path": str(queue_path),
        "source_queue_hash": str(queue.get("queue_hash", "NOT_COMPUTABLE")),
        "source_queue_run_id": str(queue.get("run_id", "NOT_COMPUTABLE")),
        "candidate_signal_count": len(candidate_signals),
        "input_envelope_ref_count": len(input_envelope_refs),
        "candidate_signals": candidate_signals,
        "input_envelope_refs": input_envelope_refs,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "queue_mutation": False,
        "pipeline_or_route_mutation": False,
        "execution_authority": False,
        "valid_for_execution": False,
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
        "recommended_next_action": "hold for governed review before any Oracle Signal implementation, route binding, queue mutation, or runtime integration",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "receipt_hash": "",
    }
    packet["receipt_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "receipt_hash"})
    return packet


def render_oracle_signal_intake_receipt_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Oracle Signal Intake Receipt",
        "",
        f"- `receipt_status`: `{packet['receipt_status']}`",
        f"- `patch_id`: `{packet['patch_id']}`",
        f"- `authority`: `{packet['authority']}`",
        f"- `candidate_signal_count`: `{packet['candidate_signal_count']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `runtime_mutation`: `{packet['runtime_mutation']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Candidate Signals",
        "",
    ]
    for candidate in packet["candidate_signals"]:
        lines.append(f"- `{candidate['signal_id']}` `{candidate['signal_status']}` `{candidate['source_ref']['source_uri']}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_oracle_signal_intake_receipt(
    *,
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
    queue_path: str | Path = QUEUE_JSON_PATH,
    spec_path: str | Path = SPEC_JSON_PATH,
    out_json: str | Path = RECEIPT_JSON_PATH,
    out_md: str | Path = RECEIPT_MD_PATH,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_oracle_signal_intake_receipt(source_root=root, queue_path=queue_path, spec_path=spec_path)
    write_canonical_json(target_root / out_json, packet)
    _write_markdown(target_root / out_md, render_oracle_signal_intake_receipt_markdown(packet))
    return packet
