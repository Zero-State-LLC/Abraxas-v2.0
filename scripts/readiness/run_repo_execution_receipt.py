#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.receipts.builder import build_receipt_markdown, build_spec_only_receipt  # noqa: E402
from core.receipts.models import (  # noqa: E402
    ExecutionInfo,
    ExecutionState,
    RepoExecutionReceipt,
    RepoInfo,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--command-id", required=True)
    parser.add_argument("--execution-state", required=True, choices=[state.value for state in ExecutionState])
    parser.add_argument("--command", required=True)
    parser.add_argument("--pipeline-id")
    parser.add_argument("--repo-name")
    parser.add_argument("--branch")
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--ci-run-id")
    parser.add_argument("--ci-run-url")
    parser.add_argument("--out", default="out/execution_receipts/latest.json")
    return parser.parse_args()


def _build_receipt(args: argparse.Namespace) -> RepoExecutionReceipt:
    state = ExecutionState(args.execution_state)
    if state == ExecutionState.not_executed:
        return build_spec_only_receipt(
            args.command_id,
            args.command,
            pipeline_id=args.pipeline_id,
            repo_name=args.repo_name,
            branch=args.branch,
        )
    return RepoExecutionReceipt(
        execution_state=state,
        command_id=args.command_id,
        operator_command=args.command,
        pipeline_id=args.pipeline_id,
        repo=RepoInfo(repo_name=args.repo_name, branch=args.branch),
        execution=ExecutionInfo(
            command=args.command,
            exit_code=args.exit_code,
            ci_run_id=args.ci_run_id,
            ci_run_url=args.ci_run_url,
        ),
        status="valid",
    )


def main() -> int:
    args = _parse_args()
    try:
        receipt = _build_receipt(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(receipt.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    out_path.with_suffix(".md").write_text(
        build_receipt_markdown(receipt, out_path),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
