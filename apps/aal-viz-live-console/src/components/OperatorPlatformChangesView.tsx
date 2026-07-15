import type {
  OperatorPlatformProjection,
  OperatorPlatformTemporalCategory,
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
}: {
  platform: OperatorPlatformProjection;
}): JSX.Element {
  const section = platform.temporal_diff;
  const diff = section.payload;
  if (diff == null) {
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

  const categoryCounts = diff.category_counts ?? ({} as typeof diff.category_counts);
  const scope = diff.comparison_scope ?? [];
  const outOfScope = diff.out_of_scope ?? ['LINEAGE', 'QUEUE', 'TRANSPORT'];
  const groups = CATEGORY_ORDER.map((category) => ({
    category,
    entries: diff.entries.filter((entry) => entry.category === category),
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

      <div className="change-generation" aria-label="Compared generations">
        <div><span>Prior</span><code title={diff.prior_generation_id ?? undefined}>{shortHash(diff.prior_generation_id)}</code></div>
        <span aria-hidden="true">-&gt;</span>
        <div><span>Current</span><code title={diff.current_generation_id ?? undefined}>{shortHash(diff.current_generation_id)}</code></div>
      </div>

      <div className="metric-strip metric-strip--five">
        <div><strong>{diff.total_change_count}</strong><span>Changes</span></div>
        <div><strong>{diff.not_computable_count ?? 0}</strong><span>Unknown</span></div>
        <div><strong>{(categoryCounts.TOPOLOGY_NODE ?? 0) + (categoryCounts.TOPOLOGY_EDGE ?? 0)}</strong><span>Topology</span></div>
        <div><strong>{(categoryCounts.OWNERSHIP ?? 0) + (categoryCounts.VALIDATOR_STATE ?? 0)}</strong><span>Assurance</span></div>
        <div><strong>{(categoryCounts.RECEIPT ?? 0) + (categoryCounts.PACKET ?? 0)}</strong><span>Evidence</span></div>
      </div>

      <div className="change-summary">
        <span>{diff.status}</span>
        <p>{diff.operator_summary}</p>
      </div>

      <div className="change-scope" aria-label="Comparison scope">
        <div><strong>Compared</strong><span>{scope.length > 0 ? scope.join(' / ') : 'LEGACY V0.2 SCOPE'}</span></div>
        <div><strong>Out of scope</strong><span>{outOfScope.join(' / ')}</span></div>
      </div>

      {diff.entries.length === 0 ? (
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
      {diff.remaining_blockers.map((blocker) => <p className="finding-text" key={blocker}>{blocker}</p>)}
    </section>
  );
}
