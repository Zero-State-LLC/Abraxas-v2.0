"""Tests for scripts/build_aal_viz_projection_bundle.py — read-only adapter."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "build_aal_viz_projection_bundle.py"
OUTPUT = ROOT / "apps" / "aal-viz-live-console" / "public" / "projection-bundle.json"
SCHEMA_VERSION = "AALViz.LiveConsoleProjectionBundle.v0.1"

EXPECTED_OPERATOR_IDS = {
    "wasserstein",
    "chamfer_distance",
    "geodesic",
    "norm_geometry",
    "transport",
    "heavy_tail",
}


@pytest.fixture(scope="module")
def bundle() -> dict:  # type: ignore[type-arg]
    """Run the script once; parse and return the output bundle."""
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
    """Script must exit 0 and produce valid JSON."""
    assert isinstance(bundle, dict)


def test_schema_version(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["schema_version"] == SCHEMA_VERSION


def test_authority_projection_only(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["projection_only"] is True


def test_authority_runtime_mutation_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["runtime_mutation_allowed"] is False


def test_authority_promotion_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["promotion_allowed"] is False


def test_authority_production_activation_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["authority"]["production_activation_allowed"] is False


def test_source_mode_live(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["source_mode"] == "LIVE_ARTIFACT_BUNDLE"


def test_fail_closed_reason_none(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle.get("fail_closed_reason") is None


def test_all_operators_detected(bundle: dict) -> None:  # type: ignore[type-arg]
    ids = {s["system_id"] for s in bundle["systems"]}
    assert ids == EXPECTED_OPERATOR_IDS


def test_systems_count(bundle: dict) -> None:  # type: ignore[type-arg]
    assert len(bundle["systems"]) == len(EXPECTED_OPERATOR_IDS)


def test_each_system_has_status(bundle: dict) -> None:  # type: ignore[type-arg]
    valid_statuses = {
        "READY", "READY_SHADOW_STUB_CLOSED", "PARTIAL",
        "PARTIAL_WITH_CPU_BASELINE_CLOSED", "FAIL_CLOSED", "NOT_COMPUTABLE",
        "RANK6_SELECTED",
    }
    for sys_ in bundle["systems"]:
        assert sys_["status"] in valid_statuses, f"{sys_['system_id']} bad status {sys_['status']}"


def test_each_system_shadow_only(bundle: dict) -> None:  # type: ignore[type-arg]
    for sys_ in bundle["systems"]:
        assert sys_["shadow_only"] is True


def test_each_system_projection_packets_have_projection_only(bundle: dict) -> None:  # type: ignore[type-arg]
    for sys_ in bundle["systems"]:
        for pkt in sys_["projection_packets"]:
            assert pkt["projection_only"] is True, (
                f"{sys_['system_id']} packet {pkt['packet_id']} missing projection_only=true"
            )


def test_operator_queue_auto_apply_blocked(bundle: dict) -> None:  # type: ignore[type-arg]
    for item in bundle["operator_queue"]:
        assert item["auto_apply_blocked"] is True


def test_operator_queue_requires_review(bundle: dict) -> None:  # type: ignore[type-arg]
    # Operators with promotion phase fully closed: REVIEWED + requires_operator_review=False
    closed_systems = {"wasserstein", "transport", "chamfer_distance"}
    for item in bundle["operator_queue"]:
        if item.get("target_system") in closed_systems:
            assert item["requires_operator_review"] is False, item.get("target_system")
        else:
            assert item["requires_operator_review"] is True, item.get("target_system")


def test_geodesic_ready(bundle: dict) -> None:  # type: ignore[type-arg]
    sys_ = next(s for s in bundle["systems"] if s["system_id"] == "geodesic")
    assert sys_["status"] == "READY"
    assert sys_["completion_pct"] == 100


def test_norm_geometry_ready(bundle: dict) -> None:  # type: ignore[type-arg]
    sys_ = next(s for s in bundle["systems"] if s["system_id"] == "norm_geometry")
    assert sys_["status"] == "READY"
    assert sys_["completion_pct"] == 100


def test_transport_baseline_promotion_phase_closed(bundle: dict) -> None:  # type: ignore[type-arg]
    sys_ = next(s for s in bundle["systems"] if s["system_id"] == "transport")
    assert sys_["status"] == "READY_SHADOW_STUB_CLOSED"
    assert sys_["completion_pct"] == 100
    assert "advisory-only" in sys_.get("reason", "")


def test_wasserstein_baseline_promotion_phase_closed(bundle: dict) -> None:  # type: ignore[type-arg]
    sys_ = next(s for s in bundle["systems"] if s["system_id"] == "wasserstein")
    assert sys_["status"] == "READY_SHADOW_STUB_CLOSED"
    assert sys_["completion_pct"] == 100
    assert "no-op parity" in sys_.get("reason", "")
    assert "advisory-only" in sys_.get("reason", "")


def test_wasserstein_has_reason_field(bundle: dict) -> None:  # type: ignore[type-arg]
    sys_ = next(s for s in bundle["systems"] if s["system_id"] == "wasserstein")
    assert "reason" in sys_
    assert sys_["reason"] != ""


def test_chamfer_baseline_promotion_phase_closed(bundle: dict) -> None:  # type: ignore[type-arg]
    sys_ = next(s for s in bundle["systems"] if s["system_id"] == "chamfer_distance")
    assert sys_["status"] == "READY_SHADOW_STUB_CLOSED"
    assert sys_["completion_pct"] == 100
    assert "advisory-only" in sys_.get("reason", "")


def test_heavy_tail_implementation_authorized(bundle: dict) -> None:  # type: ignore[type-arg]
    sys_ = next(s for s in bundle["systems"] if s["system_id"] == "heavy_tail")
    assert sys_["status"] == "PARTIAL"
    assert 0 < sys_["completion_pct"] < 50
    assert sys_["shadow_only"] is True
    pkts = sys_["projection_packets"]
    assert len(pkts) >= 1
    assert all(p["projection_only"] is True for p in pkts)
    ledger = sys_["ledger_receipts"]
    assert len(ledger) >= 1
    events = {r["event"] for r in ledger}
    assert any("HEAVY_TAIL_SHADOW_STUB_IMPLEMENTATION_AUTHORIZATION_001" in e for e in events)


def test_no_research_canary_in_source_artifacts(bundle: dict) -> None:  # type: ignore[type-arg]
    for path_str in bundle.get("source_artifacts", []):
        assert "research_canary" not in path_str, (
            f"research_canary artifact leaked into source_artifacts: {path_str}"
        )


def test_output_not_in_out_dir(bundle: dict) -> None:  # type: ignore[type-arg]
    """Output must be written to apps/aal-viz-live-console/public/ only, not out/."""
    assert "apps/aal-viz-live-console/public" in str(OUTPUT)
    assert not str(OUTPUT).startswith(str(ROOT / "out"))


def test_source_artifacts_exist(bundle: dict) -> None:  # type: ignore[type-arg]
    """Every declared source artifact must actually exist on disk."""
    for path_str in bundle.get("source_artifacts", []):
        p = Path(path_str)
        assert p.exists(), f"source_artifact declared but not found: {path_str}"


def test_json_tool_valid() -> None:
    """Output must pass python -m json.tool validation."""
    result = subprocess.run(
        [sys.executable, "-m", "json.tool", str(OUTPUT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"json.tool failed: {result.stderr}"
