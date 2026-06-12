import { describe, expect, it } from 'vitest';
import { buildStrategyAttributionDriftFrame } from './buildStrategyAttributionDriftFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { LiveConsoleProjectionBundle } from '../types';

describe('buildStrategyAttributionDriftFrame', () => {
  it('builds deterministic descriptive attribution and drift frames', () => {
    const first = buildStrategyAttributionDriftFrame(sampleProjectionBundle);
    const second = buildStrategyAttributionDriftFrame(sampleProjectionBundle);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizStrategyAttributionDriftFrame.v1');
    expect(first.authority).toBe('DESCRIPTIVE_ATTRIBUTION_AND_PROJECTION_ONLY');
    expect(first.mutation_policy).toBe('NO_FORECAST_SCORE_AUTHORITY_OR_ROUTING_MUTATION');
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('keeps missing lineage or outcome data not-computable with explicit baseline absence', () => {
    const frame = buildStrategyAttributionDriftFrame(sampleProjectionBundle);

    expect(frame.attribution_packets.every((packet) => packet.attribution_status === 'NOT_COMPUTABLE')).toBe(true);
    expect(frame.attribution_packets.every((packet) => packet.baseline_mean_brier === null)).toBe(true);
    expect(frame.attribution_packets.every((packet) => packet.contribution_score === null)).toBe(true);
    expect(frame.drift_packets.every((packet) => packet.drift_direction === 'NOT_COMPUTABLE')).toBe(true);
    expect(frame.drift_packets.every((packet) => packet.previous_mean_brier === null)).toBe(true);
  });

  it('marks low-sample attributed records as under-sampled instead of promotional', () => {
    const bundle: LiveConsoleProjectionBundle = {
      ...sampleProjectionBundle,
      systems: [
        {
          ...sampleProjectionBundle.systems[0],
          projection_packets: [
            {
              packet_id: 'forecast-outcome-pkt-001',
              packet_type: 'FORECAST_OUTCOME_RESOLUTION',
              status: 'RESOLVED',
              display_value: '1',
              authority_source: 'SHADOW_LANE',
              projection_only: true,
            },
          ],
        },
      ],
    };
    const frame = buildStrategyAttributionDriftFrame(bundle);

    expect(frame.attribution_packets[0].attribution_status).toBe('UNDER_SAMPLED');
    expect(frame.attribution_packets[0].scored_forecast_count).toBe(1);
    expect(frame.attribution_packets[0].source_forecast_probability_mutated).toBe(false);
    expect(frame.attribution_packets[0].strategy_routing_mutated).toBe(false);
    expect(frame.drift_packets[0].drift_direction).toBe('UNDER_SAMPLED');
  });

  it('locks attribution out of Notion writes, websocket broadcast, routing, score, forecast, and authority mutation', () => {
    const frame = buildStrategyAttributionDriftFrame(sampleProjectionBundle);

    expect(frame.attribution_locks.display_only).toBe(true);
    expect(frame.attribution_locks.descriptive_attribution_only).toBe(true);
    expect(frame.attribution_locks.notion_write_adapter_enabled).toBe(false);
    expect(frame.attribution_locks.websocket_broadcast_enabled).toBe(false);
    expect(frame.attribution_locks.contribution_score_promotes_or_demotes).toBe(false);
    expect(frame.attribution_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.attribution_locks.score_mutation_allowed).toBe(false);
    expect(frame.attribution_locks.authority_tier_mutation_allowed).toBe(false);
    expect(frame.attribution_locks.strategy_routing_mutation_allowed).toBe(false);
    expect(frame.attribution_locks.execution_authority).toBe(false);
    expect(frame.attribution_locks.truth_authority).toBe(false);
  });
});
