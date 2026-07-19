"""Tests for scripts/viz/build_aal_viz_projection_bundle.py — read-only adapter."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "viz" / "build_aal_viz_projection_bundle.py"
OUTPUT = ROOT / "apps" / "aal-viz-live-console" / "public" / "projection-bundle.json"
YGGDRASIL_TOPOLOGY_OUTPUT = (
    ROOT / "out" / "projections" / "aal_viz_yggdrasil_topology_v1.latest.json"
)
YGGDRASIL_TOPOLOGY_INTEGRITY_OUTPUT = (
    ROOT
    / "out"
    / "projections"
    / "aal_viz_yggdrasil_topology_integrity_v1.latest.json"
)
YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_OUTPUT = (
    ROOT
    / "out"
    / "projections"
    / "aal_viz_yggdrasil_topology_delta_intelligence_v1.latest.json"
)
ROUTE_RECEIPT_ADVISORY_ALERTS_OUTPUT = (
    ROOT
    / "out"
    / "projections"
    / "aal_viz_route_receipt_advisory_alerts_v1.latest.json"
)
P40_FUSION_OVERLAY_ARTIFACT = (
    "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json"
)
OPERATOR_NARRATIVE_OVERLAY_ARTIFACT = (
    "out/projections/operator_narrative_report_ui_overlay_001.latest.json"
)
SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT = (
    "out/audit/subsystem_health_dashboard_001.latest.json"
)
CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_RECEIPT = (
    "out/audit/continuity_namespace_migration_preflight_001.latest.json"
)
SCHEMA_VERSION = "AALViz.LiveConsoleProjectionBundle.v0.2"

EXPECTED_OPERATOR_IDS = {
    "wasserstein",
    "chamfer_distance",
    "geodesic",
    "norm_geometry",
    "transport",
    "heavy_tail",
}


def _section_available(section: object) -> bool:
    return (
        isinstance(section, dict)
        and section.get("status") == "AVAILABLE"
        and section.get("payload") is not None
    )


def _has_rich_operator_platform(bundle: dict) -> bool:  # type: ignore[type-arg]
    """True when stabilization_readiness corpus makes production_slice AVAILABLE."""
    platform = bundle.get("operator_platform")
    if not isinstance(platform, dict):
        return False
    return _section_available(platform.get("production_slice")) and _section_available(
        platform.get("contract_graph")
    )


def _has_full_yggdrasil_contract_corpus(bundle: dict) -> bool:  # type: ignore[type-arg]
    topology = bundle.get("yggdrasil_topology")
    if not isinstance(topology, dict):
        return False
    payload = topology.get("payload")
    if not isinstance(payload, dict):
        return False
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        return False
    counts = summary.get("node_class_counts")
    if not isinstance(counts, dict):
        return False
    return int(counts.get("CONTRACT", 0)) >= 1000


def _has_topology_delta_intelligence(bundle: dict) -> bool:  # type: ignore[type-arg]
    return isinstance(bundle.get("yggdrasil_topology_delta_intelligence"), dict)


def _has_route_receipt_advisory_alerts(bundle: dict) -> bool:  # type: ignore[type-arg]
    return isinstance(bundle.get("route_receipt_advisory_alerts"), dict)


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


@pytest.fixture(scope="module")
def rich_operator_platform_bundle(bundle: dict) -> dict:  # type: ignore[type-arg]
    if not _has_rich_operator_platform(bundle):
        pytest.skip(
            "operator platform production_slice/contract_graph not AVAILABLE "
            "(stabilization_readiness corpus missing from this workspace)"
        )
    return bundle


@pytest.fixture(scope="module")
def full_yggdrasil_contract_bundle(bundle: dict) -> dict:  # type: ignore[type-arg]
    if not _has_full_yggdrasil_contract_corpus(bundle):
        pytest.skip(
            "yggdrasil topology lacks full CONTRACT corpus "
            "(contract inventory sources incomplete in this workspace)"
        )
    return bundle


@pytest.fixture(scope="module")
def topology_delta_bundle(bundle: dict) -> dict:  # type: ignore[type-arg]
    if not _has_topology_delta_intelligence(bundle):
        pytest.skip(
            "yggdrasil_topology_delta_intelligence not embedded "
            "(delta sidecar missing or generation binding rejected)"
        )
    return bundle


@pytest.fixture(scope="module")
def route_alerts_bundle(bundle: dict) -> dict:  # type: ignore[type-arg]
    if not _has_route_receipt_advisory_alerts(bundle):
        pytest.skip(
            "route_receipt_advisory_alerts not embedded "
            "(alerts sidecar missing or generation binding rejected)"
        )
    return bundle


def test_script_exits_zero(bundle: dict) -> None:  # type: ignore[type-arg]
    """Script must exit 0 and produce valid JSON."""
    assert isinstance(bundle, dict)


def test_schema_version(bundle: dict) -> None:  # type: ignore[type-arg]
    assert bundle["schema_version"] == SCHEMA_VERSION


def test_operator_platform_sections_report_status_when_sources_missing(
    bundle: dict,
) -> None:  # type: ignore[type-arg]
    """Without stabilization_readiness corpus, sections fail closed to NOT_COMPUTABLE."""
    platform = bundle["operator_platform"]
    assert platform["schema_version"] == "AALViz.OperatorPlatformProjection.v0.2"
    assert platform["projection_only"] is True
    production_slice = platform["production_slice"]
    assert production_slice["status"] in {"AVAILABLE", "PARTIAL", "NOT_COMPUTABLE"}
    if production_slice["status"] != "AVAILABLE":
        assert production_slice["payload"] is None
        assert production_slice.get("not_computable_reason")


def test_operator_platform_maps_pr959_surfaces(
    rich_operator_platform_bundle: dict,
) -> None:  # type: ignore[type-arg]
    platform = rich_operator_platform_bundle["operator_platform"]
    assert platform["schema_version"] == "AALViz.OperatorPlatformProjection.v0.2"
    assert platform["projection_only"] is True
    assert platform["production_slice"]["payload"]["entrypoint"] == (
        "scripts/artifact/run_artifact_contract_inventory.py"
    )
    assert platform["contract_graph"]["payload"]["contract_count"] == 1098
    assert platform["topology"]["payload"]["nodes"]
    assert platform["evidence_index"]["payload"]["records"]


def test_yggdrasil_topology_sidecar_always_emitted(bundle: dict) -> None:  # type: ignore[type-arg]
    """Topology sidecar is always written; class counts depend on available sources."""
    topology = bundle["yggdrasil_topology"]
    assert topology["schema_version"] == "AALViz.YggdrasilTopology.v1"
    assert topology["authority"]["projection_only"] is True
    summary = topology["payload"]["summary"]
    assert isinstance(summary["node_class_counts"], dict)
    assert summary["node_count"] >= 0
    assert YGGDRASIL_TOPOLOGY_OUTPUT.exists()
    assert json.loads(YGGDRASIL_TOPOLOGY_OUTPUT.read_text(encoding="utf-8")) == topology


def test_yggdrasil_topology_sidecar_is_published_and_embedded(
    full_yggdrasil_contract_bundle: dict,
) -> None:  # type: ignore[type-arg]
    bundle = full_yggdrasil_contract_bundle
    topology = bundle["yggdrasil_topology"]
    assert topology["schema_version"] == "AALViz.YggdrasilTopology.v1"
    assert topology["authority"]["projection_only"] is True
    assert topology["payload"]["summary"]["node_class_counts"]["CONTRACT"] == 1098
    assert topology["payload"]["summary"]["node_count"] > 1500
    assert YGGDRASIL_TOPOLOGY_OUTPUT.exists()
    assert json.loads(YGGDRASIL_TOPOLOGY_OUTPUT.read_text(encoding="utf-8")) == topology
    platform_ids = {
        node["id"] for node in bundle["operator_platform"]["topology"]["payload"]["nodes"]
    }
    assert platform_ids == {node["id"] for node in topology["payload"]["nodes"]}


def test_yggdrasil_integrity_sidecar_is_published_and_embedded(bundle: dict) -> None:  # type: ignore[type-arg]
    integrity = bundle["yggdrasil_topology_integrity"]
    topology = bundle["yggdrasil_topology"]
    assert integrity["schema_version"] == "AALViz.YggdrasilTopologyIntegrity.v1"
    assert integrity["authority"]["projection_only"] is True
    assert integrity["authority"]["alert_delivery_allowed"] is False
    assert (
        integrity["generation"]["topology_generation_id"]
        == topology["generation"]["topology_generation_id"]
    )
    assert integrity["payload"]["summary"]["finding_count"] >= 0
    assert YGGDRASIL_TOPOLOGY_INTEGRITY_OUTPUT.exists()
    assert (
        json.loads(YGGDRASIL_TOPOLOGY_INTEGRITY_OUTPUT.read_text(encoding="utf-8"))
        == integrity
    )


def test_yggdrasil_delta_intelligence_is_validated_and_embedded(
    topology_delta_bundle: dict,
) -> None:  # type: ignore[type-arg]
    bundle = topology_delta_bundle
    delta = bundle["yggdrasil_topology_delta_intelligence"]
    topology = bundle["yggdrasil_topology"]
    assert delta["schema_version"] == "AALViz.YggdrasilTopologyDeltaIntelligence.v1"
    assert delta["authority"]["projection_only"] is True
    assert delta["authority"]["automatic_remediation_allowed"] is False
    assert (
        delta["generation"]["current_topology_generation_id"]
        == topology["generation"]["topology_generation_id"]
    )
    assert delta["summary"]["active_priority_count"] > 0
    assert json.loads(
        YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_OUTPUT.read_text(encoding="utf-8")
    ) == delta


def test_route_receipt_advisory_alerts_are_validated_and_embedded(
    route_alerts_bundle: dict,
) -> None:  # type: ignore[type-arg]
    bundle = route_alerts_bundle
    alerts = bundle["route_receipt_advisory_alerts"]
    delta = bundle["yggdrasil_topology_delta_intelligence"]
    assert alerts["schema_version"] == "AALViz.RouteReceiptAdvisoryAlerts.v1"
    assert alerts["authority"]["projection_only"] is True
    assert alerts["authority"]["notification_delivery_allowed"] is False
    assert alerts["authority"]["acknowledgement_writeback_allowed"] is False
    assert (
        alerts["generation"]["delta_generation_id"]
        == delta["generation"]["delta_generation_id"]
    )
    assert alerts["summary"]["active_count"] == 0
    assert alerts["summary"]["suppressed_count"] == 162
    assert ROUTE_RECEIPT_ADVISORY_ALERTS_OUTPUT.exists()
    assert json.loads(
        ROUTE_RECEIPT_ADVISORY_ALERTS_OUTPUT.read_text(encoding="utf-8")
    ) == alerts


def test_operator_platform_is_deterministic() -> None:
    import scripts.viz.build_aal_viz_projection_bundle as module

    fixed_time = "2026-07-15T00:00:00Z"
    first = module._build_operator_platform([], [], generated_at=fixed_time)[0]
    second = module._build_operator_platform([], [], generated_at=fixed_time)[0]
    assert first == second
    assert first["topology"]["payload"]["nodes"] == sorted(
        first["topology"]["payload"]["nodes"], key=lambda item: item["id"]
    )
    assert first["topology"]["payload"]["edges"] == sorted(
        first["topology"]["payload"]["edges"], key=lambda item: item["id"]
    )


def test_operator_platform_maps_temporal_diff_v1_additively(monkeypatch) -> None:
    import scripts.viz.build_aal_viz_projection_bundle as module

    cases = json.loads(
        (
            ROOT / "tests/fixtures/aal_viz_temporal_diff_v1/valid_cases.json"
        ).read_text(encoding="utf-8")
    )["cases"]
    temporal_artifact = next(
        case["artifact"] for case in cases if case["name"] == "topology_changes"
    )
    temporal_path = module.ROOT / module.OPERATOR_PLATFORM_SOURCES["temporal_diff"]
    real_load_safe = module._load_safe

    def _patched(path: Path):
        if path == temporal_path:
            return temporal_artifact
        return real_load_safe(path)

    monkeypatch.setattr(module, "_load_safe", _patched)
    monkeypatch.setattr(
        module,
        "_source_descriptor",
        lambda key, payload: {
            "source_key": key,
            "path": module.OPERATOR_PLATFORM_SOURCES[key],
            "declared_canonical_hash": (
                payload.get("canonical_hash") if payload else None
            ),
            "content_sha256": "a" * 64 if payload else None,
            "integrity_state": "VERIFIED" if payload else "NOT_COMPUTABLE",
        },
    )
    platform = module._build_operator_platform(
        [], [], generated_at="2026-07-15T00:00:00Z"
    )[0]
    payload = platform["temporal_diff"]["payload"]
    assert (
        payload["prior_generation_id"]
        == temporal_artifact["prior_generation"]["generation_id"]
    )
    assert (
        payload["current_generation_id"]
        == temporal_artifact["current_generation"]["generation_id"]
    )
    assert payload["comparison_scope"] == sorted(temporal_artifact["comparison_scope"])
    assert payload["category_counts"] == temporal_artifact["summary"]["category_counts"]
    assert payload["lineage_shift_count"] == 0
    assert payload["queue_delta_count"] == 0
    assert payload["transport_delta_count"] == 0
    assert {entry["category"] for entry in payload["entries"]} == {
        "TOPOLOGY_EDGE", "TOPOLOGY_NODE",
    }


def test_operator_platform_rejects_tampered_temporal_diff() -> None:
    import scripts.viz.build_aal_viz_projection_bundle as module

    artifact = json.loads(
        (
            ROOT / "tests/fixtures/aal_viz_temporal_diff_v1/valid_cases.json"
        ).read_text(encoding="utf-8")
    )["cases"][0]["artifact"]
    tampered = json.loads(json.dumps(artifact))
    tampered["canonical_hash"] = "0" * 64
    with pytest.raises(ValueError, match="canonical hash mismatch"):
        module._validate_temporal_diff_source(tampered)

    tampered = json.loads(json.dumps(artifact))
    tampered["authority"]["runtime_mutation_allowed"] = True
    with pytest.raises(ValueError, match="schema violation|authority locks"):
        module._validate_temporal_diff_source(tampered)


def test_operator_platform_missing_sources_are_section_not_computable(monkeypatch) -> None:
    import scripts.viz.build_aal_viz_projection_bundle as module

    platform_paths = {
        module.ROOT / path for path in module.OPERATOR_PLATFORM_SOURCES.values()
    }
    real_load_safe = module._load_safe

    def _patched(path: Path):
        if path in platform_paths:
            return None
        return real_load_safe(path)

    monkeypatch.setattr(module, "_load_safe", _patched)
    platform = module.build_bundle()["operator_platform"]
    for section in ["system_status", "topology", "production_slice", "contract_graph", "evidence_index", "temporal_diff"]:
        assert platform[section]["status"] == "NOT_COMPUTABLE"
        assert platform[section]["payload"] is None
        assert platform[section]["not_computable_reason"]


def test_operator_platform_schema_validates(bundle: dict) -> None:  # type: ignore[type-arg]
    import jsonschema

    schema = json.loads(
        (ROOT / "contracts/canon/aal_viz_operator_platform_projection.v0.2.schema.json").read_text()
    )
    jsonschema.Draft202012Validator(schema).validate(bundle["operator_platform"])


def test_operator_platform_source_paths_are_relative(bundle: dict) -> None:  # type: ignore[type-arg]
    for source in bundle["operator_platform"]["source_artifacts"]:
        assert not Path(source["path"]).is_absolute()
        assert source["content_sha256"] is None or len(source["content_sha256"]) == 64


def test_source_date_epoch_produces_repeatable_bundle(monkeypatch) -> None:
    import scripts.viz.build_aal_viz_projection_bundle as module

    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1784073600")
    first = module.build_bundle()
    second = module.build_bundle()
    assert first == second
    assert first["generated_at"] == "2026-07-15T00:00:00Z"


def test_operator_platform_authority_violation_fails_validation(bundle: dict) -> None:  # type: ignore[type-arg]
    import scripts.viz.build_aal_viz_projection_bundle as module

    mutated = json.loads(json.dumps(bundle))
    mutated["operator_platform"]["projection_only"] = False
    with pytest.raises(ValueError, match="operator_platform.projection_only"):
        module._validate_bundle(mutated)


def test_yggdrasil_topology_authority_violation_fails_validation(bundle: dict) -> None:  # type: ignore[type-arg]
    import scripts.viz.build_aal_viz_projection_bundle as module

    mutated = json.loads(json.dumps(bundle))
    mutated["yggdrasil_topology"]["authority"]["runtime_mutation_allowed"] = True
    with pytest.raises(ValueError, match="topology schema violation|authority"):
        module._validate_bundle(mutated)


def test_yggdrasil_integrity_authority_violation_fails_validation(bundle: dict) -> None:  # type: ignore[type-arg]
    import scripts.viz.build_aal_viz_projection_bundle as module

    mutated = json.loads(json.dumps(bundle))
    mutated["yggdrasil_topology_integrity"]["authority"][
        "alert_delivery_allowed"
    ] = True
    with pytest.raises(ValueError, match="integrity schema violation|authority"):
        module._validate_bundle(mutated)


def test_advisory_alert_authority_and_binding_violations_fail_validation(
    route_alerts_bundle: dict,
) -> None:  # type: ignore[type-arg]
    import scripts.viz.build_aal_viz_projection_bundle as module

    bundle = route_alerts_bundle
    mutated = json.loads(json.dumps(bundle))
    mutated["route_receipt_advisory_alerts"]["authority"][
        "notification_delivery_allowed"
    ] = True
    with pytest.raises(ValueError, match="schema violation|authority"):
        module._validate_bundle(mutated)

    mutated = json.loads(json.dumps(bundle))
    mutated["route_receipt_advisory_alerts"]["generation"][
        "delta_generation_id"
    ] = "f" * 64
    with pytest.raises(ValueError, match="generation|hash"):
        module._validate_bundle(mutated)


def test_operator_platform_never_reads_research_canary(bundle: dict) -> None:  # type: ignore[type-arg]
    assert not any("research_canary" in source for source in bundle["source_artifacts"])
    topology = bundle["yggdrasil_topology"]
    assert not any(
        "research_canary" in source["path"] for source in topology["source_artifacts"]
    )
    integrity = bundle["yggdrasil_topology_integrity"]
    assert not any(
        "research_canary" in source["path"]
        for source in integrity["source_artifacts"]
    )


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


def test_source_artifacts_are_repo_relative(bundle: dict) -> None:  # type: ignore[type-arg]
    for source in bundle["source_artifacts"]:
        assert not Path(source).is_absolute()
        assert ":\\" not in source


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
    import scripts.viz.build_aal_viz_projection_bundle as module

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
    import scripts.viz.build_aal_viz_projection_bundle as module

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


def test_migration_preflight_posture_ingested_from_preflight_receipt(
    bundle: dict,
) -> None:  # type: ignore[type-arg]
    posture = bundle.get("migration_preflight_posture")
    assert posture is not None
    assert posture["status"] == "CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_READY_ADVISORY_ONLY"
    assert posture["check_count"] == 12
    assert posture["pass_count"] == 12
    assert posture["held_count"] == 0
    assert posture["alias_design_state"] == "DESIGN_ONLY_HELD"
    assert posture["valid_for_implementation"] is False
    assert posture["authority_granted"] is False
    assert CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_RECEIPT in bundle.get(
        "source_artifacts", []
    )


def test_migration_preflight_posture_fails_closed_when_preflight_receipt_missing(
    monkeypatch,
) -> None:
    import scripts.viz.build_aal_viz_projection_bundle as module

    real_load_safe = module._load_safe

    def _patched(path: Path):
        if path == module.ROOT / CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_RECEIPT:
            return None
        return real_load_safe(path)

    monkeypatch.setattr(module, "_load_safe", _patched)
    bundle = module.build_bundle()
    posture = bundle["migration_preflight_posture"]
    assert posture["source_status"] == "MISSING"
    assert posture["status"] == "NOT_COMPUTABLE"
    assert posture["check_count"] == 0


def test_migration_preflight_posture_fails_closed_when_preflight_receipt_malformed(
    monkeypatch,
) -> None:
    import scripts.viz.build_aal_viz_projection_bundle as module

    real_load_safe = module._load_safe

    def _patched(path: Path):
        if path == module.ROOT / CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_RECEIPT:
            return {"status": "BROKEN"}
        return real_load_safe(path)

    monkeypatch.setattr(module, "_load_safe", _patched)
    bundle = module.build_bundle()
    posture = bundle["migration_preflight_posture"]
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
    import scripts.viz.build_aal_viz_projection_bundle as module

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
