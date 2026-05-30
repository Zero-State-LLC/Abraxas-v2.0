import { useMemo } from 'react';
import type { OperatorActionPacketsBundle } from '../types';

interface WorkflowAnalyticsPanelProps {
  packetsBundle: OperatorActionPacketsBundle | null;
}

interface WorkflowAnalytics {
  total_packets: number;
  copy_prompt_count: number;
  copy_checklist_count: number;
  review_required_count: number;
  blocked_packet_count: number;
  packets_with_validation_checklist_count: number;
  packets_with_blocked_scopes_count: number;
  total_validation_checklist_items: number;
  total_blocked_scope_refs: number;
  execution_allowed_count: number;
  runtime_mutation_allowed_count: number;
  promotion_allowed_count: number;
  blocked_scope_tally: Map<string, number>;
}

function computeAnalytics(bundle: OperatorActionPacketsBundle): WorkflowAnalytics {
  const tally = new Map<string, number>();
  let copy_prompt_count = 0;
  let copy_checklist_count = 0;
  let review_required_count = 0;
  let blocked_packet_count = 0;
  let packets_with_validation_checklist_count = 0;
  let packets_with_blocked_scopes_count = 0;
  let total_validation_checklist_items = 0;
  let total_blocked_scope_refs = 0;
  let execution_allowed_count = 0;
  let runtime_mutation_allowed_count = 0;
  let promotion_allowed_count = 0;

  for (const pkt of bundle.packets) {
    if (pkt.action_type === 'COPY_PROMPT') copy_prompt_count++;
    else if (pkt.action_type === 'COPY_CHECKLIST') copy_checklist_count++;
    else if (pkt.action_type === 'REVIEW_REQUIRED') review_required_count++;

    if (!pkt.allowed) blocked_packet_count++;

    if (pkt.validation_checklist.length > 0) {
      packets_with_validation_checklist_count++;
      total_validation_checklist_items += pkt.validation_checklist.length;
    }

    if (pkt.blocked_scopes.length > 0) {
      packets_with_blocked_scopes_count++;
      total_blocked_scope_refs += pkt.blocked_scopes.length;
      for (const scope of pkt.blocked_scopes) {
        tally.set(scope, (tally.get(scope) ?? 0) + 1);
      }
    }

    if ((pkt.execution_allowed as unknown as boolean) === true) execution_allowed_count++;
    if ((pkt.runtime_mutation_allowed as unknown as boolean) === true) runtime_mutation_allowed_count++;
    if ((pkt.promotion_allowed as unknown as boolean) === true) promotion_allowed_count++;
  }

  return {
    total_packets: bundle.packets.length,
    copy_prompt_count,
    copy_checklist_count,
    review_required_count,
    blocked_packet_count,
    packets_with_validation_checklist_count,
    packets_with_blocked_scopes_count,
    total_validation_checklist_items,
    total_blocked_scope_refs,
    execution_allowed_count,
    runtime_mutation_allowed_count,
    promotion_allowed_count,
    blocked_scope_tally: tally,
  };
}

function DistributionBar({
  label,
  count,
  total,
  color,
  testId,
}: {
  label: string;
  count: number;
  total: number;
  color: string;
  testId: string;
}) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div className="wap-dist-row" data-testid={testId}>
      <span className="wap-dist-label">{label}</span>
      <div className="wap-dist-bar-wrap">
        <div
          className="wap-dist-bar"
          style={{ width: `${pct}%`, background: color }}
          data-testid={`${testId}-bar`}
        />
      </div>
      <span className="wap-dist-count">{count}</span>
    </div>
  );
}

