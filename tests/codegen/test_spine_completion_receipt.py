from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.codegen.spine_completion import build_codegen_spine_completion_receipt

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_codegen_spine_completion_receipt_observes_required_paths() -> None:
    receipt = build_codegen_spine_completion_receipt(repo_root=REPO_ROOT)

    assert receipt["spine_status"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_COMPUTABLE"
    assert receipt["observed_path_count"] == receipt["required_path_count"]
    assert receipt["valid_for_execution"] is False
    assert receipt["valid_for_runtime_activation"] is False
    assert receipt["valid_for_canon_promotion"] is False
    assert receipt["authority_locks"]["notion_writeback"] is False
    assert receipt["authority_locks"]["github_writeback"] is False


def test_codegen_spine_completion_receipt_hash_is_stable() -> None:
    receipt = build_codegen_spine_completion_receipt(repo_root=REPO_ROOT)

    assert receipt["canonical_hash"] == canonical_hash(
        {key: value for key, value in receipt.items() if key != "canonical_hash"}
    )
