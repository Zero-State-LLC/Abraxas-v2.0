from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalClimateVizInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class TemporalClimateVizPanel:
    panel_id: str
    panel_type: str
    panel_title: str
    panel_posture: str
    source_ref_ids: tuple[str, ...]
    projection_only: bool
    inference_authority_allowed: bool


@dataclass(frozen=True)
class TemporalClimateVizWidget:
    widget_id: str
    widget_type: str
    widget_label: str
    widget_value: str
    widget_posture: str
    source_ref_ids: tuple[str, ...]
    projection_only: bool
    action_authorization_allowed: bool


@dataclass(frozen=True)
class TemporalClimateVizBadge:
    badge_id: str
    badge_type: str
    badge_label: str
    badge_posture: str
    required: bool


@dataclass(frozen=True)
class TemporalClimateVizAlertSurface:
    alert_surface_id: str
    alert_type: str
    severity: str
    display_priority: int
    source_ref_ids: tuple[str, ...]
    operator_review_required: bool
    action_authorization_allowed: bool


@dataclass(frozen=True)
class TemporalClimateVizInteractionHint:
    hint_id: str
    hint_type: str
    description: str
    operator_review_required: bool
    action_authorization_allowed: bool
    live_execution_allowed: bool
    routing_change_allowed: bool


@dataclass(frozen=True)
class TemporalClimateAALVizProjectionBinding:
    schema_version: str
    binding_id: str
    input_refs: tuple[TemporalClimateVizInputRef, ...]
    panels: tuple[TemporalClimateVizPanel, ...]
    widgets: tuple[TemporalClimateVizWidget, ...]
    badges: tuple[TemporalClimateVizBadge, ...]
    alert_surfaces: tuple[TemporalClimateVizAlertSurface, ...]
    interaction_hints: tuple[TemporalClimateVizInteractionHint, ...]
    binding_status: str
    binding_posture: str
    binding_policy: str
    created_by_lane: str
    authority_ref: dict | None
    projection_only: bool
    binding_authoritative: bool
    inference_authority_allowed: bool
    action_authorization_allowed: bool
    auto_transition_allowed: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    live_execution_allowed: bool
    routing_change_allowed: bool
    binding_hash: str


@dataclass(frozen=True)
class TemporalClimateVizValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class TemporalClimateVizValidationReport:
    status: str
    findings: tuple[TemporalClimateVizValidationFinding, ...]
    receipt_hash: str
