"""Bridge Oracle Signal intake → Alembic architecture-aware metadata.

Does not mutate Oracle intake receipts, queues, or create a second ingest pipeline.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.alembic.ingest_hooks import (
    architecture_aware_intake_metadata,
    task_envelope_from_intake,
)
from core.alembic.models import TaskEnvelope
from core.alembic.util import make_id


def architecture_aware_intake_from_oracle_candidate(
    candidate: Mapping[str, Any],
    *,
    default_modality: str = "structured_json",
    default_task_class: str = "advisory_analysis",
    uncertainty_requirements: float = 1.0,
    potential_architecture_families: tuple[str, ...] = (
        "symbolic_expert",
        "statistical_ml",
        "deterministic_tool",
    ),
) -> dict[str, Any]:
    """Derive Alembic intake metadata from an Oracle candidate signal packet."""
    source_ref = candidate.get("source_ref", {})
    source_class = str(
        candidate.get("adapter_id")
        or source_ref.get("source_uri")
        or "oracle_candidate"
    )
    domain = str(candidate.get("domain") or "oracle_signal")
    intake = architecture_aware_intake_metadata(
        modality=default_modality,
        source_class=source_class,
        task_class=default_task_class,
        uncertainty_requirements=uncertainty_requirements,
        potential_architecture_families=potential_architecture_families,
        provenance_quality="OBSERVED"
        if candidate.get("signal_status") == "CANDIDATE_SHADOW_ONLY"
        else "INFERRED",
        temporal_relevance="current",
        security_class="standard",
        privacy_class="internal",
    )
    intake["oracle_signal_id"] = candidate.get("signal_id")
    intake["oracle_signal_hash"] = candidate.get("signal_hash")
    intake["oracle_domain"] = domain
    intake["second_ingest_pipeline"] = False
    intake["mutates_oracle_receipt"] = False
    return intake


def task_envelope_from_oracle_candidate(
    candidate: Mapping[str, Any],
    *,
    run_id: str,
    goal: str | None = None,
) -> TaskEnvelope:
    intake = architecture_aware_intake_from_oracle_candidate(candidate)
    signal_id = str(candidate.get("signal_id") or make_id("oracle", run_id))
    return task_envelope_from_intake(
        task_id=f"alembic-from-oracle:{signal_id[:16]}",
        run_id=run_id,
        goal=goal
        or f"Advisory architecture routing for oracle candidate {signal_id[:16]}",
        intake=intake,
    )


def architecture_aware_intakes_from_oracle_receipt(
    receipt: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    """Read-only projection from an Oracle intake receipt to Alembic intake rows."""
    candidates = receipt.get("candidate_signals", [])
    if not isinstance(candidates, list):
        return ()
    return tuple(
        architecture_aware_intake_from_oracle_candidate(candidate)
        for candidate in candidates
        if isinstance(candidate, Mapping)
    )
