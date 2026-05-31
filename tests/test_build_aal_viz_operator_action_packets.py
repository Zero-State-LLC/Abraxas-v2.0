"""Tests for scripts/build_aal_viz_operator_action_packets.py — copy-only adapter."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "build_aal_viz_operator_action_packets.py"
OUTPUT = ROOT / "apps" / "aal-viz-live-console" / "public" / "operator-action-packets.json"
SCHEMA_VERSION = "AALViz.OperatorActionPackets.v0.1"

EXPECTED_PACKET_IDS = {
    "pkt-transport-baseline-promotion-closed-001",
    "pkt-chamfer-baseline-promotion-follow-through-001",
    "pkt-aal-viz-next-adapter-checklist-001",
    "pkt-sealed-pause-review-001",
}

VALID_ACTION_TYPES = {"COPY_PROMPT", "COPY_CHECKLIST", "REVIEW_REQUIRED"}


@pytest.fixture(scope="module")
def bundle() -> dict:  # type: ignore[type-arg]
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, (
        f"Script exited {result.returncode}.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert OUTPUT.exists(), "Output file was not written"
    return json.loads(OUTPUT.read_text(encoding="utf-8"))


def test_script_exits_zero(bundle: dict) -> None:  # type: ignore[type-arg]
    assert isinstance(bundle, dict)


def test_schema_version(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["schema_version"] == SCHEMA_VERSION


def test_authority_execution_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["execution_allowed"] is False


def test_authority_runtime_mutation_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["runtime_mutation_allowed"] is False


def test_authority_promotion_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["promotion_allowed"] is False


def test_authority_production_activation_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["production_activation_allowed"] is False


def test_authority_metric_emission_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["metric_emission_allowed"] is False


def test_authority_forecast_influence_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["forecast_influence_allowed"] is False


def test_authority_p43_lanes_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["p43_lanes_allowed"] is False


def test_fail_closed_reason_none(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle.get("fail_closed_reason") is None


def test_packets_count(bundle: dict) -> None:  # type: ignore[type-arg]
    assert len(bundle["packets"]) >= 4


def test_expected_packet_ids_present(bundle: dict) -> None:  # type: ignore[type-arg]
    ids = {p["packet_id"] for p in bundle["packets"]}
    for expected_id in EXPECTED_PACKET_IDS:
        assert expected_id in ids, f"Missing expected packet: {expected_id}"


def test_each_packet_has_valid_action_type(bundle: dict) -> None:  # type: ignore[type-arg]
    for pkt in bundle["packets"]:
        assert pkt["action_type"] in VALID_ACTION_TYPES, (
            f"{pkt['packet_id']} has invalid action_type: {pkt['action_type']}"
        )


def test_each_packet_execution_allowed_false(bundle: dict) -> None:  # type: ignore[type-arg]
    for pkt in bundle["packets"]:
        assert pkt["execution_allowed"] is False, (
            f"{pkt['packet_id']} has execution_allowed != false"
        )


def test_each_packet_runtime_mutation_allowed_false(bundle: dict) -> None:  # type: ignore[type-arg]
    for pkt in bundle["packets"]:
        assert pkt["runtime_mutation_allowed"] is False, (
            f"{pkt['packet_id']} has runtime_mutation_allowed != false"
        )


def test_each_packet_promotion_allowed_false(bundle: dict) -> None:  # type: ignore[type-arg]
    for pkt in bundle["packets"]:
        assert pkt["promotion_allowed"] is False, (
            f"{pkt['packet_id']} has promotion_allowed != false"
        )


def test_each_packet_has_prompt_body(bundle: dict) -> None:  # type: ignore[type-arg]
    for pkt in bundle["packets"]:
        assert isinstance(pkt["prompt_body"], str) and len(pkt["prompt_body"]) > 0, (
            f"{pkt['packet_id']} has empty prompt_body"
        )


def test_each_packet_has_validation_checklist(bundle: dict) -> None:  # type: ignore[type-arg]
    for pkt in bundle["packets"]:
        assert isinstance(pkt["validation_checklist"], list) and len(pkt["validation_checklist"]) > 0, (
            f"{pkt['packet_id']} has empty validation_checklist"
        )


def test_each_packet_has_blocked_scopes(bundle: dict) -> None:  # type: ignore[type-arg]
    for pkt in bundle["packets"]:
        assert isinstance(pkt["blocked_scopes"], list) and len(pkt["blocked_scopes"]) > 0, (
            f"{pkt['packet_id']} has empty blocked_scopes"
        )


def test_each_packet_has_provenance_refs(bundle: dict) -> None:  # type: ignore[type-arg]
    for pkt in bundle["packets"]:
        assert isinstance(pkt["provenance_refs"], list) and len(pkt["provenance_refs"]) > 0, (
            f"{pkt['packet_id']} has empty provenance_refs"
        )


def test_transport_closed_packet_references_promotion_complete_in_provenance(bundle: dict) -> None:  # type: ignore[type-arg]
    pkt = next(p for p in bundle["packets"] if p["packet_id"] == "pkt-transport-baseline-promotion-closed-001")
    provenance_str = " ".join(pkt.get("provenance_refs", []))
    assert "transport_baseline_promotion_complete_001" in provenance_str


def test_transport_closed_packet_references_shadow_stub_posture(bundle: dict) -> None:  # type: ignore[type-arg]
    pkt = next(p for p in bundle["packets"] if p["packet_id"] == "pkt-transport-baseline-promotion-closed-001")
    assert "SHADOW_STUB_ONLY" in pkt["prompt_body"]
    assert "TRANSPORT_BASELINE_PROMOTION_COMPLETE" in pkt["prompt_body"]


def test_transport_closed_checklist_has_items(bundle: dict) -> None:  # type: ignore[type-arg]
    pkt = next(p for p in bundle["packets"] if p["packet_id"] == "pkt-transport-baseline-promotion-closed-001")
    assert len(pkt["validation_checklist"]) >= 5


def test_sealed_pause_is_review_required(bundle: dict) -> None:  # type: ignore[type-arg]
    pkt = next(p for p in bundle["packets"] if p["packet_id"] == "pkt-sealed-pause-review-001")
    assert pkt["action_type"] == "REVIEW_REQUIRED"


def test_no_research_canary_in_provenance(bundle: dict) -> None:  # type: ignore[type-arg]
    for pkt in bundle["packets"]:
        for ref in pkt.get("provenance_refs", []):
            assert "research_canary" not in ref, f"research_canary in provenance: {ref}"


def test_output_not_in_out_dir(bundle: dict) -> None:  # type: ignore[type-arg]
    assert "apps/aal-viz-live-console/public" in str(OUTPUT)
    assert not str(OUTPUT).startswith(str(ROOT / "out"))


def test_json_tool_valid() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "json.tool", str(OUTPUT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"json.tool failed: {result.stderr}"
