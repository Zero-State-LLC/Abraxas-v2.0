"""Supported Abraxas CLI: analyze / validate / replay / status / os / forage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from abraxas.client import AbraxasClient
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_canonical_artifact
from core.governance.activation_policy import ActivationLane
from core.ingest.familiar_ingestion_receipt import (
    build_familiar_ingestion_receipt_from_path,
    write_familiar_ingestion_receipt,
)
from core.settings import load_runtime_settings
from core.signal.evidence_pack import validate_path
from core.signal.operation_trace_adapter import (
    receipt_to_operation_trace,
    write_operation_trace,
)
from core.signal.spine_bridge import (
    build_ai_os_kernel_status,
    build_touchpoint_from_pack_path,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def _cmd_analyze(args: argparse.Namespace) -> int:
    settings = load_runtime_settings(
        repo_root=REPO_ROOT,
        default_activation_lane=args.lane,
    )
    client = AbraxasClient(settings=settings)
    input_payload: dict[str, Any] = {}
    if args.input is not None:
        loaded = _load_json(args.input)
        if not isinstance(loaded, dict):
            _print(
                {
                    "status": "ERROR",
                    "error_class": "INPUT_INVALID",
                    "message": "--input must be a JSON object",
                }
            )
            return 2
        input_payload = loaded

    alembic_task = _load_json(args.alembic_task) if args.alembic_task else None
    oracle_candidate = (
        _load_json(args.oracle_candidate) if args.oracle_candidate else None
    )
    result = client.analyze(
        run_id=args.run_id,
        input_payload=input_payload,
        schema_ref=args.schema_ref,
        alembic_task=alembic_task if isinstance(alembic_task, dict) else None,
        oracle_candidate=(
            oracle_candidate if isinstance(oracle_candidate, dict) else None
        ),
        enable_alembic=not args.no_alembic,
        alembic_mode=args.alembic_mode,
        activation_lane=args.lane,
    )
    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=True)
        out_root = args.out.resolve()
        write_canonical_artifact(
            args.out / "advisory_spine_result.json",
            result,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=out_root,
        )
        if isinstance(result.get("alembic"), dict):
            write_canonical_artifact(
                args.out / "alembic.json",
                result["alembic"],
                artifact_class=ArtifactClass.AUDIT_EVIDENCE,
                out_root=out_root,
            )
    _print(
        {
            "ok": result.get("status") == "OK",
            "status": result.get("status"),
            "run_id": result.get("run_id"),
            "result_hash": result.get("result_hash"),
            "alembic_invoked": bool(
                (result.get("advisory_result") or {}).get("alembic_invoked")
            ),
            "error_class": result.get("error_class"),
        }
    )
    if result.get("status") == "OK":
        return 0
    if result.get("status") == "OPERATOR_GATE":
        return 3
    return 1


def _cmd_validate(args: argparse.Namespace) -> int:
    client = AbraxasClient(settings=load_runtime_settings(repo_root=REPO_ROOT))
    payload = _load_json(args.payload)
    result = client.validate(
        schema_ref=args.schema_ref,
        payload=payload,
        execution_id=args.execution_id,
    )
    _print(
        {
            "ok": result.get("status") == "OK" and result.get("valid") is True,
            "status": result.get("status"),
            "valid": result.get("valid"),
            "error_class": result.get("error_class"),
            "errors": result.get("errors"),
        }
    )
    if result.get("status") == "OK" and result.get("valid") is True:
        return 0
    return 1


def _cmd_replay(args: argparse.Namespace) -> int:
    settings = load_runtime_settings(
        repo_root=REPO_ROOT,
        default_activation_lane=args.lane,
    )
    client = AbraxasClient(settings=settings)
    receipt = _load_json(args.receipt)
    if not isinstance(receipt, dict):
        _print(
            {
                "status": "ERROR",
                "error_class": "REPLAY_INPUT_INVALID",
                "message": "--receipt must be a JSON object",
            }
        )
        return 2
    result = client.replay(receipt, run_id=args.run_id)
    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out / "replay_result.json",
            result,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=args.out.resolve(),
        )
    _print(
        {
            "ok": result.get("status") == "OK",
            "status": result.get("status"),
            "run_id": result.get("run_id"),
            "result_hash": result.get("result_hash"),
            "error_class": result.get("error_class"),
        }
    )
    return 0 if result.get("status") == "OK" else 1


def _cmd_status(_args: argparse.Namespace) -> int:
    settings = load_runtime_settings(repo_root=REPO_ROOT)
    client = AbraxasClient(settings=settings)
    snapshot = client.status()
    _print(
        {
            "ok": True,
            "candidate_status": snapshot["candidate_status"],
            "external_production_authorized": snapshot[
                "external_production_authorized"
            ],
            "repository_sha": snapshot["repository_sha"],
            "supported_interfaces": snapshot["supported_interfaces"],
            "supported_spine": snapshot["supported_spine"],
            "settings": snapshot.get("settings"),
            "canonical_hash": snapshot["canonical_hash"],
        }
    )
    return 0


def _cmd_os_status(_args: argparse.Namespace) -> int:
    payload = build_ai_os_kernel_status(REPO_ROOT)
    _print({"ok": payload.get("ai_os_kernel") == "ACTIVE_SHADOW", **payload})
    return 0 if payload.get("ai_os_kernel") == "ACTIVE_SHADOW" else 1


def _cmd_forage_validate(args: argparse.Namespace) -> int:
    report = validate_path(args.pack, repo_root=REPO_ROOT)
    _print(report)
    return 0 if report.get("ok") else 2


def _cmd_forage_ingest(args: argparse.Namespace) -> int:
    receipt = build_familiar_ingestion_receipt_from_path(args.pack, repo_root=REPO_ROOT)
    out_path = args.out
    if out_path is None and not args.print_only:
        stem = Path(args.pack).stem.replace(".v0", "")
        out_path = (
            REPO_ROOT
            / "out"
            / "ingest"
            / "familiar_ingestion"
            / f"{stem}_receipt.v0.json"
        )
    if not args.print_only and out_path is not None:
        write_familiar_ingestion_receipt(
            Path(out_path),
            receipt,
            out_root=REPO_ROOT / "out",
        )

    # Slice D closed loop: emit OperationTrace for skill-evolution / learning
    trace = receipt_to_operation_trace(
        receipt,
        source_artifact=str(out_path) if out_path else "cli:abraxas forage ingest",
    )
    trace_path = write_operation_trace(trace, out_dir=REPO_ROOT / "out" / "audit")

    _print(
        {
            "ok": receipt.get("status") == "INGESTED_SHADOW",
            "status": receipt.get("status"),
            "receipt_id": receipt.get("receipt_id"),
            "pack_id": receipt.get("pack_id"),
            "receipt_hash": receipt.get("receipt_hash"),
            "wrote": str(out_path) if out_path and not args.print_only else None,
            "operation_trace": str(trace_path),
            "commercial_claims_blocked": receipt.get("commercial_claims_blocked"),
            "evidence_density": receipt.get("evidence_density"),
            "lane": receipt.get("lane"),
            "authority": receipt.get("authority"),
        }
    )
    return 0 if receipt.get("status") == "INGESTED_SHADOW" else 2


def _cmd_forage_spine_touch(args: argparse.Namespace) -> int:
    touchpoint = build_touchpoint_from_pack_path(args.pack, repo_root=REPO_ROOT)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            touchpoint,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=(args.out.parent if args.out_root is None else args.out_root),
        )
    _print(
        {
            "ok": touchpoint.get("route") == "ORACLE_SHADOW_CANDIDATE",
            "route": touchpoint.get("route"),
            "touchpoint_id": touchpoint.get("touchpoint_id"),
            "pack_id": touchpoint.get("pack_id"),
            "reason": touchpoint.get("reason"),
            "touchpoint_hash": touchpoint.get("touchpoint_hash"),
            "input_payload_seed": touchpoint.get("input_payload_seed"),
            "oracle_candidate_seed": touchpoint.get("oracle_candidate_seed"),
            "authority": touchpoint.get("authority"),
            "advisory_only": True,
        }
    )
    return 0 if touchpoint.get("route") == "ORACLE_SHADOW_CANDIDATE" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="abraxas",
        description="Abraxas supported product CLI (Governance V3 / advisory spine)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Run advisory golden-path analysis")
    analyze.add_argument("--run-id", default="abraxas-cli-analyze")
    analyze.add_argument("--input", type=Path, default=None)
    analyze.add_argument("--alembic-task", type=Path, default=None)
    analyze.add_argument("--oracle-candidate", type=Path, default=None)
    analyze.add_argument("--schema-ref", default=None)
    analyze.add_argument("--no-alembic", action="store_true")
    analyze.add_argument(
        "--alembic-mode", choices=["advisory", "shadow"], default="advisory"
    )
    analyze.add_argument(
        "--lane",
        choices=[lane.value for lane in ActivationLane],
        default=ActivationLane.LOCAL_DEV.value,
    )
    analyze.add_argument("--out", type=Path, default=None)
    analyze.set_defaults(func=_cmd_analyze)

    validate = sub.add_parser(
        "validate", help="Validate payload against contracts/ schema"
    )
    validate.add_argument("--schema-ref", required=True)
    validate.add_argument("--payload", type=Path, required=True)
    validate.add_argument("--execution-id", default="abraxas-cli-validate")
    validate.set_defaults(func=_cmd_validate)

    replay = sub.add_parser("replay", help="Replay advisory/Alembic receipt")
    replay.add_argument("--receipt", type=Path, required=True)
    replay.add_argument("--run-id", default=None)
    replay.add_argument(
        "--lane",
        choices=[lane.value for lane in ActivationLane],
        default=ActivationLane.LOCAL_DEV.value,
    )
    replay.add_argument("--out", type=Path, default=None)
    replay.set_defaults(func=_cmd_replay)

    status = sub.add_parser("status", help="Print bounded current-state snapshot")
    status.set_defaults(func=_cmd_status)

    # --- AI OS kernel commands ---
    os_parser = sub.add_parser("os", help="AI OS kernel control plane")
    os_sub = os_parser.add_subparsers(dest="os_command", required=True)
    os_status = os_sub.add_parser("status", help="AI OS kernel posture (SHADOW)")
    os_status.set_defaults(func=_cmd_os_status)

    forage = sub.add_parser("forage", help="Signal forage / EvidencePack OS syscall")
    forage_sub = forage.add_subparsers(dest="forage_command", required=True)

    f_validate = forage_sub.add_parser(
        "validate", help="Validate EvidencePack.v0 JSON"
    )
    f_validate.add_argument("--pack", type=Path, required=True)
    f_validate.set_defaults(func=_cmd_forage_validate)

    f_ingest = forage_sub.add_parser(
        "ingest", help="Emit FamiliarIngestionReceipt.v0 (SHADOW)"
    )
    f_ingest.add_argument("--pack", type=Path, required=True)
    f_ingest.add_argument("--out", type=Path, default=None)
    f_ingest.add_argument(
        "--print-only",
        action="store_true",
        help="Do not write receipt files",
    )
    f_ingest.set_defaults(func=_cmd_forage_ingest)

    f_spine = forage_sub.add_parser(
        "spine-touch",
        help="Build advisory spine touchpoint seeds from pack (no Oracle run)",
    )
    f_spine.add_argument("--pack", type=Path, required=True)
    f_spine.add_argument("--out", type=Path, default=None)
    f_spine.add_argument("--out-root", type=Path, default=None)
    f_spine.set_defaults(func=_cmd_forage_spine_touch)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
