"""Script: emit deterministic temporal state diff artifacts."""

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
from core.temporal_state_diff import (
    PATCH_ID,
    build_temporal_state_diff_markdown,
    build_temporal_state_diff_packet,
    write_temporal_state_diff_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.temporal_state_diff_latest


def _load_manifest(path: str | None) -> dict[str, str] | None:
    if path is None:
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("manifest must be a JSON object mapping surface->path")
    return {str(key): str(value) for key, value in payload.items()}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic temporal state diff.")
    parser.add_argument(
        "--previous-manifest",
        default=None,
        help="Optional JSON map of previous surface artifact paths.",
    )
    parser.add_argument(
        "--current-manifest",
        default=None,
        help="Optional JSON map of current surface artifact paths.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    diagnostics_logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "temporal_state_diff",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "temporal_state_diff_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    previous_manifest = _load_manifest(args.previous_manifest)
    current_manifest = _load_manifest(args.current_manifest)
    packet: dict[str, Any] = build_temporal_state_diff_packet(
        packet_id="temporal_state_diff_001",
        previous_artifact_paths=previous_manifest,
        current_artifact_paths=current_manifest,
    )
    write_temporal_state_diff_packet(OUT_PATH, packet)

    markdown_path = OUT_PATH.with_suffix(".md")
    markdown_path.write_text(
        build_temporal_state_diff_markdown(packet),
        encoding="utf-8",
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "temporal_state_diff_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=markdown_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        total_change_count=packet["total_change_count"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
