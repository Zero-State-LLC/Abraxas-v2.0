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
P40_FUSION_OVERLAY_ARTIFACT = (
    "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json"
)
OPERATOR_NARRATIVE_OVERLAY_ARTIFACT = (
    "out/projections/operator_narrative_report_ui_overlay_001.latest.json"
)
SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT = (
    "out/audit/subsystem_health_dashboard_001.latest.json"
)
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


def test_fusion_overlay_ingested_when_p40_present(bundle: dict) -> None:  # type: ignore[type-arg]
    p40_path = ROOT / "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json"
    if not p40_path.exists():
        pytest.skip("P40 fusion overlay artifact not present in workspace")

    fusion = bundle.get("fusion_overlay")
    assert fusion is not None
    assert fusion["packet_type"] == "AALVizClimateMotifFusionOverlay.v1"
    assert isinstance(fusion.get("overlay_nodes"), list)
    assert len(fusion["overlay_nodes"]) > 0
    assert fusion["governance_flags"]["advisory_only"] is True
    assert fusion["governance_flags"]["projection_only"] is True
    assert P40_FUSION_OVERLAY_ARTIFACT in bundle.get("source_artifacts", [])


def test_operator_narrative_report_ingested_when_overlay_present(bundle: dict) -> None:  # type: ignore[type-arg]
    overlay_path = ROOT / "out/projections/operator_narrative_report_ui_overlay_001.latest.json"
    if not overlay_path.exists():
        pytest.skip("Operator narrative UI overlay artifact not present in workspace")

    narrative = bundle.get("operator_narrative_report")
    assert narrative is not None
    assert narrative["packet_type"] == "OperatorNarrativeReportUIOverlay.v1"
    assert isinstance(narrative.get("section_navigation"), list)
    assert len(narrative["section_navigation"]) > 0
    assert isinstance(narrative.get("overlay_cards"), list)
    assert len(narrative["overlay_cards"]) > 0
    assert narrative["governance_flags"]["advisory_only"] is True
    assert narrative["governance_flags"]["projection_only"] is True
    assert OPERATOR_NARRATIVE_OVERLAY_ARTIFACT in bundle.get("source_artifacts", [])


def test_migration_runner_posture_ingested_from_dashboard_receipt(
    bundle: dict,
) -> None:  # type: ignore[type-arg]
    posture = bundle.get("migration_runner_posture")
    assert posture is not None
    assert posture["status"] == "CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY"
    assert posture["requested_execution_result"] == "READY"
    assert (
        posture["safe_next_surface"]
        == "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
    )
    assert posture["authority_granted"] is False
    assert SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT in bundle.get("source_artifacts", [])


def test_migration_runner_posture_fails_closed_when_dashboard_receipt_missing(
    monkeypatch,
) -> None:
    import Scripts.build_aal_viz_projection_bundle as module

    real_load_safe = module._load_safe

    def _patched(path: Path):
        if path == module.ROOT / SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT:
            return None
        return real_load_safe(path)

    monkeypatch.setattr(module, "_load_safe", _patched)
    bundle = module.build_bundle()
    posture = bundle["migration_runner_posture"]
    assert posture["source_status"] == "MISSING"
    assert posture["status"] == "NOT_COMPUTABLE"
    assert posture["requested_execution_result"] == "NOT_COMPUTABLE"


def test_migration_runner_posture_fails_closed_when_dashboard_receipt_malformed(
    monkeypatch,
) -> None:
    import Scripts.build_aal_viz_projection_bundle as module

    real_load_safe = module._load_safe

    def _patched(path: Path):
        if path == module.ROOT / SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT:
            return {"status": "BROKEN"}
        return real_load_safe(path)

    monkeypatch.setattr(module, "_load_safe", _patched)
    bundle = module.build_bundle()
    posture = bundle["migration_runner_posture"]
    assert posture["source_status"] == "NOT_COMPUTABLE"
    assert posture["status"] == "NOT_COMPUTABLE"
    assert posture["blocked_action_count"] == 0


def test_combined_posture_ingested_from_dashboard_runner_and_classifier(
    bundle: dict,
) -> None:  # type: ignore[type-arg]
    posture = bundle.get("combined_health_migration_artifact_posture")
    assert posture is not None
    assert posture["health_status"] == "SUBSYSTEM_HEALTH_DASHBOARD_READY_ADVISORY_ONLY"
    assert (
        posture["migration_runner_status"]
        == "CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY"
    )
    assert posture["artifact_lifecycle_status"] == "ADVISORY_ONLY"
    assert posture["safe_next_surface"] == "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
    assert posture["authority_granted"] is False
    assert posture["findings_by_source"]["health"]
    assert posture["findings_by_source"]["migration"]
    assert posture["findings_by_source"]["artifact"]


def test_combined_posture_fails_closed_when_dashboard_receipt_missing(
    monkeypatch,
) -> None:
    import Scripts.build_aal_viz_projection_bundle as module

    real_load_safe = module._load_safe

    def _patched(path: Path):
        if path == module.ROOT / SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT:
            return None
        return real_load_safe(path)

    monkeypatch.setattr(module, "_load_safe", _patched)
    bundle = module.build_bundle()
    posture = bundle["combined_health_migration_artifact_posture"]
    assert posture["source_status"] == "MISSING"
    assert posture["status"] == "NOT_COMPUTABLE"
    assert posture["health_status"] == "MISSING"


def test_combined_posture_fails_closed_when_classifier_receipt_missing(
    monkeypatch,
) -> None:
    import core.live_projection_health_migration_artifact as module

    real_load_json = module._load_json

    def _patched(path: Path):
        if path == ROOT / module.ARTIFACT_CLASSIFIER_RECEIPT_PATH:
            return {}, "MISSING"
        return real_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    posture, observed_sources = module.build_combined_health_migration_artifact_posture(
        repo_root=ROOT
    )
    assert posture["source_status"] == "MISSING"
    assert posture["artifact_lifecycle_status"] == "ADVISORY_ONLY"
    assert module.SUBSYSTEM_HEALTH_RECEIPT_PATH in observed_sources


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
    assert sys_["completion_pct"] == 78
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
