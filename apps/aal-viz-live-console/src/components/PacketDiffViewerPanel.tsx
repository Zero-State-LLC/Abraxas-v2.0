import { useState } from 'react';
import type { OperatorActionPacket, OperatorActionPacketsBundle } from '../types';

interface PacketDiffViewerPanelProps {
  packetsBundle: OperatorActionPacketsBundle | null;
}

type DiffStatus = 'SAME' | 'DIFFERENT' | 'MISSING_LEFT' | 'MISSING_RIGHT';

interface DiffRow {
  field: string;
  left: string;
  right: string;
  status: DiffStatus;
}

function simpleChecksum(s: string): string {
  let acc = 0;
  for (let i = 0; i < s.length; i++) {
    acc = (acc + s.charCodeAt(i)) & 0xffff;
  }
  return acc.toString(16).padStart(4, '0').toUpperCase();
}

function diffStatus(a: string, b: string, missingLeft?: boolean, missingRight?: boolean): DiffStatus {
  if (missingLeft) return 'MISSING_LEFT';
  if (missingRight) return 'MISSING_RIGHT';
  return a === b ? 'SAME' : 'DIFFERENT';
}

function computeDiff(a: OperatorActionPacket, b: OperatorActionPacket): DiffRow[] {
  const rows: DiffRow[] = [];

  const addRow = (field: string, aVal: string, bVal: string) => {
    rows.push({ field, left: aVal, right: bVal, status: diffStatus(aVal, bVal) });
  };

  addRow('packet_id', a.packet_id, b.packet_id);
  addRow('action_type', a.action_type, b.action_type);
  addRow(
    'recommended_next_step',
    a.recommended_next_step.slice(0, 60) + (a.recommended_next_step.length > 60 ? '…' : ''),
    b.recommended_next_step.slice(0, 60) + (b.recommended_next_step.length > 60 ? '…' : ''),
  );
  addRow('execution_allowed', String(a.execution_allowed), String(b.execution_allowed));
  addRow('runtime_mutation_allowed', String(a.runtime_mutation_allowed), String(b.runtime_mutation_allowed));
  addRow('promotion_allowed', String(a.promotion_allowed), String(b.promotion_allowed));
  addRow(
    'blocked_scopes',
    a.blocked_scopes.join(', ') || '(none)',
    b.blocked_scopes.join(', ') || '(none)',
  );
  addRow(
    'validation_checklist_count',
    String(a.validation_checklist.length),
    String(b.validation_checklist.length),
  );
  addRow('provenance_ref_count', String(a.provenance_refs.length), String(b.provenance_refs.length));
  addRow(
    'prompt_body_length',
    String(a.prompt_body.length),
    String(b.prompt_body.length),
  );
  addRow(
    'prompt_body_checksum',
    simpleChecksum(a.prompt_body),
    simpleChecksum(b.prompt_body),
  );

  return rows;
}

const STATUS_STYLE: Record<DiffStatus, { color: string; label: string }> = {
  SAME: { color: 'var(--clr-emerald)', label: '=' },
  DIFFERENT: { color: 'var(--clr-gold)', label: '≠' },
  MISSING_LEFT: { color: 'var(--clr-red)', label: '←?' },
  MISSING_RIGHT: { color: 'var(--clr-red)', label: '?→' },
};

