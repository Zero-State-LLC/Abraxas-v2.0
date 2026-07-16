import { useMemo, useState } from 'react';
import type {
  RouteReceiptAdvisoryAlert,
  RouteReceiptAdvisoryAlertsProjection,
  RouteReceiptAlertTrigger,
  YggdrasilTopologyDeltaIntelligenceProjection,
} from '../types';

type AlertGroup = 'active' | 'resolved' | 'suppressed' | 'not_computable';

const GROUPS: Array<{ id: AlertGroup; label: string }> = [
  { id: 'active', label: 'Active' },
  { id: 'resolved', label: 'Resolved' },
  { id: 'suppressed', label: 'Suppressed' },
  { id: 'not_computable', label: 'Not computable' },
];

function shortHash(value: string | null): string {
  return value == null ? 'NOT_COMPUTABLE' : value.slice(0, 12);
}

function entityIds(
  alert: RouteReceiptAdvisoryAlert,
  delta?: YggdrasilTopologyDeltaIntelligenceProjection,
): string[] {
  const result = new Set(alert.affected_surface_ids);
  if (alert.source_ref.category === 'INTEGRITY_FINDING') {
    const correlation = delta?.sections.finding_correlation.entries?.find(
      (entry) => entry.id === alert.source_ref.entity_id,
    );
    if (correlation?.entity_ref != null) result.add(correlation.entity_ref.entity_id);
  } else {
    const structural = delta?.sections.structural_deltas.entries?.find(
      (entry) => entry.id === alert.source_ref.entity_id,
    );
    structural?.entity_refs.forEach((reference) => result.add(reference.entity_id));
  }
  return [...result].sort();
}

function groupEntries(
  projection: RouteReceiptAdvisoryAlertsProjection,
  group: AlertGroup,
): RouteReceiptAdvisoryAlert[] {
  const section = group === 'active'
    ? projection.sections.active_alerts
    : group === 'resolved'
      ? projection.sections.resolved_alerts
      : group === 'suppressed'
        ? projection.sections.suppressed_candidates
        : projection.sections.not_computable;
  return [...(section.entries ?? [])].sort(
    (left, right) => right.score - left.score || left.alert_id.localeCompare(right.alert_id),
  );
}

