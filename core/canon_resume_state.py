from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "CanonResumeState.v1"
RECOMMENDED_RESUME_LANE = "P69_CANON_RESUME_STATE_OR_TEMPORAL_CONTINUITY_SPINE_PRECHECK"


@dataclass(frozen=True)
class CanonCompletedLane:
    lane_id: str
    title: str
    required_evidence: tuple[tuple[str, str], ...]
    status_probe_path: str | None = None
    status_probe_field: str | None = None


@dataclass(frozen=True)
class CanonResumeEvidence:
    label: str
    path: str
    observed: bool
    evidence_hash: str
    status: str


@dataclass(frozen=True)
class CanonResumeRecommendation:
    recommended_resume_lane: str
    recommended_resume_reason: str


@dataclass(frozen=True)
class CanonResumeState:
    artifact_type: str
    canonical_status: str
    production_activation: bool
    canon_promotion: bool
    forecast_influence: bool
    scheduler_mutation: bool
    runtime_authority: bool
    repo_observed_lanes: tuple[dict[str, Any], ...]
    notion_expected_lanes: tuple[str, ...]
    matched_lanes: tuple[str, ...]
    missing_lanes: tuple[str, ...]
    not_computable_lanes: tuple[str, ...]
    latest_completed_lane: str
    recommended_resume_lane: str
    recommended_resume_reason: str
    blockers: tuple[str, ...]
    drift_flags: tuple[str, ...]
    evidence: tuple[dict[str, Any], ...]
    repo_matches_notion_assumptions: bool
    governance_posture: tuple[str, ...]
    packet_hash: str


DEFAULT_NOTION_EXPECTED_LANES: tuple[CanonCompletedLane, ...] = (
    CanonCompletedLane(
        lane_id="P28.1",
        title="Temporal Coherence Chain Runner",
        required_evidence=(
            ("runner_script", "scripts/run_temporal_coherence_chain.py"),
            ("runner_test", "tests/test_temporal_coherence_chain.py"),
        ),
    ),
    CanonCompletedLane(
        lane_id="P55",
        title="Archive Chain Closure Receipt",
        required_evidence=(
            ("artifact_json", "out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.json"),
            ("schema", "contracts/operator_attention/operator_narrative_archive_chain_closure_receipt.v1.schema.json"),
            ("test", "tests/test_operator_narrative_archive_chain_closure_receipt.py"),
        ),
        status_probe_path="out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.json",
        status_probe_field="final_status",
    ),
    CanonCompletedLane(
        lane_id="P56",
        title="Archive Chain Stability Receipt",
        required_evidence=(
            ("artifact_json", "out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.json"),
            ("schema", "contracts/operator_attention/operator_narrative_archive_chain_stability_receipt.v1.schema.json"),
            ("test", "tests/test_operator_narrative_archive_chain_stability_receipt.py"),
        ),
        status_probe_path="out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.json",
        status_probe_field="final_status",
    ),
    CanonCompletedLane(
        lane_id="P67",
        title="Static Archive Package Stability Receipt",
        required_evidence=(
            ("artifact_json", "out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json"),
            ("schema", "contracts/operator_attention/operator_narrative_static_archive_package_stability_receipt.v1.schema.json"),
            ("test", "tests/test_operator_narrative_static_archive_package_stability_receipt.py"),
        ),
        status_probe_path="out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json",
        status_probe_field="final_status",
    ),
    CanonCompletedLane(
        lane_id="P68",
        title="Static Archive Package Chain Closure Receipt",
        required_evidence=(
            ("artifact_json", "out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json"),
            ("schema", "contracts/operator_attention/operator_narrative_static_archive_package_chain_closure_receipt.v1.schema.json"),
            ("test", "tests/test_operator_narrative_static_archive_package_chain_closure_receipt.py"),
        ),
        status_probe_path="out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json",
        status_probe_field="final_status",
    ),
)


def _lane_sort_key(lane_id: str) -> tuple[float, str]:
    num = lane_id.removeprefix("P")
    try:
        return (float(num), lane_id)
    except ValueError:
        return (0.0, lane_id)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_probe_status(path: Path, field: str | None) -> str:
    if field is None:
        return "OBSERVED"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return "NOT_COMPUTABLE"
    if isinstance(payload, dict):
        value = payload.get(field, "NOT_COMPUTABLE")
        return str(value)
    return "NOT_COMPUTABLE"


def _iter_lanes(lanes: Sequence[CanonCompletedLane]) -> Iterable[CanonCompletedLane]:
    return sorted(lanes, key=lambda item: _lane_sort_key(item.lane_id))


