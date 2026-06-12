import { buildScoringBindingFrame } from './buildScoringBindingFrame';
import type {
  BrierWeightedNodeBehavior,
  BrierWeightedNodeBehaviorFrame,
  CalibrationBadge,
  LiveConsoleProjectionBundle,
  ScoringBindingRecord,
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

function sampleGate(sampleSize: number): number {
  if (sampleSize <= 0) return 0;
  return clamp(sampleSize / 30, 0.2, 1);
}

function badgeFor(record: ScoringBindingRecord, sampleSize: number): CalibrationBadge {
  if (record.brier_score == null) return 'CALIBRATION_NOT_COMPUTABLE';
  if (sampleSize < 10) return 'UNDER_SAMPLED';
  if (record.brier_score <= 0.1) return 'WELL_CALIBRATED';
  return 'UNSTABLE';
}

function buildBehavior(
  record: ScoringBindingRecord,
  meanBrier: number | null,
  calibrationError: number | null,
  sampleSize: number,
): BrierWeightedNodeBehavior {
  const badge = badgeFor(record, sampleSize);
  const gate = sampleGate(sampleSize);
  const brier = record.brier_score;

  if (brier == null) {
    return {
      behavior_id: `behavior-${record.score_id}`,
      forecast_id: record.forecast_id,
      run_id: record.run_id,
      brier_score: null,
      mean_brier: meanBrier,
      calibration_error: calibrationError,
      sample_size: sampleSize,
      scoring_status: record.scoring_status,
      stability_multiplier: 1,
      glow_integrity: 0.5,
      jitter_penalty: 0,
      halo_distortion: 0,
      edge_sharpness: 0.5,
      trust_drag: 0,
      calibration_badge: badge,
      projection_only: true,
      source_forecast_probability_mutated: false,
      authority_tier_mutated: false,
    };
  }

  const normalizedBrier = clamp(brier, 0, 1);
  const visualStrength = gate * (1 - normalizedBrier);
  const instability = gate * normalizedBrier;

  return {
    behavior_id: `behavior-${record.score_id}`,
    forecast_id: record.forecast_id,
    run_id: record.run_id,
    brier_score: brier,
    mean_brier: meanBrier,
    calibration_error: calibrationError,
    sample_size: sampleSize,
    scoring_status: record.scoring_status,
    stability_multiplier: round(1 + visualStrength * 0.25 - instability * 0.25),
    glow_integrity: round(0.35 + visualStrength * 0.65),
    jitter_penalty: round(instability),
    halo_distortion: round(instability * 0.9),
    edge_sharpness: round(0.3 + visualStrength * 0.7),
    trust_drag: round(instability * 0.8),
    calibration_badge: badge,
    projection_only: true,
    source_forecast_probability_mutated: false,
    authority_tier_mutated: false,
  };
}

export function buildBrierWeightedNodeBehaviorFrame(
  bundle: LiveConsoleProjectionBundle,
): BrierWeightedNodeBehaviorFrame {
  const scoringFrame = buildScoringBindingFrame(bundle);
  const sampleSize = scoringFrame.calibration_summary.sample_size;
  const meanBrier = scoringFrame.calibration_summary.mean_brier;
  const calibrationError = scoringFrame.calibration_summary.calibration_error;
  const behaviors = scoringFrame.scoring_records.map((record) =>
    buildBehavior(record, meanBrier, calibrationError, sampleSize),
  );

  const frameWithoutHash = {
    packet_type: 'AALVizBrierWeightedNodeBehaviorFrame.v1' as const,
    drop_name: 'AAL-Viz v6.9 — Brier-Weighted Node Behavior Code Drop' as const,
    authority: 'VISUAL_CALIBRATION_PROJECTION_ONLY' as const,
    mutation_policy: 'NO_FORECAST_OR_AUTHORITY_MUTATION' as const,
    projection_only: true as const,
    folded_versions: ['v6.1', 'v6.2', 'v6.3', 'v6.4', 'v6.5', 'v6.6', 'v6.7', 'v6.8'] as BrierWeightedNodeBehaviorFrame['folded_versions'],
    features: [
      'brier_visual_weight',
      'calibration_badge',
      'halo_distortion',
      'stability_multiplier',
      'sample_size_gate',
      'calibration_not_computable_state',
    ] as BrierWeightedNodeBehaviorFrame['features'],
    behaviors,
    behavior_locks: {
      display_only: true as const,
      scoring_mutation_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      authority_tier_mutation_allowed: false as const,
      automatic_promotion_allowed: false as const,
      automatic_demotion_allowed: false as const,
      execution_authority: false as const,
      truth_authority: false as const,
      low_sample_size_damps_trust_effects: true as const,
      missing_scoring_renders_calibration_not_computable: true as const,
      corrected_scores_show_correction_provenance: true as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
