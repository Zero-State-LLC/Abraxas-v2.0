from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator

from core.canonical.json import canonical_hash
from core.governance.authority import Authority


class MetricPoint(BaseModel):
    timestamp_index: int
    metric_name: str
    metric_value: float


class DeterministicMetricSeries(BaseModel):
    schema_version: Literal["DeterministicMetricSeries.v1"] = "DeterministicMetricSeries.v1"
    series_id: str
    metric_family: str
    points: list[MetricPoint]
    deterministic_series_hash: str
    authority: Authority
    status: Literal["valid", "failed"]

    @field_validator("points")
    @classmethod
    def _mono(cls, v: list[MetricPoint]) -> list[MetricPoint]:
        idx = [p.timestamp_index for p in v]
        if idx != sorted(idx):
            raise ValueError("timestamp_index must be monotonic")
        return v


def build_metric_series(metric_family: str, points: list[MetricPoint]) -> DeterministicMetricSeries:
    d_hash = canonical_hash([p.model_dump(mode="json") for p in points])
    sid = canonical_hash({"family": metric_family, "hash": d_hash})
    return DeterministicMetricSeries(series_id=sid, metric_family=metric_family, points=points, deterministic_series_hash=d_hash, authority=Authority(), status="valid")
