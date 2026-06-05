# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.receipts.builder import (
    build_receipt_markdown,
    build_simulated_receipt,
    build_spec_only_receipt,
)
from core.receipts.models import (
    ArtifactsInfo,
    ExecutionInfo,
    ExecutionState,
    FilesInfo,
    RepoExecutionReceipt,
    RepoInfo,
    RollbackInfo,
    RollbackMethod,
    TestsInfo,
    TestsStatus,
)
from core.receipts.validator import validate_receipt


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_optional_hash(path_str: str | None) -> str | None:
    if not path_str:
        return None
    path = Path(path_str)
    if not path.exists() or not path.is_file():
        return None
    return _sha256_file(path)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit a deterministic RepoExecutionReceipt.v1 packet.")
    parser.add_argument("--command-id", required=True)
    parser.add_argument("--execution-state", required=True, choices=[state.value for state in ExecutionState])
    parser.add_argument("--command", dest="operator_command", required=True)
    parser.add_argument("--pipeline-id")
    parser.add_argument("--repo-name")
    parser.add_argument("--repo-url")
    parser.add_argument("--branch")
    parser.add_argument("--base-commit")
    parser.add_argument("--result-commit")
    parser.add_argument("--cwd")
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--ci-run-id")
    parser.add_argument("--ci-run-url")
    parser.add_argument("--stdout-file")
    parser.add_argument("--stderr-file")
    parser.add_argument("--source-artifact-ref", action="append", default=[])
    parser.add_argument("--added-file", action="append", default=[])
    parser.add_argument("--modified-file", action="append", default=[])
    parser.add_argument("--deleted-file", action="append", default=[])
    parser.add_argument("--renamed-file", action="append", default=[])
    parser.add_argument("--diff-hash")
    parser.add_argument("--test-command", action="append", default=[])
    parser.add_argument(
        "--tests-status",
        default=TestsStatus.not_run.value,
        choices=[status.value for status in TestsStatus],
    )
    parser.add_argument("--test-report-hash", action="append", default=[])
    parser.add_argument("--coverage-hash")
    parser.add_argument("--generated-artifact", action="append", default=[])
    parser.add_argument("--artifact-hash", action="append", default=[])
    parser.add_argument("--rollback-available", action="store_true")
    parser.add_argument(
        "--rollback-method",
        default=RollbackMethod.not_available.value,
        choices=[method.value for method in RollbackMethod],
    )
    parser.add_argument("--rollback-ref")
    parser.add_argument("--rollback-patch-hash")
    parser.add_argument(
        "--status",
        default="valid",
        choices=["valid", "invalid", "failed", "not_computable", "spec_only", "simulated"],
    )
    parser.add_argument("--not-computable-reason", action="append", default=[])
    parser.add_argument("--out", default="out/execution_receipts/latest.json")
    return parser.parse_args()


def _parse_artifact_hashes(entries: list[str]) -> dict[str, str]:
    artifact_hashes: dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError("--artifact-hash entries must be PATH=HASH")
        key, value = entry.split("=", 1)
        artifact_hashes[key] = value
    return artifact_hashes


def _build_receipt(args: argparse.Namespace) -> RepoExecutionReceipt:
    state = ExecutionState(args.execution_state)
    if state == ExecutionState.not_executed:
        return build_spec_only_receipt(
            args.command_id,
            args.operator_command,
            pipeline_id=args.pipeline_id,
            repo_name=args.repo_name,
            branch=args.branch,
            source_artifact_refs=args.source_artifact_ref,
        )

    if state == ExecutionState.simulated:
        return build_simulated_receipt(
            args.command_id,
            args.operator_command,
            pipeline_id=args.pipeline_id,
            repo_name=args.repo_name,
            branch=args.branch,
            source_artifact_refs=args.source_artifact_ref,
            produced_artifacts=args.generated_artifact,
            artifact_hashes=_parse_artifact_hashes(args.artifact_hash),
        )

    files = FilesInfo(
        added=args.added_file,
        modified=args.modified_file,
        deleted=args.deleted_file,
        renamed=args.renamed_file,
        diff_hash=args.diff_hash,
    )
    tests = TestsInfo(
        commands=args.test_command,
        status=TestsStatus(args.tests_status),
        test_report_hashes=args.test_report_hash,
        coverage_hash=args.coverage_hash,
    )
    artifacts = ArtifactsInfo(
        generated=args.generated_artifact,
        artifact_hashes=_parse_artifact_hashes(args.artifact_hash),
    )
    rollback = RollbackInfo(
        available=args.rollback_available,
        method=RollbackMethod(args.rollback_method),
        rollback_ref=args.rollback_ref,
        rollback_patch_hash=args.rollback_patch_hash,
    )
    repo = RepoInfo(
        repo_url=args.repo_url,
        repo_name=args.repo_name,
        branch=args.branch,
        base_commit=args.base_commit,
        result_commit=args.result_commit,
    )
    execution = ExecutionInfo(
        command=args.operator_command,
        cwd=args.cwd,
        exit_code=args.exit_code,
        stdout_hash=_read_optional_hash(args.stdout_file),
        stderr_hash=_read_optional_hash(args.stderr_file),
        ci_run_id=args.ci_run_id,
        ci_run_url=args.ci_run_url,
    )
    return RepoExecutionReceipt(
        execution_state=state,
        command_id=args.command_id,
        operator_command=args.operator_command,
        pipeline_id=args.pipeline_id,
        source_artifact_refs=args.source_artifact_ref,
        repo=repo,
        execution=execution,
        files=files,
        tests=tests,
        artifacts=artifacts,
        rollback=rollback,
        status=args.status,
        not_computable_reasons=args.not_computable_reason,
        recommended_next_state="repair" if state == ExecutionState.failed else "review",
    )


def main() -> int:
    args = _parse_args()
    receipt = _build_receipt(args)
    validation = validate_receipt(receipt)
    if validation["status"] != "valid":
        raise SystemExit(str(validation))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(receipt.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    out_path.with_suffix(".md").write_text(build_receipt_markdown(receipt, out_path), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"receipt_id={receipt.receipt_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
