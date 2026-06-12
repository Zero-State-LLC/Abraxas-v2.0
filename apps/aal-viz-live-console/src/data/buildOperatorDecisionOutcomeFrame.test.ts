import { describe, expect, it } from 'vitest';
import { buildOperatorDecisionOutcomeFrame } from './buildOperatorDecisionOutcomeFrame';
import type { OperatorActionPacketsBundle } from '../types';

const LOCKED_PACKET_AUTHORITY = {
  execution_allowed: false as const,
  runtime_mutation_allowed: false as const,
  promotion_allowed: false as const,
  production_activation_allowed: false as const,
  metric_emission_allowed: false as const,
  forecast_influence_allowed: false as const,
  p43_lanes_allowed: false as const,
};

const SAMPLE_BUNDLE: OperatorActionPacketsBundle = {
  schema_version: 'AALViz.OperatorActionPackets.v0.1',
  generated_at: '2026-05-30T00:00:00Z',
  authority: LOCKED_PACKET_AUTHORITY,
  source_projection_bundle_hash: null,
  fail_closed_reason: null,
  packets: [
    {
      packet_id: 'test-pkt-002',
      source_frontier_ref: 'run-002',
      action_title: 'REVIEW PACKET',
      action_type: 'REVIEW_REQUIRED',
      operator_id: 'operator-shadow',
      subsystem_id: 'subsystem-002',
      recommended_next_step: 'ESCALATE_FOR_REVIEW',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false,
      runtime_mutation_allowed: false,
      promotion_allowed: false,
      prompt_body: 'Review this packet before any manual continuation.',
      validation_checklist: ['review evidence'],
      blocked_scopes: ['EXECUTION', 'MUTATION', 'PROMOTION'],
      provenance_refs: ['forecast-001', 'strategy-001', 'signal-001'],
      fail_closed_reason: null,
    },
    {
      packet_id: 'test-pkt-001',
      source_frontier_ref: null,
      action_title: 'WATCH PACKET',
      action_type: 'COPY_PROMPT',
      recommended_next_step: 'WATCH_FOR_OUTCOME',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false,
      runtime_mutation_allowed: false,
      promotion_allowed: false,
      prompt_body: 'Track this packet without changing forecasts.',
      validation_checklist: ['track only'],
      blocked_scopes: ['FORECAST_MUTATION', 'ROUTING_MUTATION'],
      provenance_refs: [],
      fail_closed_reason: null,
    },
  ],
};

describe('buildOperatorDecisionOutcomeFrame', () => {
  it('builds deterministic operator decision and outcome attribution frames', () => {
    const first = buildOperatorDecisionOutcomeFrame(SAMPLE_BUNDLE);
    const second = buildOperatorDecisionOutcomeFrame(SAMPLE_BUNDLE);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizOperatorDecisionOutcomeFrame.v1');
    expect(first.authority).toBe('DESCRIPTIVE_DECISION_LOGGING_AND_PROJECTION_ONLY');
    expect(first.mutation_policy).toBe('NO_EXECUTION_FORECAST_SCORE_AUTHORITY_OR_ROUTING_MUTATION');
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('sorts packets and maps copy/review actions into log-only decision types', () => {
    const frame = buildOperatorDecisionOutcomeFrame(SAMPLE_BUNDLE);

    expect(frame.decision_packets.map((packet) => packet.decision_id)).toEqual([
      'decision-test-pkt-001',
      'decision-test-pkt-002',
    ]);
    expect(frame.decision_packets.map((packet) => packet.decision_type)).toEqual(['WATCH', 'ESCALATE']);
    expect(frame.decision_packets.every((packet) => packet.authority === 'OPERATOR_LOG_ONLY')).toBe(true);
    expect(frame.decision_packets.every((packet) => packet.autonomous_execution_triggered === false)).toBe(true);
  });

  it('keeps missing outcomes pending and decision quality not-computable', () => {
    const frame = buildOperatorDecisionOutcomeFrame(SAMPLE_BUNDLE);

    expect(frame.outcome_attributions).toHaveLength(2);
    expect(frame.outcome_attributions.every((packet) => packet.outcome_id === null)).toBe(true);
    expect(frame.outcome_attributions.every((packet) => packet.attribution_status === 'PENDING')).toBe(true);
    expect(frame.outcome_attributions.every((packet) => packet.decision_effect === 'NOT_COMPUTABLE')).toBe(true);
    expect(frame.outcome_attributions.every((packet) => packet.decision_quality_score === null)).toBe(true);
  });

  it('links forecast, strategy, and signal refs without granting mutation authority', () => {
    const frame = buildOperatorDecisionOutcomeFrame(SAMPLE_BUNDLE);
    const reviewPacket = frame.decision_packets.find((packet) => packet.decision_type === 'ESCALATE');

    expect(reviewPacket?.linked_forecast_ids).toEqual(['forecast-001']);
    expect(reviewPacket?.linked_strategy_ids).toEqual(['strategy-001']);
    expect(reviewPacket?.linked_signal_ids).toEqual(['signal-001']);
    expect(reviewPacket?.source_forecast_probability_mutated).toBe(false);
    expect(reviewPacket?.source_score_mutated).toBe(false);
    expect(reviewPacket?.authority_tier_mutated).toBe(false);
    expect(reviewPacket?.strategy_routing_mutated).toBe(false);
  });

  it('locks decision logging out of writes, broadcasts, execution, score, forecast, routing, and authority mutation', () => {
    const frame = buildOperatorDecisionOutcomeFrame(SAMPLE_BUNDLE);

    expect(frame.decision_locks.display_only).toBe(true);
    expect(frame.decision_locks.descriptive_decision_logging_only).toBe(true);
    expect(frame.decision_locks.operator_log_only).toBe(true);
    expect(frame.decision_locks.notion_write_adapter_enabled).toBe(false);
    expect(frame.decision_locks.websocket_broadcast_enabled).toBe(false);
    expect(frame.decision_locks.autonomous_execution_allowed).toBe(false);
    expect(frame.decision_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.decision_locks.score_mutation_allowed).toBe(false);
    expect(frame.decision_locks.authority_tier_mutation_allowed).toBe(false);
    expect(frame.decision_locks.strategy_routing_mutation_allowed).toBe(false);
    expect(frame.decision_locks.execution_authority).toBe(false);
    expect(frame.decision_locks.truth_authority).toBe(false);
    expect(frame.decision_locks.decision_quality_score_promotes_or_demotes).toBe(false);
  });

  it('renders an empty fail-closed projection when no operator action bundle is loaded', () => {
    const frame = buildOperatorDecisionOutcomeFrame(null);

    expect(frame.decision_packets).toEqual([]);
    expect(frame.outcome_attributions).toEqual([]);
    expect(frame.decision_locks.notion_write_adapter_enabled).toBe(false);
    expect(frame.decision_locks.websocket_broadcast_enabled).toBe(false);
  });
});
