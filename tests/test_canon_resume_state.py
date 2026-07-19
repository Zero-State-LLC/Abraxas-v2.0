from __future__ import annotations

import json
from pathlib import Path

from core.canon_resume_state import (
    DEFAULT_NOTION_EXPECTED_LANES,
    RECOMMENDED_RESUME_LANE,
    build_canon_resume_state,
    write_canon_resume_state,
)
from scripts.readiness import run_canon_resume_state


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str = "ok\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_repo(root: Path) -> None:
    lane_status_overrides = {
        "P55": "CLOSURE_RECEIPT_DEGRADED",
        "P56": "STABILITY_RECEIPT_DEGRADED",
        "P67": "PACKAGE_STABILITY_RECEIPT_DEGRADED",
        "P68": "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED",
    }
    for lane in DEFAULT_NOTION_EXPECTED_LANES:
        for _label, rel_path in lane.required_evidence:
            target = root / rel_path
            if rel_path.endswith(".json"):
                payload = {"final_status": lane_status_overrides.get(lane.lane_id, "ADVISORY_ONLY")}
                _write_json(target, payload)
            else:
                _write_text(target)


def _assert_schema_required_fields(payload: dict[str, object]) -> None:
    required = {
        "artifact_type",
        "canonical_status",
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repo_observed_lanes",
        "notion_expected_lanes",
        "matched_lanes",
        "missing_lanes",
        "not_computable_lanes",
        "latest_completed_lane",
        "recommended_resume_lane",
        "recommended_resume_reason",
        "blockers",
        "drift_flags",
        "evidence",
        "packet_hash",
    }
    assert required.issubset(payload.keys())


def test_packet_hash_deterministic() -> None:
    packet_a = build_canon_resume_state()
    packet_b = build_canon_resume_state()
    assert packet_a["packet_hash"] == packet_b["packet_hash"]


def test_canonical_json_ends_with_exactly_one_newline(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    packet = build_canon_resume_state(repo_root=tmp_path)
    out = tmp_path / "out" / "canon_resume_state" / "latest.json"
    write_canon_resume_state(out, packet)
    text = out.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_missing_expected_evidence_is_not_computable(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    p68_schema_path = next(
        rel_path
        for lane in DEFAULT_NOTION_EXPECTED_LANES
        if lane.lane_id == "P68"
        for label, rel_path in lane.required_evidence
        if label == "schema"
    )
    (tmp_path / p68_schema_path).unlink()
    packet = build_canon_resume_state(repo_root=tmp_path)
    assert "P68" in packet["not_computable_lanes"]
    evidence = next(
        item
        for item in packet["evidence"]
        if item["path"] == p68_schema_path
    )
    assert evidence["observed"] is False
    assert evidence["status"] == "NOT_COMPUTABLE"


def test_authority_flags_remain_false() -> None:
    packet = build_canon_resume_state()
    assert packet["production_activation"] is False
    assert packet["canon_promotion"] is False
    assert packet["forecast_influence"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["runtime_authority"] is False


def test_recommended_resume_lane_stable_under_input_order(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    forward = build_canon_resume_state(repo_root=tmp_path, notion_expected_lanes=DEFAULT_NOTION_EXPECTED_LANES)
    reverse = build_canon_resume_state(repo_root=tmp_path, notion_expected_lanes=tuple(reversed(DEFAULT_NOTION_EXPECTED_LANES)))
    assert forward["recommended_resume_lane"] == reverse["recommended_resume_lane"] == RECOMMENDED_RESUME_LANE


def test_schema_required_fields_present() -> None:
    schema = json.loads(Path("contracts/canon/canon_resume_state.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["artifact_type"]["const"] == "CanonResumeState.v1"
    _assert_schema_required_fields(build_canon_resume_state())


def test_runner_writes_deterministic_latest_json(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    out = tmp_path / "out" / "canon_resume_state" / "latest.json"
    first = run_canon_resume_state.run(repo_root=tmp_path, out_path=out)
    first_text = out.read_text(encoding="utf-8")
    second = run_canon_resume_state.run(repo_root=tmp_path, out_path=out)
    second_text = out.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text
