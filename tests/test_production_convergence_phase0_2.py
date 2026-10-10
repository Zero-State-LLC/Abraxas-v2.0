"""Phase 0–2 production convergence package tests."""

from __future__ import annotations

import json
from pathlib import Path

from core.application.advisory_spine import AdvisorySpineRequest, run_advisory_spine
from core.canonical.json import canonical_hash
from core.governance.activation_policy import ActivationLane
from core.production_convergence.phase0_2 import build_phase0_2_package
from tests._repo_mirror import make_repo_mirror

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_phase0_2_package_hashes_stable_without_write() -> None:
    first = build_phase0_2_package(REPO_ROOT, write=False, run_validation=False)
    second = build_phase0_2_package(REPO_ROOT, write=False, run_validation=False)
    assert first["artifacts"] == second["artifacts"]
    entrypoints = first["package"]["entrypoint_inventory.v1.json"]
    assert entrypoints["summary"]["entry_count"] >= 700
    assert entrypoints["summary"]["by_classification"]["SUPPORTED_CLI"] >= 1
    assert entrypoints["summary"]["by_classification"]["EXPERIMENTAL"] >= 1
    interfaces = first["package"]["interface_inventory.v1.json"]
    assert interfaces["summary"]["supported_count"] >= 5
    clusters = first["package"]["duplication_clusters.v1.json"]
    assert clusters["summary"]["cluster_count"] >= 5
    golden = first["package"]["golden_path_trace.v1.json"]
    assert "AlembicSpine?" in golden["supported_spine_target"]["shape"]
    gov = first["package"]["governance_contradiction_map.v1.json"]
    assert gov["summary"]["contradiction_count"] >= 3
    ledger = first["package"]["deprecation_ledger.v1.json"]
    assert ledger["summary"]["entry_count"] >= 3
    assert ledger["canonical_cli"] == "python -m abraxas"
    baseline = first["package"]["baseline.v1.json"]
    assert baseline["baseline_sha"]
    assert baseline["canonical_hash"] == canonical_hash(
        {k: v for k, v in baseline.items() if k != "canonical_hash"}
    )


def test_phase0_2_write_roundtrip(tmp_path: Path) -> None:
    # The package writes under its repo root; use a working-tree mirror so the
    # tracked out/production_convergence files are never rewritten.
    mirror = make_repo_mirror(tmp_path)
    result = build_phase0_2_package(mirror, write=True, run_validation=False)
    out_dir = mirror / result["output_dir"]
    for name in result["artifacts"]:
        path = out_dir / name
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        assert text.endswith("\n")


def test_advisory_spine_local_dev_with_alembic_fixture() -> None:
    task = json.loads(
        (REPO_ROOT / "fixtures/alembic/example_task.json").read_text(encoding="utf-8")
    )
    task = {**task, "run_id": "convergence-spine-test-001"}
    result = run_advisory_spine(
        AdvisorySpineRequest(
            run_id="convergence-spine-test-001",
            activation_lane=ActivationLane.LOCAL_DEV,
            input_payload={"goal": task["goal"]},
            alembic_task=task,
            enable_alembic=True,
        )
    )
    assert result["status"] == "OK"
    assert result["activation"]["permitted"] is True
    assert result["alembic"] is not None
    assert result["advisory_result"]["lane"] == "SHADOW"
    assert result["influences_current_state"] is False
    assert result["result_hash"] == canonical_hash(
        {k: v for k, v in result.items() if k != "result_hash"}
    )


def test_advisory_spine_blocks_external_production() -> None:
    result = run_advisory_spine(
        {
            "run_id": "ext-prod-blocked",
            "activation_lane": "EXTERNAL_PRODUCTION",
            "enable_alembic": False,
        }
    )
    assert result["status"] == "OPERATOR_GATE"
    assert result["error_class"] == "EXTERNAL_PRODUCTION_OPERATOR_GATED"
