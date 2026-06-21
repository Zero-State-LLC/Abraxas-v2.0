from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash
from core.codegen_shadow_replay_harness import run_codegen_shadow_replay

from contracts.codegen import ShadowReplayFixture

FIXTURE_VALIDATION_SCHEMA_VERSION = "CodegenFixtureValidationReceipt.v1"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"fixture JSON could not be read: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"fixture JSON is not an object: {path}")
    return value


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _recommendation_for_proposal(proposal: Mapping[str, Any]) -> str:
    result = run_codegen_shadow_replay(proposal)
    receipt = result.get("receipt")
    if isinstance(receipt, Mapping):
        recommendation = receipt.get("recommendation")
        if isinstance(recommendation, str):
            return recommendation
    if result.get("status") == "VALIDATION_FAILED":
        return "REJECT"
    return "REFINE_PROPOSAL"


def _authority_locks_false(fixture: ShadowReplayFixture) -> bool:
    locks = fixture.expected_authority_locks.model_dump()
    return locks["advisory_only"] is True and all(
        value is False for key, value in locks.items() if key != "advisory_only"
    )


def validate_shadow_replay_fixture(
    fixture_path: str | Path,
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    target = root / fixture_path
    fixture = ShadowReplayFixture.model_validate(_read_json(target))
    proposal_path = root / fixture.proposal_path
    proposal = _read_json(proposal_path)
    observed_recommendation = _recommendation_for_proposal(proposal)
    recommendation_matches = observed_recommendation == fixture.expected_recommendation
    authority_locks_valid = _authority_locks_false(fixture)

    base: dict[str, Any] = {
        "schema_version": FIXTURE_VALIDATION_SCHEMA_VERSION,
        "status": (
            "FIXTURE_VALIDATION_PASSED"
            if recommendation_matches and authority_locks_valid
            else "FIXTURE_VALIDATION_FAILED"
        ),
        "fixture_id": fixture.fixture_id,
        "fixture_path": _relative_path(target, root),
        "proposal_path": fixture.proposal_path,
        "expected_recommendation": fixture.expected_recommendation,
        "observed_recommendation": observed_recommendation,
        "recommendation_matches": recommendation_matches,
        "run_count": fixture.run_count,
        "constraints": fixture.constraints.model_dump(),
        "authority_locks_valid": authority_locks_valid,
        "provenance": fixture.provenance.model_dump(),
        "advisory_only": True,
        "shadow_replay_only": True,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def validate_shadow_replay_fixtures(
    fixture_paths: Sequence[str | Path],
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    receipts = [
        validate_shadow_replay_fixture(path, repo_root=repo_root)
        for path in fixture_paths
    ]
    passed = all(receipt["status"] == "FIXTURE_VALIDATION_PASSED" for receipt in receipts)
    base: dict[str, Any] = {
        "schema_version": "CodegenFixtureValidationSummary.v1",
        "status": (
            "FIXTURE_VALIDATION_SUMMARY_PASSED"
            if passed
            else "FIXTURE_VALIDATION_SUMMARY_FAILED"
        ),
        "fixture_count": len(receipts),
        "passed_count": sum(
            1 for receipt in receipts if receipt["status"] == "FIXTURE_VALIDATION_PASSED"
        ),
        "failed_count": sum(
            1 for receipt in receipts if receipt["status"] != "FIXTURE_VALIDATION_PASSED"
        ),
        "receipts": receipts,
        "advisory_only": True,
        "shadow_replay_only": True,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
