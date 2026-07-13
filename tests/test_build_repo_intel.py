"""Tests for skills/abraxas-repo-intel/scripts/build_repo_intel.py (TEST candidate dcb30f82a8a5816f)"""

import sys
import tempfile
from pathlib import Path
import hashlib

sys.path.insert(0, "skills/abraxas-repo-intel/scripts")
import build_repo_intel as b

def test_sha256():
    h = b.sha256("test")
    assert len(h) == 64
    assert isinstance(h, str)

def test_get_file_hash(tmp_path):
    p = tmp_path / "f.txt"
    p.write_text("hello")
    h = b.get_file_hash(p)
    assert len(h) == 64

def test_classify_file_test():
    p = Path("tests/foo.py")
    assert b.classify_file(p) == "test"

def test_classify_file_skill():
    p = Path("skills/bar/SKILL.md")
    assert b.classify_file(p) == "skill"

def test_classify_file_script():
    p = Path("scripts/baz.py")
    assert b.classify_file(p) == "script"

def test_safe_read(tmp_path):
    p = tmp_path / "t.txt"
    p.write_text("short content")
    assert "short" in b.safe_read(p)
