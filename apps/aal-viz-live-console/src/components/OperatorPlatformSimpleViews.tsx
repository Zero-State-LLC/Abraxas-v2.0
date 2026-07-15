import { useState } from 'react';
import type { OperatorPlatformProjection } from '../types';

function SourceState({ state }: { state: string }): JSX.Element {
  return <span className={`source-state source-state--${state.toLowerCase()}`}>{state}</span>;
}

function EmptyState({ title, detail }: { title: string; detail: string }): JSX.Element {
  return <div className="operator-empty" role="status"><strong>{title}</strong><span>{detail}</span></div>;
}

function SectionFindings({ findings }: { findings: string[] }): JSX.Element | null {
  if (findings.length === 0) return null;
  return <div className="section-findings" role="status"><strong>Projection findings</strong>{findings.map((finding) => <span key={finding}>{finding}</span>)}</div>;
}

function ProductionView({ platform }: { platform: OperatorPlatformProjection }): JSX.Element {
  const section = platform.production_slice;
  const slice = section.payload;
  if (slice == null) {
    return <section className="operator-view" aria-labelledby="production-heading"><div className="view-heading-row"><h1 id="production-heading">Production slice</h1><SourceState state={section.status} /></div><EmptyState title="Production slice not computable" detail={section.not_computable_reason ?? 'Required evidence is unavailable.'} /></section>;
  }
  const stages = [
    { label: 'Entry', items: [slice.entrypoint] },
    { label: 'Orchestration', items: slice.orchestration },
    { label: 'Validators', items: slice.validators },
    { label: 'Execution', items: slice.execution_flow },
    { label: 'Artifacts', items: slice.artifacts },
    { label: 'Receipts', items: slice.receipts },
  ];
  return (
    <section className="operator-view" aria-labelledby="production-heading">
      <div className="view-heading-row"><div><span className="view-kicker">Observed runtime path</span><h1 id="production-heading">Production slice</h1></div><SourceState state={section.status} /></div>
      <SectionFindings findings={section.validation_findings} />
      <div className="slice-meta"><span>{slice.classification}</span><code>{slice.invocation}</code><span>{slice.external_calls ? 'EXTERNAL CALLS OBSERVED' : 'NO EXTERNAL CALLS'}</span></div>
      <div className="production-flow">{stages.map((stage, index) => <div className="production-stage" key={stage.label}><div className="stage-index">{String(index + 1).padStart(2, '0')}</div><div><h2>{stage.label}</h2>{stage.items.length === 0 ? <span>NOT_COMPUTABLE</span> : stage.items.map((item) => <code key={item}>{item}</code>)}</div></div>)}</div>
      <div className="finding-columns"><section><h2>Unresolved links</h2>{slice.unresolved_links.map((item) => <p key={item}>{item}</p>)}</section><section><h2>Excluded surfaces</h2>{slice.excluded_surfaces.map((item) => <code key={item}>{item}</code>)}</section></div>
    </section>
  );
}

function EvidenceView({ platform }: { platform: OperatorPlatformProjection }): JSX.Element {
  const [query, setQuery] = useState('');
  const normalized = query.trim().toLowerCase();
  const section = platform.evidence_index;
  const evidence = (section.payload?.records ?? []).filter((record) => normalized.length === 0 || record.id.toLowerCase().includes(normalized) || record.source_path.toLowerCase().includes(normalized) || record.status.toLowerCase().includes(normalized));
  return (
    <section className="operator-view" aria-labelledby="evidence-heading">
      <div className="view-heading-row"><div><span className="view-kicker">Receipts and proofs</span><h1 id="evidence-heading">Evidence explorer</h1></div><SourceState state={section.status} /></div>
      <SectionFindings findings={section.validation_findings} />
      <label className="search-field"><span>Search evidence</span><input value={query} onChange={(event) => setQuery(event.target.value)} /></label>
      <div className="evidence-list">{evidence.map((record) => <article key={record.id} className="evidence-record"><header><div><span>{record.status}</span><h2>{record.id}</h2></div><SourceState state={record.source_status} /></header><code>{record.source_path}</code><dl><dt>Canonical hash</dt><dd>{record.canonical_hash ?? 'NOT_COMPUTABLE'}</dd><dt>Schema</dt><dd>{record.schemas.join(', ') || 'NOT_COMPUTABLE'}</dd></dl>{record.fail_closed_reason != null && <p className="finding-text">{record.fail_closed_reason}</p>}{record.inputs.length > 0 && <details><summary>Inputs ({record.inputs.length})</summary>{record.inputs.map((item) => <code key={item}>{item}</code>)}</details>}{record.links.length > 0 && <details><summary>Links and blockers ({record.links.length})</summary>{record.links.map((item) => <p key={item}>{item}</p>)}</details>}</article>)}</div>
      {evidence.length === 0 && <EmptyState title="No matching evidence" detail={section.not_computable_reason ?? 'Try a packet ID, status, or source path.'} />}
    </section>
  );
}

export function OperatorPlatformSimpleViewPanel({ view, platform }: { view: 'production' | 'evidence'; platform: OperatorPlatformProjection }): JSX.Element {
  return view === 'production' ? <ProductionView platform={platform} /> : <EvidenceView platform={platform} />;
}
