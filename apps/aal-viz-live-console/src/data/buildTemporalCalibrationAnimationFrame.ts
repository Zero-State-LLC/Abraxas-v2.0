import { buildBrierWeightedClusterBehaviorFrame } from './buildBrierWeightedClusterBehaviorFrame';
import type {
  BrierWeightedClusterBehavior,
  LiveConsoleProjectionBundle,
  TemporalCalibrationAnimation,
  TemporalCalibrationAnimationBadge,
  TemporalCalibrationAnimationFrame,
  TemporalCalibrationWindow,
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

function windowFor(cluster: BrierWeightedClusterBehavior): TemporalCalibrationWindow {
  return {
    window_id: `window-${cluster.cluster_id}-current`,
    start_at: cluster.window_start,
    end_at: cluster.window_end,
    mean_brier: cluster.mean_brier,
    calibration_error: cluster.calibration_error,
    score_variance: cluster.score_variance,
    sample_size: cluster.sample_size,
    scoring_status: cluster.scoring_status,
  };
}

function badgeFor(cluster: BrierWeightedClusterBehavior): TemporalCalibrationAnimationBadge {
  if (cluster.scoring_status === 'NOT_COMPUTABLE') return 'NOT_COMPUTABLE';
  if (cluster.scoring_status === 'UNDER_SAMPLED') return 'UNDER_SAMPLED';
  if ((cluster.score_variance ?? 0) >= 0.05 || cluster.calibration_weather === 'TURBULENT') return 'VOLATILE';
  if ((cluster.mean_brier ?? 0) >= 0.2) return 'DECAYING';
  return 'STABLE';
}

function buildTimeline(cluster: BrierWeightedClusterBehavior): TemporalCalibrationAnimation {
  const window = windowFor(cluster);
  const gapMarkers = cluster.scoring_status === 'NOT_COMPUTABLE' ? [window.window_id] : [];

  return {
    timeline_id: `temporal-${cluster.cluster_id}`,
    entity_id: cluster.cluster_id,
    entity_type: 'CLUSTER',
    windows: [window],
    playback: {
      speed: 1,
      loop: false,
      smoothing: cluster.scoring_status === 'NOT_COMPUTABLE' ? 'NONE' : 'EASED',
      mode: 'SNAPSHOT',
    },
    temporal_cohesion_curve: [round(cluster.cohesion_multiplier)],
    turbulence_curve: [round(cluster.turbulence)],
    trust_halo_curve: [round(cluster.trust_halo)],
    boundary_integrity_curve: [round(cluster.boundary_sharpness)],
    gap_markers: gapMarkers,
    animation_badge: badgeFor(cluster),
    projection_only: true,
    source_forecast_probability_mutated: false,
    source_score_mutated: false,
    authority_tier_mutated: false,
  };
}

export function buildTemporalCalibrationAnimationFrame(
  bundle: LiveConsoleProjectionBundle,
): TemporalCalibrationAnimationFrame {
  const clusterFrame = buildBrierWeightedClusterBehaviorFrame(bundle);
  const timelines = clusterFrame.clusters.map((cluster) => buildTimeline(cluster));

  const frameWithoutHash = {
    packet_type: 'AALVizTemporalCalibrationAnimationFrame.v1' as const,
    drop_name: 'AAL-Viz v7.1 — Temporal Calibration Animation Code Drop' as const,
    authority: 'VISUAL_TEMPORAL_CALIBRATION_PROJECTION_ONLY' as const,
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
      'v7.0',
    ] as TemporalCalibrationAnimationFrame['folded_versions'],
    features: [
      'calibration_timeline',
      'chronoscope_scrubber',
      'temporal_trails',
      'morph_animation',
      'temporal_gap_markers',
      'accessibility_static_summary',
    ] as TemporalCalibrationAnimationFrame['features'],
    timelines,
    animation_locks: {
      display_only: true as const,
      static_timeline_table_available: true as const,
      animated_playback_controls_enabled: false as const,
      scoring_mutation_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      score_mutation_allowed: false as const,
      authority_tier_mutation_allowed: false as const,
      automatic_promotion_allowed: false as const,
      automatic_demotion_allowed: false as const,
      execution_authority: false as const,
      truth_authority: false as const,
      missing_windows_render_temporal_gaps: true as const,
      missing_windows_interpolated_as_certainty: false as const,
      low_sample_windows_render_under_sampled: true as const,
      corrected_windows_show_correction_provenance: true as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
