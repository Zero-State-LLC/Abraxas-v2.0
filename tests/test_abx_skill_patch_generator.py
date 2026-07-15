"""Tests for skills/abx-hermes-skill-evolution/abx_skill_patch_generator.py (TEST candidate 46cc490e05563de8)"""

import sys
import json
sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_patch_generator as p
from core.canonical.json import canonical_dumps

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


def test_generate_stabilization_patch_is_bounded_and_reversible():
    patch = p.generate_stabilization_patch(
        {
            "failure_class": "FAILURE.CLASS.PUBLIC_API_BREAK",
            "exact_regression_test": "tests/test_public_api.py::test_compatibility",
        }
    )
    assert patch["patch_mode"] == "PATCH_MODE.MINIMAL_COMPATIBILITY_REPAIR"
    assert patch["preserve_public_behavior"] is True
    assert patch["reversible"] is True
    assert patch["authority_conferred"] is False

def test_main_emits_receipt(tmp_path, monkeypatch):
    audit = tmp_path / "out" / "audit"
    audit.mkdir(parents=True)
    cand_file = audit / "skill_evolution_analyzer_stub_receipt.json"
    cand_file.write_text(json.dumps({"candidates": [{"skill_id": "stub-skill", "triggering_patterns": ["p"]}]}))

    monkeypatch.chdir(tmp_path)
    p.main()
    output = audit / "skill_patch_generator_stub_receipt.json"
    data = json.loads(output.read_text(encoding="utf-8"))
    assert len(data["patches"]) == 1
    assert data["patches"][0]["skill_id"] == "stub-skill"
    assert output.read_text(encoding="utf-8") == canonical_dumps(data) + "\n"
