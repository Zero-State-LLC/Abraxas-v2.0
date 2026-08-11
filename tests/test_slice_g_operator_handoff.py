from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.operator_loop import validate_handoff
from core.slice_g_operator_handoff import (
    AUTHORITY_LOCKS,
    DEFAULT_FIXTURE,
    build_slice_g_operator_handoff_review,
    render_slice_g_operator_handoff_markdown,
    write_slice_g_operator_handoff_review,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_slice_g_builds_volume_derived_handoff_and_patch() -> None:
    receipt = build_slice_g_operator_handoff_review(repo_root=REPO_ROOT)

    assert receipt["status"] == "SLICE_G_OPERATOR_HANDOFF_READY_ADVISORY_ONLY"
    assert receipt["issue"] == 1111
    assert receipt["trace_count"] == 2
    assert receipt["operator_review"]["disposition_state"] == "OPERATOR_REVIEW_REQUIRED"

    patch = receipt["skill_patch_candidate"]
    assert patch["schema_version"] == "SkillPatchCandidate.v1"
    assert patch["status"] == "CANDIDATE_ONLY"
    assert patch["promotion_authorized"] is False
    assert patch["execution_authority"] is False
    assert patch["canon_mutation_allowed"] is False
    assert patch["mount_authorized"] is False
    assert patch["clear_coupling_allowed"] is False
    assert "high_hermes_signal_volume" in patch["rationale_refs"]

    handoff = receipt["handoff_envelope"]
    validate_handoff(handoff)
    assert handoff["schema_version"] == "HandoffEnvelope.v1"
    assert handoff["authority"]["execution_authority"] is False
    assert handoff["authority"]["auto_canon_promotion"] is False
    assert handoff["authority"]["operator_review_on_semantic_conflict"] is True


def test_slice_g_receipt_hash_and_ids_are_deterministic() -> None:
    first = build_slice_g_operator_handoff_review(repo_root=REPO_ROOT)
    second = build_slice_g_operator_handoff_review(repo_root=REPO_ROOT)

    assert first == second
    body = {key: value for key, value in first.items() if key != "canonical_hash"}
    assert first["canonical_hash"] == canonical_hash(body)
    assert first["handoff_envelope"]["handoff_id"].startswith("HO-slice-g-")
    assert first["skill_patch_candidate"]["patch_id"].startswith("patch-slice-g-")


def test_slice_g_authority_locks_are_closed() -> None:
    receipt = build_slice_g_operator_handoff_review(repo_root=REPO_ROOT)

    assert receipt["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in receipt["authority_locks"].values())
    assert "No CLEAR or production activation coupling." in receipt["non_goals"]
    assert "do not promote" in receipt["handoff_envelope"]["next_recommended_action"]


def test_slice_g_runner_writes_receipt_and_markdown(tmp_path: Path) -> None:
    out = tmp_path / "slice_g.json"
    md = tmp_path / "slice_g.md"
    receipt = write_slice_g_operator_handoff_review(
        repo_root=REPO_ROOT,
        fixture_path=DEFAULT_FIXTURE,
        out_path=out,
        md_path=md,
    )

    assert out.exists()
    assert md.exists()
    assert json.loads(out.read_text(encoding="utf-8"))["canonical_hash"] == receipt["canonical_hash"]
    markdown = md.read_text(encoding="utf-8")
    assert "Operator disposition is required" in markdown
    assert "execution_authority: `false`" in markdown


def test_slice_g_operator_markdown_documents_cli_and_risks() -> None:
    receipt = build_slice_g_operator_handoff_review(repo_root=REPO_ROOT)
    markdown = render_slice_g_operator_handoff_markdown(receipt)

    assert "abraxas os evolution-review" in markdown
    assert "SkillPatchCandidate" in markdown
    assert "Residual risks" in markdown
    assert "clear_coupling_allowed: `false`" in markdown