def build_canon_resume_state(
    *,
    repo_root: str | Path = ".",
    notion_expected_lanes: Sequence[CanonCompletedLane] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    expected = tuple(_iter_lanes(notion_expected_lanes or DEFAULT_NOTION_EXPECTED_LANES))

    evidence_items: list[CanonResumeEvidence] = []
    observed_lanes: list[dict[str, Any]] = []
    matched_lanes: list[str] = []
    missing_lanes: list[str] = []
    not_computable_lanes: list[str] = []
    blockers: set[str] = set()
    degraded_lanes: list[str] = []

    for lane in expected:
        missing_paths: list[str] = []
        for label, rel_path in lane.required_evidence:
            target = root / rel_path
            observed = target.exists()
            evidence_items.append(
                CanonResumeEvidence(
                    label=f"{lane.lane_id}:{label}",
                    path=rel_path,
                    observed=observed,
                    evidence_hash=_sha256_file(target) if observed else "NOT_COMPUTABLE",
                    status="OBSERVED" if observed else "NOT_COMPUTABLE",
                )
            )
            if not observed:
                missing_paths.append(rel_path)
                blockers.add(f"{lane.lane_id} missing evidence: {rel_path}")

        lane_status = _load_probe_status(
            root / lane.status_probe_path if lane.status_probe_path else root / lane.required_evidence[0][1],
            lane.status_probe_field,
        )
        observed_entry = {
            "lane_id": lane.lane_id,
            "title": lane.title,
            "status": lane_status,
            "required_evidence_present": not missing_paths,
            "missing_evidence_paths": tuple(sorted(missing_paths)),
        }
        observed_lanes.append(observed_entry)

        if not missing_paths:
            matched_lanes.append(lane.lane_id)
        else:
            missing_lanes.append(lane.lane_id)
            not_computable_lanes.append(lane.lane_id)

        status_upper = lane_status.upper()
        if "NOT_COMPUTABLE" in status_upper and lane.lane_id not in not_computable_lanes:
            not_computable_lanes.append(lane.lane_id)
            blockers.add(f"{lane.lane_id} status not computable")
        if "FAIL" in status_upper:
            blockers.add(f"{lane.lane_id} status indicates fail: {lane_status}")
        if "DEGRADED" in status_upper:
            degraded_lanes.append(lane.lane_id)
            blockers.add(f"{lane.lane_id} preserves degraded status: {lane_status}")

    matched_sorted = tuple(sorted(set(matched_lanes), key=_lane_sort_key))
    missing_sorted = tuple(sorted(set(missing_lanes), key=_lane_sort_key))
    not_computable_sorted = tuple(sorted(set(not_computable_lanes), key=_lane_sort_key))
    blockers_sorted = tuple(sorted(blockers))

    latest_completed_lane = matched_sorted[-1] if matched_sorted else "NOT_COMPUTABLE"
    drift_flags: list[str] = []
    if missing_sorted:
        drift_flags.append("MISSING_EXPECTED_LANE_EVIDENCE")
    if not_computable_sorted:
        drift_flags.append("NOT_COMPUTABLE_LANE_EVIDENCE")
    if degraded_lanes:
        drift_flags.append("DEGRADED_UPSTREAM_LANE_STATUS")

    repo_matches = not missing_sorted and not not_computable_sorted
    if not repo_matches:
        drift_flags.append("REPO_NOTION_ASSUMPTION_DRIFT")

    recommendation = CanonResumeRecommendation(
        recommended_resume_lane=RECOMMENDED_RESUME_LANE,
        recommended_resume_reason=(
            "Critical lane evidence is incomplete; run advisory continuity precheck before any new subsystem coding."
            if missing_sorted or not_computable_sorted
            else "Sealed lane evidence is locally present; continue with advisory-only canon resume precheck."
        ),
    )

    packet_base = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repo_observed_lanes": tuple(sorted(observed_lanes, key=lambda item: _lane_sort_key(str(item["lane_id"])))),
        "notion_expected_lanes": tuple(lane.lane_id for lane in expected),
        "matched_lanes": matched_sorted,
        "missing_lanes": missing_sorted,
        "not_computable_lanes": not_computable_sorted,
        "latest_completed_lane": latest_completed_lane,
        "recommended_resume_lane": recommendation.recommended_resume_lane,
        "recommended_resume_reason": recommendation.recommended_resume_reason,
        "blockers": blockers_sorted,
        "drift_flags": tuple(sorted(drift_flags)),
        "evidence": tuple(
            asdict(item)
            for item in sorted(
                evidence_items,
                key=lambda item: (item.path, item.label),
            )
        ),
        "repo_matches_notion_assumptions": repo_matches,
        "governance_posture": (
            "advisory_only",
            "projection_only",
            "non_authoritative",
            "mutation_denied",
            "execution_denied",
            "forecast_authority_denied",
            "canon_runtime_queue_mutation_denied",
        ),
    }
    packet_hash = canonical_hash(packet_base)
    packet = CanonResumeState(
        **packet_base,
        packet_hash=packet_hash,
    )
    return json.loads(_canonical_json(asdict(packet)))


def write_canon_resume_state(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
