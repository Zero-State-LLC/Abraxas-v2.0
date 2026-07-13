#!/usr/bin/env python3
"""
Dependency and Blocker Resolver for Engineering Oracle v1.

Uses import_graph to find prerequisite candidates.
Classifies blockers: DEPENDENCY, AUTHORITY, EVIDENCE, etc.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path.cwd()
INTEL_DIR = REPO_ROOT / "out" / "repo_intel"
GRAPHS_DIR = INTEL_DIR / "graphs"
ORACLE_DIR = REPO_ROOT / "out" / "repo_intelligence" / "engineering_oracle"


def load_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def build_dependency_graph(candidates: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Simple dep resolver using import_graph nodes/edges."""
    try:
        ig = load_json(GRAPHS_DIR / "import_graph.v1.json")
    except Exception:
        ig = {"nodes": [], "edges": []}

    edges = ig.get("edges", [])

    # Build reverse map: file -> importers
    importers: Dict[str, List[str]] = {}
    for e in edges:
        if isinstance(e, dict):
            src = e.get("source")
            tgt = e.get("target")
            if src and tgt:
                importers.setdefault(tgt, []).append(src)

    cand_paths = {c["candidate_id"]: c["affected_paths"][0] for c in candidates}

    dep_graph: Dict[str, List[str]] = {}
    for cid, path in cand_paths.items():
        deps = []
        # Files that this path depends on (if in graph)
        for e in edges:
            if e.get("source") == path:
                tgt = e.get("target")
                if tgt:
                    deps.append(tgt)
        # Or reverse: who imports this (downstream)
        for imp in importers.get(path, []):
            if imp != path:
                deps.append(imp)
        dep_graph[cid] = list(set(deps))[:5]  # cap for determinism
    return dep_graph


def resolve_blockers(candidates: List[Dict[str, Any]], dep_graph: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
    blockers = {}
    for c in candidates:
        cid = c["candidate_id"]
        path = c["affected_paths"][0]
        blks = []
        if dep_graph.get(cid):
            blks.append({"class": "DEPENDENCY", "detail": f"imports or imported by {len(dep_graph[cid])} others"})
        if "core/" not in path and "governance" not in path.lower():
            blks.append({"class": "LOW_PRIORITY", "detail": "not in high value subsystem"})
        blockers[cid] = blks
    return blockers
