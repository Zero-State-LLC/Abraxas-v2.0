"""Receipt builders for governed repo execution surfaces."""

from __future__ import annotations

from pathlib import Path

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


def build_spec_only_receipt(
    command_id: str,
    operator_command: str,
    *,
    pipeline_id: str | None = None,
    repo_name: str | None = None,
    branch: str | None = None,
    source_artifact_refs: list[str] | None = None,
) -> RepoExecutionReceipt:
    return RepoExecutionReceipt(
        execution_state=ExecutionState.not_executed,
        command_id=command_id,
        operator_command=operator_command,
        pipeline_id=pipeline_id,
        source_artifact_refs=source_artifact_refs or [],
        repo=RepoInfo(repo_name=repo_name, branch=branch),
        tests=TestsInfo(status=TestsStatus.not_run),
        rollback=RollbackInfo(available=False, method=RollbackMethod.not_available),
        status="spec_only",
        recommended_next_state="hold",
    )


def build_simulated_receipt(
    command_id: str,
    operator_command: str,
    *,
    pipeline_id: str | None = None,
    repo_name: str | None = None,
    branch: str | None = None,
    source_artifact_refs: list[str] | None = None,
    produced_artifacts: list[str] | None = None,
    artifact_hashes: dict[str, str] | None = None,
) -> RepoExecutionReceipt:
    return RepoExecutionReceipt(
        execution_state=ExecutionState.simulated,
        command_id=command_id,
        operator_command=operator_command,
        pipeline_id=pipeline_id,
        source_artifact_refs=source_artifact_refs or [],
        repo=RepoInfo(repo_name=repo_name, branch=branch),
        execution=ExecutionInfo(command=operator_command),
        tests=TestsInfo(status=TestsStatus.simulated),
        artifacts=ArtifactsInfo(
            generated=produced_artifacts or [],
            artifact_hashes=artifact_hashes or {},
        ),
        rollback=RollbackInfo(available=False, method=RollbackMethod.not_available),
        status="simulated",
        recommended_next_state="eligible_for_operator_review",
    )


def build_local_execution_receipt(
    command_id: str,
    operator_command: str,
    *,
    pipeline_id: str | None = None,
    repo_name: str | None = None,
    branch: str | None = None,
    base_commit: str | None = None,
    dirty_worktree_before: bool | None = None,
    dirty_worktree_after: bool | None = None,
    cwd: str | None = None,
    exit_code: int | None = None,
    changed_files: FilesInfo | None = None,
    tests: TestsInfo | None = None,
    artifacts: ArtifactsInfo | None = None,
    rollback: RollbackInfo | None = None,
    source_artifact_refs: list[str] | None = None,
) -> RepoExecutionReceipt:
    return RepoExecutionReceipt(
        execution_state=ExecutionState.local_executed,
        command_id=command_id,
        operator_command=operator_command,
        pipeline_id=pipeline_id,
        source_artifact_refs=source_artifact_refs or [],
        repo=RepoInfo(
            repo_name=repo_name,
            branch=branch,
            base_commit=base_commit,
            dirty_worktree_before=dirty_worktree_before,
            dirty_worktree_after=dirty_worktree_after,
        ),
        execution=ExecutionInfo(command=operator_command, cwd=cwd, exit_code=exit_code),
        files=changed_files or FilesInfo(),
        tests=tests or TestsInfo(status=TestsStatus.not_run),
        artifacts=artifacts or ArtifactsInfo(),
        rollback=rollback or RollbackInfo(available=False, method=RollbackMethod.not_computable),
        status="valid" if exit_code == 0 else "failed",
        recommended_next_state="review" if exit_code == 0 else "repair",
    )


def build_receipt_markdown(receipt: RepoExecutionReceipt, out_path: Path) -> str:
    lines = [
        "# Repo Execution Receipt",
        "",
        f"- `command_id`: `{receipt.command_id}`",
        f"- `receipt_id`: `{receipt.receipt_id}`",
        f"- `execution_state`: `{receipt.execution_state.value}`",
        f"- `status`: `{receipt.status}`",
        f"- `recommended_next_state`: `{receipt.recommended_next_state}`",
        f"- `out_path`: `{out_path.as_posix()}`",
        "",
        "## Repo",
        f"- `repo_name`: `{receipt.repo.repo_name}`",
        f"- `branch`: `{receipt.repo.branch}`",
        f"- `base_commit`: `{receipt.repo.base_commit}`",
        f"- `result_commit`: `{receipt.repo.result_commit}`",
        "",
        "## Execution",
        f"- `operator_command`: `{receipt.operator_command}`",
        f"- `execution.command`: `{receipt.execution.command}`",
        f"- `exit_code`: `{receipt.execution.exit_code}`",
        f"- `cwd`: `{receipt.execution.cwd}`",
        "",
        "## Tests",
        f"- `status`: `{receipt.tests.status.value}`",
        f"- `commands`: `{receipt.tests.commands}`",
        "",
        "## Artifacts",
        f"- `generated`: `{receipt.artifacts.generated}`",
        "",
        "## Rollback",
        f"- `available`: `{receipt.rollback.available}`",
        f"- `method`: `{receipt.rollback.method.value}`",
        f"- `rollback_ref`: `{receipt.rollback.rollback_ref}`",
        "",
        "## Authority",
        "- all authority flags remain false",
    ]
    return "\n".join(lines) + "\n"
