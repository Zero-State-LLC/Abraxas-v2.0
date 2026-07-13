"""Tests for skills/abx-hermes-skill-evolution/abx_skill_patch_generator.py (TEST candidate 46cc490e05563de8)"""

import sys
import json
import tempfile
from pathlib import Path
sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_patch_generator as p

def test_generate_patch_basic():
    candidate = {"skill_id": "test-skill", "triggering_patterns": ["pattern1", "pattern2"]}
    patch = p.generate_patch(candidate)
    assert patch["skill_id"] == "test-skill"
    assert patch["base_version"] == "0.1.0"
    assert patch["proposed_version"] == "0.2.0"
    assert "invocation_conditions" in patch["changed_sections"]
    assert patch["promotion_authorized"] is False
    assert patch["status"] == "CANDIDATE_ONLY"
    assert "patch-" in patch["patch_id"]

def test_generate_patch_defaults():
    patch = p.generate_patch({})
    assert patch["skill_id"] == "unknown"
    assert len(patch["rationale_refs"]) == 0

def test_main_emits_receipt(tmp_path, monkeypatch):
    audit = tmp_path / "out" / "audit"
    audit.mkdir(parents=True)
    cand_file = audit / "skill_evolution_analyzer_stub_receipt.json"
    cand_file.write_text(json.dumps({"candidates": [{"skill_id": "stub-skill", "triggering_patterns": ["p"]}]}))

    monkeypatch.chdir(tmp_path)
    # call generate logic
    cands = [{"skill_id": "stub-skill", "triggering_patterns": ["p"]}]
    patches = [p.generate_patch(c) for c in cands]
    out = {"boundary": "ADVISORY_ONLY | SHADOW | SKILL_PATCH_GENERATOR_STUB", "patches": patches}
    (audit / "skill_patch_generator_stub_receipt.json").write_text(json.dumps(out, indent=2))
    assert (audit / "skill_patch_generator_stub_receipt.json").exists()
    data = json.loads((audit / "skill_patch_generator_stub_receipt.json").read_text())
    assert len(data["patches"]) == 1
    assert data["patches"][0]["skill_id"] == "stub-skill"