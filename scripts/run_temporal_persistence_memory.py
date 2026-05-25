"""Script: emit deterministic temporal persistence memory artifacts."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.temporal_persistence_memory import (
    PATCH_ID,
    build_temporal_persistence_memory_markdown,
    build_temporal_persistence_memory_packet,
    write_temporal_persistence_memory_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.temporal_persistence_memory_latest


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run deterministic temporal persistence memory analytics."
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
        "temporal_persistence_memory",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "temporal_persistence_memory_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet: dict[str, Any] = build_temporal_persistence_memory_packet(
        packet_id="temporal_persistence_memory_001",
        source_artifact_paths=_manifest_sources(args.manifest),
    )
    write_temporal_persistence_memory_packet(OUT_PATH, packet)

    markdown_path = OUT_PATH.with_suffix(".md")
    markdown_path.write_text(
        build_temporal_persistence_memory_markdown(packet),
        encoding="utf-8",
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "temporal_persistence_memory_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=markdown_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        aggregate_memory_score=packet["aggregate_memory_score"],
        memory_zone_count=packet["memory_zone_count"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
