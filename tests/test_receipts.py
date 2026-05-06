"""Tests for receipt models and builder."""

from __future__ import annotations

import pytest

from core.receipts.builder import build_simulated_receipt, build_spec_only_receipt
from core.receipts.models import (
    ExecutionInfo,
    ExecutionState,
    FilesInfo,
    RepoExecutionReceipt,
)


def test_simulated_receipt_builds():
    receipt = build_simulated_receipt(
        command_id="TEST_CMD",
        operator_command="test command",
    )
    assert receipt.execution_state == ExecutionState.simulated
    assert receipt.command_id == "TEST_CMD"


def test_spec_only_receipt_builds():
    receipt = build_spec_only_receipt(
        command_id="SPEC_CMD",
        operator_command="spec command",
    )
    assert receipt.execution_state == ExecutionState.not_executed


def test_committed_requires_result_commit():
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.committed,
            command_id="CMD",
            operator_command="op cmd",
            execution=ExecutionInfo(result_commit=None),
        )


def test_committed_with_result_commit_ok():
    receipt = RepoExecutionReceipt(
        execution_state=ExecutionState.committed,
        command_id="CMD",
        operator_command="op cmd",
        execution=ExecutionInfo(result_commit="abc123"),
    )
    assert receipt.execution_state == ExecutionState.committed


def test_local_executed_requires_exit_code():
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.local_executed,
            command_id="CMD",
            operator_command="op cmd",
            execution=ExecutionInfo(exit_code=None),
        )


def test_local_executed_with_exit_code_ok():
    receipt = RepoExecutionReceipt(
        execution_state=ExecutionState.local_executed,
        command_id="CMD",
        operator_command="op cmd",
        execution=ExecutionInfo(exit_code=0),
    )
    assert receipt.execution_state == ExecutionState.local_executed


def test_simulated_cannot_claim_result_commit():
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.simulated,
            command_id="CMD",
            operator_command="op cmd",
            execution=ExecutionInfo(result_commit="abc123"),
        )


def test_not_executed_cannot_claim_changed_files():
    with pytest.raises(Exception):
        RepoExecutionReceipt(
            execution_state=ExecutionState.not_executed,
            command_id="CMD",
            operator_command="op cmd",
            files=FilesInfo(changed=["some_file.py"]),
        )


def test_authority_locked_in_receipt():
    receipt = build_simulated_receipt("ID", "cmd")
    receipt.authority.assert_locked()
