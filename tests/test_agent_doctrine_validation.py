from __future__ import annotations

from scripts.governance.validate_agent_doctrine import (
    AGENTS,
    MASTER,
    ROOT,
    SKILLS,
    parse_skill_registry,
    validate,
)


def test_agent_doctrine_validator_passes_current_surfaces() -> None:
    result = validate()

    assert result["ok"] is True, result["errors"]
    assert result["skill_count"] >= 10


def test_skills_registry_references_existing_skill_files() -> None:
    rows = parse_skill_registry(SKILLS.read_text(encoding="utf-8"))

    assert rows
    for row in rows:
        assert row.default == "false"
        assert row.status in {
            "ACTIVE",
            "SPECIALIZED",
            "SUPERSEDED",
            "LEGACY",
            "CANDIDATE_FOR_MERGE",
        }
        assert (ROOT / row.path).is_file()


def test_agents_declares_required_execution_model() -> None:
    text = AGENTS.read_text(encoding="utf-8")

    assert "MSW execution kernel" in text
    assert "DIRECT" in text
    assert "BOUNDED" in text
    assert "OPERATOR_LOOP" in text
    assert "FORECAST" in text
    assert "MASTER_LOOP" in text
    assert "Normal bounded engineering does not require WorkPackets" in text
    assert "SHADOW:" in text and "FORECAST:" in text
    assert "docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md" in text


def test_master_loop_is_specialized_not_default() -> None:
    text = MASTER.read_text(encoding="utf-8")

    assert "status: SPECIALIZED" in text
    assert "default: false" in text
    assert "Not the default for bounded engineering" in text
    assert "Never just respond" not in text
    assert "ordinary bounded engineering" in text


def test_historical_material_was_extracted_from_agents() -> None:
    agents = AGENTS.read_text(encoding="utf-8")
    historical = (ROOT / "docs/status/HISTORICAL_GOVERNANCE_AGENT_NOTES.md").read_text(
        encoding="utf-8"
    )

    assert "Temporal continuity P102 handoff" not in agents
    assert "Research canary spine-refresh isolation guardrail" not in agents
    assert "HISTORICAL_GOVERNANCE_AGENT_NOTES.md" in agents
    assert "Temporal continuity P102 handoff archive" in historical
    assert "Research canary spine-refresh isolation guardrail" in historical


def test_codex_and_cursor_packet_workflow_is_conditional() -> None:
    codex = (ROOT / "docs/CODEX_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")
    cursor = (ROOT / ".cursor/rules/operator-loop-ownership.mdc").read_text(
        encoding="utf-8"
    )

    assert "Before ordinary bounded edits" in codex
    assert "When an active WorkPacket is supplied" in codex
    assert "Routine bounded engineering" in cursor
    assert "When an active `WorkPacket.v1` is supplied" in cursor
