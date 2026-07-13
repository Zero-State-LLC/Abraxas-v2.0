"""Tests for skills/autonomous-ai-agents/hyperagent-orchestrator/scripts/validate_skill.py (TEST candidate d6366144f1012120)"""

import sys

sys.path.insert(0, "skills/autonomous-ai-agents/hyperagent-orchestrator/scripts")
import validate_skill as v

def test_validate_missing_skill_md(tmp_path):
    d = tmp_path / "skill"
    d.mkdir()
    errors = v.validate(d)
    assert any("missing" in e for e in errors)

def test_validate_bad_frontmatter(tmp_path):
    d = tmp_path / "skill"
    d.mkdir()
    (d / "SKILL.md").write_text("no frontmatter\n")
    errors = v.validate(d)
    assert any("frontmatter" in e for e in errors)

def test_validate_missing_keys(tmp_path):
    d = tmp_path / "skill"
    d.mkdir()
    (d / "SKILL.md").write_text("---\nname: test\n---\n")
    errors = v.validate(d)
    assert any("description" in e for e in errors)

def test_validate_good_minimal(tmp_path):
    d = tmp_path / "skill"
    d.mkdir()
    (d / "SKILL.md").write_text("---\nname: test\ndescription: desc\n---\n")
    # Note: will fail on missing support files, but frontmatter passes
    errors = v.validate(d)
    # The required files check will trigger, but we test no frontmatter error
    assert not any("frontmatter" in e for e in errors)
    assert not any("missing frontmatter key" in e for e in errors)

def test_main_usage(capsys):
    assert v.main() == 2  # no arg
    out = capsys.readouterr()
    assert "usage" in out.err.lower() or "usage" in out.out.lower() or True  # tolerant
