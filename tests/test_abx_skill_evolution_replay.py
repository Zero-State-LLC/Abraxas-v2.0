import json
import pytest
from pathlib import Path

def test_replay_corpus_schema_and_frozen():
    corpus = json.loads(Path("out/audit/abx_hermes_replay_corpus_v2_2.latest.json").read_text())
    assert corpus["status"] == "FROZEN"
    assert corpus["case_count"] >= 6
    assert corpus["provenance_complete"] is True

def test_replay_comparison_has_no_regressions():
    comp = json.loads(Path("out/audit/abx_hermes_replay_comparison_v2_2.latest.json").read_text())
    assert len(comp.get("candidate_regressions", [])) == 0 or comp["promotion_recommendation"] in ("CANARY_ELIGIBLE", "HOLD")