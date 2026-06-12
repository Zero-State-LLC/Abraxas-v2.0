import { describe, expect, it } from 'vitest';
import { buildAnalyticsNarrativeSummaryFrame } from './buildAnalyticsNarrativeSummaryFrame';
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

describe('buildAnalyticsNarrativeSummaryFrame', () => {
  it('builds a deterministic v7.9 narrative summary frame', () => {
    const frame = buildAnalyticsNarrativeSummaryFrame(sampleProjectionBundle, SAMPLE_PACKETS);
    const repeat = buildAnalyticsNarrativeSummaryFrame(sampleProjectionBundle, SAMPLE_PACKETS);

    expect(frame).toEqual(repeat);
    expect(frame.packet_type).toBe('AALVizAnalyticsNarrativeSummaryFrame.v1');
    expect(frame.drop_name).toBe('AAL-Viz v7.9 — Analytics Narrative Summary Engine Code Drop');
    expect(frame.authority).toBe('NARRATIVE_COMPRESSION_AND_PROJECTION_ONLY');
    expect(frame.folded_versions).toContain('v7.8');
    expect(frame.features).toContain('analytics_narrative_packet');
    expect(frame.features).toContain('briefing_card_surface');
    expect(frame.provenance_hash).toMatch(/^[0-9a-f]{8}$/);
  });

  it('compresses analytics into sourced findings, gaps, and review prompts only', () => {
    const frame = buildAnalyticsNarrativeSummaryFrame(sampleProjectionBundle, SAMPLE_PACKETS);
    const packet = frame.narrative_packet;

    expect(packet.authority).toBe('NARRATIVE_COMPRESSION_ONLY');
    expect(packet.projection_only).toBe(true);
    expect(packet.creates_new_facts).toBe(false);
    expect(packet.recommendations_review_prompts_only).toBe(true);
    expect(packet.execution_allowed).toBe(false);
    expect(packet.outcome_resolution_allowed).toBe(false);
    expect(packet.forecast_mutation_allowed).toBe(false);
    expect(packet.promotion_allowed).toBe(false);
    expect(packet.key_findings.length).toBeGreaterThan(0);
    expect(packet.recommended_review_items.length).toBeGreaterThan(0);
    expect(packet.not_computable_items).toContain('Operator Feedback');

    for (const finding of packet.key_findings) {
      expect(finding.source_metric_ids.length).toBeGreaterThan(0);
      expect(finding.confidence).toBeGreaterThanOrEqual(0);
      expect(finding.confidence).toBeLessThanOrEqual(finding.provenance === 'OBSERVED' ? 0.86 : 0.62);
    }
  });

  it('keeps template rules and narrative locks fail-closed', () => {
    const frame = buildAnalyticsNarrativeSummaryFrame(sampleProjectionBundle, SAMPLE_PACKETS);

    expect(frame.template_rules.length).toBeGreaterThanOrEqual(3);
    expect(frame.generation_flow).toContain('gap_detection');
    expect(frame.generation_flow).toContain('projection_only_briefing_surface');
    expect(frame.narrative_locks.display_only).toBe(true);
    expect(frame.narrative_locks.narrative_compression_only).toBe(true);
    expect(frame.narrative_locks.no_new_facts_created).toBe(true);
    expect(frame.narrative_locks.every_finding_has_source_metric_ids).toBe(true);
    expect(frame.narrative_locks.unsupported_claims_render_not_computable).toBe(true);
    expect(frame.narrative_locks.recommendations_review_prompts_only).toBe(true);
    expect(frame.narrative_locks.notion_write_adapter_enabled).toBe(false);
    expect(frame.narrative_locks.websocket_broadcast_enabled).toBe(false);
    expect(frame.narrative_locks.autonomous_execution_allowed).toBe(false);
    expect(frame.narrative_locks.outcome_resolution_allowed).toBe(false);
    expect(frame.narrative_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.narrative_locks.score_mutation_allowed).toBe(false);
    expect(frame.narrative_locks.provider_authority_mutation_allowed).toBe(false);
    expect(frame.narrative_locks.strategy_routing_mutation_allowed).toBe(false);
    expect(frame.narrative_locks.promotion_allowed).toBe(false);
    expect(frame.narrative_locks.truth_authority).toBe(false);
  });
});
