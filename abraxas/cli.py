"""Supported Abraxas CLI: analyze / validate / replay / status."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from abraxas.client import AbraxasClient
from core.canonical.json import write_canonical_json
from core.governance.activation_policy import ActivationLane

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def _cmd_analyze(args: argparse.Namespace) -> int:
    client = AbraxasClient(repo_root=REPO_ROOT, default_lane=args.lane)
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
        write_canonical_json(args.out / "advisory_spine_result.json", result)
        if result.get("alembic") is not None:
            write_canonical_json(args.out / "alembic.json", result["alembic"])
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
    client = AbraxasClient(repo_root=REPO_ROOT)
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
    client = AbraxasClient(repo_root=REPO_ROOT, default_lane=args.lane)
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
        write_canonical_json(args.out / "replay_result.json", result)
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
    client = AbraxasClient(repo_root=REPO_ROOT)
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
            "canonical_hash": snapshot["canonical_hash"],
        }
    )
    return 0


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
    analyze.add_argument("--alembic-mode", choices=["advisory", "shadow"], default="advisory")
    analyze.add_argument(
        "--lane",
        choices=[lane.value for lane in ActivationLane],
        default=ActivationLane.LOCAL_DEV.value,
    )
    analyze.add_argument("--out", type=Path, default=None)
    analyze.set_defaults(func=_cmd_analyze)

    validate = sub.add_parser("validate", help="Validate payload against contracts/ schema")
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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
