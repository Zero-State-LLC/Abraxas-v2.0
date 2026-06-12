import { useMemo } from 'react';
import { buildBrierWeightedClusterBehaviorFrame } from '../data/buildBrierWeightedClusterBehaviorFrame';
import type { LiveConsoleProjectionBundle } from '../types';

interface ClusterCalibrationPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

function formatMetric(value: number | null): string {
  return value == null ? 'NOT_COMPUTABLE' : value.toFixed(4);
}

export function ClusterCalibrationPanel({ bundle }: ClusterCalibrationPanelProps): JSX.Element {
  const frame = useMemo(() => buildBrierWeightedClusterBehaviorFrame(bundle), [bundle]);
  const notComputable = frame.clusters.filter((cluster) => cluster.calibration_weather === 'NOT_COMPUTABLE').length;
  const preview = frame.clusters.slice(0, 8);
  const firstCluster = preview[0] ?? null;

  return (
    <section
      className="cluster-calibration-panel"
      data-testid="cluster-calibration-panel"
      aria-label="AAL-Viz Brier Weighted Cluster Behavior"
    >
      <div className="cluster-calibration-panel__header">
        <span className="cluster-calibration-panel__title">BRIER-WEIGHTED CLUSTER BEHAVIOR</span>
        <span className="cluster-calibration-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="cluster-calibration-grid">
        <div
          className="cluster-calibration-section cluster-calibration-section--wide"
          data-testid="cluster-calibration-summary"
        >
          <div className="cluster-calibration-section__label">CLUSTER CALIBRATION WEATHER</div>
          <div className="cluster-calibration-summary-row">
            <span>{frame.clusters.length} CLUSTERS</span>
            <span>{notComputable} CLUSTER_CALIBRATION_NOT_COMPUTABLE</span>
            <span>DISPLAY ONLY</span>
            <span>STATIC MODE AVAILABLE</span>
          </div>
          <div className="cluster-calibration-section__meta">
            Mixed clusters express variance as shear; low sample size damps trust and weather intensity.
          </div>
        </div>

        <div className="cluster-calibration-section" data-testid="cluster-calibration-clusters">
          <div className="cluster-calibration-section__label">CLUSTER PREVIEW</div>
          <ul className="cluster-calibration-list">
            {preview.map((cluster) => (
              <li
                className={`cluster-calibration-row cluster-calibration-row--${cluster.calibration_weather}`}
                key={cluster.cluster_id}
              >
                <span>{cluster.cluster_id}</span>
                <span>{cluster.scoring_status}</span>
                <strong>{cluster.calibration_weather}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="cluster-calibration-section" data-testid="cluster-calibration-effects">
          <div className="cluster-calibration-section__label">CLUSTER EFFECT MAP</div>
          <div className="cluster-calibration-effect-grid">
            <span>COHESION</span><strong>{firstCluster?.cohesion_multiplier.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
            <span>BOUNDARY</span><strong>{firstCluster?.boundary_sharpness.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
            <span>JITTER</span><strong>{firstCluster?.cluster_jitter.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
            <span>TURBULENCE</span><strong>{firstCluster?.turbulence.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
            <span>SHEAR</span><strong>{firstCluster?.shear_force.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
            <span>WARNING</span><strong>{firstCluster?.warning_ring_opacity.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
          </div>
          <div className="cluster-calibration-section__meta">
            MEAN BRIER {formatMetric(firstCluster?.mean_brier ?? null)} · VARIANCE{' '}
            {formatMetric(firstCluster?.score_variance ?? null)}
          </div>
        </div>

        <div className="cluster-calibration-section" data-testid="cluster-calibration-locks">
          <div className="cluster-calibration-section__label">CLUSTER LOCKS</div>
          <div className="cluster-calibration-effect-grid">
            <span>FORECAST MUTATION</span>
            <strong>{String(frame.cluster_locks.forecast_probability_mutation_allowed).toUpperCase()}</strong>
            <span>SCORE MUTATION</span><strong>{String(frame.cluster_locks.score_mutation_allowed).toUpperCase()}</strong>
            <span>AUTHORITY MUTATION</span>
            <strong>{String(frame.cluster_locks.authority_tier_mutation_allowed).toUpperCase()}</strong>
            <span>AUTO PROMOTION</span><strong>{String(frame.cluster_locks.automatic_promotion_allowed).toUpperCase()}</strong>
            <span>EXECUTION</span><strong>{String(frame.cluster_locks.execution_authority).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(frame.cluster_locks.truth_authority).toUpperCase()}</strong>
          </div>
          <div className="cluster-calibration-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
