#!/usr/bin/env python3
"""Evaluate explicit topology evidence and publish integrity findings v1."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.aal_viz_yggdrasil_topology import (  # noqa: E402
    validate_yggdrasil_topology,
)
from core.aal_viz_yggdrasil_topology_integrity import (  # noqa: E402
    YggdrasilTopologyIntegrityError,
    evaluate_yggdrasil_topology_integrity,
    validate_yggdrasil_topology_integrity,
)

OUTPUT_PATH = (
    ROOT / "out/projections/aal_viz_yggdrasil_topology_integrity_v1.latest.json"
)
TOPOLOGY_SCHEMA = (
    ROOT / "contracts/canon/aal_viz_yggdrasil_topology.v1.schema.json"
)
INTEGRITY_SCHEMA = (
    ROOT / "contracts/canon/aal_viz_yggdrasil_topology_integrity.v1.schema.json"
)
TEMPORAL_SCHEMA = ROOT / "contracts/canon/aal_viz_temporal_diff.v1.schema.json"


def _repository_path(value: str) -> Path:
    candidate = PurePosixPath(value)
    if (
        not value
        or candidate.is_absolute()
        or ".." in candidate.parts
        or "\\" in value
        or (len(value) > 2 and value[1] == ":")
    ):
        raise YggdrasilTopologyIntegrityError(
            f"input path must be repository-relative POSIX: {value}"
        )
    return ROOT / candidate


def _load(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise YggdrasilTopologyIntegrityError(
            f"malformed JSON input: {path.relative_to(ROOT)}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise YggdrasilTopologyIntegrityError(
            f"projection input must be an object: {path.relative_to(ROOT)}"
        )
    return value, hashlib.sha256(raw).hexdigest()


def _generated_at() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch is not None:
        try:
            timestamp = int(epoch)
        except ValueError as exc:
            raise YggdrasilTopologyIntegrityError(
                "SOURCE_DATE_EPOCH must be an integer"
            ) from exc
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_temporal_diff(temporal: dict[str, Any]) -> None:
    schema = json.loads(TEMPORAL_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(temporal),
        key=lambda error: list(error.path),
    )
    if errors:
        raise YggdrasilTopologyIntegrityError(
            f"Temporal Diff schema violation: {errors[0].message}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--topology", required=True, help="Repository-relative topology projection"
    )
    parser.add_argument(
        "--temporal-diff",
        help="Optional repository-relative matching Temporal Diff projection",
    )
    args = parser.parse_args(argv)
    try:
        topology_path = _repository_path(args.topology)
        topology, topology_hash = _load(topology_path)
        validate_yggdrasil_topology(topology, TOPOLOGY_SCHEMA)
        temporal = None
        temporal_hash = None
        if args.temporal_diff is not None:
            temporal_path = _repository_path(args.temporal_diff)
            temporal, temporal_hash = _load(temporal_path)
            _validate_temporal_diff(temporal)
        artifact = evaluate_yggdrasil_topology_integrity(
            topology,
            temporal,
            topology_path=args.topology,
            temporal_diff_path=(
                args.temporal_diff
                or "out/projections/aal_viz_temporal_diff_v1.latest.json"
            ),
            topology_content_sha256=topology_hash,
            temporal_diff_content_sha256=temporal_hash,
            generated_at=_generated_at(),
        )
        validate_yggdrasil_topology_integrity(
            artifact, INTEGRITY_SCHEMA, topology=topology
        )
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    except (OSError, YggdrasilTopologyIntegrityError, ValueError) as exc:
        sys.stderr.write(f"FAIL_CLOSED: {exc}\n")
        return 1
    sys.stdout.write(
        "wrote out/projections/aal_viz_yggdrasil_topology_integrity_v1.latest.json "
        f"[{artifact['status']}]\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
