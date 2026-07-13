#!/usr/bin/env python3
"""
Abraxas Engineering Candidate Extractor (v1)

Consumes ONLY verified repository-intelligence artifacts.
Converts observed gaps (primarily missing_tests) into normalized candidates.

Deterministic, no wall-clock in canon fields, advisory/SHADOW only.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path.cwd()
INTEL_DIR = REPO_ROOT / "out" / "repo_intel"
ORACLE_DIR = REPO_ROOT / "out" / "repo_intelligence" / "engineering_oracle"
CANDIDATES_FILE = ORACLE_DIR / "engineering_candidates.v1.json"

GAP_SOURCES = {
    "gap_discovery": INTEL_DIR / "gap_discovery.v1.json",
    "repo_intel_receipt": INTEL_DIR / "repo_intel_receipt.v1.json",
    "manifest": INTEL_DIR / "repository_manifest.v1.json",
}

HIGH_VALUE_PREFIXES = ("core/", "contracts/", "skills/", "abraxas/v2/governance/")


def stable_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def is_high_value(path: str) -> bool:
    return any(path.startswith(p) for p in HIGH_VALUE_PREFIXES)


def extract_candidates() -> List[Dict[str, Any]]:
    gaps = load_json(GAP_SOURCES["gap_discovery"])
    _ = load_json(GAP_SOURCES["repo_intel_receipt"])
    _ = load_json(GAP_SOURCES["manifest"])

    candidates: List[Dict[str, Any]] = []
    seen_ids: set = set()

    missing_tests = gaps.get("gaps", {}).get("missing_tests", [])

    for path in missing_tests:
        if path in seen_ids:  # dedup by path for now
            continue

        cid = stable_id(f"missing_test:{path}")
        if cid in seen_ids:
            continue
        seen_ids.add(cid)

        cls = "TEST"
        if any(x in path for x in ("governance", "validator", "decision", "receipt", "canon")):
            cls = "GOVERNANCE"
        elif "core/" in path:
            cls = "HARDENING"

        affected_sub = path.split("/")[0] if "/" in path else "root"

        cand = {
            "schema_version": "1.0.0",
            "candidate_id": cid,
            "title": f"Add tests for {path}",
            "candidate_class": cls,
            "source_artifacts": ["gap_discovery.v1.json", "repository_manifest.v1.json"],
            "source_evidence": [f"gap:missing_tests:{path}"],
            "affected_subsystems": [affected_sub],
            "affected_paths": [path],
            "dependency_ids": [],
            "governance_surfaces": ["GOVERNANCE_V3.md"] if cls == "GOVERNANCE" else [],
            "authority_required": ["advisory_engineering"],
            "authority_observed": ["broad_operator_grant_all_engineering_tied_to_approval"],
            "execution_boundary": "ADVISORY_ONLY",
            "estimated_impact": 0.7 if is_high_value(path) else 0.4,
            "estimated_effort": 0.3,
            "estimated_risk": 0.1,
            "confidence": 0.85 if is_high_value(path) else 0.6,
            "status": "ACTIONABLE",
            "provenance": {
                "repo_intel_receipt": str(GAP_SOURCES["repo_intel_receipt"].relative_to(REPO_ROOT)),
                "generated_at_observed": "from_repo_intel_artifacts",
                "builder_commit": "HEAD",  # observed only
            },
            "packet_hash": stable_id(f"candidate:{cid}"),
        }
        candidates.append(cand)

    # Sort deterministically by id for stable output
    candidates.sort(key=lambda c: c["candidate_id"])
    return candidates


def main() -> None:
    ORACLE_DIR.mkdir(parents=True, exist_ok=True)
    cands = extract_candidates()
    out = {
        "schema_version": "1.0.0",
        "candidates": cands,
        "count": len(cands),
        "generated_from": [str(p.relative_to(REPO_ROOT)) for p in GAP_SOURCES.values()],
    }
    CANDIDATES_FILE.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"Wrote {CANDIDATES_FILE} with {len(cands)} candidates")


if __name__ == "__main__":
    main()
