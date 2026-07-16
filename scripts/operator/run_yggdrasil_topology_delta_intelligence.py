#!/usr/bin/env python3
"""Compare explicit YGGDRASIL generations and publish delta intelligence v1."""

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
from core.aal_viz_yggdrasil_topology_delta_intelligence import (  # noqa: E402
    YggdrasilTopologyDeltaIntelligenceError,
    evaluate_yggdrasil_topology_delta_intelligence,
    validate_yggdrasil_topology_delta_intelligence,
)
from core.aal_viz_temporal_diff import AUTHORITY as TEMPORAL_AUTHORITY  # noqa: E402
from core.aal_viz_yggdrasil_topology_integrity import (  # noqa: E402
    validate_yggdrasil_topology_integrity,
)

OUTPUT_PATH = (
    ROOT
    / "out/projections/aal_viz_yggdrasil_topology_delta_intelligence_v1.latest.json"
)
TOPOLOGY_SCHEMA = ROOT / "contracts/canon/aal_viz_yggdrasil_topology.v1.schema.json"
INTEGRITY_SCHEMA = (
    ROOT / "contracts/canon/aal_viz_yggdrasil_topology_integrity.v1.schema.json"
)
TEMPORAL_SCHEMA = ROOT / "contracts/canon/aal_viz_temporal_diff.v1.schema.json"
DELTA_SCHEMA = (
    ROOT
    / "contracts/canon/aal_viz_yggdrasil_topology_delta_intelligence.v1.schema.json"
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
        raise YggdrasilTopologyDeltaIntelligenceError(
            f"input path must be repository-relative POSIX: {value}"
        )
    return ROOT / candidate


def _load(value: str) -> tuple[dict[str, Any], str]:
    path = _repository_path(value)
    raw = path.read_bytes()
    try:
        artifact = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise YggdrasilTopologyDeltaIntelligenceError(
            f"malformed JSON input: {value}: {exc}"
        ) from exc
    if not isinstance(artifact, dict):
        raise YggdrasilTopologyDeltaIntelligenceError(
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
        raise YggdrasilTopologyDeltaIntelligenceError(
            "SOURCE_DATE_EPOCH must be an integer"
        ) from exc
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def _validate_temporal(artifact: dict[str, Any]) -> None:
    schema = json.loads(TEMPORAL_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(artifact),
        key=lambda error: list(error.path),
    )
    if errors:
        raise YggdrasilTopologyDeltaIntelligenceError(
            f"Temporal Diff schema violation: {errors[0].message}"
        )
    if artifact.get("authority") != TEMPORAL_AUTHORITY:
        raise YggdrasilTopologyDeltaIntelligenceError(
            "Temporal Diff authority locks are malformed"
        )
    expected_hash = hashlib.sha256(
        json.dumps(
            {key: value for key, value in artifact.items() if key != "canonical_hash"},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()
    if artifact.get("canonical_hash") != expected_hash:
        raise YggdrasilTopologyDeltaIntelligenceError(
            "Temporal Diff canonical hash mismatch"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prior-topology", required=True)
    parser.add_argument("--current-topology", required=True)
    parser.add_argument("--prior-integrity")
    parser.add_argument("--current-integrity")
    parser.add_argument("--temporal-diff")
    args = parser.parse_args(argv)
    try:
        prior_topology, prior_topology_hash = _load(args.prior_topology)
        current_topology, current_topology_hash = _load(args.current_topology)
        validate_yggdrasil_topology(prior_topology, TOPOLOGY_SCHEMA)
        validate_yggdrasil_topology(current_topology, TOPOLOGY_SCHEMA)
        prior_integrity, prior_integrity_hash = _optional(args.prior_integrity)
        current_integrity, current_integrity_hash = _optional(args.current_integrity)
        if prior_integrity is not None:
            validate_yggdrasil_topology_integrity(
                prior_integrity, INTEGRITY_SCHEMA, topology=prior_topology
            )
        if current_integrity is not None:
            validate_yggdrasil_topology_integrity(
                current_integrity, INTEGRITY_SCHEMA, topology=current_topology
            )
        temporal_diff, temporal_hash = _optional(args.temporal_diff)
        if temporal_diff is not None:
            _validate_temporal(temporal_diff)
        default_integrity = (
            "out/projections/aal_viz_yggdrasil_topology_integrity_v1.latest.json"
        )
        artifact = evaluate_yggdrasil_topology_delta_intelligence(
            prior_topology,
            current_topology,
            prior_integrity=prior_integrity,
            current_integrity=current_integrity,
            temporal_diff=temporal_diff,
            source_paths={
                "prior_topology": args.prior_topology,
                "current_topology": args.current_topology,
                "prior_integrity": args.prior_integrity or default_integrity,
                "current_integrity": args.current_integrity or default_integrity,
                "temporal_diff": args.temporal_diff
                or "out/projections/aal_viz_temporal_diff_v1.latest.json",
            },
            content_hashes={
                "prior_topology": prior_topology_hash,
                "current_topology": current_topology_hash,
                "prior_integrity": prior_integrity_hash,
                "current_integrity": current_integrity_hash,
                "temporal_diff": temporal_hash,
            },
            generated_at=_generated_at(),
        )
        validate_yggdrasil_topology_delta_intelligence(artifact, DELTA_SCHEMA)
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, YggdrasilTopologyDeltaIntelligenceError) as exc:
        sys.stderr.write(f"FAIL_CLOSED: {exc}\n")
        return 1
    sys.stdout.write(
        "wrote out/projections/aal_viz_yggdrasil_topology_delta_intelligence_v1.latest.json "
        f"[{artifact['status']}]\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
