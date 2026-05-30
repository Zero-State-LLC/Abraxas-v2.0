import { useState, useCallback } from 'react';
import type {
  OperatorActionPacketsBundle,
  DecisionOutcomeStatus,
  DecisionOutcomeAttribution,
} from '../types';

interface DecisionAttributionPanelProps {
  packetsBundle: OperatorActionPacketsBundle | null;
}

const OUTCOME_STATUSES: DecisionOutcomeStatus[] = [
  'UNKNOWN',
  'MERGED',
  'FAILED',
  'HELD',
  'SUPERSEDED',
];

const OUTCOME_COLORS: Record<DecisionOutcomeStatus, string> = {
  UNKNOWN: 'var(--clr-text-muted)',
  MERGED: 'var(--clr-emerald)',
  FAILED: 'var(--clr-red)',
  HELD: 'var(--clr-gold)',
  SUPERSEDED: 'var(--clr-violet)',
};

function makeAttribution(packet_id: string): DecisionOutcomeAttribution {
  return {
    packet_id,
    outcome_status: 'UNKNOWN',
    copied_at: null,
    manual_result: '',
    linked_pr: '',
    _ui_only: true,
    _non_authoritative: true,
  };
}

export function DecisionAttributionPanel({
  packetsBundle,
}: DecisionAttributionPanelProps): JSX.Element {
  const packets = packetsBundle?.packets ?? [];
  const [selectedId, setSelectedId] = useState<string>(packets[0]?.packet_id ?? '');
  const [attributions, setAttributions] = useState<
    Map<string, DecisionOutcomeAttribution>
  >(() => {
    const m = new Map<string, DecisionOutcomeAttribution>();
    for (const pkt of packets) {
      m.set(pkt.packet_id, makeAttribution(pkt.packet_id));
    }
    return m;
  });

  const attr = attributions.get(selectedId) ?? null;

  const patch = useCallback(
    (id: string, updates: Partial<DecisionOutcomeAttribution>) => {
      setAttributions((prev) => {
        const next = new Map(prev);
        const existing = next.get(id) ?? makeAttribution(id);
        next.set(id, { ...existing, ...updates });
        return next;
      });
    },
    [],
  );

  const handleSelectPacket = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      setSelectedId(e.target.value);
    },
    [],
  );

  return (
    <section
      className="dap-panel"
      data-testid="decision-attribution-panel"
      aria-label="Decision Attribution Panel"
    >
      <div className="dap-panel__header">
        <span className="dap-panel__title">◈ DECISION ATTRIBUTION</span>
        <span className="dap-panel__notice">UI_ONLY · NON_AUTHORITATIVE</span>
      </div>

      <div className="dap-panel__warning" data-testid="dap-warning">
        ⚠ UI_ONLY — DOES NOT UPDATE REPO, NOTION, OR ARTIFACTS
      </div>

      {packets.length === 0 ? (
        <div className="dap-panel__empty" data-testid="dap-empty">
          NO PACKETS LOADED — FAIL CLOSED
        </div>
      ) : (
        <>
          <div className="dap-selector-row">
            <label className="dap-label" htmlFor="dap-packet-select">
              PACKET
            </label>
            <select
              id="dap-packet-select"
              className="dap-select"
              data-testid="dap-packet-select"
              value={selectedId}
              onChange={handleSelectPacket}
            >
              {packets.map((pkt) => (
                <option key={pkt.packet_id} value={pkt.packet_id}>
                  {pkt.action_title}
                </option>
              ))}
            </select>
          </div>

          {attr == null ? (
            <div className="dap-panel__empty" data-testid="dap-empty">
              NO PACKET SELECTED — FAIL CLOSED
            </div>
          ) : (
            <div className="dap-fields">
              <div className="dap-field-row">
                <span className="dap-field-label">PACKET ID</span>
                <span
                  className="dap-field-value dap-field-value--mono"
                  data-testid="dap-packet-id"
                >
                  {attr.packet_id}
                </span>
              </div>

              <div className="dap-field-row">
                <span className="dap-field-label">OUTCOME STATUS [UI_ONLY]</span>
                <div
                  className="dap-outcome-buttons"
                  data-testid="dap-outcome-buttons"
                >
                  {OUTCOME_STATUSES.map((status) => (
                    <button
                      key={status}
                      className={`dap-outcome-btn${attr.outcome_status === status ? ' dap-outcome-btn--active' : ''}`}
                      data-testid={`dap-outcome-btn-${status}`}
                      style={
                        attr.outcome_status === status
                          ? { color: OUTCOME_COLORS[status], borderColor: OUTCOME_COLORS[status] }
                          : undefined
                      }
                      onClick={() =>
                        patch(attr.packet_id, { outcome_status: status })
                      }
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </div>

              <div className="dap-field-row">
                <label className="dap-field-label" htmlFor="dap-linked-pr">
                  LINKED PR [UI_ONLY]
                </label>
                <input
                  id="dap-linked-pr"
                  type="text"
                  className="dap-text-input"
                  data-testid="dap-linked-pr"
                  value={attr.linked_pr}
                  placeholder="e.g. #379"
                  onChange={(e) =>
                    patch(attr.packet_id, { linked_pr: e.target.value })
                  }
                />
              </div>

              <div className="dap-field-row dap-field-row--col">
                <label className="dap-field-label" htmlFor="dap-manual-result">
                  MANUAL RESULT NOTE [UI_ONLY]
                </label>
                <textarea
                  id="dap-manual-result"
                  className="dap-textarea"
                  data-testid="dap-manual-result"
                  value={attr.manual_result}
                  placeholder="Enter any operator result notes here…"
                  rows={3}
                  onChange={(e) =>
                    patch(attr.packet_id, { manual_result: e.target.value })
                  }
                />
              </div>

              <div
                className="dap-current-summary"
                data-testid="dap-current-summary"
              >
                <span className="dap-summary-label">CURRENT ATTRIBUTION:</span>
                <span
                  className="dap-summary-status"
                  style={{ color: OUTCOME_COLORS[attr.outcome_status] }}
                  data-testid="dap-current-outcome"
                >
                  {attr.outcome_status}
                </span>
                {attr.linked_pr && (
                  <span className="dap-summary-pr" data-testid="dap-summary-pr">
                    PR: {attr.linked_pr}
                  </span>
                )}
              </div>
            </div>
          )}
        </>
      )}

      <div className="dap-panel__footer">
        NO_EXECUTION · NO_RUNTIME_MUTATION · NO_BACKEND_WRITES · NO_PERSISTENCE · REVIEW_ONLY
      </div>
    </section>
  );
}
