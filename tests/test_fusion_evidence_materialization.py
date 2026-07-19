from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.viz import run_fusion_evidence_materialization


def _seed_lineage_sources(output_dir: Path) -> None:
    projections = output_dir / "projections"
    projections.mkdir(parents=True, exist_ok=True)
    for name in (
        "projection_chronoscope_001.latest.json",
        "temporal_snapshot_spine_001.latest.json",
    ):
        shutil.copy2(Path("out/projections") / name, projections / name)


def test_runner_materializes_non_empty_ledgers_and_fusion_sources(
    capsys, tmp_path: Path, monkeypatch
) -> None:
    output_dir = tmp_path / "out"
    monkeypatch.setenv("OUT_DIR", str(output_dir))
    _seed_lineage_sources(output_dir)
    run_fusion_evidence_materialization.main(transient_root=tmp_path)
    captured = capsys.readouterr()
    summary = json.loads(captured.out)

    assert summary["diff_pulse_count"] >= 1
    assert summary["lineage_pulse_count"] >= 1
    assert summary["temporal_state_diff_pulse_ledger_status"] == "ADVISORY_ONLY"
    assert summary["temporal_lineage_pulse_ledger_status"] == "ADVISORY_ONLY"

    drift_ledger = json.loads(
        (output_dir / "projections/temporal_state_diff_pulse_ledger_001.latest.json").read_text(
            encoding="utf-8"
        )
    )
    lineage_ledger = json.loads(
        (output_dir / "projections/temporal_lineage_pulse_ledger_001.latest.json").read_text(
            encoding="utf-8"
        )
    )
    fusion_packet = json.loads(
        (output_dir / "projections/cross_run_topology_fusion_001.latest.json").read_text(
            encoding="utf-8"
        )
    )

    assert drift_ledger["pulse_count"] > 0
    assert lineage_ledger["entry_count"] > 0

    source_entries = {x["source_key"]: x for x in fusion_packet["source_entries"]}
    assert source_entries["temporal_state_diff_pulse_ledger"]["source_status"] == "PRESENT"
    assert source_entries["temporal_lineage_pulse_ledger"]["source_status"] == "PRESENT"

    for payload in (drift_ledger, lineage_ledger, fusion_packet):
        assert payload.get("advisory_only") is True
        assert payload.get("authority_granted") is False
        assert payload.get("mutation_allowed") is False


def test_runner_output_is_deterministic_shape(capsys, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OUT_DIR", str(tmp_path / "out"))
    run_fusion_evidence_materialization.main(transient_root=tmp_path)
    first = json.loads(capsys.readouterr().out)
    run_fusion_evidence_materialization.main(transient_root=tmp_path)
    second = json.loads(capsys.readouterr().out)

    assert first == second
