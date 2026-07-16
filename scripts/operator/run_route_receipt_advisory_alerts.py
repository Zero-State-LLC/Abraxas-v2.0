#!/usr/bin/env python3
"""Evaluate explicit delta intelligence and publish advisory alerts v1."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.aal_viz_route_receipt_advisory_alerts import (  # noqa: E402
    RouteReceiptAdvisoryAlertsError,
    evaluate_route_receipt_advisory_alerts,
    validate_route_receipt_advisory_acknowledgements,
    validate_route_receipt_advisory_alerts,
)
from core.aal_viz_yggdrasil_topology_delta_intelligence import (  # noqa: E402
    validate_yggdrasil_topology_delta_intelligence,
)

OUTPUT_PATH = (
    ROOT
    / "out/projections/aal_viz_route_receipt_advisory_alerts_v1.latest.json"
)
DELTA_SCHEMA = (
    ROOT
    / "contracts/canon/aal_viz_yggdrasil_topology_delta_intelligence.v1.schema.json"
)
ALERT_SCHEMA = (
    ROOT / "contracts/canon/aal_viz_route_receipt_advisory_alerts.v1.schema.json"
)
ACKNOWLEDGEMENT_SCHEMA = (
    ROOT
    / "contracts/canon/aal_viz_route_receipt_advisory_acknowledgements.v1.schema.json"
)


def _repository_path(value: str) -> Path:
    candidate = PurePosixPath(value)
    if (
        not value
        or candidate.is_absolute()
        or ".." in candidate.parts
        or "\\" in value
        or (len(value) > 2 and value[1] == ":")
    ):
        raise RouteReceiptAdvisoryAlertsError(
            f"input path must be repository-relative POSIX: {value}"
        )
    return ROOT / candidate


def _load(value: str) -> tuple[dict[str, Any], str]:
    raw = _repository_path(value).read_bytes()
    try:
        artifact = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RouteReceiptAdvisoryAlertsError(
            f"malformed JSON input: {value}: {exc}"
        ) from exc
    if not isinstance(artifact, dict):
        raise RouteReceiptAdvisoryAlertsError(
            f"projection input must be an object: {value}"
        )
    return artifact, hashlib.sha256(raw).hexdigest()


def _optional(value: str | None) -> tuple[dict[str, Any] | None, str | None]:
    return (None, None) if value is None else _load(value)


def _generated_at() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        timestamp = int(epoch)
    except ValueError as exc:
        raise RouteReceiptAdvisoryAlertsError(
            "SOURCE_DATE_EPOCH must be an integer"
        ) from exc
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delta-intelligence", required=True)
    parser.add_argument("--prior-alerts")
    parser.add_argument("--acknowledgements")
    args = parser.parse_args(argv)
    try:
        delta, delta_hash = _load(args.delta_intelligence)
        validate_yggdrasil_topology_delta_intelligence(delta, DELTA_SCHEMA)
        prior, prior_hash = _optional(args.prior_alerts)
        if prior is not None:
            validate_route_receipt_advisory_alerts(prior, ALERT_SCHEMA)
        acknowledgements, acknowledgement_hash = _optional(args.acknowledgements)
        if acknowledgements is not None:
            validate_route_receipt_advisory_acknowledgements(
                acknowledgements, ACKNOWLEDGEMENT_SCHEMA
            )
        artifact = evaluate_route_receipt_advisory_alerts(
            delta,
            prior_alerts=prior,
            acknowledgements=acknowledgements,
            source_paths={
                "delta_intelligence": args.delta_intelligence,
                "prior_alerts": args.prior_alerts
                or "out/projections/aal_viz_route_receipt_advisory_alerts_v1.latest.json",
                "acknowledgements": args.acknowledgements
                or "out/projections/route_receipt_advisory_acknowledgements.json",
            },
            content_hashes={
                "delta_intelligence": delta_hash,
                "prior_alerts": prior_hash,
                "acknowledgements": acknowledgement_hash,
            },
            generated_at=_generated_at(),
        )
        validate_route_receipt_advisory_alerts(artifact, ALERT_SCHEMA)
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, RouteReceiptAdvisoryAlertsError) as exc:
        sys.stderr.write(f"FAIL_CLOSED: {exc}\n")
        return 1
    sys.stdout.write(
        "wrote out/projections/aal_viz_route_receipt_advisory_alerts_v1.latest.json "
        f"[{artifact['status']}]\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
