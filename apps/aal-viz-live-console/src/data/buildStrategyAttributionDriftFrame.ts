import { buildTemporalCalibrationAnimationFrame } from './buildTemporalCalibrationAnimationFrame';
import type {
  DomainScoreDriftPacket,
  DriftDirection,
  LiveConsoleProjectionBundle,
  StrategyAttributionDriftFrame,
  StrategyAttributionPacket,
  StrategyAttributionStatus,
  SystemProjection,
  TemporalCalibrationAnimation,
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

function round(value: number): number {
  return Number(value.toFixed(4));
}

function statusFor(timeline: TemporalCalibrationAnimation): StrategyAttributionStatus {
  if (timeline.animation_badge === 'NOT_COMPUTABLE') return 'NOT_COMPUTABLE';
  if (timeline.animation_badge === 'UNDER_SAMPLED') return 'UNDER_SAMPLED';
  return 'ATTRIBUTED';
}

function driftFor(timeline: TemporalCalibrationAnimation, sampleSize: number): DriftDirection {
  if (timeline.animation_badge === 'NOT_COMPUTABLE') return 'NOT_COMPUTABLE';
  if (sampleSize < 10) return 'UNDER_SAMPLED';
  if (timeline.animation_badge === 'VOLATILE') return 'VOLATILE';
  if (timeline.animation_badge === 'IMPROVING') return 'IMPROVING';
  if (timeline.animation_badge === 'DECAYING') return 'DECAYING';
  return 'STABLE';
}

function forecastIdsFor(system: SystemProjection): string[] {
  return system.projection_packets
    .filter((packet) => packet.packet_type.includes('FORECAST') || packet.packet_type.includes('CLAIM'))
    .map((packet) => packet.packet_id)
    .sort((a, b) => a.localeCompare(b));
}

function buildAttributionPacket(
  system: SystemProjection,
  timeline: TemporalCalibrationAnimation,
  computedAt: string,
): StrategyAttributionPacket {
  const window = timeline.windows[0];
  const status = statusFor(timeline);
  const baseline = null;
  const brierDelta = baseline == null || window.mean_brier == null ? null : round(window.mean_brier - baseline);
  const contributionScore = baseline == null || window.mean_brier == null ? null : round(baseline - window.mean_brier);
  const forecastIds = forecastIdsFor(system);

  return {
    attribution_id: `attribution-${system.system_id}`,
    run_id: system.system_id,
    strategy_id: `strategy-${system.system_id}`,
    strategy_name: system.display_name,
    domain: system.system_id,
    signal_family: system.risk_level,
    forecast_ids: forecastIds,
    scored_forecast_count: window.sample_size,
    mean_brier: window.mean_brier,
    baseline_mean_brier: baseline,
    brier_delta: brierDelta,
    calibration_error_delta: brierDelta,
    contribution_score: contributionScore,
    attribution_status: status,
    computed_at: computedAt,
    lineage_join_state:
      status === 'NOT_COMPUTABLE'
        ? forecastIds.length === 0
          ? 'MISSING_STRATEGY_LINEAGE'
          : 'MISSING_OUTCOME_DATA'
        : 'JOINED',
    projection_only: true,
    source_forecast_probability_mutated: false,
    source_score_mutated: false,
    authority_tier_mutated: false,
    strategy_routing_mutated: false,
  };
}

function buildDriftPacket(timeline: TemporalCalibrationAnimation, computedAt: string): DomainScoreDriftPacket {
  const window = timeline.windows[0];
  const previousMeanBrier = null;
  const brierDelta =
    previousMeanBrier == null || window.mean_brier == null ? null : round(window.mean_brier - previousMeanBrier);

  return {
    drift_id: `drift-${timeline.entity_id}`,
    domain: timeline.entity_id,
    window_start: window.start_at,
    window_end: window.end_at,
    mean_brier: window.mean_brier,
    previous_mean_brier: previousMeanBrier,
    brier_delta: brierDelta,
    calibration_error: window.calibration_error,
    sample_size: window.sample_size,
    drift_direction: driftFor(timeline, window.sample_size),
    computed_at: computedAt,
    projection_only: true,
    source_forecast_probability_mutated: false,
    source_score_mutated: false,
    authority_tier_mutated: false,
    strategy_routing_mutated: false,
  };
}

export function buildStrategyAttributionDriftFrame(bundle: LiveConsoleProjectionBundle): StrategyAttributionDriftFrame {
  const temporalFrame = buildTemporalCalibrationAnimationFrame(bundle);
  const systemsById = new Map(bundle.systems.map((system) => [system.system_id, system]));
  const computedAt = bundle.generated_at;
  const attributionPackets = temporalFrame.timelines.map((timeline) =>
    buildAttributionPacket(systemsById.get(timeline.entity_id) ?? bundle.systems[0], timeline, computedAt),
  );
  const driftPackets = temporalFrame.timelines.map((timeline) => buildDriftPacket(timeline, computedAt));

  const frameWithoutHash = {
    packet_type: 'AALVizStrategyAttributionDriftFrame.v1' as const,
    drop_name: 'AAL-Viz v7.2 — Strategy Attribution + Domain Score Drift Timeline Code Drop' as const,
    authority: 'DESCRIPTIVE_ATTRIBUTION_AND_PROJECTION_ONLY' as const,
    mutation_policy: 'NO_FORECAST_SCORE_AUTHORITY_OR_ROUTING_MUTATION' as const,
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
    ] as StrategyAttributionDriftFrame['folded_versions'],
    features: [
      'strategy_attribution_ledger',
      'domain_score_drift_timeline',
      'contribution_score',
      'rolling_brier_windows',
      'attribution_visual_weight',
      'under_sampled_guard',
      'not_computable_guard',
    ] as StrategyAttributionDriftFrame['features'],
    attribution_packets: attributionPackets,
    drift_packets: driftPackets,
    attribution_locks: {
      display_only: true as const,
      descriptive_attribution_only: true as const,
      notion_write_adapter_enabled: false as const,
      websocket_broadcast_enabled: false as const,
      contribution_score_promotes_or_demotes: false as const,
      scoring_mutation_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      score_mutation_allowed: false as const,
      authority_tier_mutation_allowed: false as const,
      strategy_routing_mutation_allowed: false as const,
      automatic_promotion_allowed: false as const,
      automatic_demotion_allowed: false as const,
      execution_authority: false as const,
      truth_authority: false as const,
      low_sample_size_renders_under_sampled: true as const,
      missing_strategy_lineage_renders_not_computable: true as const,
      missing_outcome_data_renders_not_computable: true as const,
      baseline_comparison_required: true as const,
      corrected_scores_show_correction_provenance: true as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
