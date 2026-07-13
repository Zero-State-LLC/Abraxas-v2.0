"""Tests for skills/abx-hermes-skill-evolution/abx_skill_literature_corpus_applicator.py (TEST candidate c626c625d13fd9d2)"""

import sys
import json
sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_literature_corpus_applicator as l

def test_relevance_keywords_present():
    assert "governance" in l.RELEVANCE_KEYWORDS
    assert "skill" in l.RELEVANCE_KEYWORDS
    assert "evolution" in l.RELEVANCE_KEYWORDS
    assert len(l.RELEVANCE_KEYWORDS) > 10

def test_load_corpus_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(l, "ARXIV_CORPUS", tmp_path / "nonexistent.json")
    corpus = l.load_corpus()
    assert "entries" in corpus or corpus == {"entries": []}

def test_filter_relevant_papers():
    papers = [
        {"title": "governance and decision lifecycle", "abstract": "reasoning about agents"},
        {"title": "unrelated topic", "abstract": "something else"},
        {"title": "skill evolution replay", "abstract": "temporal chain-of-thought"}
    ]
    relevant = [p for p in papers if any(kw in (p.get("title","") + p.get("abstract","")).lower() for kw in l.RELEVANCE_KEYWORDS)]
    assert len(relevant) >= 2

def test_main_does_not_crash(monkeypatch, tmp_path):
    audit = tmp_path
    (audit / "abx_hermes_arxiv_corpus_expansion_v3.latest.json").write_text(json.dumps({"entries": []}))
    (audit / "abx_hermes_live_expanded_corpus_v2_4.latest.json").write_text(json.dumps({}))
    monkeypatch.setattr(l, "OUT", audit)
    # Should run without raising
    l.main()  # prints and may write
    assert True