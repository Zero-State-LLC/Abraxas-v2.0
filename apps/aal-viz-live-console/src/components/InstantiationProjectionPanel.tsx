import { useEffect, useState } from 'react';
import {
  loadInstantiationProjection,
  type InstantiationLineageEdge,
  type InstantiationProjectionView,
  type InstantiationStateTile,
} from '../data/loadInstantiationProjection';

/** Compact epistemic chip per dimension: OBSERVED/INFERRED/SPECULATIVE/NOT_COMPUTABLE. */
function statusGlyph(status: string): string {
  if (status === 'OBSERVED') return '●';
  if (status === 'INFERRED') return '◐';
  if (status === 'SPECULATIVE') return '○';
  return '∅'; // NOT_COMPUTABLE
}

function StateRow({ state }: { state: InstantiationStateTile }): JSX.Element {
  return (
    <div className="instantiation-state" data-testid={`instantiation-state-${state.state_id}`}>
      <div className="authority-table__row">
        <span className="authority-table__key">{state.state_id}</span>
        <span className="authority-table__val">
          {state.observation_window.start} · {state.causal_exposure}
        </span>
      </div>
      <div className="instantiation-state__dimensions">
        {state.dimensions.map((d) => (
          <span
            key={d.name}
            className={`instantiation-dimension instantiation-dimension--${d.epistemic_status.toLowerCase()}`}
            title={`${d.name}: ${d.epistemic_status}${d.not_computable_reason ? ` (${d.not_computable_reason})` : ''}`}
          >
            {statusGlyph(d.epistemic_status)}
          </span>
        ))}
        <span className="instantiation-state__depth">
          depth={state.aggregate_instantiation_depth}
        </span>
      </div>
    </div>
  );
}

function EdgeRow({ edge }: { edge: InstantiationLineageEdge }): JSX.Element {
  const changes = edge.dimension_changes
    .map((c) => `${c.dimension}:${c.change_kind}`)
    .join(' · ');
  return (
    <div className="instantiation-edge" data-testid={`instantiation-edge-${edge.transition_id}`}>
      <div className="authority-table__row">
        <span className="authority-table__key">
          {edge.from_state_id} → {edge.to_state_id}
        </span>
        <span
          className={`authority-table__val authority-table__val--${!edge.feedback_contaminated}`}
        >
          {edge.causal_exposure}
          {edge.feedback_contaminated ? ' · CONTAMINATED' : ''}
        </span>
      </div>
      <div className="instantiation-edge__changes">{changes}</div>
      {edge.feedback_contaminated && (
        <div className="instantiation-edge__note">
          not independent confirmation (eligible=
          {String(edge.independent_confirmation_eligible)})
        </div>
      )}
    </div>
  );
}

export function InstantiationProjectionPanel(): JSX.Element {
  const [view, setView] = useState<InstantiationProjectionView | null>(null);
  const [loadState, setLoadState] = useState<'loading' | 'ready' | 'missing'>('loading');

  useEffect(() => {
    let cancelled = false;
    void loadInstantiationProjection()
      .then((data) => {
        if (cancelled) return;
        setView(data);
        setLoadState(data == null ? 'missing' : 'ready');
      })
      .catch(() => {
        if (!cancelled) {
          setView(null);
          setLoadState('missing');
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const anomalies =
    view?.shadow_overlay?.findings.filter((f) => f.severity === 'anomaly') ?? [];
  const observations =
    view?.shadow_overlay?.findings.filter((f) => f.severity === 'observation') ?? [];

  return (
    <div className="panel-block" data-testid="instantiation-projection-panel">
      <div className="panel-header">
        <span className="panel-icon">⟁</span>
        INSTANTIATION · STATE / LINEAGE (RDI)
      </div>
      <div className="panel-body">
        {loadState === 'loading' && <div role="status">Loading instantiation projection…</div>}
        {loadState === 'missing' && (
          <div className="instantiation-missing">
            No instantiation-projection.json (or authority validation failed). Run:
            <code> python scripts/viz/build_aal_viz_instantiation_projection.py</code>
          </div>
        )}
        {loadState === 'ready' && view != null && (
          <>
            {view.construct_timelines.map((timeline) => (
              <div
                key={timeline.construct_ref.object_id}
                className="instantiation-timeline"
                data-testid={`instantiation-timeline-${timeline.construct_ref.object_id}`}
              >
                <div className="authority-table__row">
                  <span className="authority-table__key">CONSTRUCT</span>
                  <span className="authority-table__val">
                    {timeline.construct_ref.object_id}
                  </span>
                </div>
                {timeline.states.map((state) => (
                  <StateRow key={state.state_id} state={state} />
                ))}
              </div>
            ))}

            {view.lineage_edges.map((edge) => (
              <EdgeRow key={edge.transition_id} edge={edge} />
            ))}

            {view.shadow_overlay != null && (
              <div className="instantiation-shadow" data-testid="instantiation-shadow-overlay">
                <div className="authority-table__row">
                  <span className="authority-table__key">SHADOW FINDINGS</span>
                  <span className="authority-table__val">
                    {anomalies.length} anomalies · {observations.length} observations
                  </span>
                </div>
                {anomalies.slice(0, 6).map((finding, idx) => (
                  <div key={idx} className="instantiation-shadow__finding">
                    {finding.code} · {finding.subject_id}
                  </div>
                ))}
              </div>
            )}

            <div className="authority-table" data-testid="instantiation-authority">
              <div className="authority-table__row">
                <span className="authority-table__key">PROJECTION ONLY</span>
                <span className="authority-table__val authority-table__val--true">
                  {String(view.authority.projection_only).toUpperCase()}
                </span>
              </div>
              <div className="authority-table__row">
                <span className="authority-table__key">EXEC / FORECAST / INTERVENTION</span>
                <span className="authority-table__val authority-table__val--false">
                  FALSE / FALSE / FALSE
                </span>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
