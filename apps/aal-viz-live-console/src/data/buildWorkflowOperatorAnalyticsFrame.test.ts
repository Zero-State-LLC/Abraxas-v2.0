import { describe, expect, it } from 'vitest';
import { buildWorkflowOperatorAnalyticsFrame } from './buildWorkflowOperatorAnalyticsFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { OperatorActionPacketsBundle } from '../types';

const SAMPLE_PACKETS: OperatorActionPacketsBundle = {
  schema_version: 'AALViz.OperatorActionPackets.v0.1',
  generated_at: '2026-05-30T00:00:00Z',
  authority: {
    execution_allowed: false,
    runtime_mutation_allowed: false,
    promotion_allowed: false,
    production_activation_allowed: false,
    metric_emission_allowed: false,
    forecast_influence_allowed: false,
    p43_lanes_allowed: false,
  },
  source_projection_bundle_hash: null,
  fail_closed_reason: null,
  packets: [],
};

describe('buildWorkflowOperatorAnalyticsFrame', () => {
  it('builds a deterministic v7.8 workflow/operator analytics frame', () => {
    const frame = buildWorkflowOperatorAnalyticsFrame(sampleProjectionBundle, SAMPLE_PACKETS);
    const repeat = buildWorkflowOperatorAnalyticsFrame(sampleProjectionBundle, SAMPLE_PACKETS);

    expect(frame).toEqual(repeat);
    expect(frame.packet_type).toBe('AALVizWorkflowOperatorAnalyticsFrame.v1');
    expect(frame.drop_name).toBe('AAL-Viz v7.8 — Workflow Analytics + Operator Performance Tracking Code Drop');
    expect(frame.authority).toBe('DESCRIPTIVE_WORKFLOW_AND_OPERATOR_FEEDBACK_ONLY');
    expect(frame.folded_versions).toContain('v7.7');
    expect(frame.features).toContain('workflow_bottleneck_detection');
    expect(frame.features).toContain('operator_performance_tracking');
    expect(frame.provenance_hash).toMatch(/^[0-9a-f]{8}$/);
  });

  it('computes descriptive workflow analytics without mutation authority', () => {
    const frame = buildWorkflowOperatorAnalyticsFrame(sampleProjectionBundle, SAMPLE_PACKETS);
    const analytics = frame.workflow_analytics;

    expect(analytics.workflow_count).toBeGreaterThan(0);
    expect(analytics.analytics_status).toBe('COMPUTED');
    expect(analytics.bottleneck_step).not.toBe('NOT_COMPUTABLE');
    expect(analytics.projection_only).toBe(true);
    expect(analytics.descriptive_only).toBe(true);
    expect(analytics.promotion_authority).toBe(false);
    expect(analytics.routing_mutation_allowed).toBe(false);
  });

  it('keeps operator performance feedback-only and locks write/broadcast/authority paths', () => {
    const frame = buildWorkflowOperatorAnalyticsFrame(sampleProjectionBundle, SAMPLE_PACKETS);
    const operator = frame.operator_performance[0];

    expect(operator.feedback_only).toBe(true);
    expect(operator.rank_authority).toBe(false);
    expect(operator.truth_authority).toBe(false);
    expect(operator.pending_decision_rate).not.toBeNull();

    expect(frame.analytics_locks.display_only).toBe(true);
    expect(frame.analytics_locks.descriptive_analytics_only).toBe(true);
    expect(frame.analytics_locks.operator_feedback_only).toBe(true);
    expect(frame.analytics_locks.pending_decisions_not_scored_positive_or_negative).toBe(true);
    expect(frame.analytics_locks.notion_write_adapter_enabled).toBe(false);
    expect(frame.analytics_locks.websocket_broadcast_enabled).toBe(false);
    expect(frame.analytics_locks.autonomous_execution_allowed).toBe(false);
    expect(frame.analytics_locks.promotion_allowed).toBe(false);
    expect(frame.analytics_locks.outcome_mutation_allowed).toBe(false);
    expect(frame.analytics_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.analytics_locks.score_mutation_allowed).toBe(false);
    expect(frame.analytics_locks.provider_authority_mutation_allowed).toBe(false);
    expect(frame.analytics_locks.strategy_routing_mutation_allowed).toBe(false);
    expect(frame.analytics_locks.operator_rank_authority).toBe(false);
    expect(frame.analytics_locks.truth_authority).toBe(false);
  });
});
