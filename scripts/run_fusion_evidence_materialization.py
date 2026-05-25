from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canonical.json import write_canonical_json
from core.config import RuntimePaths
from core.cross_run_topology_fusion import build_cross_run_topology_fusion_packet, write_cross_run_topology_fusion_packet
from core.ingest.universal_ingest_receipt import build_from_input_path, write_universal_ingest_receipt
from core.temporal_lineage_pulse_ledger import build_temporal_lineage_pulse_ledger, write_temporal_lineage_pulse_ledger
from core.temporal_state_diff import build_temporal_state_diff_packet, write_temporal_state_diff_packet
from core.temporal_state_diff_pulse_ledger import build_temporal_state_diff_pulse_ledger, write_temporal_state_diff_pulse_ledger


def _write_lineage_fixture(path: Path, *, pulse_id: str, chronoscope: Path, snapshot_spine: Path) -> None:
    write_canonical_json(
        path,
        {
            "schema": "LocalLineagePulseFixture.v1",
            "pulse_id": pulse_id,
            "projection_chronoscope": chronoscope.as_posix(),
            "temporal_snapshot_spine": snapshot_spine.as_posix(),
            "advisory_only": True,
            "authority_granted": False,
            "mutation_allowed": False,
        },
    )


def main() -> None:
    paths = RuntimePaths.from_env()
    tmp_dir = Path(".tmp") / "fusion_evidence"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    ingest_fixtures = [
        Path("fixtures/ingest/local_signal_test_001.json"),
        Path("fixtures/ingest/local_signal_test_002.json"),
        Path("fixtures/ingest/local_signal_test_003.json"),
        Path("fixtures/ingest/local_signal_test_004.json"),
        Path("fixtures/ingest/local_signal_test_005.json"),
    ]

    ingest_receipts: list[Path] = []
    for idx, fixture in enumerate(ingest_fixtures, start=1):
        packet = build_from_input_path(fixture)
        out = tmp_dir / f"ingest_receipt_{idx:03d}.json"
        write_universal_ingest_receipt(out, packet)
        ingest_receipts.append(out)

    diff_pulses: list[Path] = []
    for idx, (prev_path, curr_path) in enumerate(zip(ingest_receipts, ingest_receipts[1:]), start=1):
        packet = build_temporal_state_diff_packet(
            packet_id=f"temporal_state_diff_local_pulse_{idx:03d}",
            previous_artifact_paths={"universal_ingest_receipt": prev_path.as_posix()},
            current_artifact_paths={"universal_ingest_receipt": curr_path.as_posix()},
        )
        out = tmp_dir / f"temporal_state_diff_pulse_{idx:03d}.json"
        write_temporal_state_diff_packet(out, packet)
        diff_pulses.append(out)

    diff_ledger = build_temporal_state_diff_pulse_ledger(pulse_paths=[x.as_posix() for x in diff_pulses])

    latest_diff_packet = build_temporal_state_diff_packet(packet_id="temporal_state_diff_001")
    write_temporal_state_diff_packet(paths.temporal_state_diff_latest, latest_diff_packet)
    write_temporal_state_diff_pulse_ledger(paths.temporal_state_diff_pulse_ledger_latest, diff_ledger)

    lineage_dir = Path("fixtures/lineage")
    lineage_dir.mkdir(parents=True, exist_ok=True)
    chronoscope = paths.projection_chronoscope_latest
    snapshot_spine = paths.temporal_snapshot_spine_latest
    lineage_fixtures = [
        lineage_dir / "local_lineage_pulse_001.json",
        lineage_dir / "local_lineage_pulse_002.json",
        lineage_dir / "local_lineage_pulse_003.json",
    ]
    for idx, target in enumerate(lineage_fixtures, start=1):
        _write_lineage_fixture(
            target,
            pulse_id=f"local_lineage_pulse_{idx:03d}",
            chronoscope=chronoscope,
            snapshot_spine=snapshot_spine,
        )

    lineage_ledger = build_temporal_lineage_pulse_ledger(pulses=[x.as_posix() for x in lineage_fixtures])
    write_temporal_lineage_pulse_ledger(paths.temporal_lineage_pulse_ledger_latest, lineage_ledger)

    fusion_packet = build_cross_run_topology_fusion_packet(packet_id="cross_run_topology_fusion_001")
    write_cross_run_topology_fusion_packet(paths.cross_run_topology_fusion_latest, fusion_packet)

    drift_summary = fusion_packet.get("drift_corridor_summary") or {}
    lineage_corridors = [
        x for x in fusion_packet.get("lineage_fusion_corridors", []) if isinstance(x, dict)
    ]
    lineage_evidence_count = sum(int(x.get("evidence_count", 0)) for x in lineage_corridors)
    lineage_status = "NOT_COMPUTABLE" if not lineage_corridors else "ADVISORY_ONLY"

    summary = {
        "ingest_pulse_count": len(ingest_receipts),
        "diff_pulse_count": len(diff_pulses),
        "lineage_pulse_count": len(lineage_fixtures),
        "temporal_state_diff_pulse_ledger_status": "ADVISORY_ONLY" if diff_ledger.get("pulse_count", 0) > 0 else "NOT_COMPUTABLE",
        "temporal_lineage_pulse_ledger_status": "ADVISORY_ONLY" if lineage_ledger.get("entry_count", 0) > 0 else "NOT_COMPUTABLE",
        "fusion_final_status": fusion_packet.get("final_status"),
        "drift_corridor_status": drift_summary.get("drift_corridor_status"),
        "drift_evidence_count": drift_summary.get("evidence_count"),
        "lineage_corridor_status": lineage_status,
        "lineage_evidence_count": lineage_evidence_count,
        "remaining_blockers": fusion_packet.get("remaining_blockers", []),
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
