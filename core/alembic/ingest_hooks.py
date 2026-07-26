"""Architecture-aware ingest metadata — extends existing ingest, no second pipeline."""

from __future__ import annotations

from typing import Any

from core.alembic.constants import ARCHITECTURE_FAMILIES
from core.alembic.models import TaskEnvelope
from core.alembic.util import make_id


def architecture_aware_intake_metadata(
    *,
    modality: str,
    source_class: str,
    task_class: str,
    uncertainty_requirements: float,
    potential_architecture_families: tuple[str, ...] | None = None,
    provenance_quality: str = "OBSERVED",
    temporal_relevance: str = "current",
    security_class: str = "standard",
    privacy_class: str = "internal",
) -> dict[str, Any]:
    families = potential_architecture_families or ()
    unknown = sorted(set(families) - set(ARCHITECTURE_FAMILIES))
    if unknown:
        raise ValueError(f"unknown architecture families: {unknown}")
    return {
        "schema_version": "AlembicArchitectureAwareIntake.v1",
        "intake_id": make_id("intake", modality, source_class, task_class),
        "modality": modality,
        "source_class": source_class,
        "task_class": task_class,
        "uncertainty_requirements": uncertainty_requirements,
        "potential_architecture_families": list(families),
        "provenance_quality": provenance_quality,
        "temporal_relevance": temporal_relevance,
        "security_class": security_class,
        "privacy_class": privacy_class,
        "integrates_with": "contracts/ingest + Oracle Signal Layer",
        "second_ingest_pipeline": False,
        "FINAL_STATUS": "ALEMBIC_SPINE_ADVISORY_ONLY",
    }


def task_envelope_from_intake(
    *,
    task_id: str,
    run_id: str,
    goal: str,
    intake: dict[str, Any],
    required_output_contract: str = "ArchitectureContribution.v1",
) -> TaskEnvelope:
    return TaskEnvelope(
        task_id=task_id,
        run_id=run_id,
        goal=goal,
        task_type=str(intake.get("task_class", "advisory_analysis")),
        input_modalities=(str(intake.get("modality", "structured_json")),),
        required_output_contract=required_output_contract,
        uncertainty_tolerance=float(intake.get("uncertainty_requirements", 1.0)),
        privacy_class=str(intake.get("privacy_class", "internal")),
        security_class=str(intake.get("security_class", "standard")),
        allowed_architecture_families=tuple(intake.get("potential_architecture_families", ())),
        governance_context={"intake_id": intake.get("intake_id")},
    )
