from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.geometric_binder_orchestrator_integration_harness import (
    BRIER_SCORE,
    DEFAULT_OUT_PATH,
    STATUS,
    build_geometric_binder_orchestrator_integration_harness,
)
from scripts.viz.run_geometric_binder_orchestrator_integration_harness import run


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_geometric_binder_orchestrator_packet_preserves_authority_locks() -> None:
    packet = build_geometric_binder_orchestrator_integration_harness(
        repo_root=REPO_ROOT
    )

    assert packet["status"] == STATUS
    assert packet["brier_score"] == BRIER_SCORE
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["integration_status"] in {
        "READY_WITH_DEGRADED_EVIDENCE",
        "NOT_COMPUTABLE",
    }


def test_geometric_binder_orchestrator_packet_hash_is_canonical() -> None:
    packet = build_geometric_binder_orchestrator_integration_harness(
        repo_root=REPO_ROOT
    )
    without_hash = {
        key: value for key, value in packet.items() if key != "canonical_hash"
    }

    assert packet["canonical_hash"] == canonical_hash(without_hash)


def test_geometric_binder_orchestrator_sources_are_repo_real() -> None:
    packet = build_geometric_binder_orchestrator_integration_harness(
        repo_root=REPO_ROOT
    )
    sources = {source["path"]: source for source in packet["source_summaries"]}

    assert sources["out/temporal_continuity_spine_binder_contract/latest.json"][
        "observed"
    ] is True
    assert sources["out/temporal_continuity_binder_readiness_audit/latest.json"][
        "observed"
    ] is True
    assert sources["out/projections/geometric_projection_spec_001.latest.json"][
        "observed"
    ] is True
    pipeline = sources["contracts/pipelines/aal_viz_projection.v1_1.json"]
    assert pipeline["observed"] is True
    assert "Pipeline" in pipeline["description"]
    assert pipeline["authority_locked"] is True


def test_geometric_binder_orchestrator_runner_writes_receipt(tmp_path: Path) -> None:
    out_path = tmp_path / "receipt.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=out_path)
    written = json.loads(out_path.read_text(encoding="utf-8"))

    assert out_path.exists()
    assert written == packet
    assert written["status"] == STATUS
    assert written["canonical_hash"] == packet["canonical_hash"]


def test_geometric_binder_orchestrator_missing_sources_fail_closed(
    tmp_path: Path,
) -> None:
    packet = build_geometric_binder_orchestrator_integration_harness(
        repo_root=tmp_path
    )

    assert packet["integration_status"] == "NOT_COMPUTABLE"
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["canonical_hash"] == canonical_hash(
        {key: value for key, value in packet.items() if key != "canonical_hash"}
    )
    assert DEFAULT_OUT_PATH.endswith(".latest.json")
