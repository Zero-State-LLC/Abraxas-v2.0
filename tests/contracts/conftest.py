"""Bootstrap P2C-D5 artifacts through the centralized regeneration spine."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.generated_artifact_registry import (
    build_generated_artifact_registry,
    execute_artifact_regeneration,
)


_D5OP = Path("out/contracts/artifact_contract_p2c_d5_operator_decision.latest.json")
_D5H = Path("out/contracts/artifact_contract_p2c_d5_human_approval.latest.json")
_REVERIFY = Path("out/contracts/artifact_contract_p2c_d5_approval_repair_reverify.latest.json")
_REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session", autouse=True)
def bootstrap_p2c_d5_artifacts() -> None:
    """Regenerate the managed D5 artifact chain if any artifact is missing."""
    if not _D5OP.exists() or not _D5H.exists() or not _REVERIFY.exists():
        registry = build_generated_artifact_registry(_REPO_ROOT)
        execute_artifact_regeneration(
            registry,
            repo_root=_REPO_ROOT,
            selected_artifacts=[
                _D5OP.as_posix(),
                _D5H.as_posix(),
                _REVERIFY.as_posix(),
            ],
        )
