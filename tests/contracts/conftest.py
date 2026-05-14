"""Bootstrap P2C-D5 artifact chain for clean CI checkout.

In a fresh clone the d5 artifacts do not exist on disk.  Any test that calls
``d5h.build()`` or reads the d5 files via ``global_closure_audit.build()``
will fail with FileNotFoundError.  This session-scoped fixture generates the
three d5 artifact groups (operator_decision → human_approval →
approval_repair_reverify) exactly once per test session, only when the files
are absent.  The build functions are deterministic, require no network or
external state, and produce sorted-key compact-JSON with a trailing newline.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import run_artifact_contract_p2c_d5_approval_repair_reverify as reverify
from scripts import run_artifact_contract_p2c_d5_human_approval as d5h
from scripts import run_artifact_contract_p2c_d5_operator_decision as d5op


_D5OP = Path("out/contracts/artifact_contract_p2c_d5_operator_decision.latest.json")
_D5H = Path("out/contracts/artifact_contract_p2c_d5_human_approval.latest.json")
_REVERIFY = Path("out/contracts/artifact_contract_p2c_d5_approval_repair_reverify.latest.json")


@pytest.fixture(scope="session", autouse=True)
def bootstrap_p2c_d5_artifacts() -> None:
    """Generate P2C-D5 artifact chain if any artifact in the chain is absent.

    Regenerates from the start of the chain whenever any file is missing so
    that a partial prior run cannot leave the three artifacts in an inconsistent
    state.  In a complete checkout (all files present) this is a no-op.
    """
    if not _D5OP.exists() or not _D5H.exists() or not _REVERIFY.exists():
        d5op.main()
        d5h.main()
        reverify.main()
