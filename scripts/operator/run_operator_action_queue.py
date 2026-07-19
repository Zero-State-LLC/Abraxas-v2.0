"""Script: emit deterministic operator action queue artifacts."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.operator_action_queue import (
    PATCH_ID,
    build_operator_action_queue_markdown,
    build_operator_action_queue_packet,
    write_operator_action_queue_packet,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_action_queue_latest


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "operator_action_queue",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "operator_action_queue_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_operator_action_queue_packet(queue_id="operator_action_queue_001")
    write_operator_action_queue_packet(OUT_PATH, packet)

    markdown_path = OUT_PATH.with_suffix(".md")
    markdown_path.write_text(
        build_operator_action_queue_markdown(packet),
        encoding="utf-8",
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "operator_action_queue_completed",
        artifact_path=OUT_PATH.as_posix(),
        markdown_path=markdown_path.as_posix(),
        correlation_id=correlation_id,
        final_status=packet["final_status"],
        operator_action_item_count=packet["operator_action_item_count"],
        escalation_count=packet["escalation_count"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
