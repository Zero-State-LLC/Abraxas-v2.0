import { buildWorkflowOperatorAnalyticsFrame } from './buildWorkflowOperatorAnalyticsFrame';
import type {
  AnalyticsNarrativeFinding,
  AnalyticsNarrativePacket,
  AnalyticsNarrativeSeverityBand,
  AnalyticsNarrativeSummaryFrame,
  LiveConsoleProjectionBundle,
  NarrativeTemplateRule,
  OperatorActionPacketsBundle,
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

function confidenceFor(provenance: AnalyticsNarrativeFinding['provenance'], base: number): number {
  const cap = provenance === 'OBSERVED' ? 0.86 : provenance === 'INFERRED' ? 0.62 : 0;
  return Number(Math.min(base, cap).toFixed(2));
}

function severityFor(analytics: WorkflowOperatorAnalyticsFrame): AnalyticsNarrativeSeverityBand {
  const workflow = analytics.workflow_analytics;
  if (workflow.analytics_status === 'NOT_COMPUTABLE') return 'WARNING';
  if (workflow.blocked_count >= Math.max(3, Math.ceil(workflow.workflow_count * 0.4))) return 'WARNING';
  if (workflow.not_computable_count > 0) return 'WATCH';
  return 'INFO';
}

function templateRules(): NarrativeTemplateRule[] {
  const rules: NarrativeTemplateRule[] = [
    {
      template_id: 'template-workflow-bottleneck-observed',
      input_metric_type: 'WORKFLOW',
      trigger_condition: 'bottleneck_step != NONE and analytics_status == COMPUTED',
      output_block_type: 'FINDING',
      wording_rule: 'Name the bottleneck step and explain review flow pressure.',
      provenance_rule: 'OBSERVED',
      confidence_rule: 'min(0.86, workflow evidence class cap)',
    },
    {
      template_id: 'template-operator-feedback-gap',
      input_metric_type: 'OPERATOR',
      trigger_condition: 'decision quality fields are null',
      output_block_type: 'GAP',
      wording_rule: 'State that decision quality is not computable from missing outcomes.',
      provenance_rule: 'NOT_COMPUTABLE',
      confidence_rule: '0 when evidence is missing',
    },
    {
      template_id: 'template-review-prompt-selection',
      input_metric_type: 'REVIEW',
      trigger_condition: 'blocked_count > 0 or stale_review_rate > 0',
      output_block_type: 'REVIEW_PROMPT',
      wording_rule: 'Convert blocked or stale review analytics into operator review prompts.',
      provenance_rule: 'OBSERVED',
      confidence_rule: 'cap at source metric confidence',
    },
  ];
  return rules.sort((a, b) => a.template_id.localeCompare(b.template_id));
}

function findingsFor(analytics: WorkflowOperatorAnalyticsFrame): AnalyticsNarrativeFinding[] {
  const workflow = analytics.workflow_analytics;
  const operator = analytics.operator_performance[0] ?? null;
  const findings: AnalyticsNarrativeFinding[] = [
    {
      finding_id: 'finding-workflow-bottleneck',
      label: 'Workflow Bottleneck',
      claim:
        workflow.bottleneck_step === 'NOT_COMPUTABLE'
          ? 'Workflow bottleneck is not computable from the current analytics packet.'
          : `${workflow.bottleneck_step} is the current workflow pressure point.`,
      provenance: workflow.bottleneck_step === 'NOT_COMPUTABLE' ? 'NOT_COMPUTABLE' : 'OBSERVED',
      confidence: confidenceFor(workflow.bottleneck_step === 'NOT_COMPUTABLE' ? 'NOT_COMPUTABLE' : 'OBSERVED', 0.86),
      source_metric_ids: ['workflow_analytics.bottleneck_step', 'workflow_analytics.workflow_count'],
      why_it_matters: 'Bottleneck state tells operators where review attention is delayed without changing outcomes or scores.',
    },
    {
      finding_id: 'finding-review-aging',
      label: 'Review Aging',
      claim:
        workflow.stale_review_rate == null
          ? 'Review aging is not computable because stale review metrics are unavailable.'
          : `Stale or evidence-requested reviews represent ${Math.round(workflow.stale_review_rate * 100)}% of the current window.`,
      provenance: workflow.stale_review_rate == null ? 'NOT_COMPUTABLE' : 'OBSERVED',
      confidence: confidenceFor(workflow.stale_review_rate == null ? 'NOT_COMPUTABLE' : 'OBSERVED', 0.78),
      source_metric_ids: ['workflow_analytics.stale_review_rate'],
      why_it_matters: 'Aging review pressure should remain visible as a gap or prompt, not be smoothed over.',
    },
    {
      finding_id: 'finding-operator-feedback',
      label: 'Operator Feedback',
      claim:
        operator?.mean_decision_quality_score == null
          ? 'Operator decision quality remains not computable until outcome-linked evidence is present.'
          : `Operator decision quality is ${operator.mean_decision_quality_score.toFixed(2)} in this window.`,
      provenance: operator?.mean_decision_quality_score == null ? 'NOT_COMPUTABLE' : 'OBSERVED',
      confidence: confidenceFor(operator?.mean_decision_quality_score == null ? 'NOT_COMPUTABLE' : 'OBSERVED', 0.74),
      source_metric_ids: ['operator_performance.mean_decision_quality_score', 'operator_performance.pending_decision_rate'],
      why_it_matters: 'Operator summaries are descriptive feedback only and cannot rank operators or grant authority.',
    },
  ];

  return findings.sort((a, b) => a.finding_id.localeCompare(b.finding_id));
}

function notComputableItems(findings: AnalyticsNarrativeFinding[], analytics: WorkflowOperatorAnalyticsFrame): string[] {
  const gapLabels = findings
    .filter((finding) => finding.provenance === 'NOT_COMPUTABLE')
    .map((finding) => finding.label);
  if (analytics.workflow_analytics.mean_time_to_decision_ms == null) gapLabels.push('Decision Latency');
  return [...new Set(gapLabels)].sort((a, b) => a.localeCompare(b));
}

function reviewPrompts(analytics: WorkflowOperatorAnalyticsFrame): string[] {
  const prompts = [
    analytics.workflow_analytics.blocked_count > 0 ? 'review_blocked_workflows' : null,
    analytics.workflow_analytics.stale_review_rate != null && analytics.workflow_analytics.stale_review_rate > 0
      ? 'review_stale_or_evidence_requested_items'
      : null,
    analytics.operator_performance.some((operator) => operator.mean_decision_quality_score == null)
      ? 'inspect_missing_operator_outcome_evidence'
      : null,
  ].filter((prompt): prompt is string => prompt != null);

  return prompts.sort((a, b) => a.localeCompare(b));
}

function buildNarrativePacket(
  analytics: WorkflowOperatorAnalyticsFrame,
  generatedAt: string,
): AnalyticsNarrativePacket {
  const findings = findingsFor(analytics);
  const severity = severityFor(analytics);
  const gaps = notComputableItems(findings, analytics);
  const prompts = reviewPrompts(analytics);
  const headline =
    analytics.workflow_analytics.bottleneck_step === 'NOT_COMPUTABLE'
      ? 'Workflow narrative has missing analytics evidence'
      : `${analytics.workflow_analytics.bottleneck_step} is the current workflow story`;

  return {
    narrative_id: 'analytics-narrative-latest',
    window_start: analytics.workflow_analytics.window_start,
    window_end: analytics.workflow_analytics.window_end,
    source_packet_ids: [
      analytics.workflow_analytics.analytics_id,
      ...analytics.operator_performance.map((operator) => operator.performance_id),
    ].sort((a, b) => a.localeCompare(b)),
    narrative_type: 'WORKFLOW_SUMMARY',
    headline,
    summary: `${analytics.workflow_analytics.workflow_count} workflow items are compressed into ${findings.length} provenance-labeled findings with ${gaps.length} explicit gap(s).`,
    key_findings: findings,
    recommended_review_items: prompts,
    not_computable_items: gaps,
    severity_band: severity,
    generated_at: generatedAt,
    authority: 'NARRATIVE_COMPRESSION_ONLY',
    projection_only: true,
    creates_new_facts: false,
    recommendations_review_prompts_only: true,
    execution_allowed: false,
    outcome_resolution_allowed: false,
    forecast_mutation_allowed: false,
    promotion_allowed: false,
  };
}

export function buildAnalyticsNarrativeSummaryFrame(
  bundle: LiveConsoleProjectionBundle,
  packetsBundle: OperatorActionPacketsBundle | null,
): AnalyticsNarrativeSummaryFrame {
  const analyticsFrame = buildWorkflowOperatorAnalyticsFrame(bundle, packetsBundle);
  const narrativePacket = buildNarrativePacket(analyticsFrame, bundle.generated_at);

  const frameWithoutHash = {
    packet_type: 'AALVizAnalyticsNarrativeSummaryFrame.v1' as const,
    drop_name: 'AAL-Viz v7.9 — Analytics Narrative Summary Engine Code Drop' as const,
    authority: 'NARRATIVE_COMPRESSION_AND_PROJECTION_ONLY' as const,
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
      'v7.8',
    ] as AnalyticsNarrativeSummaryFrame['folded_versions'],
    features: [
      'analytics_narrative_packet',
      'metric_to_story_compiler',
      'deterministic_insight_templates',
      'provenance_labeled_findings',
      'narrative_gap_detection',
      'review_prompt_selection',
      'briefing_card_surface',
    ] as AnalyticsNarrativeSummaryFrame['features'],
    narrative_packet: narrativePacket,
    template_rules: templateRules(),
    generation_flow: [
      'analytics_packets',
      'metric_normalization',
      'template_rule_matching',
      'finding_generation',
      'provenance_labeling',
      'confidence_severity_assignment',
      'gap_detection',
      'narrative_packet_creation',
      'projection_only_briefing_surface',
    ] as AnalyticsNarrativeSummaryFrame['generation_flow'],
    narrative_locks: {
      display_only: true as const,
      narrative_compression_only: true as const,
      no_new_facts_created: true as const,
      every_finding_has_source_metric_ids: true as const,
      unsupported_claims_render_not_computable: true as const,
      inferred_claims_labeled_inferred: true as const,
      confidence_capped_by_evidence_class: true as const,
      recommendations_review_prompts_only: true as const,
      missing_metrics_render_as_gaps: true as const,
      operator_summaries_descriptive_only: true as const,
      notion_write_adapter_enabled: false as const,
      websocket_broadcast_enabled: false as const,
      autonomous_execution_allowed: false as const,
      outcome_resolution_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      score_mutation_allowed: false as const,
      provider_authority_mutation_allowed: false as const,
      strategy_routing_mutation_allowed: false as const,
      promotion_allowed: false as const,
      truth_authority: false as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
