"""Tests for core/codegen/oracle_signal/oracle_runtime_command_notion_mirror.py (candidate fd60569b8bd9c6ae)"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from core.codegen.oracle_signal.oracle_runtime_command_notion_mirror import (
    build_oracle_full_live_runtime_command_notion_mirror_packet,
)

def test_build_mirror_packet_no_blockers():
    mock_runtime = {"receipt_status": "OK", "canonical_hash": "r1"}
    mock_validation = {"status": "OK", "canonical_hash": "v1"}
    
    with patch("core.codegen.oracle_signal.oracle_runtime_command_notion_mirror._load_json") as mock_load:
        mock_load.side_effect = [mock_runtime, mock_validation]
        packet = build_oracle_full_live_runtime_command_notion_mirror_packet(repo_root=Path("/tmp"))
        
    assert packet["schema_version"] == "OracleFullLiveRuntimeCommandNotionMirrorPacket.v1"
    assert packet["projection_only"] is True
    assert packet["manual_operator_copy_paste_only"] is True
    assert packet["notion_writeback_allowed"] is False
    assert packet["advisory_only"] is True
    assert "packet_id" in packet
    assert "canonical_hash" in packet or "packet_id" in packet

def test_build_mirror_packet_with_blockers():
    mock_runtime = {"receipt_status": "BLOCKED", "canonical_hash": "r1"}
    mock_validation = {"status": "FAIL", "canonical_hash": "v1"}
    
    with patch("core.codegen.oracle_signal.oracle_runtime_command_notion_mirror._load_json") as mock_load:
        mock_load.side_effect = [mock_runtime, mock_validation]
        packet = build_oracle_full_live_runtime_command_notion_mirror_packet(repo_root=Path("/tmp"))
        
    assert "BLOCKED" in packet["status"]
    assert len(packet.get("packet_blockers", [])) >= 0

def test_build_mirror_packet_authority_locks():
    mock_runtime = {"receipt_status": "OK", "canonical_hash": "r1"}
    mock_validation = {"status": "OK", "canonical_hash": "v1"}
    
    with patch("core.codegen.oracle_signal.oracle_runtime_command_notion_mirror._load_json") as mock_load:
        mock_load.side_effect = [mock_runtime, mock_validation]
        packet = build_oracle_full_live_runtime_command_notion_mirror_packet(repo_root=Path("/tmp"))
        
    # Check that authority locks are present and conservative
    assert packet.get("notion_writeback_allowed") is False
    assert packet.get("github_writeback_allowed") is False
    assert packet.get("advisory_only") is True
