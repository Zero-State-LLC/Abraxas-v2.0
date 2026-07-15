import type { OperatorPlatformProjection } from '../types';

export default function OperatorPlatformChangesView({ platform }: { platform: OperatorPlatformProjection }): JSX.Element {
  const section = platform.temporal_diff;
  const diff = section.payload;
  if (diff == null) return <section className="operator-view" aria-labelledby="changes-heading"><div className="view-heading-row"><h1 id="changes-heading">Changes</h1><span className="source-state source-state--not_computable">{section.status}</span></div><div className="operator-empty" role="status"><strong>Temporal diff not computable</strong><span>{section.not_computable_reason ?? 'Required evidence is unavailable.'}</span></div></section>;
  const groups = diff.entries.reduce<Record<string, typeof diff.entries>>((acc, entry) => { (acc[entry.operation] ??= []).push(entry); return acc; }, {});
  return (
    <section className="operator-view" aria-labelledby="changes-heading">
      <div className="view-heading-row"><div><span className="view-kicker">Generation delta</span><h1 id="changes-heading">Changes</h1></div><span className={`source-state source-state--${section.status.toLowerCase()}`}>{section.status}</span></div>
      {section.validation_findings.length > 0 && <div className="section-findings" role="status"><strong>Projection findings</strong>{section.validation_findings.map((finding) => <span key={finding}>{finding}</span>)}</div>}
      <div className="metric-strip metric-strip--five"><div><strong>{diff.total_change_count}</strong><span>Total</span></div><div><strong>{diff.topology_change_count}</strong><span>Topology</span></div><div><strong>{diff.lineage_shift_count}</strong><span>Lineage</span></div><div><strong>{diff.queue_delta_count}</strong><span>Queue</span></div><div><strong>{diff.transport_delta_count}</strong><span>Transport</span></div></div>
      <div className="change-summary"><span>{diff.status}</span><p>{diff.operator_summary}</p></div>
      {diff.entries.length === 0 ? <div className="operator-empty" role="status"><strong>No changes observed</strong><span>The current evidence-bound generation is stable.</span></div> : Object.entries(groups).map(([operation, entries]) => <section className="change-group" key={operation}><h2>{operation}</h2>{entries.map((entry) => <article key={entry.id}><span>{entry.severity}</span><div><strong>{entry.surface}</strong><p>{entry.summary}</p><code>{entry.field_path || 'FIELD_PATH_NOT_COMPUTABLE'}</code></div></article>)}</section>)}
      {diff.remaining_blockers.map((blocker) => <p className="finding-text" key={blocker}>{blocker}</p>)}
    </section>
  );
}
