"""Receipt models for ABRAXAS v2.0."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority
from core.governance.doctrine import SCHEMA_VERSION_RECEIPT


class ExecutionState(str, Enum):
    not_executed = "not_executed"
    simulated = "simulated"
    local_executed = "local_executed"
    ci_executed = "ci_executed"
    committed = "committed"
    failed = "failed"
    not_computable = "not_computable"


class RepoInfo(BaseModel):
    repo_name: str = ""
    branch: str = ""
    commit_sha: str = ""

    model_config = {"frozen": True}


class ExecutionInfo(BaseModel):
    exit_code: int | None = None
    result_commit: str | None = None
    duration_seconds: float | None = None

    model_config = {"frozen": True}


class FilesInfo(BaseModel):
    changed: list[str] = []
    created: list[str] = []
    deleted: list[str] = []

    model_config = {"frozen": True}


class TestsInfo(BaseModel):
    status: str = "not_run"
    test_command: str = ""
    passed: int = 0
    failed: int = 0

    model_config = {"frozen": True}


class ArtifactsInfo(BaseModel):
    produced: list[str] = []

    model_config = {"frozen": True}


class RollbackInfo(BaseModel):
    rollback_available: bool = False
    rollback_command: str = ""

    model_config = {"frozen": True}


class RepoExecutionReceipt(BaseModel):
    """Execution receipt for a Kernel Zero operation."""

    schema_version: Literal["RepoExecutionReceipt.v1"] = SCHEMA_VERSION_RECEIPT
    execution_state: ExecutionState
    command_id: str
    operator_command: str
    pipeline_id: str | None = None
    repo: RepoInfo = RepoInfo()
    execution: ExecutionInfo = ExecutionInfo()
    files: FilesInfo = FilesInfo()
    tests: TestsInfo = TestsInfo()
    artifacts: ArtifactsInfo = ArtifactsInfo()
    rollback: RollbackInfo = RollbackInfo()
    authority: Authority = Authority()
    status: str = "pending"
    not_computable_reasons: list[str] = []
    recommended_next_state: str = "review"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate_state_constraints(self) -> "RepoExecutionReceipt":
        state = self.execution_state

        if state == ExecutionState.committed and not self.execution.result_commit:
            raise ValueError("committed state requires execution.result_commit")

        if state == ExecutionState.local_executed and self.execution.exit_code is None:
            raise ValueError("local_executed state requires execution.exit_code")

        if state == ExecutionState.simulated and self.execution.result_commit:
            raise ValueError("simulated state cannot claim result_commit")

        if state == ExecutionState.not_executed and (
            self.files.changed or self.files.created or self.files.deleted
        ):
            raise ValueError("not_executed state cannot claim changed files")

        if self.tests.status == "passed" and not self.tests.test_command:
            raise ValueError("tests.status='passed' requires tests.test_command")

        self.authority.assert_locked()
        return self

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
