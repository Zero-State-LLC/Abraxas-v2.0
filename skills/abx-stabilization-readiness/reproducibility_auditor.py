"""Reproducibility auditor — advisory toolchain checks (no destructive actions)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .contracts import REPRODUCIBILITY_CLASSIFICATIONS
from .models import ReproducibilityFinding, stable_hash

LOCK_CANDIDATES = [
    ("python", "uv.lock"),
    ("python", "requirements-lock.txt"),
    ("node", "package-lock.json"),
    ("node", "pnpm-lock.yaml"),
    ("node", "yarn.lock"),
]

TOOLCHAIN_MARKERS = [
    ("python", "pyproject.toml"),
    ("typescript", "package.json"),
    ("typescript", "tsconfig.json"),
]


def _exists(repo_root: Path, rel: str) -> bool:
    return (repo_root / rel).is_file()


def audit_reproducibility(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    root = repo_root or Path(".")
    findings: List[ReproducibilityFinding] = []

    locks_found = [name for _, name in LOCK_CANDIDATES if _exists(root, name)]
    if locks_found:
        findings.append(
            ReproducibilityFinding(
                surface="dependency_locks",
                classification="REPRODUCIBLE_WITH_DECLARED_VARIANCE",
                evidence_refs=locks_found,
                notes="Lock files present; full fresh-checkout replay not executed in advisory mode.",
            )
        )
    else:
        findings.append(
            ReproducibilityFinding(
                surface="dependency_locks",
                classification="NOT_COMPUTABLE",
                evidence_refs=[],
                notes="No recognized lock files at repo root.",
            )
        )

    for lang, marker in TOOLCHAIN_MARKERS:
        if _exists(root, marker):
            findings.append(
                ReproducibilityFinding(
                    surface=marker,
                    classification="REPRODUCIBLE_WITH_DECLARED_VARIANCE",
                    evidence_refs=[marker],
                    notes=f"{lang} toolchain marker present.",
                )
            )
        else:
            findings.append(
                ReproducibilityFinding(
                    surface=marker,
                    classification="NOT_COMPUTABLE",
                    evidence_refs=[],
                    notes=f"Missing {marker} for {lang} surface.",
                )
            )

    # AAL-Viz / TypeScript emphasis per spec
    ts_ready = _exists(root, "package.json") and (
        _exists(root, "pnpm-lock.yaml") or _exists(root, "package-lock.json")
    )
    findings.append(
        ReproducibilityFinding(
            surface="typescript_toolchain",
            classification="REPRODUCIBLE" if ts_ready else "NON_REPRODUCIBLE",
            evidence_refs=["package.json"] if _exists(root, "package.json") else [],
            notes="TypeScript reproducibility requires package.json plus a lockfile.",
        )
    )

    classifications = {f.classification for f in findings}
    if "NON_REPRODUCIBLE" in classifications:
        overall = "NON_REPRODUCIBLE"
    elif classifications == {"NOT_COMPUTABLE"}:
        overall = "NOT_COMPUTABLE"
    elif "NOT_COMPUTABLE" in classifications:
        overall = "REPRODUCIBLE_WITH_DECLARED_VARIANCE"
    else:
        overall = "REPRODUCIBLE_WITH_DECLARED_VARIANCE"

    if overall not in REPRODUCIBILITY_CLASSIFICATIONS:
        overall = "NOT_COMPUTABLE"

    report = {
        "boundary": "ADVISORY_ONLY | NO_FRESH_CHECKOUT_EXECUTION",
        "audit_id": "abx_stabilization_reproducibility_v1",
        "overall_classification": overall,
        "findings": [f.to_dict() for f in findings],
    }
    report["audit_hash"] = stable_hash(report["findings"])
    return report


def write_reproducibility_artifact(repo_root: Path, out_dir: Optional[Path] = None) -> Path:
    out = out_dir or repo_root / "out" / "stabilization_readiness"
    out.mkdir(parents=True, exist_ok=True)
    data = audit_reproducibility(repo_root)
    path = out / "reproducibility_audit.latest.json"
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path