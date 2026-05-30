import { useState, useCallback } from 'react';
import type { OperatorActionPacketsBundle, OperatorActionPacket } from '../types';

interface EvidenceChecklistPanelProps {
  packetsBundle: OperatorActionPacketsBundle | null;
}

function stripCheckboxPrefix(item: string): string {
  return item.replace(/^\[\s*[xX ]?\s*\]\s*/, '').trim();
}

export function EvidenceChecklistPanel({
  packetsBundle,
}: EvidenceChecklistPanelProps): JSX.Element {
  const packets = packetsBundle?.packets ?? [];
  const [selectedId, setSelectedId] = useState<string>(packets[0]?.packet_id ?? '');
  const [checked, setChecked] = useState<Set<number>>(new Set());

  const selectedPacket: OperatorActionPacket | null =
    packets.find((p) => p.packet_id === selectedId) ?? null;

  const handleSelect = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      setSelectedId(e.target.value);
      setChecked(new Set());
    },
    [],
  );

  const toggleItem = useCallback((idx: number) => {
    setChecked((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) {
        next.delete(idx);
      } else {
        next.add(idx);
      }
      return next;
    });
  }, []);

  const checklist = selectedPacket?.validation_checklist ?? [];
  const checkedCount = checked.size;
  const totalCount = checklist.length;

  return (
    <section
      className="ecl-panel"
      data-testid="evidence-checklist-panel"
      aria-label="Evidence Checklist Panel"
    >
      <div className="ecl-panel__header">
        <span className="ecl-panel__title">◈ EVIDENCE CHECKLIST</span>
        <span className="ecl-panel__notice">UI_ONLY · NON_AUTHORITATIVE</span>
      </div>

      {packets.length === 0 ? (
        <div className="ecl-panel__empty" data-testid="ecl-empty">
          NO PACKETS LOADED — FAIL CLOSED
        </div>
      ) : (
        <>
          <div className="ecl-panel__selector-row">
            <label className="ecl-label" htmlFor="ecl-packet-select">
              PACKET
            </label>
            <select
              id="ecl-packet-select"
              className="ecl-select"
              data-testid="ecl-packet-select"
              value={selectedId}
              onChange={handleSelect}
            >
              {packets.map((pkt) => (
                <option key={pkt.packet_id} value={pkt.packet_id}>
                  {pkt.action_title}
                </option>
              ))}
            </select>
          </div>

          {selectedPacket == null ? (
            <div className="ecl-panel__empty" data-testid="ecl-empty">
              NO PACKET SELECTED — FAIL CLOSED
            </div>
          ) : (
            <>
              <div className="ecl-panel__authority" data-testid="ecl-authority-locks">
                <span
                  className="ecl-lock ecl-lock--blocked"
                  data-testid="ecl-lock-execution"
                >
                  EXEC BLOCKED
                </span>
                <span
                  className="ecl-lock ecl-lock--blocked"
                  data-testid="ecl-lock-mutation"
                >
                  MUTATION BLOCKED
                </span>
                <span
                  className="ecl-lock ecl-lock--blocked"
                  data-testid="ecl-lock-promotion"
                >
                  PROMOTION BLOCKED
                </span>
              </div>

              {checklist.length === 0 ? (
                <div className="ecl-panel__empty" data-testid="ecl-no-checklist">
                  NO CHECKLIST — FAIL CLOSED
                </div>
              ) : (
                <div className="ecl-checklist" data-testid="ecl-checklist">
                  <div className="ecl-progress" data-testid="ecl-progress">
                    <span className="ecl-progress__label">REVIEWED</span>
                    <span className="ecl-progress__value">
                      {checkedCount} / {totalCount}
                    </span>
                    <span className="ecl-progress__notice">[UI_ONLY]</span>
                  </div>

                  <ul className="ecl-list">
                    {checklist.map((item, idx) => {
                      const isChecked = checked.has(idx);
                      return (
                        <li
                          key={idx}
                          className={`ecl-item${isChecked ? ' ecl-item--checked' : ''}`}
                          data-testid={`ecl-item-${idx}`}
                        >
                          <label className="ecl-item__label">
                            <input
                              type="checkbox"
                              className="ecl-item__checkbox"
                              data-testid={`ecl-checkbox-${idx}`}
                              checked={isChecked}
                              onChange={() => toggleItem(idx)}
                              aria-label={`Checklist item ${idx + 1}`}
                            />
                            <span className="ecl-item__text">
                              {stripCheckboxPrefix(item)}
                            </span>
                          </label>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}

              {selectedPacket.blocked_scopes.length > 0 && (
                <div
                  className="ecl-blocked-scopes"
                  data-testid="ecl-blocked-scopes"
                >
                  <div className="ecl-blocked-scopes__label">BLOCKED SCOPES</div>
                  <div className="ecl-blocked-scopes__tags">
                    {selectedPacket.blocked_scopes.map((s) => (
                      <span key={s} className="ecl-scope-tag">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedPacket.provenance_refs.length > 0 && (
                <div
                  className="ecl-provenance"
                  data-testid="ecl-provenance-refs"
                >
                  <div className="ecl-provenance__label">PROVENANCE REFS</div>
                  <ul className="ecl-provenance__list">
                    {selectedPacket.provenance_refs.map((ref) => (
                      <li key={ref} className="ecl-provenance__item">
                        {ref}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </>
      )}

      <div className="ecl-panel__footer">
        NO_EXECUTION · NO_RUNTIME_MUTATION · NO_BACKEND_WRITES · NO_PERSISTENCE · REVIEW_ONLY
      </div>
    </section>
  );
}
