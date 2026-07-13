"""Tests for core/sync/notion_sync_packet.py (HARDENING candidate 729dd57a44347555)"""

from core.sync.notion_sync_packet import REQUIRED_FIELDS, ARTIFACT_TYPE, _iso8601_utc

def test_required_fields():
    assert "notion_page_id" in REQUIRED_FIELDS
    assert len(REQUIRED_FIELDS) >= 7

def test_artifact_type():
    assert ARTIFACT_TYPE == "NotionSyncPacket.v1"

def test_iso8601():
    ts = _iso8601_utc()
    assert "Z" in ts or "T" in ts