export function PacketDiffViewerPanel({
  packetsBundle,
}: PacketDiffViewerPanelProps): JSX.Element {
  const packets = packetsBundle?.packets ?? [];
  const [leftId, setLeftId] = useState<string>(packets[0]?.packet_id ?? '');
  const [rightId, setRightId] = useState<string>(packets[1]?.packet_id ?? packets[0]?.packet_id ?? '');

  const leftPacket = packets.find((p) => p.packet_id === leftId) ?? null;
  const rightPacket = packets.find((p) => p.packet_id === rightId) ?? null;
  const samePacket = leftId !== '' && leftId === rightId;

  const diffRows =
    leftPacket && rightPacket && !samePacket ? computeDiff(leftPacket, rightPacket) : null;

  const authorityClean =
    leftPacket &&
    rightPacket &&
    (leftPacket.execution_allowed as unknown as boolean) !== true &&
    (rightPacket.execution_allowed as unknown as boolean) !== true &&
    (leftPacket.runtime_mutation_allowed as unknown as boolean) !== true &&
    (rightPacket.runtime_mutation_allowed as unknown as boolean) !== true &&
    (leftPacket.promotion_allowed as unknown as boolean) !== true &&
    (rightPacket.promotion_allowed as unknown as boolean) !== true;

  const authorityViolation = leftPacket && rightPacket && !authorityClean;

  return (
    <section
      className="pdv-panel"
      data-testid="packet-diff-viewer-panel"
      aria-label="Packet Diff Viewer Panel"
    >
      <div className="pdv-panel__header">
        <span className="pdv-panel__title">◈ PACKET DIFF VIEWER</span>
        <span className="pdv-panel__notice">READ_ONLY · DISPLAY_ONLY</span>
      </div>

      {packets.length === 0 ? (
        <div className="pdv-panel__empty" data-testid="pdv-empty">
          NO PACKETS LOADED — FAIL CLOSED
        </div>
      ) : (
        <>
          {authorityViolation && (
            <div className="pdv-authority-violation" data-testid="pdv-authority-violation">
              ⊘ FAIL_CLOSED — AUTHORITY_DIFF_VIOLATION
            </div>
          )}

          <div className="pdv-selectors" data-testid="pdv-selectors">
            <div className="pdv-selector-group">
              <label className="pdv-label" htmlFor="pdv-left-select">PACKET A</label>
              <select
                id="pdv-left-select"
                className="pdv-select"
                data-testid="pdv-left-select"
                value={leftId}
                onChange={(e) => setLeftId(e.target.value)}
              >
                {packets.map((p) => (
                  <option key={p.packet_id} value={p.packet_id}>{p.action_title}</option>
                ))}
              </select>
            </div>
            <span className="pdv-vs">VS</span>
            <div className="pdv-selector-group">
              <label className="pdv-label" htmlFor="pdv-right-select">PACKET B</label>
              <select
                id="pdv-right-select"
                className="pdv-select"
                data-testid="pdv-right-select"
                value={rightId}
                onChange={(e) => setRightId(e.target.value)}
              >
                {packets.map((p) => (
                  <option key={p.packet_id} value={p.packet_id}>{p.action_title}</option>
                ))}
              </select>
            </div>
          </div>

          {samePacket ? (
            <div className="pdv-same-packet" data-testid="pdv-same-packet">
              SAME PACKET SELECTED — select two different packets to compare
            </div>
          ) : diffRows ? (
            <>
              {authorityClean && (
                <div className="pdv-authority-clean" data-testid="pdv-authority-clean">
                  ✓ AUTHORITY_CLEAN — both packets have all authority flags = false
                </div>
              )}

              <div className="pdv-diff-table" data-testid="pdv-diff-table">
                <div className="pdv-diff-header-row">
                  <span className="pdv-diff-field-col">FIELD</span>
                  <span className="pdv-diff-val-col">PACKET A</span>
                  <span className="pdv-diff-status-col">Δ</span>
                  <span className="pdv-diff-val-col">PACKET B</span>
                </div>
                {diffRows.map((row) => {
                  const s = STATUS_STYLE[row.status];
                  return (
                    <div
                      key={row.field}
                      className={`pdv-diff-row pdv-diff-row--${row.status.toLowerCase()}`}
                      data-testid={`pdv-diff-row-${row.field}`}
                    >
                      <span className="pdv-diff-field-col">{row.field}</span>
                      <span
                        className="pdv-diff-val-col"
                        data-testid={`pdv-left-val-${row.field}`}
                      >
                        {row.left}
                      </span>
                      <span
                        className="pdv-diff-status-col"
                        style={{ color: s.color }}
                        data-testid={`pdv-diff-status-${row.field}`}
                      >
                        {s.label}
                      </span>
                      <span
                        className="pdv-diff-val-col"
                        data-testid={`pdv-right-val-${row.field}`}
                      >
                        {row.right}
                      </span>
                    </div>
                  );
                })}
              </div>

              <div className="pdv-legend" data-testid="pdv-legend">
                <span className="pdv-legend-item pdv-legend--same">= SAME</span>
                <span className="pdv-legend-item pdv-legend--different">≠ DIFFERENT</span>
                <span className="pdv-legend-item pdv-legend--missing">←? / ?→ MISSING</span>
              </div>
            </>
          ) : null}
        </>
      )}

      <div className="pdv-panel__footer">
        READ_ONLY · DISPLAY_ONLY · KEY_FIELDS_ONLY · NO_BACKEND_WRITES · NO_PERSISTENCE
      </div>
    </section>
  );
}
