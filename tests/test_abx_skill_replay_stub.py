"""Tests for skills/abx-hermes-skill-evolution/abx_skill_replay_stub.py (TEST candidate 9da2d4c2da9932f3)"""

import sys
sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_replay_stub as r

def test_score_case_holler_oracle():
    case = {"task_class": "holler_oracle_full_live"}
    s = r.score_case(case, True)
    assert s["required_satisfied"] == 1
    assert s["completion_correct"] == 1
    assert s["evidence_correct"] == 1

def test_score_case_repo_canonicalization():
    case = {"task_class": "repo_canonicalization"}
    s_active = r.score_case(case, False)
    s_cand = r.score_case(case, True)
    assert s_active["forbidden_triggered"] == 1
    assert s_cand["forbidden_triggered"] == 0

def test_score_case_hermes_skill_evolution():
    case = {"task_class": "hermes_skill_evolution"}
    s_active = r.score_case(case, False)
    s_cand = r.score_case(case, True)
    assert s_cand["required_satisfied"] == 1
    assert s_active["authority_violation"] == 1

def test_agg_and_delta():
    cases = [{"task_class": "holler_oracle_full_live"}, {"task_class": "repo_canonicalization"}]
    active = [r.score_case(c, False) for c in cases]
    cand = [r.score_case(c, True) for c in cases]
    def agg(s): return {k: sum(x[k] for x in s) for k in s[0]}
    a = agg(active)
    c = agg(cand)
    assert c["required_satisfied"] >= a["required_satisfied"]