"""Representation-driven instantiation composition contracts."""

from .artifact_resolver import (
    ArtifactResolutionError,
    ResolvedArtifactRef,
    resolve_artifact_refs,
    resolve_intervention_ref,
    resolve_transition_intervention_ref,
)
from .contracts import (
    CAUSAL_EXPOSURES,
    DIMENSIONS,
    build_instantiation_state,
    build_instantiation_transition,
    build_intervention_declaration,
    canonical_intervention_json,
    canonical_state_json,
    canonical_transition_json,
    validate_instantiation_state,
    validate_instantiation_transition,
    validate_intervention_declaration,
)
from .harness import (
    run_fixture_experiment,
    validate_experiment_record,
)
from .projection import (
    build_instantiation_projection,
    validate_instantiation_projection,
)
from .shadow import (
    detect_instantiation_anomalies,
    validate_instantiation_shadow_report,
)

__all__ = [
    "CAUSAL_EXPOSURES",
    "DIMENSIONS",
    "ArtifactResolutionError",
    "ResolvedArtifactRef",
    "build_instantiation_projection",
    "build_instantiation_state",
    "build_instantiation_transition",
    "build_intervention_declaration",
    "canonical_intervention_json",
    "canonical_state_json",
    "canonical_transition_json",
    "detect_instantiation_anomalies",
    "resolve_artifact_refs",
    "resolve_intervention_ref",
    "resolve_transition_intervention_ref",
    "run_fixture_experiment",
    "validate_experiment_record",
    "validate_instantiation_projection",
    "validate_instantiation_shadow_report",
    "validate_instantiation_state",
    "validate_instantiation_transition",
    "validate_intervention_declaration",
]
