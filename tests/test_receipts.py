"""Tests for receipt models and builders."""

from __future__ import annotations

import pytest

from core.receipts.builder import build_simulated_receipt, build_spec_only_receipt
from core.receipts.models import (
    ArtifactsInfo,
    ExecutionInfo,
    ExecutionState,
    FilesInfo,
    RepoExecutionReceipt,
    RepoInfo,
    RollbackInfo,
    RollbackMethod,
    TestsInfo as ReceiptTestsInfo,
    TestsStatus as ReceiptTestsStatus,
)


def test_simulated_receipt_builds() -> None:
    receipt = build_simulated_receipt(
        command_id="TEST_CMD",
        operator_command="test command",
    )
    assert receipt.execution_state == ExecutionState.simulated
    assert receipt.command_id == "TEST_CMD"
    assert receipt.tests.status == ReceiptTestsStatus.simulated


def test_spec_only_receipt_builds() -> None:
    receipt = build_spec_only_receipt(
        command_id="SPEC_CMD",
        operator_command="spec command",
    )
    assert receipt.execution_state == ExecutionState.not_executed
    assert receipt.status == "spec_only"


def test_committed_requires_result_commit() -> None:
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.committed,
            command_id="CMD",
            operator_command="op cmd",
            repo=RepoInfo(result_commit=None),
        )


def test_committed_with_result_commit_ok() -> None:
    receipt = RepoExecutionReceipt(
        execution_state=ExecutionState.committed,
        command_id="CMD",
        operator_command="op cmd",
        repo=RepoInfo(result_commit="abc123"),
    )
    assert receipt.execution_state == ExecutionState.committed


def test_local_executed_requires_exit_code() -> None:
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.local_executed,
            command_id="CMD",
            operator_command="op cmd",
            execution=ExecutionInfo(exit_code=None),
        )


def test_local_executed_with_exit_code_ok() -> None:
    receipt = RepoExecutionReceipt(
        execution_state=ExecutionState.local_executed,
        command_id="CMD",
        operator_command="op cmd",
        execution=ExecutionInfo(exit_code=0),
    )
    assert receipt.execution_state == ExecutionState.local_executed


def test_simulated_cannot_claim_result_commit() -> None:
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.simulated,
            command_id="CMD",
            operator_command="op cmd",
            repo=RepoInfo(result_commit="abc123"),
        )


def test_not_executed_cannot_claim_changed_files() -> None:
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.not_executed,
            command_id="CMD",
            operator_command="op cmd",
            files=FilesInfo(added=["some_file.py"]),
        )


def test_passed_tests_require_test_commands() -> None:
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.local_executed,
            command_id="CMD",
            operator_command="pytest -q",
            execution=ExecutionInfo(exit_code=0),
            tests=ReceiptTestsInfo(status=ReceiptTestsStatus.passed),
        )


def test_artifact_hashes_require_generated_entries() -> None:
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.simulated,
            command_id="CMD",
            operator_command="python demo.py",
            artifacts=ArtifactsInfo(
                generated=[],
                artifact_hashes={"out/demo.json": "abc"},
            ),
        )


def test_rollback_available_requires_method_and_ref() -> None:
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.local_executed,
            command_id="CMD",
            operator_command="pytest -q",
            execution=ExecutionInfo(exit_code=0),
            rollback=RollbackInfo(
                available=True,
                method=RollbackMethod.git_revert,
                rollback_ref=None,
                rollback_patch_hash=None,
            ),
        )


def test_receipt_id_is_deterministic() -> None:
    first = RepoExecutionReceipt(
        execution_state=ExecutionState.simulated,
        command_id="CMD",
        operator_command="python demo.py",
    )
    second = RepoExecutionReceipt(
        execution_state=ExecutionState.simulated,
        command_id="CMD",
        operator_command="python demo.py",
    )
    assert first.receipt_id == second.receipt_id
