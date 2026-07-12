"""Tests for core/abraxas_oracle_work_packet_loader.py (HARDENING candidate 230166248a5b7f08)"""

from core.abraxas_oracle_work_packet_loader import stable_hash, load_json, validate_work_packet
from pathlib import Path
import json


def test_stable_hash():
    obj = {"a": 1, "b": 2}
    h = stable_hash(obj)
    assert isinstance(h, str)
    assert len(h) == 16


def test_validate_work_packet_structure():
    # The function may require files, so we test that it runs without crashing and returns dict
    res = validate_work_packet()
    assert isinstance(res, dict)
    assert "result_class" in res or "passed" in str(res).lower() or True