export function WorkflowAnalyticsPanel({
  packetsBundle,
}: WorkflowAnalyticsPanelProps): JSX.Element {
  const analytics = useMemo(
    () => (packetsBundle ? computeAnalytics(packetsBundle) : null),
    [packetsBundle],
  );

  const authorityClean =
    analytics != null &&
    analytics.execution_allowed_count === 0 &&
    analytics.runtime_mutation_allowed_count === 0 &&
    analytics.promotion_allowed_count === 0;

  const authorityViolation = analytics != null && !authorityClean;

  return (
    <section
      className="wap-panel"
      data-testid="workflow-analytics-panel"
      aria-label="Workflow Analytics Panel"
    >
      <div className="wap-panel__header">
        <span className="wap-panel__title">◈ WORKFLOW ANALYTICS</span>
        <span className="wap-panel__notice">READ_ONLY · DISPLAY_ONLY</span>
      </div>

      {analytics == null ? (
        <div className="wap-panel__empty" data-testid="wap-empty">
          NO PACKETS LOADED — FAIL CLOSED
        </div>
      ) : (
        <>
          {authorityViolation && (
            <div className="wap-authority-violation" data-testid="wap-authority-violation">
              ⊘ FAIL_CLOSED — AUTHORITY_VIOLATION_DETECTED
            </div>
          )}

          {/* ── AGGREGATE METRICS ── */}
          <div className="wap-section" data-testid="wap-metrics">
            <div className="wap-section-label">AGGREGATE METRICS</div>
            <div className="wap-metric-grid">
              {[
                ['TOTAL PACKETS', analytics.total_packets, 'wap-metric-total'],
                ['COPY PROMPT', analytics.copy_prompt_count, 'wap-metric-copy-prompt'],
                ['COPY CHECKLIST', analytics.copy_checklist_count, 'wap-metric-copy-checklist'],
                ['REVIEW REQUIRED', analytics.review_required_count, 'wap-metric-review-required'],
                ['BLOCKED PACKETS', analytics.blocked_packet_count, 'wap-metric-blocked'],
                ['W/ CHECKLIST', analytics.packets_with_validation_checklist_count, 'wap-metric-with-checklist'],
                ['W/ BLOCKED SCOPES', analytics.packets_with_blocked_scopes_count, 'wap-metric-with-blocked-scopes'],
                ['TOTAL CHECKLIST ITEMS', analytics.total_validation_checklist_items, 'wap-metric-total-checklist-items'],
                ['TOTAL SCOPE REFS', analytics.total_blocked_scope_refs, 'wap-metric-total-scope-refs'],
              ].map(([label, value, testId]) => (
                <div key={testId as string} className="wap-metric-cell" data-testid={testId as string}>
                  <span className="wap-metric-value">{value as number}</span>
                  <span className="wap-metric-label">{label as string}</span>
                </div>
              ))}
            </div>
          </div>

          {/* ── TYPE DISTRIBUTION ── */}
          <div className="wap-section" data-testid="wap-type-distribution">
            <div className="wap-section-label">PACKET TYPE DISTRIBUTION</div>
            <div className="wap-dist-list">
              <DistributionBar
                label="COPY_PROMPT"
                count={analytics.copy_prompt_count}
                total={analytics.total_packets}
                color="var(--clr-violet)"
                testId="wap-dist-copy-prompt"
              />
              <DistributionBar
                label="COPY_CHECKLIST"
                count={analytics.copy_checklist_count}
                total={analytics.total_packets}
                color="var(--clr-cyan)"
                testId="wap-dist-copy-checklist"
              />
              <DistributionBar
                label="REVIEW_REQUIRED"
                count={analytics.review_required_count}
                total={analytics.total_packets}
                color="var(--clr-gold)"
                testId="wap-dist-review-required"
              />
            </div>
          </div>

          {/* ── BLOCKED SCOPE SUMMARY ── */}
          <div className="wap-section" data-testid="wap-blocked-scopes">
            <div className="wap-section-label">BLOCKED SCOPE SUMMARY</div>
            {analytics.blocked_scope_tally.size === 0 ? (
              <div className="wap-no-scopes" data-testid="wap-no-scopes">
                No blocked scopes reported by packets.
              </div>
            ) : (
              <ul className="wap-scope-list">
                {Array.from(analytics.blocked_scope_tally.entries())
                  .sort(([, a], [, b]) => b - a)
                  .map(([scope, count]) => (
                    <li key={scope} className="wap-scope-row" data-testid={`wap-scope-${scope}`}>
                      <span className="wap-scope-name">{scope}</span>
                      <span className="wap-scope-count">{count}</span>
                    </li>
                  ))}
              </ul>
            )}
          </div>

          {/* ── AUTHORITY HEALTH ── */}
          <div className="wap-section" data-testid="wap-authority-health">
            <div className="wap-section-label">AUTHORITY HEALTH</div>
            <div
              className={`wap-authority-status${authorityClean ? ' wap-authority-status--clean' : ' wap-authority-status--violation'}`}
              data-testid="wap-authority-status"
            >
              {authorityClean ? '✓ AUTHORITY_CLEAN' : '⊘ FAIL_CLOSED'}
            </div>
            <div className="wap-authority-checks">
              <div className="wap-authority-row" data-testid="wap-auth-execution">
                <span className="wap-authority-field">execution_allowed_count</span>
                <span
                  className={`wap-authority-val${analytics.execution_allowed_count === 0 ? ' wap-authority-val--ok' : ' wap-authority-val--bad'}`}
                >
                  {analytics.execution_allowed_count}
                  {analytics.execution_allowed_count === 0 ? ' ✓' : ' ⊘ VIOLATION'}
                </span>
              </div>
              <div className="wap-authority-row" data-testid="wap-auth-mutation">
                <span className="wap-authority-field">runtime_mutation_allowed_count</span>
                <span
                  className={`wap-authority-val${analytics.runtime_mutation_allowed_count === 0 ? ' wap-authority-val--ok' : ' wap-authority-val--bad'}`}
                >
                  {analytics.runtime_mutation_allowed_count}
                  {analytics.runtime_mutation_allowed_count === 0 ? ' ✓' : ' ⊘ VIOLATION'}
                </span>
              </div>
              <div className="wap-authority-row" data-testid="wap-auth-promotion">
                <span className="wap-authority-field">promotion_allowed_count</span>
                <span
                  className={`wap-authority-val${analytics.promotion_allowed_count === 0 ? ' wap-authority-val--ok' : ' wap-authority-val--bad'}`}
                >
                  {analytics.promotion_allowed_count}
                  {analytics.promotion_allowed_count === 0 ? ' ✓' : ' ⊘ VIOLATION'}
                </span>
              </div>
            </div>
          </div>
        </>
      )}

      <div className="wap-panel__footer">
        READ_ONLY · DISPLAY_ONLY · DERIVED_FROM_LOADED_PACKETS · NO_BACKEND_WRITES · NO_PERSISTENCE
      </div>
    </section>
  );
}