export default function OperatorPlatformAlertsView({
  alerts,
  deltaIntelligence,
  onOpenInYggdrasil,
}: {
  alerts?: RouteReceiptAdvisoryAlertsProjection;
  deltaIntelligence?: YggdrasilTopologyDeltaIntelligenceProjection;
  onOpenInYggdrasil: (alertId: string, entityId: string) => void;
}): JSX.Element {
  const [group, setGroup] = useState<AlertGroup>('active');
  const [severity, setSeverity] = useState('ALL');
  const [trigger, setTrigger] = useState<'ALL' | RouteReceiptAlertTrigger>('ALL');
  const [acknowledgement, setAcknowledgement] = useState('ALL');
  const availableTriggers = useMemo(() => {
    if (alerts == null) return [];
    return [...new Set(GROUPS.flatMap(({ id }) => groupEntries(alerts, id)).flatMap((entry) => entry.trigger_types))].sort();
  }, [alerts]);
  const filtered = useMemo(() => {
    if (alerts == null) return [];
    return groupEntries(alerts, group).filter((entry) =>
      (severity === 'ALL' || entry.severity === severity) &&
      (trigger === 'ALL' || entry.trigger_types.includes(trigger)) &&
      (acknowledgement === 'ALL' ||
        acknowledgement === 'ACKNOWLEDGED' && entry.acknowledged === true ||
        acknowledgement === 'UNACKNOWLEDGED' && entry.acknowledged !== true),
    );
  }, [acknowledgement, alerts, group, severity, trigger]);

  if (alerts == null) {
    return (
      <section className="operator-view" aria-labelledby="alerts-heading">
        <div className="view-heading-row"><div><span className="view-kicker">Advisory receipts</span><h1 id="alerts-heading">Alerts</h1></div></div>
        <div className="operator-empty" role="status">
          <strong>Alert projection unavailable</strong>
          <span>Topology and Changes remain available without advisory receipts.</span>
        </div>
      </section>
    );
  }

  return (
    <section className="operator-view alerts-view" aria-labelledby="alerts-heading">
      <div className="view-heading-row">
        <div><span className="view-kicker">Projection-only ROUTE_RECEIPT</span><h1 id="alerts-heading">Alerts</h1></div>
        <span className={`source-state source-state--${alerts.status.toLowerCase()}`}>{alerts.status}</span>
      </div>
      <div className="change-generation" aria-label="Alert generation binding">
        <div><span>Delta generation</span><code title={alerts.generation.delta_generation_id}>{shortHash(alerts.generation.delta_generation_id)}</code></div>
        <div><span>Alert generation</span><code title={alerts.generation.alert_generation_id}>{shortHash(alerts.generation.alert_generation_id)}</code></div>
        <div><span>Prior alerts</span><code>{shortHash(alerts.generation.prior_alert_generation_id)}</code></div>
      </div>
      <div className="metric-strip metric-strip--five">
        <div><strong>{alerts.summary.active_count}</strong><span>Active</span></div>
        <div><strong>{alerts.summary.resolved_count}</strong><span>Resolved</span></div>
        <div><strong>{alerts.summary.suppressed_count}</strong><span>Suppressed</span></div>
        <div><strong>{alerts.summary.not_computable_count}</strong><span>Unknown</span></div>
        <div><strong>{alerts.summary.published_receipt_count}</strong><span>Published receipts</span></div>
      </div>
      {alerts.validation_findings.length > 0 && (
        <div className="section-findings" role="status">
          <strong>Projection findings</strong>
          {alerts.validation_findings.map((finding) => <span key={finding}>{finding}</span>)}
        </div>
      )}
      <div className="alert-group-tabs" role="tablist" aria-label="Alert groups">
        {GROUPS.map((item) => (
          <button key={item.id} type="button" role="tab" aria-selected={group === item.id} onClick={() => setGroup(item.id)}>
            {item.label}
          </button>
        ))}
      </div>
      <div className="alert-filters" aria-label="Alert filters">
        <label>Severity<select value={severity} onChange={(event) => setSeverity(event.target.value)}><option>ALL</option><option>HIGH</option><option>MEDIUM</option><option>LOW</option><option>INFO</option><option>NOT_COMPUTABLE</option></select></label>
        <label>Trigger<select value={trigger} onChange={(event) => setTrigger(event.target.value as typeof trigger)}><option>ALL</option>{availableTriggers.map((value) => <option key={value}>{value}</option>)}</select></label>
        <label>Acknowledgement<select value={acknowledgement} onChange={(event) => setAcknowledgement(event.target.value)}><option>ALL</option><option>ACKNOWLEDGED</option><option>UNACKNOWLEDGED</option></select></label>
      </div>
      <div className="alert-list" aria-live="polite">
        {filtered.length === 0 ? (
          <div className="operator-empty" role="status"><strong>No matching alerts</strong><span>This group has no records under the selected filters.</span></div>
        ) : filtered.map((alert, index) => {
          const affected = entityIds(alert, deltaIntelligence);
          return (
            <article className={`alert-record alert-record--${alert.severity.toLowerCase().replace('_', '-')}`} key={alert.receipt_id}>
              <div className="alert-rank"><strong>{alert.score}</strong><span>#{index + 1}</span></div>
              <div className="alert-record__body">
                <header><span>{alert.event_type}</span><strong>{alert.severity} / {alert.score_tier}</strong></header>
                <h2>{alert.why_this_fired}</h2>
                <p>{alert.trigger_types.join(' / ') || alert.suppression_reasons.join(' / ') || 'NOT_COMPUTABLE'}</p>
                <div className="alert-meta"><span>{alert.confidence}</span><span>{alert.receipt_disposition}</span><span>{alert.acknowledged === true ? 'ACKNOWLEDGED' : alert.acknowledged === false ? 'UNACKNOWLEDGED' : 'ACK_NOT_COMPUTABLE'}</span><span>{alert.delivery_state}</span></div>
                {affected.length > 0 && <button type="button" onClick={() => onOpenInYggdrasil(alert.alert_id, affected[0])}>Open in YGGDRASIL</button>}
                <details><summary>Why this fired</summary><dl><dt>Alert</dt><dd>{alert.alert_id}</dd><dt>Receipt</dt><dd>{alert.receipt_id}</dd><dt>Priority</dt><dd>{alert.priority_id ?? 'NOT_COMPUTABLE'}</dd><dt>Persistence</dt><dd>{alert.persistence_seconds_lower_bound ?? 'NOT_COMPUTABLE'}</dd></dl>{affected.map((id) => <code key={id}>{id}</code>)}{alert.evidence_refs.map((reference) => <code key={reference}>{reference}</code>)}</details>
              </div>
            </article>
          );
        })}
      </div>
      <footer className="view-footer">{filtered.length} records · advisory only · no delivery or acknowledgement writeback</footer>
    </section>
  );
}
