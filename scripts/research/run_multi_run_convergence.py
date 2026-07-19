"""Script: emit deterministic multi-run convergence artifacts."""

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
from core.multi_run_convergence import (
    PATCH_ID,
    build_multi_run_convergence_markdown,
    build_multi_run_convergence_packet,
    write_multi_run_convergence_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.multi_run_convergence_latest


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run deterministic multi-run convergence analytics."
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help="Optional JSON list/object describing source artifact paths.",
    )
    return parser.parse_args(argv)


def _manifest_sources(path: str | None) -> list[str] | None:
    if path is None:
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return sorted(str(item) for item in payload if str(item))
    if isinstance(payload, dict):
        if isinstance(payload.get("source_artifacts"), list):
            return sorted(
                str(item) for item in payload["source_artifacts"] if str(item)
            )
        if isinstance(payload.get("source_artifact_paths"), dict):
            values = payload["source_artifact_paths"].values()
            return sorted(str(item) for item in values if str(item))
        return sorted(str(item) for item in payload.values() if isinstance(item, str))
    raise ValueError("manifest must be a JSON list or object")


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    diagnostics_logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "multi_run_convergence",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "multi_run_convergence_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet: dict[str, Any] = build_multi_run_convergence_packet(
        packet_id="multi_run_convergence_001",
        source_artifacts=_manifest_sources(args.manifest),
    )
    write_multi_run_convergence_packet(OUT_PATH, packet)

    markdown_path = OUT_PATH.with_suffix(".md")
    markdown_path.write_text(
        build_multi_run_convergence_markdown(packet), encoding="utf-8"
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "multi_run_convergence_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=markdown_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        regime_classification=packet["regime_classification"],
        run_observation_count=packet["run_observation_count"],
        remaining_blockers=packet["remaining_blockers"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
