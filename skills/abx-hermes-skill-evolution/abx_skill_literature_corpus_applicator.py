#!/usr/bin/env python3
"""
Literature Corpus Applicator for abx-hermes-skill-evolution (v3.1)
Advisory only. Turns the arXiv governance/decision/replay corpus into
deterministic "literature-derived replay cases" and signals.

These are additive to the live expanded corpus.
Used for:
- Enriching replay/canary observation with external literature patterns.
- Generating synthetic governance signals for evidence history.
- Informing operator decision with "literature alignment" evidence.
- Increasing trace diversity via new signal types (literature_governance, literature_replay, literature_observation).

Never mutates active skill or frozen base corpus.
Deterministic outputs.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")
SKILL_DIR = Path("skills/abx-hermes-skill-evolution")
FIXTURES = SKILL_DIR / "fixtures" / "literature_cases"

ARXIV_CORPUS = OUT / "abx_hermes_arxiv_corpus_expansion_v3.latest.json"
EXPANDED_CORPUS = OUT / "abx_hermes_live_expanded_corpus_v2_4.latest.json"

# Relevance keywords for filtering high-value papers for our spine
RELEVANCE_KEYWORDS = [
    "governance", "decision", "lifecycle", "replay", "replayable",
    "observation", "extended", "ledger", "agent", "proactive",
    "benchmark", "self-distillation", "on-policy", "reasoning",
    "temporal", "chain-of", "skill", "evolution"
]

def load_corpus():
    if not ARXIV_CORPUS.exists():
        return {"entries": []}
    return json.loads(ARXIV_CORPUS.read_text())

def is_relevant(entry):
    text = (entry.get("title", "") + " " + entry.get("summary", "") + " " + entry.get("query", "")).lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)

def paper_to_literature_case(paper, idx):
    """Turn a paper into a deterministic literature-derived replay case."""
    case_id = f"lit-{paper.get('arxiv_id', idx)}"
    title = paper.get("title", "untitled")
    paper.get("summary", "")[:600]

    # Extract crude governance/engineering signals (deterministic, rule-based)
    signals = []
    if "proactive" in title.lower() or "agent" in title.lower():
        signals.append("proactive_agent_benchmark")
    if "on-policy" in title.lower() or "self-distillation" in title.lower():
        signals.append("on_policy_improvement")
    if "replay" in title.lower() or "replayable" in paper.get("query", "").lower():
        signals.append("replayable_artifact")
    if "observation" in title.lower() or "extended" in title.lower() or "temporal" in title.lower():
        signals.append("extended_observation")
    if "decision" in title.lower() or "lifecycle" in title.lower() or "ledger" in title.lower():
        signals.append("decision_lifecycle")
    if not signals:
        signals.append("general_governance")

    engineering_implication = (
        "Literature-derived pattern: " + title[:80] + ". "
        "Apply to Abraxas: strengthen " + ", ".join(signals) + " in replay/canary/evidence."
    )

    case = {
        "case_id": case_id,
        "task_class": "literature_governance",
        "skill_id": "abx-hermes-skill-evolution",
        "skill_version": "lit-v3.1",
        "input_refs": [paper.get("arxiv_id", "")],
        "expected_behavior": {
            "outcome": "LITERATURE_PATTERN_APPLIED",
            "signals": signals,
            "paper_title": title,
            "source": "arxiv_corpus_v3"
        },
        "forbidden_behavior": [],
        "validation_requirements": ["deterministic", "advisory_only", "no_mutation"],
        "source_commit": "corpus-derived",
        "provenance_hash": hashlib.sha256(json.dumps(paper, sort_keys=True).encode()).hexdigest()[:16],
        "literature_source": paper.get("arxiv_id"),
        "query": paper.get("query"),
        "engineering_implication": engineering_implication,
        "source": "arxiv_literature_corpus"
    }
    return case

def main():
    corpus = load_corpus()
    papers = corpus.get("entries", [])

    # Filter to most relevant (prioritize governance/decision/replay/agents)
    relevant_papers = [p for p in papers if is_relevant(p)]
    # Dedup by arxiv_id while preserving order
    seen = set()
    unique_relevant = []
    for p in relevant_papers:
        aid = p.get("arxiv_id")
        if aid and aid not in seen:
            seen.add(aid)
            unique_relevant.append(p)

    # Limit to top N for determinism and cleanliness (can be tuned)
    top_papers = unique_relevant[:8]

    lit_cases = [paper_to_literature_case(p, i) for i, p in enumerate(top_papers)]

    # Load existing expanded corpus if present (additive only)
    if EXPANDED_CORPUS.exists():
        expanded = json.loads(EXPANDED_CORPUS.read_text())
        existing_cases = expanded.get("cases", [])
        # Avoid duplicating literature cases
        existing_ids = {c.get("case_id") for c in existing_cases}
        new_lit_cases = [c for c in lit_cases if c["case_id"] not in existing_ids]
    else:
        expanded = {
            "corpus_id": "abx_hermes_live_expanded_corpus_v2_4",
            "version": "0.1-live",
            "base_corpus": "abx_hermes_replay_corpus_v2_2",
            "cases": [],
            "live_trace_count": 0,
        }
        new_lit_cases = lit_cases

    all_cases = existing_cases + new_lit_cases if 'existing_cases' in locals() else new_lit_cases

    expanded.update({
        "cases": all_cases,
        "literature_cases_added": len(new_lit_cases),
        "total_literature_cases": len([c for c in all_cases if c.get("source") == "arxiv_literature_corpus"]),
        "last_literature_update": datetime.now(timezone.utc).isoformat(),
        "status": "ADDITIVE_LIVE_ONLY + LITERATURE_DERIVED",
        "deterministic_hash": hashlib.sha256(json.dumps(all_cases, sort_keys=True).encode()).hexdigest()[:16]
    })

    EXPANDED_CORPUS.write_text(json.dumps(expanded, indent=2))

    # Write individual literature cases for inspection
    FIXTURES.mkdir(parents=True, exist_ok=True)
    for case in lit_cases:
        case_path = FIXTURES / f"{case['case_id']}.json"
        case_path.write_text(json.dumps(case, indent=2))

    print("Literature corpus applied.")
    print(f"Relevant papers processed: {len(top_papers)}")
    print(f"New literature cases added: {len(new_lit_cases)}")
    print(f"Total cases in expanded corpus: {len(all_cases)}")
    print(f"Artifact: {EXPANDED_CORPUS}")
    print(f"Deterministic hash: {expanded['deterministic_hash']}")

    return {
        "literature_cases": len(lit_cases),
        "new_added": len(new_lit_cases),
        "artifact": str(EXPANDED_CORPUS)
    }

if __name__ == "__main__":
    main()
