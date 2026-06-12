import { buildBrierWeightedNodeBehaviorFrame } from './buildBrierWeightedNodeBehaviorFrame';
import type {
  BrierWeightedClusterBehavior,
  BrierWeightedClusterBehaviorFrame,
  BrierWeightedNodeBehavior,
  ClusterCalibrationWeather,
  ClusterScoringStatus,
  LiveConsoleProjectionBundle,
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

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function round(value: number): number {
  return Number(value.toFixed(4));
}

function mean(values: number[]): number | null {
  if (values.length === 0) return null;
  return Number((values.reduce((sum, value) => sum + value, 0) / values.length).toFixed(10));
}

function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? Number(((sorted[middle - 1] + sorted[middle]) / 2).toFixed(10)) : sorted[middle];
}

function variance(values: number[], average: number | null): number | null {
  if (values.length < 2 || average == null) return null;
  return Number((values.reduce((sum, value) => sum + (value - average) ** 2, 0) / values.length).toFixed(10));
}

function sampleGate(sampleSize: number): number {
  if (sampleSize <= 0) return 0;
  return clamp(sampleSize / 30, 0.2, 1);
}

function scoringStatus(memberCount: number, scoredCount: number): ClusterScoringStatus {
  if (scoredCount === 0) return 'NOT_COMPUTABLE';
  if (scoredCount < 10) return 'UNDER_SAMPLED';
  if (scoredCount < memberCount) return 'MIXED';
  return 'SCORED';
}

function weatherFor(
  status: ClusterScoringStatus,
  meanBrier: number | null,
  calibrationError: number | null,
  scoreVariance: number | null,
): ClusterCalibrationWeather {
  if (status === 'NOT_COMPUTABLE') return 'NOT_COMPUTABLE';
  if (status === 'UNDER_SAMPLED') return 'UNDER_SAMPLED';
  if ((meanBrier ?? 0) >= 0.25 || (calibrationError ?? 0) >= 0.2 || (scoreVariance ?? 0) >= 0.05) return 'TURBULENT';
  if ((meanBrier ?? 0) >= 0.1 || (calibrationError ?? 0) >= 0.1 || (scoreVariance ?? 0) >= 0.02) return 'NOISY';
  return 'CLEAR';
}

function neutralCluster(clusterId: string, memberCount: number, windowStart: string, windowEnd: string): BrierWeightedClusterBehavior {
  return {
    cluster_id: clusterId,
    cluster_type: 'DOMAIN',
    member_count: memberCount,
    scored_member_count: 0,
    mean_brier: null,
    median_brier: null,
    calibration_error: null,
    score_variance: null,
    sample_size: 0,
    window_start: windowStart,
    window_end: windowEnd,
    scoring_status: 'NOT_COMPUTABLE',
    cohesion_multiplier: 1,
    boundary_sharpness: 0.5,
    cluster_jitter: 0,
    turbulence: 0,
    trust_halo: 0.5,
    shear_force: 0,
    warning_ring_opacity: 0,
    calibration_weather: 'NOT_COMPUTABLE',
    projection_only: true,
    source_forecast_probability_mutated: false,
    source_score_mutated: false,
    authority_tier_mutated: false,
  };
}

function buildCluster(
  clusterId: string,
  members: BrierWeightedNodeBehavior[],
  windowStart: string,
  windowEnd: string,
): BrierWeightedClusterBehavior {
  const scored = members.map((member) => member.brier_score).filter((value): value is number => value != null);
  const average = mean(scored);
  const scoreVariance = variance(scored, average);

  if (average == null) {
    return neutralCluster(clusterId, members.length, windowStart, windowEnd);
  }

  const scoredCount = scored.length;
  const status = scoringStatus(members.length, scoredCount);
  const gate = sampleGate(scoredCount);
  const normalizedMean = clamp(average, 0, 1);
  const calibrationError = average;
  const normalizedVariance = clamp(scoreVariance ?? 0, 0, 1);
  const instability = gate * normalizedMean;
  const stability = gate * (1 - normalizedMean);
  const shear = gate * Math.sqrt(normalizedVariance);

  return {
    cluster_id: clusterId,
    cluster_type: 'DOMAIN',
    member_count: members.length,
    scored_member_count: scoredCount,
    mean_brier: average,
    median_brier: median(scored),
    calibration_error: calibrationError,
    score_variance: scoreVariance,
    sample_size: scoredCount,
    window_start: windowStart,
    window_end: windowEnd,
    scoring_status: status,
    cohesion_multiplier: round(1 + stability * 0.25 - instability * 0.35),
    boundary_sharpness: round(0.35 + stability * 0.65 - shear * 0.2),
    cluster_jitter: round(instability),
    turbulence: round(instability * 0.75 + shear * 0.25),
    trust_halo: round(0.4 + stability * 0.6 - instability * 0.2),
    shear_force: round(shear),
    warning_ring_opacity: round(gate * clamp(calibrationError * 2, 0, 1)),
    calibration_weather: weatherFor(status, average, calibrationError, scoreVariance),
    projection_only: true,
    source_forecast_probability_mutated: false,
    source_score_mutated: false,
    authority_tier_mutated: false,
  };
}

export function buildBrierWeightedClusterBehaviorFrame(
  bundle: LiveConsoleProjectionBundle,
): BrierWeightedClusterBehaviorFrame {
  const nodeFrame = buildBrierWeightedNodeBehaviorFrame(bundle);
  const windowStart = bundle.generated_at;
  const windowEnd = bundle.generated_at;
  const clusters = bundle.systems.map((system) =>
    buildCluster(
      system.system_id,
      nodeFrame.behaviors.filter((behavior) => behavior.run_id === system.system_id),
      windowStart,
      windowEnd,
    ),
  );

  const frameWithoutHash = {
    packet_type: 'AALVizBrierWeightedClusterBehaviorFrame.v1' as const,
    drop_name: 'AAL-Viz v7.0 — Brier-Weighted Cluster Behavior Code Drop' as const,
    authority: 'VISUAL_CALIBRATION_PROJECTION_ONLY' as const,
    mutation_policy: 'NO_FORECAST_SCORE_OR_AUTHORITY_MUTATION' as const,
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
    ] as BrierWeightedClusterBehaviorFrame['folded_versions'],
    features: [
      'cluster_brier_weight',
      'calibration_weather',
      'cohesion_multiplier',
      'cluster_turbulence',
      'internal_shear',
      'sample_size_gate',
      'cluster_not_computable_state',
    ] as BrierWeightedClusterBehaviorFrame['features'],
    clusters,
    cluster_locks: {
      display_only: true as const,
      cluster_weather_static_mode_available: true as const,
      scoring_mutation_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      score_mutation_allowed: false as const,
      authority_tier_mutation_allowed: false as const,
      automatic_promotion_allowed: false as const,
      automatic_demotion_allowed: false as const,
      execution_authority: false as const,
      truth_authority: false as const,
      low_sample_size_damps_trust_effects: true as const,
      missing_scoring_renders_cluster_calibration_not_computable: true as const,
      mixed_clusters_show_variance_and_shear: true as const,
      corrected_scores_show_correction_provenance: true as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
