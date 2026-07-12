"""Tests for core/abraxas_oracle_execution_boundary.py - comprehensive coverage for governance boundary."""

import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.abraxas_oracle_execution_boundary import create_execution_boundary, compute_boundary_hash

def test_create_execution_boundary_layer0():
    cand = {"candidate_id": "026cbd84c4d47685", "title": "Add comprehensive tests for core/abraxas_oracle_execution_boundary.py"}
    pkt = {"affected_paths": ["core/abraxas_oracle_execution_boundary.py"], "allowed_operations": ["CREATE_TEST_FILE"]}
    b = create_execution_boundary(candidate_id="026cbd84c4d47685", work_packet=pkt, candidate=cand)
    assert b["governance_layer"] == 0
    assert b["automatic_under_engineering_approval"] is True
    assert b["execution_mode"] == "ADVISORY_ENGINEERING"
    assert "boundary_hash" in b
    assert b["all_authority_false"] is True
    assert "production_activation_allowed" not in b or b.get("production_activation_allowed") is False

def test_boundary_hash_deterministic():
    cand = {"candidate_id": "test123", "title": "test"}
    pkt = {"affected_paths": ["core/foo.py"]}
    b1 = create_execution_boundary("test123", pkt, cand)
    b2 = create_execution_boundary("test123", pkt, cand)
    assert b1["boundary_hash"] == b2["boundary_hash"]

def test_prohibited_operations_present():
    cand = {"candidate_id": "test456", "title": "test"}
    pkt = {"affected_paths": ["core/bar.py"]}
    b = create_execution_boundary("test456", pkt, cand)
    prohibited = b["prohibited_operations"]
    assert "production_activation" in prohibited
    assert "canon_mutation" in prohibited
    assert "shadow_promotion" in prohibited
    assert "test_weakening" in prohibited

def test_stratification_evidence_present():
    cand = {"candidate_id": "test789", "title": "test"}
    pkt = {"affected_paths": ["core/baz.py"]}
    b = create_execution_boundary("test789", pkt, cand)
    assert "stratification_evidence" in b
    assert b["stratification_evidence"]["layer"] == 0

if __name__ == "__main__":
    pytest.main([__file__, "-q"])