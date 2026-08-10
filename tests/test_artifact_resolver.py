"""Tests for deterministic, fail-closed RDI artifact resolution."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from core.forecasting.forecast_object import build_forecast_object
from core.instantiation.artifact_resolver import (
    ArtifactResolutionError,
    resolve_artifact_refs,
)


def _forecast(forecast_id: str) -> dict[str, object]:
    forecast = build_forecast_object(
        forecast_id,
        "fixture event occurs",
        0.5,
        "rdi_fixture",
        "fixture-t1",
        "SHADOW",
        "DRAFT",
        None,
    )
    return asdict(forecast)


def _write(root: Path, kind: str, payload: dict[str, object]) -> None:
    directory = {
        "forecast": "forecast",
        "settlement": "settlement",
        "transition": "instantiation",
        "intervention": "intervention",
    }[kind]
    object_id = next(value for key, value in payload.items() if key.endswith("_id"))
    target = root / "out" / directory / f"{object_id}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload), encoding="utf-8")


def _ref(kind: str, payload: dict[str, object]) -> dict[str, object]:
    id_key = next(key for key in payload if key.endswith("_id"))
    hash_key = next(key for key in payload if key.endswith("_hash"))
    return {
        "kind": kind,
        "object_id": payload[id_key],
        "schema_version": payload["schema_version"],
        "canonical_hash": payload[hash_key],
    }


def test_happy_path_and_deterministic_order(tmp_path: Path) -> None:
    first = _forecast("forecast-b")
    second = _forecast("forecast-a")
    _write(tmp_path, "forecast", first)
    _write(tmp_path, "forecast", second)
    refs = [_ref("forecast", first), _ref("forecast", second)]

    result = resolve_artifact_refs(refs, tmp_path)
    shuffled = resolve_artifact_refs(list(reversed(refs)), tmp_path)

    assert [item.object_id for item in result] == ["forecast-a", "forecast-b"]
    assert result == shuffled
    assert result[0].path == "out/forecast/forecast-a.json"


@pytest.mark.parametrize(
    ("code", "refs"),
    [
        ("MISSING_ARTIFACT", [_ref("forecast", _forecast("missing"))]),
        (
            "DUPLICATE_REF",
            lambda: [_ref("forecast", _forecast("same"))] * 2,
        ),
        (
            "PATH_ESCAPE",
            [{"kind": "forecast", "object_id": "../escape", "schema_version": "ForecastObject.v1", "canonical_hash": "a" * 64}],
        ),
    ],
)
def test_fail_closed_reference_errors(
    tmp_path: Path, code: str, refs: object
) -> None:
    actual_refs = refs() if callable(refs) else refs
    with pytest.raises(ArtifactResolutionError, match=code):
        resolve_artifact_refs(actual_refs, tmp_path)  # type: ignore[arg-type]


def test_malformed_json_schema_and_hash_errors(tmp_path: Path) -> None:
    payload = _forecast("bad")
    _write(tmp_path, "forecast", payload)
    path = tmp_path / "out/forecast/bad.json"

    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ArtifactResolutionError, match="MALFORMED_JSON"):
        resolve_artifact_refs([_ref("forecast", payload)], tmp_path)

    _write(tmp_path, "forecast", payload)
    bad_schema = dict(payload, schema_version="SettlementVerdict.v1")
    path.write_text(json.dumps(bad_schema), encoding="utf-8")
    with pytest.raises(ArtifactResolutionError, match="SCHEMA_MISMATCH"):
        resolve_artifact_refs([_ref("forecast", payload)], tmp_path)

    _write(tmp_path, "forecast", payload)
    bad_hash = dict(payload, forecast_hash="0" * 64)
    path.write_text(json.dumps(bad_hash), encoding="utf-8")
    with pytest.raises(ArtifactResolutionError, match="HASH_MISMATCH"):
        resolve_artifact_refs([_ref("forecast", payload)], tmp_path)


def test_ref_schema_mismatch_is_rejected(tmp_path: Path) -> None:
    payload = _forecast("ref-schema")
    _write(tmp_path, "forecast", payload)
    ref = _ref("forecast", payload)
    ref["schema_version"] = "SettlementVerdict.v1"
    with pytest.raises(ArtifactResolutionError, match="SCHEMA_MISMATCH"):
        resolve_artifact_refs([ref], tmp_path)
