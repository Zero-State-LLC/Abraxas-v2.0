"""Receipt builder for ABRAXAS v2.0."""

from __future__ import annotations

from core.receipts.models import (
    ArtifactsInfo,
    ExecutionInfo,
    ExecutionState,
    FilesInfo,
    RepoExecutionReceipt,
    RepoInfo,
    RollbackInfo,
    TestsInfo,
)


def build_simulated_receipt(
    command_id: str,
    operator_command: str,
    pipeline_id: str | None = None,
    repo_name: str = "",
    branch: str = "",
    produced_artifacts: list[str] | None = None,
) -> RepoExecutionReceipt:
    """Build a simulated (spec-only) execution receipt."""
    return RepoExecutionReceipt(
        execution_state=ExecutionState.simulated,
        command_id=command_id,
        operator_command=operator_command,
        pipeline_id=pipeline_id,
        repo=RepoInfo(repo_name=repo_name, branch=branch),
        execution=ExecutionInfo(),
        files=FilesInfo(),
        tests=TestsInfo(),
        artifacts=ArtifactsInfo(produced=produced_artifacts or []),
        rollback=RollbackInfo(),
        status="simulated",
        recommended_next_state="review",
    )


def build_spec_only_receipt(
    command_id: str,
    operator_command: str,
) -> RepoExecutionReceipt:
    """Build a not-executed (spec-only) receipt."""
    return RepoExecutionReceipt(
        execution_state=ExecutionState.not_executed,
        command_id=command_id,
        operator_command=operator_command,
        status="spec_only",
        recommended_next_state="review",
    )
