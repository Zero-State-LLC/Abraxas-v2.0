import { useMemo } from 'react';
import { buildBrierWeightedNodeBehaviorFrame } from '../data/buildBrierWeightedNodeBehaviorFrame';
import type { LiveConsoleProjectionBundle } from '../types';

interface BrierNodeBehaviorPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

function formatMetric(value: number | null): string {
  return value == null ? 'NOT_COMPUTABLE' : value.toFixed(4);
}

export function BrierNodeBehaviorPanel({ bundle }: BrierNodeBehaviorPanelProps): JSX.Element {
  const frame = useMemo(() => buildBrierWeightedNodeBehaviorFrame(bundle), [bundle]);
  const notComputable = frame.behaviors.filter(
    (behavior) => behavior.calibration_badge === 'CALIBRATION_NOT_COMPUTABLE',
  ).length;
  const preview = frame.behaviors.slice(0, 8);

  return (
    <section
      className="brier-node-panel"
      data-testid="brier-node-behavior-panel"
      aria-label="AAL-Viz Brier Weighted Node Behavior"
    >
      <div className="brier-node-panel__header">
        <span className="brier-node-panel__title">BRIER-WEIGHTED NODE BEHAVIOR</span>
        <span className="brier-node-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="brier-node-grid">
        <div className="brier-node-section brier-node-section--wide" data-testid="brier-node-summary">
          <div className="brier-node-section__label">VISUAL CALIBRATION POSTURE</div>
          <div className="brier-node-summary-row">
            <span>{frame.behaviors.length} NODE BEHAVIORS</span>
            <span>{notComputable} CALIBRATION_NOT_COMPUTABLE</span>
            <span>DISPLAY ONLY</span>
            <span>NO FORECAST MUTATION</span>
          </div>
          <div className="brier-node-section__meta">
            Low sample size damps visual trust effects; missing scoring data keeps neutral behavior.
          </div>
        </div>

        <div className="brier-node-section" data-testid="brier-node-behaviors">
          <div className="brier-node-section__label">NODE BEHAVIOR PREVIEW</div>
          <ul className="brier-node-list">
            {preview.map((behavior) => (
              <li className={`brier-node-row brier-node-row--${behavior.calibration_badge}`} key={behavior.behavior_id}>
                <span>{behavior.forecast_id}</span>
                <span>{behavior.calibration_badge}</span>
                <strong>{formatMetric(behavior.brier_score)}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="brier-node-section" data-testid="brier-node-visual-effects">
          <div className="brier-node-section__label">VISUAL EFFECT MAP</div>
          <div className="brier-node-effect-grid">
            <span>STABILITY</span><strong>{preview[0]?.stability_multiplier.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
            <span>GLOW</span><strong>{preview[0]?.glow_integrity.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
            <span>JITTER</span><strong>{preview[0]?.jitter_penalty.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
            <span>HALO</span><strong>{preview[0]?.halo_distortion.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
            <span>EDGE</span><strong>{preview[0]?.edge_sharpness.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
            <span>TRUST DRAG</span><strong>{preview[0]?.trust_drag.toFixed(4) ?? 'NOT_COMPUTABLE'}</strong>
          </div>
        </div>

        <div className="brier-node-section" data-testid="brier-node-locks">
          <div className="brier-node-section__label">BEHAVIOR LOCKS</div>
          <div className="brier-node-effect-grid">
            <span>SCORING MUTATION</span><strong>{String(frame.behavior_locks.scoring_mutation_allowed).toUpperCase()}</strong>
            <span>FORECAST MUTATION</span><strong>{String(frame.behavior_locks.forecast_probability_mutation_allowed).toUpperCase()}</strong>
            <span>AUTHORITY MUTATION</span><strong>{String(frame.behavior_locks.authority_tier_mutation_allowed).toUpperCase()}</strong>
            <span>AUTO PROMOTION</span><strong>{String(frame.behavior_locks.automatic_promotion_allowed).toUpperCase()}</strong>
            <span>AUTO DEMOTION</span><strong>{String(frame.behavior_locks.automatic_demotion_allowed).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(frame.behavior_locks.truth_authority).toUpperCase()}</strong>
          </div>
          <div className="brier-node-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}

