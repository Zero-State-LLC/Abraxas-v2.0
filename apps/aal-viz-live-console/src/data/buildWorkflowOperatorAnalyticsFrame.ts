import { buildOperatorWorkflowCommandCenterFrame } from './buildOperatorWorkflowCommandCenterFrame';
import type {
  LiveConsoleProjectionBundle,
  OperatorActionPacketsBundle,
  OperatorPerformancePacket,
  OperatorWorkflowActiveStep,
  OperatorWorkflowStatePacket,
  WorkflowAnalyticsPacket,
  WorkflowBottleneckStep,
  WorkflowOperatorAnalyticsFrame,
} from '../types';

function stableStringify(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map((item) => stableStringify(item)).join(',')}]`;
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

function round(value: number): number {
  return Number(value.toFixed(4));
}

function rate(numerator: number, denominator: number): number | null {
  if (denominator === 0) return null;
  return round(numerator / denominator);
}

function bottleneckStep(workflows: OperatorWorkflowStatePacket[]): WorkflowBottleneckStep {
  if (workflows.length === 0) return 'NOT_COMPUTABLE';
  const counts = workflows.reduce<Record<OperatorWorkflowActiveStep, number>>(
    (acc, workflow) => ({ ...acc, [workflow.active_step]: acc[workflow.active_step] + 1 }),
    { TRIAGE: 0, EVIDENCE: 0, COMPARE: 0, DECIDE: 0, CORRECT: 0, COMMIT: 0, ARCHIVE: 0 },
  );
  const [step, count] = Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0];
  return count === 0 ? 'NONE' : (step as OperatorWorkflowActiveStep);
}

function buildWorkflowAnalytics(workflows: OperatorWorkflowStatePacket[], computedAt: string): WorkflowAnalyticsPacket {
  const completedCount = workflows.filter((workflow) => workflow.status === 'COMMITTED' || workflow.status === 'ARCHIVED').length;
  const blockedCount = workflows.filter((workflow) => workflow.status === 'BLOCKED').length;
  const dismissedCount = workflows.filter((workflow) => workflow.status === 'DISMISSED').length;
  const notComputableCount = workflows.filter((workflow) => workflow.status === 'NOT_COMPUTABLE').length;
  const evidenceRequestedCount = workflows.filter((workflow) => workflow.status === 'EVIDENCE_REQUESTED').length;
  const correctionCount = workflows.filter((workflow) => workflow.active_step === 'CORRECT').length;
  const staleCount = workflows.filter((workflow) => workflow.required_evidence.includes('outcome_feed_evidence')).length;
  const analyticsStatus =
    workflows.length === 0 ? 'NOT_COMPUTABLE' : workflows.length < 3 ? 'UNDER_SAMPLED' : 'COMPUTED';

  return {
    analytics_id: 'workflow-analytics-latest',
    window_start: computedAt,
    window_end: computedAt,
    workflow_count: workflows.length,
    completed_count: completedCount,
    blocked_count: blockedCount,
    dismissed_count: dismissedCount,
    not_computable_count: notComputableCount,
    mean_time_to_triage_ms: workflows.length === 0 ? null : 0,
    mean_time_to_decision_ms: completedCount === 0 ? null : 0,
    mean_time_to_commit_ms: completedCount === 0 ? null : 0,
    bottleneck_step: bottleneckStep(workflows),
    suggestion_acceptance_rate: rate(completedCount + dismissedCount, workflows.length),
    correction_rate: rate(correctionCount, workflows.length),
    stale_review_rate: rate(staleCount + evidenceRequestedCount, workflows.length),
    analytics_status: analyticsStatus,
    computed_at: computedAt,
    projection_only: true,
    descriptive_only: true,
    promotion_authority: false,
    routing_mutation_allowed: false,
  };
}

function buildOperatorPerformance(workflows: OperatorWorkflowStatePacket[], computedAt: string): OperatorPerformancePacket[] {
  const reviewedCount = workflows.filter((workflow) => workflow.completed_evidence.length > 0).length;
  const correctionCount = workflows.filter((workflow) => workflow.active_step === 'CORRECT').length;
  const pendingCount = workflows.filter((workflow) => workflow.status !== 'COMMITTED' && workflow.status !== 'ARCHIVED').length;
  const totalEvidence = workflows.reduce((sum, workflow) => sum + workflow.required_evidence.length, 0);
  const completedEvidence = workflows.reduce((sum, workflow) => sum + workflow.completed_evidence.length, 0);
  const performanceStatus =
    workflows.length === 0 ? 'NOT_COMPUTABLE' : workflows.length < 3 ? 'UNDER_SAMPLED' : 'COMPUTED';

  return [
    {
      performance_id: 'operator-performance-unassigned-latest',
      operator_id: 'operator-unassigned',
      window_start: computedAt,
      window_end: computedAt,
      decision_count: 0,
      reviewed_count: reviewedCount,
      override_count: 0,
      correction_count: correctionCount,
      mean_decision_quality_score: null,
      positive_decision_rate: null,
      negative_decision_rate: null,
      neutral_decision_rate: workflows.length === 0 ? null : 0,
      pending_decision_rate: rate(pendingCount, workflows.length),
      evidence_completion_rate: rate(completedEvidence, totalEvidence),
      mean_review_latency_ms: null,
      operator_calibration_error: null,
      performance_status: performanceStatus,
      computed_at: computedAt,
      feedback_only: true,
      rank_authority: false,
      truth_authority: false,
    },
  ];
}

export function buildWorkflowOperatorAnalyticsFrame(
  bundle: LiveConsoleProjectionBundle,
  packetsBundle: OperatorActionPacketsBundle | null,
): WorkflowOperatorAnalyticsFrame {
  const workflowFrame = buildOperatorWorkflowCommandCenterFrame(bundle, packetsBundle);
  const workflowAnalytics = buildWorkflowAnalytics(workflowFrame.workflows, bundle.generated_at);
  const operatorPerformance = buildOperatorPerformance(workflowFrame.workflows, bundle.generated_at);

  const frameWithoutHash = {
    packet_type: 'AALVizWorkflowOperatorAnalyticsFrame.v1' as const,
    drop_name: 'AAL-Viz v7.8 — Workflow Analytics + Operator Performance Tracking Code Drop' as const,
    authority: 'DESCRIPTIVE_WORKFLOW_AND_OPERATOR_FEEDBACK_ONLY' as const,
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
      'v7.7',
    ] as WorkflowOperatorAnalyticsFrame['folded_versions'],
    features: [
      'workflow_analytics',
      'workflow_bottleneck_detection',
      'review_aging',
      'suggestion_effectiveness',
      'operator_performance_tracking',
      'operator_calibration_profile',
      'override_outcome_tracking',
      'correction_quality_tracking',
    ] as WorkflowOperatorAnalyticsFrame['features'],
    workflow_analytics: workflowAnalytics,
    operator_performance: operatorPerformance,
    visual_mapping: {
      workflow_bottleneck: 'congested step glows amber with queue pressure',
      stale_review_growth: 'slow red-orange accumulation on workflow rail',
      high_suggestion_acceptance: 'suggestion layer stabilizes and brightens',
      low_suggestion_acceptance: 'suggestion layer dims with review flag',
      positive_operator_trend: 'operator trail sharpens and stabilizes',
      negative_operator_trend: 'operator trail frays with correction prompts',
      under_sampled_operator: 'muted profile, UNDER_SAMPLED badge',
      not_computable_operator: 'gray profile marker, missing-outcome state',
    },
    analytics_locks: {
      display_only: true as const,
      descriptive_analytics_only: true as const,
      operator_feedback_only: true as const,
      windowed_and_timestamped: true as const,
      pending_decisions_not_scored_positive_or_negative: true as const,
      low_sample_size_renders_under_sampled: true as const,
      missing_outcomes_render_not_computable: true as const,
      prior_and_corrected_hashes_preserved: true as const,
      notion_write_adapter_enabled: false as const,
      websocket_broadcast_enabled: false as const,
      autonomous_execution_allowed: false as const,
      promotion_allowed: false as const,
      outcome_mutation_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      score_mutation_allowed: false as const,
      provider_authority_mutation_allowed: false as const,
      strategy_routing_mutation_allowed: false as const,
      operator_rank_authority: false as const,
      truth_authority: false as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
