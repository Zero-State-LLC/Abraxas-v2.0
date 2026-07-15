#!/usr/bin/env python3
"""Compare two explicit Operator Platform projections and publish Temporal Diff v1."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.aal_viz_temporal_diff import (  # noqa: E402
    PROJECTION_VERSION,
    TemporalDiffError,
    compare_operator_platform_projections,
    generation_id,
    not_computable_artifact,
    validate_projection,
)

OUTPUT_PATH = ROOT / "out/projections/aal_viz_temporal_diff_v1.latest.json"
PROJECTION_SCHEMA = (
    ROOT / "contracts/canon/aal_viz_operator_platform_projection.v0.2.schema.json"
)
TEMPORAL_SCHEMA = ROOT / "contracts/canon/aal_viz_temporal_diff.v1.schema.json"


def _repository_path(value: str) -> Path:
    candidate = PurePosixPath(value)
    if not value or candidate.is_absolute() or ".." in candidate.parts or "\\" in value:
        raise TemporalDiffError(f"input path must be repository-relative: {value}")
    return ROOT / candidate


def _load_projection(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    try:
        display_path = str(path.relative_to(ROOT))
    except ValueError:
        display_path = str(path)
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TemporalDiffError(f"malformed JSON input: {display_path}: {exc}") from exc
    if not isinstance(document, dict):
        raise TemporalDiffError(f"projection input must be an object: {display_path}")
    if document.get("schema_version") == "AALViz.LiveConsoleProjectionBundle.v0.2":
        platform = document.get("operator_platform")
        if not isinstance(platform, dict):
            raise TemporalDiffError(f"bundle lacks operator_platform: {display_path}")
        document = platform
    return document, hashlib.sha256(raw).hexdigest()


def _write(artifact: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _generation_descriptor(
    projection: dict[str, Any], source_path: str, source_sha256: str
) -> dict[str, Any]:
    validate_projection(projection, PROJECTION_SCHEMA)
    return {
        "generation_id": generation_id(projection),
        "source_path": source_path,
        "source_sha256": source_sha256,
        "projection_schema_version": PROJECTION_VERSION,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prior", required=True, help="Repository-relative prior projection"
    )
    parser.add_argument(
        "--current", required=True, help="Repository-relative current projection"
    )
    args = parser.parse_args(argv)
    try:
        prior_path = _repository_path(args.prior)
        current_path = _repository_path(args.current)
        missing = (
            "prior"
            if not prior_path.is_file()
            else "current"
            if not current_path.is_file()
            else None
        )
        if missing is not None:
            prior_descriptor = None
            current_descriptor = None
            if prior_path.is_file():
                prior, prior_sha = _load_projection(prior_path)
                prior_descriptor = _generation_descriptor(prior, args.prior, prior_sha)
            if current_path.is_file():
                current, current_sha = _load_projection(current_path)
                current_descriptor = _generation_descriptor(
                    current, args.current, current_sha
                )
            artifact = not_computable_artifact(
                prior_path=args.prior,
                current_path=args.current,
                missing_reason=missing,
                temporal_schema_path=TEMPORAL_SCHEMA,
                prior_generation=prior_descriptor,
                current_generation=current_descriptor,
            )
        else:
            prior, prior_sha = _load_projection(prior_path)
            current, current_sha = _load_projection(current_path)
            artifact = compare_operator_platform_projections(
                prior,
                current,
                prior_source_path=args.prior,
                current_source_path=args.current,
                prior_source_sha256=prior_sha,
                current_source_sha256=current_sha,
                projection_schema_path=PROJECTION_SCHEMA,
                temporal_schema_path=TEMPORAL_SCHEMA,
            )
        _write(artifact)
    except (OSError, TemporalDiffError) as exc:
        sys.stderr.write(f"FAIL_CLOSED: {exc}\n")
        return 1
    sys.stdout.write(
        "wrote out/projections/aal_viz_temporal_diff_v1.latest.json "
        f"[{artifact['status']}]\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
