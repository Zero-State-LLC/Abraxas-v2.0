"""Script: emit deterministic temporal stability pressure artifacts."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.temporal_stability_pressure import (
    PATCH_ID,
    build_temporal_stability_pressure_markdown,
    build_temporal_stability_pressure_packet,
    write_temporal_stability_pressure_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.temporal_stability_pressure_latest


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run deterministic temporal stability pressure and stress tensor analytics."
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help="Optional JSON object mapping source keys to artifact paths.",
    )
    return parser.parse_args(argv)


def _manifest_sources(path: str | None) -> dict[str, str] | None:
    if path is None:
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("manifest must be a JSON object mapping source->path")
    return {str(key): str(value) for key, value in payload.items()}


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    diagnostics_logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "temporal_stability_pressure",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "temporal_stability_pressure_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet: dict[str, Any] = build_temporal_stability_pressure_packet(
        packet_id="temporal_stability_pressure_001",
        source_artifact_paths=_manifest_sources(args.manifest),
    )
    write_temporal_stability_pressure_packet(OUT_PATH, packet)

    markdown_path = OUT_PATH.with_suffix(".md")
    markdown_path.write_text(
        build_temporal_stability_pressure_markdown(packet),
        encoding="utf-8",
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "temporal_stability_pressure_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=markdown_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        aggregate_stress_score=packet["aggregate_stress_score"],
        resilience_score=packet["resilience_score"],
        pressure_zone_count=packet["pressure_zone_count"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
