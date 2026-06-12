import { buildReviewSuggestionMatrixFrame } from './buildReviewSuggestionMatrixFrame';
import type {
  LiveConsoleProjectionBundle,
  OperatorActionPacketsBundle,
  OperatorDecisionProvenance,
  OperatorWorkflowActionPacket,
  OperatorWorkflowActionType,
  OperatorWorkflowActiveStep,
  OperatorWorkflowCommandCenterFrame,
  OperatorWorkflowStatePacket,
  OperatorWorkflowStatus,
  ReviewSuggestionPacket,
} from '../types';

function stableStringify(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(',')}]`;
  }
  if (value !== null && typeof value === 'object') {
    return `{${Object.entries(value)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, item]) => `${JSON.stringify(key)}:${stableStringify(item)}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}

function stableUiHash(value: unknown): string {
  const input = stableStringify(value);
  let hash = 0x811c9dc5;
  for (let index = 0; index < input.length; index++) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return (hash >>> 0).toString(16).padStart(8, '0');
}

function statusFor(suggestion: ReviewSuggestionPacket): OperatorWorkflowStatus {
  if (suggestion.suggestion_type === 'MARK_NOT_COMPUTABLE') return 'NOT_COMPUTABLE';
  if (suggestion.suggestion_type === 'REQUEST_SECOND_SOURCE') return 'EVIDENCE_REQUESTED';
  if (suggestion.suggestion_type === 'APPLY_CORRECTION_REVIEW') return 'READY_FOR_DECISION';
  if (suggestion.suggestion_type === 'ESCALATE_CONFLICT') return 'TRIAGED';
  if (suggestion.suggestion_type === 'REVIEW_NOW') return 'NEW';
  if (suggestion.suggestion_type === 'DISMISS_LOW_PRIORITY') return 'DISMISSED';
  return 'BLOCKED';
}

function activeStepFor(status: OperatorWorkflowStatus, suggestion: ReviewSuggestionPacket): OperatorWorkflowActiveStep {
  if (status === 'EVIDENCE_REQUESTED') return 'EVIDENCE';
  if (status === 'READY_FOR_DECISION') {
    return suggestion.suggestion_type === 'APPLY_CORRECTION_REVIEW' ? 'CORRECT' : 'DECIDE';
  }
  if (status === 'DECISION_DRAFTED') return 'COMMIT';
  if (status === 'COMMITTED' || status === 'DISMISSED') return 'ARCHIVE';
  if (status === 'TRIAGED') return 'COMPARE';
  return 'TRIAGE';
}

function completedEvidenceFor(suggestion: ReviewSuggestionPacket): string[] {
  if (suggestion.provenance !== 'complete') return [];
  return suggestion.required_evidence.slice(0, 1);
}

function buildWorkflowState(suggestion: ReviewSuggestionPacket): OperatorWorkflowStatePacket {
  const status = statusFor(suggestion);

  return {
    workflow_id: `workflow-${suggestion.review_id}`,
    review_id: suggestion.review_id,
    target_type: suggestion.target_type,
    target_id: suggestion.target_id,
    status,
    active_step: activeStepFor(status, suggestion),
    assigned_operator_id: null,
    priority_score: suggestion.priority_score,
    urgency_band: suggestion.urgency_band,
    blockers: suggestion.blocked_by,
    required_evidence: suggestion.required_evidence,
    completed_evidence: completedEvidenceFor(suggestion),
    last_updated_at: suggestion.created_at,
    provenance: suggestion.provenance,
    projection_only: true,
    review_state_management_only: true,
    commit_authority: false,
    outcome_mutation_allowed: false,
    forecast_mutation_allowed: false,
    score_mutation_allowed: false,
    routing_mutation_allowed: false,
  };
}

function actionTypeFor(workflow: OperatorWorkflowStatePacket): OperatorWorkflowActionType {
  if (workflow.status === 'EVIDENCE_REQUESTED') return 'REQUEST_EVIDENCE';
  if (workflow.status === 'READY_FOR_DECISION') return workflow.active_step === 'CORRECT' ? 'DRAFT_CORRECTION' : 'DRAFT_DECISION';
  if (workflow.status === 'TRIAGED') return 'TRIAGE';
  if (workflow.status === 'ARCHIVED') return 'ANNOTATE';
  if (workflow.status === 'BLOCKED') return 'BLOCK';
  if (workflow.status === 'DISMISSED') return 'DISMISS';
  if (workflow.status === 'NOT_COMPUTABLE') return 'ANNOTATE';
  return 'OPEN';
}

function rationaleFor(workflow: OperatorWorkflowStatePacket): string {
  if (workflow.status === 'EVIDENCE_REQUESTED') return 'Required evidence is incomplete; keep workflow in evidence collection.';
  if (workflow.status === 'READY_FOR_DECISION') return 'Evidence is sufficient for a drafted review packet, not for truth mutation.';
  if (workflow.status === 'TRIAGED') return 'Provider or source conflict requires comparison before decision drafting.';
  if (workflow.status === 'NOT_COMPUTABLE') return 'Missing evidence must stay explicit and fail-closed.';
  return 'Workflow item is visible for operator review only.';
}

function buildAction(workflow: OperatorWorkflowStatePacket, createdAt: string): OperatorWorkflowActionPacket {
  const payloadHash = stableUiHash({
    workflow_id: workflow.workflow_id,
    status: workflow.status,
    active_step: workflow.active_step,
    required_evidence: workflow.required_evidence,
    completed_evidence: workflow.completed_evidence,
  });

  return {
    action_id: `workflow-action-${workflow.workflow_id}`,
    workflow_id: workflow.workflow_id,
    operator_id: 'operator-unassigned',
    action_type: actionTypeFor(workflow),
    created_at: createdAt,
    payload_hash: payloadHash,
    rationale: rationaleFor(workflow),
    authority: 'OPERATOR_WORKFLOW_LOG_ONLY',
    provenance: workflow.provenance as OperatorDecisionProvenance,
    append_only: true,
    external_execution_allowed: false,
    notion_write_allowed: false,
  };
}

export function buildOperatorWorkflowCommandCenterFrame(
  bundle: LiveConsoleProjectionBundle,
  packetsBundle: OperatorActionPacketsBundle | null,
): OperatorWorkflowCommandCenterFrame {
  const suggestionFrame = buildReviewSuggestionMatrixFrame(bundle, packetsBundle);
  const workflows = suggestionFrame.suggestions
    .map(buildWorkflowState)
    .sort((a, b) => b.priority_score - a.priority_score || a.workflow_id.localeCompare(b.workflow_id));
  const actions = workflows.map((workflow) => buildAction(workflow, bundle.generated_at));

  const statusTransitions: OperatorWorkflowCommandCenterFrame['status_transitions'] = {
    NEW: ['TRIAGED', 'DISMISSED', 'BLOCKED'],
    TRIAGED: ['EVIDENCE_REQUESTED', 'READY_FOR_DECISION', 'DISMISSED', 'BLOCKED'],
    EVIDENCE_REQUESTED: ['READY_FOR_DECISION', 'BLOCKED', 'NOT_COMPUTABLE'],
    READY_FOR_DECISION: ['DECISION_DRAFTED', 'DISMISSED', 'BLOCKED'],
    DECISION_DRAFTED: ['COMMITTED', 'READY_FOR_DECISION', 'BLOCKED'],
    COMMITTED: ['ARCHIVED'],
    ARCHIVED: [],
    DISMISSED: ['ARCHIVED'],
    BLOCKED: ['TRIAGED', 'EVIDENCE_REQUESTED', 'NOT_COMPUTABLE'],
    NOT_COMPUTABLE: [],
  };

  const frameWithoutHash = {
    packet_type: 'AALVizOperatorWorkflowCommandCenterFrame.v1' as const,
    drop_name: 'AAL-Viz v7.7 — Operator Workflow UI Code Drop' as const,
    authority: 'WORKFLOW_GUIDANCE_REVIEW_STATE_AND_PROJECTION_ONLY' as const,
    mutation_policy: 'NO_EXECUTION_OUTCOME_FORECAST_SCORE_PROVIDER_AUTHORITY_OR_ROUTING_MUTATION' as const,
    projection_only: true as const,
    folded_versions: [
      'v6.1',
      'v6.2',
      'v6.3',
      'v6.4',
      'v6.5',
      'v6.6',
      'v6.7',
      'v6.8',
      'v6.9',
      'v7.0',
      'v7.1',
      'v7.2',
      'v7.3',
      'v7.4',
      'v7.5',
      'v7.6',
    ] as OperatorWorkflowCommandCenterFrame['folded_versions'],
    features: [
      'workflow_inbox',
      'workflow_state_machine',
      'evidence_checklist',
      'provider_side_panel',
      'decision_composer',
      'correction_composer',
      'audit_preview',
      'workflow_timeline',
      'keyboard_command_bar',
      'notion_context_panel',
    ] as OperatorWorkflowCommandCenterFrame['features'],
    workflows,
    actions,
    status_transitions: statusTransitions,
    ui_zones: {
      left_rail: 'queue filters, urgency bands, status groups',
      center_panel: 'active review detail, evidence, decision/correction composer',
      right_panel: 'provider comparison, Notion links, lineage context',
      bottom_timeline: 'actions, status transitions, audit trail',
      command_bar: 'keyboard shortcuts, commit preview, safe actions',
      field_overlay: 'highlight selected review target in AAL-Viz field',
    },
    workflow_locks: {
      display_only: true as const,
      workflow_guidance_only: true as const,
      review_state_management_only: true as const,
      append_only_actions: true as const,
      audit_preview_required_before_commit: true as const,
      evidence_completion_is_not_truth_validation: true as const,
      notion_deep_links_context_only: true as const,
      accessibility_static_review_mode: true as const,
      notion_write_adapter_enabled: false as const,
      websocket_live_updates_enabled: false as const,
      autonomous_execution_allowed: false as const,
      external_action_execution_allowed: false as const,
      outcome_mutation_allowed: false as const,
      correction_application_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      score_mutation_allowed: false as const,
      provider_authority_mutation_allowed: false as const,
      strategy_routing_mutation_allowed: false as const,
      truth_authority: false as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
