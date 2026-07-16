import { useMemo, useState } from 'react';
import type {
  OperatorPlatformProjection,
  OperatorPlatformTemporalCategory,
  YggdrasilDeltaStructuralClass,
  YggdrasilTopologyDeltaIntelligenceProjection,
} from '../types';

const CATEGORY_ORDER: OperatorPlatformTemporalCategory[] = [
  'TOPOLOGY_NODE',
  'TOPOLOGY_EDGE',
  'CONTRACT_FIELD',
  'OWNERSHIP',
  'VALIDATOR_STATE',
  'RECEIPT',
  'PACKET',
  'SOURCE_INTEGRITY',
  'SECTION_STATUS',
];

function shortHash(value: string | null | undefined): string {
  return value == null ? 'NOT_COMPUTABLE' : value.slice(0, 12);
}

function formatValue(value: unknown): string {
  if (value === null) return 'null';
  if (typeof value === 'string') return value;
  return JSON.stringify(value, null, 2);
}

export default function OperatorPlatformChangesView({
  platform,
  deltaIntelligence,
}: {
  platform: OperatorPlatformProjection;
  deltaIntelligence?: YggdrasilTopologyDeltaIntelligenceProjection;
}): JSX.Element {
  const [severity, setSeverity] = useState('ALL');
  const [structuralClass, setStructuralClass] = useState<'ALL' | YggdrasilDeltaStructuralClass>('ALL');
  const section = platform.temporal_diff;
  const diff = section.payload;
  const priorities = useMemo(() => (deltaIntelligence?.sections.review_priorities.entries ?? []).filter(
    (entry) => (severity === 'ALL' || entry.severity === severity) &&
      (structuralClass === 'ALL' || entry.structural_classes.includes(structuralClass)),
  ), [deltaIntelligence, severity, structuralClass]);
  const correlations = deltaIntelligence?.sections.finding_correlation.entries ?? [];
  const structural = deltaIntelligence?.sections.structural_deltas.entries ?? [];
  const paths = deltaIntelligence?.sections.changed_paths.entries ?? [];
  if (diff == null && deltaIntelligence == null) {
    return (
      <section className="operator-view" aria-labelledby="changes-heading">
        <div className="view-heading-row">
          <h1 id="changes-heading">Changes</h1>
          <span className="source-state source-state--not_computable">{section.status}</span>
        </div>
        <div className="operator-empty" role="status">
          <strong>Temporal diff not computable</strong>
          <span>{section.not_computable_reason ?? 'Explicit prior and current evidence are unavailable.'}</span>
        </div>
      </section>
    );
  }

  const effectiveDiff = diff ?? {
    status: 'NOT_COMPUTABLE', prior_generation_id: null, current_generation_id: null,
    comparison_scope: [], out_of_scope: ['LINEAGE', 'QUEUE', 'TRANSPORT'],
    category_counts: {}, entries: [], total_change_count: 0, not_computable_count: 1,
    operator_summary: section.not_computable_reason ?? 'Temporal Diff evidence is unavailable.',
    remaining_blockers: section.validation_findings,
  };
  const categoryCounts = effectiveDiff.category_counts as Partial<Record<OperatorPlatformTemporalCategory, number>>;
  const scope = effectiveDiff.comparison_scope ?? [];
  const outOfScope = effectiveDiff.out_of_scope ?? ['LINEAGE', 'QUEUE', 'TRANSPORT'];
  const groups = CATEGORY_ORDER.map((category) => ({
    category,
    entries: effectiveDiff.entries.filter((entry) => entry.category === category),
  })).filter((group) => group.entries.length > 0);

  return (
    <section className="operator-view" aria-labelledby="changes-heading">
      <div className="view-heading-row">
        <div>
          <span className="view-kicker">Explicit generation comparison</span>
          <h1 id="changes-heading">Changes</h1>
        </div>
        <span className={`source-state source-state--${section.status.toLowerCase()}`}>{section.status}</span>
      </div>

      {section.validation_findings.length > 0 && (
        <div className="section-findings" role="status">
          <strong>Projection findings</strong>
          {section.validation_findings.map((finding) => <span key={finding}>{finding}</span>)}
        </div>
      )}

      {deltaIntelligence == null ? (
        <div className="section-findings" role="status">
          Delta intelligence unavailable. Temporal Diff remains the active changes projection.
        </div>
      ) : (
        <section className="delta-intelligence" aria-labelledby="delta-intelligence-heading">
          <div className="view-heading-row">
            <div>
              <span className="view-kicker">Deterministic review order</span>
              <h2 id="delta-intelligence-heading">Topology delta intelligence</h2>
            </div>
            <span className={`source-state source-state--${deltaIntelligence.status.toLowerCase()}`}>{deltaIntelligence.status}</span>
          </div>
          <div className="change-generation" aria-label="Topology generations">
            <div><span>Prior topology</span><code>{shortHash(deltaIntelligence.generation.prior_topology_generation_id)}</code></div>
            <span aria-hidden="true">-&gt;</span>
            <div><span>Current topology</span><code>{shortHash(deltaIntelligence.generation.current_topology_generation_id)}</code></div>
          </div>
          <div className="metric-strip metric-strip--five">
            <div><strong>{deltaIntelligence.summary.active_priority_count}</strong><span>Active</span></div>
            <div><strong>{deltaIntelligence.summary.highest_score ?? 0}</strong><span>Peak score</span></div>
            <div><strong>{correlations.filter((entry) => entry.state === 'NEW').length}</strong><span>New</span></div>
            <div><strong>{correlations.filter((entry) => entry.state === 'RESOLVED').length}</strong><span>Resolved</span></div>
            <div><strong>{paths.length}</strong><span>Changed paths</span></div>
          </div>
          <div className="delta-filters" aria-label="Delta intelligence filters">
            <label>Severity<select value={severity} onChange={(event) => setSeverity(event.target.value)}><option>ALL</option><option>HIGH</option><option>MEDIUM</option><option>LOW</option><option>INFO</option></select></label>
            <label>Structure<select value={structuralClass} onChange={(event) => setStructuralClass(event.target.value as typeof structuralClass)}><option>ALL</option>{[...new Set(structural.map((entry) => entry.structural_class))].sort().map((value) => <option key={value}>{value}</option>)}</select></label>
          </div>
          {deltaIntelligence.validation_findings.map((finding) => <p className="finding-text" key={finding}>{finding}</p>)}
          <div className="delta-priority-list" aria-label="Recommended review order">
            {priorities.length === 0 ? <p className="inspector-muted">No active priorities match these filters.</p> : priorities.map((entry) => (
              <article key={entry.id} style={{ '--delta-score': `${entry.score}%` } as React.CSSProperties}>
                <div className="delta-score"><strong>{entry.score}</strong><span>#{entry.rank}</span></div>
                <div><span className={`change-impact change-impact--${entry.severity.toLowerCase()}`}>{entry.severity}</span><strong>{entry.why_this_matters}</strong><p>{entry.structural_classes.join(' / ') || 'INTEGRITY FINDING'}</p><small>{entry.evidence_count} evidence references · {entry.confidence}</small><div className="delta-score-bar" aria-label={`Impact score ${entry.score} of 100`}><span /></div><details><summary>Score and evidence</summary><pre>{JSON.stringify(entry.score_breakdown, null, 2)}</pre>{entry.evidence_refs.map((reference) => <code key={reference}>{reference}</code>)}</details></div>
              </article>
            ))}
          </div>
          <div className="delta-timeline" aria-label="Finding timeline">
            {(['NEW', 'PERSISTENT', 'RESOLVED', 'NOT_COMPUTABLE'] as const).map((state) => <div key={state}><strong>{correlations.filter((entry) => entry.state === state).length}</strong><span>{state}</span></div>)}
          </div>
          {paths.map((path) => <details className="changed-path" key={path.id}><summary>{path.change}: {path.source_id} to {path.target_id}</summary><div className="change-values"><div><span>Before</span><pre>{path.prior_node_ids.join('\n')}</pre></div><div><span>After</span><pre>{path.current_node_ids.join('\n') || 'NOT_CONNECTED'}</pre></div></div></details>)}
        </section>
      )}

      <div className="change-generation" aria-label="Compared generations">
        <div><span>Prior</span><code title={effectiveDiff.prior_generation_id ?? undefined}>{shortHash(effectiveDiff.prior_generation_id)}</code></div>
        <span aria-hidden="true">-&gt;</span>
        <div><span>Current</span><code title={effectiveDiff.current_generation_id ?? undefined}>{shortHash(effectiveDiff.current_generation_id)}</code></div>
      </div>

      <div className="metric-strip metric-strip--five">
        <div><strong>{effectiveDiff.total_change_count}</strong><span>Changes</span></div>
        <div><strong>{effectiveDiff.not_computable_count ?? 0}</strong><span>Unknown</span></div>
        <div><strong>{(categoryCounts.TOPOLOGY_NODE ?? 0) + (categoryCounts.TOPOLOGY_EDGE ?? 0)}</strong><span>Topology</span></div>
        <div><strong>{(categoryCounts.OWNERSHIP ?? 0) + (categoryCounts.VALIDATOR_STATE ?? 0)}</strong><span>Assurance</span></div>
        <div><strong>{(categoryCounts.RECEIPT ?? 0) + (categoryCounts.PACKET ?? 0)}</strong><span>Evidence</span></div>
      </div>

      <div className="change-summary">
        <span>{effectiveDiff.status}</span>
        <p>{effectiveDiff.operator_summary}</p>
      </div>

      <div className="change-scope" aria-label="Comparison scope">
        <div><strong>Compared</strong><span>{scope.length > 0 ? scope.join(' / ') : 'LEGACY V0.2 SCOPE'}</span></div>
        <div><strong>Out of scope</strong><span>{outOfScope.join(' / ')}</span></div>
      </div>

      {effectiveDiff.entries.length === 0 ? (
        <div className="operator-empty" role="status">
          <strong>No changes observed</strong>
          <span>The supplied evidence-bound generations are semantically identical.</span>
        </div>
      ) : (
        groups.map(({ category, entries }) => (
          <section className="change-group" key={category} aria-labelledby={`change-${category}`}>
            <h2 id={`change-${category}`}>{category.replace(/_/g, ' ')}</h2>
            {entries.map((entry) => (
              <article key={entry.id}>
                <span className={`change-impact change-impact--${(entry.impact ?? 'NEUTRAL').toLowerCase()}`}>
                  {entry.impact ?? entry.severity}
                </span>
                <div>
                  <strong>{entry.operation} / {entry.entity_id ?? entry.surface}</strong>
                  <p>{entry.summary}</p>
                  <code>{entry.field_path || 'FIELD_PATH_NOT_COMPUTABLE'}</code>
                  <details>
                    <summary>Evidence values</summary>
                    <div className="change-values">
                      <div><span>Prior</span><pre>{formatValue(entry.prior_value)}</pre></div>
                      <div><span>Current</span><pre>{formatValue(entry.current_value)}</pre></div>
                    </div>
                  </details>
                </div>
              </article>
            ))}
          </section>
        ))
      )}
      {effectiveDiff.remaining_blockers.map((blocker) => <p className="finding-text" key={blocker}>{blocker}</p>)}
    </section>
  );
}
