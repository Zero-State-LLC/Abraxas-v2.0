"""Tests for WP-H Notion readiness mapping."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.production_readiness.notion_readiness_mapping import (
    build_notion_readiness_mapping,
)


REPO = Path(__file__).resolve().parents[1]


def test_notion_mapping_shape_and_writeback_flags() -> None:
    mapping = build_notion_readiness_mapping(REPO, write=False)
    assert mapping["schema_version"] == "notion_readiness_mapping.v1"
    # WP-H+ records live writeback refs; producer itself does not call Notion.
    assert mapping["writeback_performed"] is True
    assert mapping["summary"]["live_writeback"] is True
    assert mapping["evidence_state"] == "Partial"
    assert mapping["risk_012"]["status"] == "MITIGATING"
    assert len(mapping["notion_surfaces"]) >= 3
    assert mapping["summary"]["repo_link_count"] >= 5
    # Hub page id from MCP discovery must be present
    ids = {s["page_id"] for s in mapping["notion_surfaces"]}
    assert "3a03e8ba-2f5c-81da-bb78-c514f5ce06e2" in ids
    assert mapping["live_writeback_refs"]["evidence_child_page_id"]


def test_notion_mapping_schema() -> None:
    mapping = build_notion_readiness_mapping(REPO, write=False)
    schema = json.loads(
        (
            REPO
            / "contracts/production_readiness/notion_readiness_mapping.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=mapping, schema=schema)


def test_repo_evidence_paths_mostly_present() -> None:
    mapping = build_notion_readiness_mapping(REPO, write=False)
    assert mapping["summary"]["repo_paths_missing"] == 0
