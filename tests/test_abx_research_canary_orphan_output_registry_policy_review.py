from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_orphan_output_registry_policy_review import (
    REVIEW_ID,
    build_abx_research_canary_orphan_output_registry_policy_review,
    render_abx_research_canary_orphan_output_registry_policy_review_markdown,
    write_abx_research_canary_orphan_output_registry_policy_review,
)
from core.generated_artifact_registry import build_generated_artifact_registry
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_research_canary_orphan_output_registry_policy_review.py",
    "local_abx_research_canary_orphan_output_registry_policy_review_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/abx_research_canary_orphan_output_registry_policy_review.v1.schema.json"
)


def test_orphan_policy_review_is_deterministic_and_held() -> None:
    first = build_abx_research_canary_orphan_output_registry_policy_review(source_root=REPO_ROOT)
    second = build_abx_research_canary_orphan_output_registry_policy_review(source_root=REPO_ROOT)

    assert first["review_hash"] == second["review_hash"]
    assert first["artifact_id"] == REVIEW_ID
    assert first["status"] == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_HELD_FOR_OPERATOR"
    assert first["policy_review_only"] is True
    assert first["registry_mutation_performed"] is False
    assert first["orphan_count"] == 10
    assert len(first["orphan_records"]) == 10
    assert first["recommended_policy"] == "EXCLUDE_FROM_CANONICAL_REPAIR"
    assert first["downstream_status"] == "ORPHAN_POLICY_REVIEW_HELD_FOR_OPERATOR"
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["execution_allowed"] is False
    assert first["valid_for_execution"] is False
    assert "ORPHAN_OUTPUT_REGISTRY_INCLUSION" in first["blocked_actions"]


def test_orphan_policy_review_blocked_without_audit(tmp_path: Path) -> None:
    packet = build_abx_research_canary_orphan_output_registry_policy_review(source_root=tmp_path)
    assert packet["status"] == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_BLOCKED"
    assert packet["orphan_count"] == 0


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_abx_research_canary_orphan_output_registry_policy_review(
        REPO_ROOT,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["review_hash"] == packet["review_hash"]

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
    markdown = render_abx_research_canary_orphan_output_registry_policy_review_markdown(packet)
    assert markdown[0] == "# ABX Research Canary Orphan Output Registry Policy Review 001"


def test_orphan_policy_review_in_derived_optional_registry() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    emap = {entry.artifact_path: entry for entry in registry.entries}
    json_path = (
        "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.json"
    )
    md_path = (
        "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.md"
    )
    assert emap[json_path].determinism_class == "DERIVED_OPTIONAL"
    assert emap[md_path].determinism_class == "DERIVED_OPTIONAL"
