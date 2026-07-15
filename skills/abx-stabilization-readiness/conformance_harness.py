"""Conformance harness — language-independent behavioral corpus (advisory loader)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .contracts import COMPARISON_MODES
from .models import ConformanceCase, stable_hash


def _load_fixture(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_to_case(data: Dict[str, Any]) -> ConformanceCase:
    return ConformanceCase(
        case_id=data["case_id"],
        input_payload=data.get("input", {}),
        expected=data.get("expected", {}),
        comparison_mode=data.get("comparison_mode", "SEMANTIC_EXACT"),
        implementations=list(data.get("implementations", ["python"])),
        allowed_variance=data.get("allowed_variance"),
    )


def validate_case_shape(case: ConformanceCase) -> List[str]:
    errors: List[str] = []
    if not case.case_id:
        errors.append("missing case_id")
    if case.comparison_mode not in COMPARISON_MODES:
        errors.append(f"invalid comparison_mode: {case.comparison_mode}")
    if not case.implementations:
        errors.append("implementations must be non-empty")
    return errors


def load_corpus(fixtures_dir: Path) -> List[ConformanceCase]:
    cases: List[ConformanceCase] = []
    for path in sorted(fixtures_dir.glob("*.json")):
        if path.name == "sample_campaign_state.json":
            continue
        data = _load_fixture(path)
        if "case_id" not in data:
            continue
        cases.append(fixture_to_case(data))
    return cases


def build_harness_report(fixtures_dir: Path) -> Dict[str, Any]:
    cases = load_corpus(fixtures_dir)
    validation: Dict[str, List[str]] = {}
    for c in cases:
        validation[c.case_id] = validate_case_shape(c)

    ready = all(not v for v in validation.values())
    report = {
        "boundary": "ADVISORY_ONLY | CORPUS_LOADER",
        "harness_id": "abx_stabilization_conformance_harness_v1",
        "corpus_ready": ready,
        "case_count": len(cases),
        "cases": [c.to_dict() for c in cases],
        "validation_errors": {k: v for k, v in validation.items() if v},
        "comparison_modes_supported": list(COMPARISON_MODES),
    }
    report["harness_hash"] = stable_hash(
        {"case_ids": [c.case_id for c in cases], "ready": ready}
    )
    return report


def write_harness_artifact(repo_root: Path, fixtures_dir: Optional[Path] = None) -> Path:
    fixtures = fixtures_dir or repo_root / "skills" / "abx-stabilization-readiness" / "fixtures"
    out = repo_root / "out" / "stabilization_readiness"
    out.mkdir(parents=True, exist_ok=True)
    data = build_harness_report(fixtures)
    path = out / "conformance_harness.latest.json"
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path