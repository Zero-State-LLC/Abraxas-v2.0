import { useEffect, useState } from 'react';
import {
  loadOperatorLoopProjection,
  type OperatorLoopProjection,
  type OperatorLoopTruthSurface,
} from '../data/loadOperatorLoopProjection';

/** Status-glance row text for known truth-surface item kinds (display only). */
function renderItem(item: Record<string, unknown>): string {
  const kind = String(item.kind || '');
  if (kind === 'open_pr') {
    const n = item.number;
    const title = item.title;
    const draft = item.is_draft ? 'draft' : 'ready';
    const mergeable = item.mergeable ?? 'UNKNOWN';
    return `#${n} ${title} · ${draft} · ${mergeable}`;
  }
  if (kind === 'pr_checks_summary') {
    return `PR #${item.pr_number} checks · ${item.primary} (pass=${item.pass} fail=${item.fail} pending=${item.pending})`;
  }
  if (kind === 'git_tip') {
    return `tip ${String(item.sha).slice(0, 7)} @ ${item.branch}`;
  }
  if (kind === 'main_workflow') {
    return `${item.workflow} · ${item.conclusion || item.status}`;
  }
  return JSON.stringify(item);
}

function SurfaceBlock({
  title,
  surface,
}: {
  title: string;
  surface: OperatorLoopTruthSurface;
}): JSX.Element {
  return (
    <div className="operator-loop-surface" data-testid={`operator-loop-surface-${title.toLowerCase()}`}>
      <div className="authority-table__row">
        <span className="authority-table__key">{title}</span>
        <span className={`authority-table__val authority-table__val--${surface.status === 'PRESENT'}`}>
          {surface.status}
        </span>
      </div>
      <div className="operator-loop-surface__claim">{surface.truth_claim}</div>
      <div className="operator-loop-surface__meta">
        glyph={surface.glyph} · source={surface.source} · items={surface.items.length}
      </div>
      <div className="operator-loop-surface__locks">
        assign={String(surface.can_assign)} · approve={String(surface.can_approve)} ·
        merge={String(surface.can_merge)} · deploy={String(surface.can_deploy)}
      </div>
      {surface.items.slice(0, 8).map((item, idx) => (
        <div key={idx} className="operator-loop-surface__item">
          {renderItem(item as Record<string, unknown>)}
        </div>
      ))}
    </div>
  );
}

export function OperatorLoopProjectionPanel(): JSX.Element {
  const [projection, setProjection] = useState<OperatorLoopProjection | null>(null);
  const [loadState, setLoadState] = useState<'loading' | 'ready' | 'missing'>('loading');

  useEffect(() => {
    let cancelled = false;
    void loadOperatorLoopProjection()
      .then((data) => {
        if (cancelled) return;
        setProjection(data);
        setLoadState(data == null ? 'missing' : 'ready');
      })
      .catch(() => {
        if (!cancelled) {
          setProjection(null);
          setLoadState('missing');
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="panel-block" data-testid="operator-loop-projection-panel">
      <div className="panel-header">
        <span className="panel-icon">⧉</span>
        OPERATOR LOOP · TRUTH SURFACES
      </div>
      <div className="panel-body">
        {loadState === 'loading' && (
          <div role="status">Loading operator-loop projection…</div>
        )}
        {loadState === 'missing' && (
          <div className="operator-loop-missing">
            No operator-loop-projection.json (or authority validation failed). Run:
            <code> python scripts/viz/build_aal_viz_operator_loop_projection.py</code>
          </div>
        )}
        {loadState === 'ready' && projection != null && (
          <>
            <div className="authority-table" data-testid="operator-loop-summary">
              <div className="authority-table__row">
                <span className="authority-table__key">PACKETS</span>
                <span className="authority-table__val">{projection.summary.work_packet_count}</span>
              </div>
              <div className="authority-table__row">
                <span className="authority-table__key">HANDOFFS</span>
                <span className="authority-table__val">{projection.summary.handoff_count}</span>
              </div>
              <div className="authority-table__row">
                <span className="authority-table__key">FILE OVERLAPS</span>
                <span className="authority-table__val">{projection.summary.file_overlap_count}</span>
              </div>
              <div className="authority-table__row">
                <span className="authority-table__key">PROJECTION ONLY</span>
                <span className="authority-table__val authority-table__val--true">
                  {String(projection.authority.projection_only).toUpperCase()}
                </span>
              </div>
              <div className="authority-table__row">
                <span className="authority-table__key">ASSIGN / APPROVE</span>
                <span className="authority-table__val authority-table__val--false">
                  FALSE / FALSE
                </span>
              </div>
            </div>

            {projection.truth_surfaces != null && (
              <div className="operator-loop-surfaces" data-testid="operator-loop-truth-surfaces">
                <SurfaceBlock title="GITHUB" surface={projection.truth_surfaces.github} />
                <SurfaceBlock title="NOTION" surface={projection.truth_surfaces.notion} />
                <SurfaceBlock title="CI" surface={projection.truth_surfaces.ci} />
                {projection.truth_surfaces.lineage_rule != null && (
                  <div className="operator-loop-lineage">{projection.truth_surfaces.lineage_rule}</div>
                )}
              </div>
            )}

            {projection.work_packets.slice(0, 5).map((pkt) => (
              <div key={pkt.work_packet_id} className="operator-loop-packet">
                <strong>{pkt.work_packet_id}</strong> · {pkt.producer_system} · {pkt.work_state}
                <div className="operator-loop-packet__goal">{pkt.goal}</div>
              </div>
            ))}

            {projection.file_overlaps.length > 0 && (
              <div className="operator-loop-overlaps" data-testid="operator-loop-overlaps">
                {projection.file_overlaps.map((o, i) => (
                  <div key={i}>
                    {o.conflict_class}: {o.detail}
                  </div>
                ))}
              </div>
            )}

            <div className="forbidden-controls__header">
              ⊘ DISPLAY ONLY — NO ASSIGNMENT · NO APPROVAL · NO MERGE
            </div>
          </>
        )}
      </div>
    </div>
  );
}
