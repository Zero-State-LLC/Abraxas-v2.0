#!/usr/bin/env python3
"""AAL-Viz instantiation projection builder (RDI-4/5 console feed).

Reads:  input/fixtures/instantiation/experiments/*.v1.json (synthetic specs)
Runs:   the RDI-5 fixture harness (pure; no live evidence, no intervention)
Writes: out/instantiation/experiment_records.latest.json      (AUDIT_EVIDENCE)
        out/instantiation/projection_view.latest.json          (AUDIT_EVIDENCE)
        apps/aal-viz-live-console/public/instantiation-projection.json

The console feed is the InstantiationProjectionView.v1 payload itself:
projection-only authority, shadow findings overlaid verbatim, no scores or
aggregate depth. Fails closed: any fixture or contract error aborts the build
without writing partial output.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canonical.artifact_classification import ArtifactClass  # noqa: E402
from core.canonical.json import write_canonical_json, write_classified_json  # noqa: E402
from core.instantiation import (  # noqa: E402
    build_instantiation_projection,
    detect_instantiation_anomalies,
    run_fixture_experiment,
    validate_experiment_record,
    validate_instantiation_projection,
)

FIXTURES_DIR = ROOT / "input" / "fixtures" / "instantiation" / "experiments"
OUT_DIR = ROOT / "out" / "instantiation"
CONSOLE_FEED = (
    ROOT / "apps" / "aal-viz-live-console" / "public" / "instantiation-projection.json"
)


def build() -> dict:
    specs = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(FIXTURES_DIR.glob("*.v1.json"))
    ]
    if not specs:
        raise SystemExit(f"no experiment fixtures found under {FIXTURES_DIR}")

    records = [run_fixture_experiment(spec) for spec in specs]
    for record in records:
        validate_experiment_record(record)

    states = [record["baseline_state"] for record in records] + [
        record["observed_state"] for record in records
    ]
    transitions = [record["transition"] for record in records]
    shadow = detect_instantiation_anomalies(
        states, transitions, report_id="isr-aal-viz-instantiation"
    )
    view = build_instantiation_projection(
        states,
        transitions,
        view_id="ipv-aal-viz-instantiation",
        shadow_report=shadow,
    )
    validate_instantiation_projection(view)
    return {"records": records, "view": view}


def main() -> int:
    built = build()
    records_payload = {
        "schema_version": "InstantiationExperimentRecordSet.v1",
        "records": built["records"],
        "record_count": len(built["records"]),
    }
    write_classified_json(
        OUT_DIR / "experiment_records.latest.json",
        records_payload,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
    )
    # Wrap the sealed view so the classification stamp never mutates the
    # view payload itself (its view_hash must keep verifying as-built).
    write_classified_json(
        OUT_DIR / "projection_view.latest.json",
        {"schema_version": "InstantiationProjectionArtifact.v1", "view": built["view"]},
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
    )
    # Console feed keeps the exact sealed view payload (hash must verify
    # client-side against the view body, so no classification stamp here).
    write_canonical_json(CONSOLE_FEED, built["view"])
    summary = {
        "records": len(built["records"]),
        "findings": len(built["view"]["shadow_overlay"]["findings"]),
        "view_hash": built["view"]["view_hash"],
        "console_feed": str(CONSOLE_FEED.relative_to(ROOT)),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
