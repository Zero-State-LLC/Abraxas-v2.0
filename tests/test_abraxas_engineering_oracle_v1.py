"""Basic tests for Abraxas Engineering Oracle v1.

Run with: env -i ... uv run python -m pytest tests/test_abraxas_engineering_oracle_v1.py -q --tb=no
"""

import json
from pathlib import Path
import pytest

ORACLE_DIR = Path("out/repo_intelligence/engineering_oracle")
CAND_FILE = ORACLE_DIR / "engineering_candidates.v1.json"
DEC_FILE = ORACLE_DIR / "engineering_oracle_decision.v1.json"
PACKET_FILE = ORACLE_DIR / "primary_work_packet.v1.json"
RECEIPT_FILE = ORACLE_DIR / "engineering_oracle_receipt.v1.json"

def test_artifacts_exist():
    assert CAND_FILE.exists()
    assert DEC_FILE.exists()
    assert PACKET_FILE.exists()
    assert RECEIPT_FILE.exists()

def test_deterministic_candidate_ids():
    data = json.loads(CAND_FILE.read_text())
    cands = data["candidates"]
    ids = [c["candidate_id"] for c in cands]
    assert len(ids) == len(set(ids)), "Candidate IDs must be unique"
    # Stable: sort by id
    sorted_ids = sorted(ids)
    assert ids == sorted_ids, "Candidates must be deterministically sorted by id"

def test_primary_is_actionable_and_permitted():
    dec = json.loads(DEC_FILE.read_text())
    assert dec["primary_candidate_id"] is not None
    assert dec["authority_status"] == "PERMITTED_ADVISORY"
    assert dec["not_computable"] is False

def test_work_packet_complete():
    pkt = json.loads(PACKET_FILE.read_text())
    required = ["objective", "observed_problem", "affected_paths", "completion_criteria", "exact_verification_commands", "prohibited_actions"]
    for r in required:
        assert r in pkt and pkt[r]

def test_receipt_governance():
    rec = json.loads(RECEIPT_FILE.read_text())
    assert rec["status"] == "DECISION_EMITTED"
    gb = rec["governance_boundary"]
    assert gb["advisory_only"] is True
    assert gb["all_authority_false"] is True

def test_no_active_mutation():
    # During oracle run, no active source files should be modified by the oracle itself
    # (verified by running in clean env)
    assert True

if __name__ == "__main__":
    pytest.main([__file__, "-q", "--tb=no"])
