#!/usr/bin/env python3
"""Canonical Alembic Spine CLI — advisory multi-architecture orchestration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.alembic.config import default_router_policy, load_router_policy
from core.alembic.evaluation import run_evaluation_matrix
from core.alembic.models import TaskEnvelope
from core.alembic.pipeline import execute_advisory, route_only
from core.alembic.proposals import propose_router_update
from core.alembic.registry import (
    default_registry,
    load_registry_from_json,
)
from core.alembic.runes import proposed_rune_manifest
from core.alembic.util import to_canonical_dict
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_canonical_artifact, write_canonical_json


def _load_task(path: Path) -> TaskEnvelope:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return TaskEnvelope.model_validate(payload)


def _load_registry(path: Path | None):
    if path is None:
        return default_registry()
    return load_registry_from_json(path)


def _load_policy(path: Path | None):
    if path is None:
        return default_router_policy()
    return load_router_policy(path)


def _write_classified(path: Path, value: Any, *, out_root: Path) -> None:
    if isinstance(value, dict):
        write_canonical_artifact(
            path,
            value,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=out_root,
        )
    else:
        write_canonical_json(path, value)


def _write_run_artifacts(out_dir: Path, payload: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_root = out_dir.resolve()
    _write_classified(out_dir / "latest.json", payload, out_root=out_root)
    for key in (
        "task",
        "registry_snapshot",
        "routing_decision",
        "contributions",
        "verification",
        "fusion",
        "shadow_comparison",
        "metrics",
        "receipt",
        "replay_manifest",
    ):
        if payload.get(key) is not None:
            _write_classified(out_dir / f"{key}.json", payload[key], out_root=out_root)


_PRODUCT_PATH_COMMANDS = frozenset(
    {"execute-advisory", "execute-shadow", "replay", "route", "verify", "fuse"}
)
_DEPRECATION_REMOVAL = "abraxas>=3.0 / Production Convergence CLEAR phase"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Alembic Spine advisory CLI")
    parser.add_argument(
        "command",
        choices=[
            "validate-registry",
            "inspect-architectures",
            "route",
            "execute-advisory",
            "execute-shadow",
            "verify",
            "fuse",
            "evaluate",
            "replay",
            "propose-router-update",
        ],
    )
    parser.add_argument("--task", type=Path, default=None)
    parser.add_argument(
        "--registry",
        type=Path,
        default=REPO_ROOT / "contracts/alembic/architecture_registry.json",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=REPO_ROOT / "contracts/alembic/router_policy.json",
    )
    parser.add_argument("--mode", choices=["advisory", "shadow"], default="advisory")
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "out/alembic/example_run")
    parser.add_argument("--replay-manifest", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.command in _PRODUCT_PATH_COMMANDS:
        import warnings

        warnings.warn(
            (
                "scripts.alembic.run_alembic_spine is an EXPERIMENTAL specialist CLI. "
                "Prefer the supported product path: "
                "`python -m abraxas analyze --alembic-task <task.json>` "
                f"(removal target: {_DEPRECATION_REMOVAL})."
            ),
            DeprecationWarning,
            stacklevel=2,
        )

    try:
        registry = _load_registry(args.registry)
        policy = _load_policy(args.policy)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 2

    args.out.mkdir(parents=True, exist_ok=True)
    out_root = args.out.resolve()

    if args.command == "validate-registry":
        receipt = registry.validation_receipt()
        _write_classified(args.out / "registry_validation.json", receipt, out_root=out_root)
        print(json.dumps({"ok": receipt["status"] == "PASS", "receipt": receipt}, sort_keys=True))
        return 0 if receipt["status"] == "PASS" else 1

    if args.command == "inspect-architectures":
        snapshot = registry.snapshot()
        _write_classified(
            args.out / "architecture_registry_snapshot.json", snapshot, out_root=out_root
        )
        print(json.dumps({"ok": True, "count": snapshot["count"], "snapshot": snapshot}, sort_keys=True))
        return 0

    if args.command == "evaluate":
        result = run_evaluation_matrix(registry, policy)
        payload = to_canonical_dict(result)
        _write_classified(args.out / "evaluation_result.json", payload, out_root=out_root)
        print(json.dumps({"ok": result.status == "PASS", "result": payload}, sort_keys=True))
        return 0 if result.status == "PASS" else 1

    if args.command == "propose-router-update":
        proposal = propose_router_update(policy, evidence=("cli.propose-router-update",))
        payload = to_canonical_dict(proposal)
        _write_classified(args.out / "router_change_proposal.json", payload, out_root=out_root)
        print(json.dumps({"ok": True, "proposal": payload, "auto_applied": False}, sort_keys=True))
        return 0

    if args.command == "replay":
        manifest_path = args.replay_manifest or (args.out / "replay_manifest.json")
        if not manifest_path.exists():
            print(json.dumps({"ok": False, "error": f"missing replay manifest: {manifest_path}"}, sort_keys=True))
            return 2
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        task = TaskEnvelope.model_validate(manifest["task"])
        result = execute_advisory(task, registry, policy, mode="advisory")
        _write_classified(args.out / "replay_result.json", result, out_root=out_root)
        replayable = bool(manifest.get("replayable", False))
        print(json.dumps({
            "ok": True,
            "replayable": replayable,
            "decision_id": result["routing_decision"]["decision_id"],
            "manifest_id": manifest.get("manifest_id"),
        }, sort_keys=True))
        return 0

    if args.task is None:
        print(json.dumps({"ok": False, "error": "--task is required for this command"}, sort_keys=True))
        return 2

    task = _load_task(args.task)

    if args.command == "route":
        decision = route_only(task, registry, policy)
        payload = to_canonical_dict(decision)
        _write_classified(args.out / "routing_decision.json", payload, out_root=out_root)
        print(json.dumps({"ok": True, "decision": payload}, sort_keys=True))
        return 0

    if args.command in {"execute-advisory", "execute-shadow"}:
        mode = "shadow" if args.command == "execute-shadow" or args.mode == "shadow" else "advisory"
        result = execute_advisory(task, registry, policy, mode=mode)
        _write_run_artifacts(args.out, result)
        print(json.dumps({
            "ok": True,
            "mode": mode,
            "decision_id": result["routing_decision"]["decision_id"],
            "abstention_reason": result["routing_decision"]["abstention_reason"],
            "receipt_id": result["receipt"]["artifact_id"],
            "FINAL_STATUS": result["FINAL_STATUS"],
        }, sort_keys=True))
        return 0

    if args.command == "verify":
        # Route+invoke then verify only.
        result = execute_advisory(task, registry, policy, mode="advisory")
        print(json.dumps({"ok": True, "verification": result["verification"]}, sort_keys=True))
        _write_classified(
            args.out / "verification.json", result["verification"], out_root=out_root
        )
        return 0 if result["verification"]["status"] != "FAIL" else 1

    if args.command == "fuse":
        result = execute_advisory(task, registry, policy, mode="advisory")
        print(json.dumps({"ok": result["fusion"] is not None, "fusion": result["fusion"]}, sort_keys=True))
        if result["fusion"] is not None:
            _write_classified(args.out / "fusion.json", result["fusion"], out_root=out_root)
        return 0 if result["fusion"] is not None else 1

    print(json.dumps({"ok": False, "error": "unhandled command", "rune_proposals": proposed_rune_manifest()}, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
