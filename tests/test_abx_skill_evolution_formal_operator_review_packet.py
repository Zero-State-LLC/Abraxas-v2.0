import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "audit"
PACKET_GEN = ROOT / "skills" / "abx-hermes-skill-evolution" / "abx_skill_formal_operator_review_packet.py"

def test_formal_operator_review_packet_ready_on_valid_evidence():
    res = subprocess.run([sys.executable, str(PACKET_GEN)], capture_output=True, text=True, cwd=ROOT)
    assert res.returncode == 0
    pkt = json.loads((OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").read_text())
    assert pkt["packet_status"] == "FORMAL_OPERATOR_REVIEW_PACKET_READY"
    assert "formal-op-review-v2.5-" in pkt["formal_review_id"]
    assert pkt["evidence_summary"]["targeted_tests_passed"] >= 9
    assert pkt["evidence_summary"]["targeted_tests_failed"] == 0
    assert pkt["evidence_summary"]["live_traces"] >= 7
    assert pkt["evidence_summary"]["active_modified"] is False
    assert pkt["evidence_summary"]["reference_count"] == 3
    assert pkt["authority_boundary"]["advisory_only"] is True
    assert pkt["authority_boundary"]["operator_decision_present"] is False
    assert pkt["authority_boundary"]["promotion_authorized"] is False
    assert pkt["authority_boundary"]["production_activation_allowed"] is False
    assert "APPROVE_EXTENDED_OBSERVATION" in [d["decision"] for d in pkt["allowed_operator_decisions"]]
    assert "FORMAL_OPERATOR_DECISION_REQUIRED" == pkt["recommended_next_lane"]
    assert len(pkt["cross_surface_signals"]) >= 1
    assert pkt["deterministic_hash"]

def test_packet_resolves_formal_review_and_reports_no_mutation():
    pkt = json.loads((OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").read_text())
    assert "formal-op-review-v2.5-" in pkt["formal_review_id"]
    cycle = json.loads((OUT / "abx_hermes_evolution_cycle_001.latest.json").read_text())
    assert cycle.get("active_skill_modified") is False

def test_packet_cross_signals_have_provenance_or_unresolved():
    pkt = json.loads((OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").read_text())
    for sig in pkt["cross_surface_signals"]:
        assert "signal_id" in sig
        assert sig.get("source_artifact") is not None  # either resolved name or SOURCE_UNRESOLVED
        assert sig.get("authority_conferred") is False

def test_packet_no_operator_decision_synthesized():
    pkt = json.loads((OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").read_text())
    assert pkt["authority_boundary"]["operator_decision_present"] is False
    assert "APPROVED" not in str(pkt)
    assert "PROMOTE" not in str(pkt).upper()

def test_packet_deterministic_replay():
    p1 = json.loads((OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").read_text())
    # re-run
    subprocess.run([sys.executable, str(PACKET_GEN)], capture_output=True, text=True, cwd=ROOT)
    p2 = json.loads((OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").read_text())
    assert p1["deterministic_hash"] == p2["deterministic_hash"]

def test_existing_skill_evolution_tests_still_pass():
    # run known passing subset (explicit to avoid glob issues in subprocess)
    res = subprocess.run([sys.executable, "-m", "pytest", "tests/test_abx_skill_evolution_replay.py", "tests/test_abx_skill_evolution_canary.py", "tests/test_abx_skill_evolution_promotion_readiness.py", "tests/test_abx_skill_evolution_promotion_gate.py", "-q", "--tb=no"], capture_output=True, text=True, cwd=ROOT)
    assert res.returncode == 0
    out = res.stdout + res.stderr
    assert "passed" in out.lower() or "....." in out
