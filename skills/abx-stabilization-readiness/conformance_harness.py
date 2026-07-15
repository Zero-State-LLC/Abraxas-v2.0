"""Deterministic conformance-case evaluator foundation."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash

from .contracts import validate_comparison_mode
from .models import ComparisonMode, ConformanceCase

DEFAULT_FIXTURE_PATH = Path(__file__).with_name("fixtures") / "foundation_cases.v1.json"


def load_foundation_cases(path: Path = DEFAULT_FIXTURE_PATH) -> tuple[ConformanceCase, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return tuple(
        ConformanceCase(
            case_id=item["case_id"],
            description=item["description"],
            input=item["input"],
            expected=item["expected"],
            comparison_mode=item["comparison_mode"],
            implementations=tuple(item["implementations"]),
            allowed_variance=item.get("allowed_variance"),
            provenance=item["provenance"],
        )
        for item in raw["cases"]
    )


def _compare(case: ConformanceCase) -> tuple[bool, str]:
    validate_comparison_mode(case.comparison_mode)
    actual = case.input.get("actual")
    expected = case.expected.get("value")
    mode = case.comparison_mode
    if mode == ComparisonMode.BYTE_EXACT:
        passed = str(actual).encode("utf-8") == str(expected).encode("utf-8")
    elif mode == ComparisonMode.HASH_EXACT:
        actual_hash = hashlib.sha256(str(actual).encode("utf-8")).hexdigest()
        passed = actual_hash == case.expected.get("sha256")
    elif mode in {ComparisonMode.SEMANTIC_EXACT, ComparisonMode.SCHEMA_EXACT}:
        passed = actual == expected
    elif mode == ComparisonMode.SET_EQUIVALENT:
        passed = set(_as_sequence(actual)) == set(_as_sequence(expected))
    elif mode == ComparisonMode.ORDERED_EQUIVALENT:
        passed = list(_as_sequence(actual)) == list(_as_sequence(expected))
    else:
        variance = case.allowed_variance
        passed = (
            variance is not None
            and isinstance(actual, (int, float))
            and isinstance(expected, (int, float))
            and abs(actual - expected) <= variance
        )
    return passed, "matched" if passed else "comparison failed"


def _as_sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    raise ValueError("equivalence comparison requires a sequence")


def run_conformance_cases(
    cases: Iterable[ConformanceCase] | None = None,
) -> dict[str, Any]:
    selected = tuple(cases) if cases is not None else load_foundation_cases()
    results: list[dict[str, Any]] = []
    for case in sorted(selected, key=lambda item: item.case_id):
        passed, reason = _compare(case)
        results.append(
            {
                "case_id": case.case_id,
                "comparison_mode": case.comparison_mode,
                "implementations": list(case.implementations),
                "passed": passed,
                "reason": reason,
            }
        )
    manifest: dict[str, Any] = {
        "schema_version": "StabilizationConformanceManifest.v1",
        "case_count": len(results),
        "passed_count": sum(item["passed"] for item in results),
        "ready": bool(results) and all(item["passed"] for item in results),
        "cases": results,
        "typescript_equivalence_claimed": False,
        "advisory_only": True,
    }
    manifest["canonical_hash"] = canonical_hash(manifest)
    return manifest
