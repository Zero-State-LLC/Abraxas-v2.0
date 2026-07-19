"""Script: emit deterministic cross-run topology fusion artifacts."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.cross_run_topology_fusion import (
    PATCH_ID,
    build_cross_run_topology_fusion_markdown,
    build_cross_run_topology_fusion_packet,
    write_cross_run_topology_fusion_packet,
)
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.cross_run_topology_fusion_latest


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run deterministic cross-run topology and lineage fusion."
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
        "cross_run_topology_fusion",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "cross_run_topology_fusion_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet: dict[str, Any] = build_cross_run_topology_fusion_packet(
        packet_id="cross_run_topology_fusion_001",
        source_artifact_paths=_manifest_sources(args.manifest),
    )
    write_cross_run_topology_fusion_packet(OUT_PATH, packet)

    markdown_path = OUT_PATH.with_suffix(".md")
    markdown_path.write_text(
        build_cross_run_topology_fusion_markdown(packet),
        encoding="utf-8",
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "cross_run_topology_fusion_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=markdown_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        fusion_node_count=packet["fusion_node_count"],
        fusion_edge_count=packet["fusion_edge_count"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
