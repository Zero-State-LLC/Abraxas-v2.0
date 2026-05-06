"""Pipeline orchestrator stub for ABRAXAS v2.0."""

from __future__ import annotations

from core.pipelines.models import PipelineContractV11


def describe_pipeline(contract: PipelineContractV11) -> str:
    """Return a human-readable description of a pipeline contract."""
    return (
        f"Pipeline '{contract.pipeline_id}' "
        f"(lane={contract.lane.value}, trigger='{contract.trigger}')"
    )
