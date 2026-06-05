"""Receipt models for ABRAXAS v2.0."""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from core.governance.authority import Authority
from core.governance.doctrine import SCHEMA_VERSION_RECEIPT


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ExecutionState(str, Enum):
    not_executed = "not_executed"
    simulated = "simulated"
    local_executed = "local_executed"
    ci_executed = "ci_executed"
    committed = "committed"
    failed = "failed"
    not_computable = "not_computable"


class RollbackMethod(str, Enum):
    git_revert = "git_revert"
    patch_reverse = "patch_reverse"
    snapshot_restore = "snapshot_restore"
    not_available = "not_available"
    not_computable = "not_computable"


class TestsStatus(str, Enum):
    passed = "passed"
    failed = "failed"
    not_run = "not_run"
    not_computable = "not_computable"
    simulated = "simulated"


class VerificationInfo(BaseModel):
    receipt_hash_algorithm: Literal["sha256_canonical_json"] = "sha256_canonical_json"
    canonical_json: bool = True
    deterministic_sorting: bool = True
    numeric_rounding: int = 6

    model_config = {"frozen": True}


class RepoInfo(BaseModel):
    repo_url: str | None = None
    repo_name: str | None = None
    branch: str | None = None
    base_commit: str | None = None
    result_commit: str | None = None
    dirty_worktree_before: bool | None = None
    dirty_worktree_after: bool | None = None

    model_config = {"frozen": True}


class ExecutionInfo(BaseModel):
    command: str | None = None
    cwd: str | None = None
    exit_code: int | None = None
    stdout_hash: str | None = None
    stderr_hash: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    duration_ms: int | None = None
    ci_run_id: str | None = None
    ci_run_url: str | None = None

    model_config = {"frozen": True}


class FilesInfo(BaseModel):
    added: list[str] = Field(default_factory=list)
    modified: list[str] = Field(default_factory=list)
    deleted: list[str] = Field(default_factory=list)
    renamed: list[str] = Field(default_factory=list)
    diff_hash: str | None = None

    model_config = {"frozen": True}

    def has_changes(self) -> bool:
        return bool(self.added or self.modified or self.deleted or self.renamed)


class TestsInfo(BaseModel):
    commands: list[str] = Field(default_factory=list)
    status: TestsStatus = TestsStatus.not_run
    test_report_hashes: list[str] = Field(default_factory=list)
    coverage_hash: str | None = None

    model_config = {"frozen": True}


class ArtifactsInfo(BaseModel):
    generated: list[str] = Field(default_factory=list)
    artifact_hashes: dict[str, str] = Field(default_factory=dict)

    model_config = {"frozen": True}


class RollbackInfo(BaseModel):
    available: bool = False
    method: RollbackMethod = RollbackMethod.not_available
    rollback_ref: str | None = None
    rollback_patch_hash: str | None = None

    model_config = {"frozen": True}


class RepoExecutionReceipt(BaseModel):
    """Execution receipt for governed repo work."""

    schema_version: Literal["RepoExecutionReceipt.v1"] = SCHEMA_VERSION_RECEIPT
    receipt_id: str | None = None
    execution_state: ExecutionState
    command_id: str
    operator_command: str
    pipeline_id: str | None = None
    source_artifact_refs: list[str] = Field(default_factory=list)
    repo: RepoInfo = Field(default_factory=RepoInfo)
    execution: ExecutionInfo = Field(default_factory=ExecutionInfo)
    files: FilesInfo = Field(default_factory=FilesInfo)
    tests: TestsInfo = Field(default_factory=TestsInfo)
    artifacts: ArtifactsInfo = Field(default_factory=ArtifactsInfo)
    rollback: RollbackInfo = Field(default_factory=RollbackInfo)
    authority: Authority = Field(default_factory=Authority)
    verification: VerificationInfo = Field(default_factory=VerificationInfo)
    status: Literal["valid", "invalid", "failed", "not_computable", "spec_only", "simulated"] = "valid"
    not_computable_reasons: list[str] = Field(default_factory=list)
    recommended_next_state: str = "review"

    model_config = {"frozen": True}

    def canonical_payload(self) -> dict[str, Any]:
        payload = self.model_dump()
        payload.pop("receipt_id", None)
        return payload

    def canonical_json(self) -> str:
        return _canonical_json(self.canonical_payload())

    def computed_receipt_id(self) -> str:
        return _sha256_text(self.canonical_json())

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

    @model_validator(mode="after")
    def _validate_state_constraints(self) -> "RepoExecutionReceipt":
        state = self.execution_state

        if state == ExecutionState.committed and not self.repo.result_commit:
            raise ValueError("committed state requires repo.result_commit")

        if state == ExecutionState.local_executed and self.execution.exit_code is None:
            raise ValueError("local_executed state requires execution.exit_code")

        if state == ExecutionState.ci_executed:
            if self.execution.exit_code is None:
                raise ValueError("ci_executed state requires execution.exit_code")
            if not (self.execution.ci_run_id or self.execution.ci_run_url):
                raise ValueError("ci_executed state requires execution.ci_run_id or execution.ci_run_url")

        if state == ExecutionState.simulated and self.repo.result_commit:
            raise ValueError("simulated state cannot claim repo.result_commit")

        if state == ExecutionState.not_executed and self.files.has_changes():
            raise ValueError("not_executed state cannot claim changed files")

        if self.tests.status == TestsStatus.passed and not self.tests.commands:
            raise ValueError("tests.status='passed' requires tests.commands")

        if self.artifacts.artifact_hashes:
            missing = sorted(set(self.artifacts.artifact_hashes) - set(self.artifacts.generated))
            if missing:
                raise ValueError(f"artifact hashes reference missing generated artifacts: {missing}")

        if self.rollback.available:
            if self.rollback.method in {RollbackMethod.not_available, RollbackMethod.not_computable}:
                raise ValueError("rollback.available=true requires a concrete rollback.method")
            if not (self.rollback.rollback_ref or self.rollback.rollback_patch_hash):
                raise ValueError("rollback.available=true requires rollback_ref or rollback_patch_hash")

        self.authority.assert_locked()

        expected = self.computed_receipt_id()
        if self.receipt_id is None:
            object.__setattr__(self, "receipt_id", expected)
        elif self.receipt_id != expected:
            raise ValueError("receipt_id does not match canonical receipt hash")

        return self
