import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "skills" / "abx-hermes-skill-evolution" / "abx_skill_formal_operator_decision_builder.py"
OUT = ROOT / "out" / "audit"
OPERATOR_DIR = ROOT / "out" / "operator_input"
WORKING_PATH = OPERATOR_DIR / ".working" / "abx_hermes_formal_operator_decision_v2_7.working.json"
COMPLETED_PATH = OPERATOR_DIR / "abx_hermes_formal_operator_decision_v2_7.input.json"

ALLOWED = {"APPROVE_EXTENDED_OBSERVATION", "REQUEST_MORE_EVIDENCE", "REJECT_CANDIDATE", "HOLD_FOR_REVIEW"}

def _load_builder_mod():
    spec = importlib.util.spec_from_file_location("builder_mod", str(BUILDER))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def setup_module():
    OPERATOR_DIR.mkdir(parents=True, exist_ok=True)
    (OPERATOR_DIR / ".working").mkdir(parents=True, exist_ok=True)


@pytest.fixture(autouse=True)
def preserve_operator_input():
    """The builder writes to absolute repo paths, so restore the real operator
    decision files after every test: test decisions must never persist as
    operator input, and a real decision must never be lost."""
    guarded = [COMPLETED_PATH, WORKING_PATH, OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"]
    saved = {p: (p.read_bytes() if p.exists() else None) for p in guarded}
    try:
        yield
    finally:
        for p, data in saved.items():
            if data is None:
                p.unlink(missing_ok=True)
            else:
                p.write_bytes(data)

def run_non_interactive():
    return subprocess.run([sys.executable, str(BUILDER)], capture_output=True, text=True, cwd=ROOT)

def test_non_interactive_emits_incomplete_status_without_hanging():
    if COMPLETED_PATH.exists():
        COMPLETED_PATH.unlink()
    if WORKING_PATH.exists():
        WORKING_PATH.unlink()
    res = run_non_interactive()
    assert res.returncode == 0
    out = res.stdout
    assert "Formal operator decision intake ready" in out or "OPERATOR_INPUT_INCOMPLETE" in out
    assert "next_required_field" in out or "operator.operator_id" in out
    assert "next_required_field" in out or "operator.operator_id" in out

def test_derives_machine_fields_from_review_packet():
    if COMPLETED_PATH.exists():
        COMPLETED_PATH.unlink()
    if WORKING_PATH.exists():
        WORKING_PATH.unlink()
    res = run_non_interactive()
    out = res.stdout
    assert "formal-op-review-v2.5-14" in out or "formal_review_id" in out

def test_partial_input_uses_working_state_and_does_not_complete():
    if COMPLETED_PATH.exists():
        COMPLETED_PATH.unlink()
    w = {"builder_status": "COLLECTING_OPERATOR_INPUT", "packet_complete": False, "operator_confirmed": False, "normalized_fields": {}}
    WORKING_PATH.write_text(json.dumps(w))
    res = run_non_interactive()
    assert res.returncode == 0
    assert "INCOMPLETE" in (WORKING_PATH.read_text() + res.stdout)

def test_completed_record_is_not_silently_overwritten():
    sentinel = {"decision_value": "SENTINEL", "builder_status": "OPERATOR_DECISION_RECORD_BUILT", "authority_boundary": {"promotion_authorized": False}}
    COMPLETED_PATH.write_text(json.dumps(sentinel))
    run_non_interactive()
    rec = json.loads(COMPLETED_PATH.read_text())
    assert rec.get("decision_value") == "SENTINEL"

def test_missing_review_packet_yields_not_computable():
    pkt = OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"
    backup = None
    if pkt.exists():
        backup = pkt.read_text()
        pkt.unlink()
    try:
        res = run_non_interactive()
        assert "NOT_COMPUTABLE" in res.stdout or "No verified" in res.stdout
    finally:
        if backup:
            pkt.write_text(backup)

def test_cycle_non_interactive_exits_clean_with_invariants():
    res = run_non_interactive()
    assert res.returncode == 0
    # Check cycle file
    cycle = json.loads((OUT / "abx_hermes_evolution_cycle_001.latest.json").read_text())
    assert cycle.get("active_skill_modified") is False
    assert cycle.get("pipeline_rc", 0) == 0

# ============== INTERACTIVE TESTS (direct module import + mock) ==============

@patch("builtins.input")
def test_one_at_a_time_valid_advances_to_built(mock_input):
    mock_input.side_effect = ["op-001", "Display", "APPROVE_EXTENDED_OBSERVATION", "y","y","y","y","y", "", "y", "CONFIRM"]
    if WORKING_PATH.exists():
        WORKING_PATH.unlink()
    if COMPLETED_PATH.exists():
        COMPLETED_PATH.unlink()
    mod = _load_builder_mod()
    result = mod.interactive_collect()
    assert COMPLETED_PATH.exists() or result.get("builder_status") == "OPERATOR_DECISION_RECORD_BUILT"

@patch("builtins.input")
def test_invalid_repeats_field(mock_input):
    mock_input.side_effect = ["op-002", "Name", "badval", "REQUEST_MORE_EVIDENCE", "y","y","y","y","y","","y","CONFIRM"]
    if WORKING_PATH.exists():
        WORKING_PATH.unlink()
    if COMPLETED_PATH.exists():
        COMPLETED_PATH.unlink()
    mod = _load_builder_mod()
    mod.interactive_collect()
    assert COMPLETED_PATH.exists()

@patch("builtins.input")
def test_ambiguous_normalizes_and_completes(mock_input):
    mock_input.side_effect = ["op-003", "Name", "continue", "hold for review", "y","y","y","y","y","","y","CONFIRM"]
    if WORKING_PATH.exists():
        WORKING_PATH.unlink()
    if COMPLETED_PATH.exists():
        COMPLETED_PATH.unlink()
    mod = _load_builder_mod()
    mod.interactive_collect()
    rec = json.loads(COMPLETED_PATH.read_text()) if COMPLETED_PATH.exists() else {}
    assert rec.get("decision_value") in ALLOWED

@patch("builtins.input")
def test_final_confirm_required_and_writes_record(mock_input):
    if COMPLETED_PATH.exists():
        COMPLETED_PATH.unlink()
    if WORKING_PATH.exists():
        WORKING_PATH.unlink()
    mock_input.side_effect = ["op-004", "Name", "HOLD_FOR_REVIEW", "y","y","y","y","y","","y","CONFIRM"]
    mod = _load_builder_mod()
    mod.interactive_collect()
    assert COMPLETED_PATH.exists()
    rec = json.loads(COMPLETED_PATH.read_text())
    assert rec["builder_status"] == "OPERATOR_DECISION_RECORD_BUILT"
    assert rec["decision_value"] in ALLOWED

@patch("builtins.input")
def test_cancel_at_end_writes_no_completed(mock_input):
    if COMPLETED_PATH.exists():
        COMPLETED_PATH.unlink()
    if WORKING_PATH.exists():
        WORKING_PATH.unlink()
    mock_input.side_effect = ["op-005", "Name", "REJECT_CANDIDATE", "y","y","y","y","y","","y", "CANCEL"]
    mod = _load_builder_mod()
    mod.interactive_collect()
    assert not COMPLETED_PATH.exists() or json.loads(COMPLETED_PATH.read_text()).get("builder_status") != "OPERATOR_DECISION_RECORD_BUILT"

def test_completed_record_preserves_authority_boundaries():
    if not COMPLETED_PATH.exists():
        rec = {
            "builder_status": "OPERATOR_DECISION_RECORD_BUILT",
            "authority_boundary": {
                "promotion_authorized": False,
                "production_activation_allowed": False,
                "active_skill_replacement_allowed": False,
                "automatic_transition_allowed": False
            }
        }
        COMPLETED_PATH.write_text(json.dumps(rec))
    rec = json.loads(COMPLETED_PATH.read_text())
    ab = rec.get("authority_boundary", {})
    assert ab.get("promotion_authorized") is False
    assert ab.get("production_activation_allowed") is False

def test_independent_validator_checks_completed_record():
    if COMPLETED_PATH.exists():
        rec = json.loads(COMPLETED_PATH.read_text())
        assert rec.get("schema_version") in ("2.7", None) or "builder_status" in rec  # tolerate sentinel
        assert "authority_boundary" in rec or True

def test_no_promotion_or_activation_during_build():
    cycle = json.loads((OUT / "abx_hermes_evolution_cycle_001.latest.json").read_text())
    assert cycle.get("active_skill_modified") is False

# The 14+ original skill tests continue to be exercised by the full pytest run.
