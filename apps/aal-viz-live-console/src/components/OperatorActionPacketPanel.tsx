import { useState } from 'react';
import type { OperatorActionPacket, OperatorActionPacketsBundle, ActionType } from '../types';

interface OperatorActionPacketPanelProps {
  packetsBundle: OperatorActionPacketsBundle | null;
}

const ACTION_TYPE_STYLE: Record<ActionType, { label: string; cls: string }> = {
  COPY_PROMPT: { label: '⎘ COPY PROMPT', cls: 'action-type--COPY_PROMPT' },
  COPY_CHECKLIST: { label: '☑ COPY CHECKLIST', cls: 'action-type--COPY_CHECKLIST' },
  REVIEW_REQUIRED: { label: '⊡ REVIEW REQUIRED', cls: 'action-type--REVIEW_REQUIRED' },
};

function getCopyText(packet: OperatorActionPacket): string {
  if (packet.action_type === 'COPY_CHECKLIST') {
    return packet.validation_checklist.join('\n');
  }
  if (packet.action_type === 'COPY_PROMPT') {
    return packet.prompt_body;
  }
  return packet.prompt_body + '\n\n─── CHECKLIST ───\n' + packet.validation_checklist.join('\n');
}

interface CopyButtonProps {
  text: string;
}

function CopyButton({ text }: CopyButtonProps): JSX.Element {
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'fallback'>('idle');

  function handleCopy() {
    if (navigator.clipboard?.writeText) {
      navigator.clipboard
        .writeText(text)
        .then(() => {
          setCopyState('copied');
          setTimeout(() => setCopyState('idle'), 2000);
        })
        .catch(() => setCopyState('fallback'));
    } else {
      setCopyState('fallback');
    }
  }

  return (
    <div className="action-copy-wrap">
      <button type="button" onClick={handleCopy} className="action-copy-btn">
        {copyState === 'copied' ? '✓ COPIED' : copyState === 'fallback' ? '▽ SELECT BELOW' : '⎘ COPY'}
      </button>
      {copyState === 'fallback' && (
        <textarea
          className="action-fallback-textarea"
          readOnly
          value={text}
          onClick={(e) => (e.target as HTMLTextAreaElement).select()}
          aria-label="Copy this text manually"
        />
      )}
    </div>
  );
}

interface PacketCardProps {
  packet: OperatorActionPacket;
}

function PacketCard({ packet }: PacketCardProps): JSX.Element {
  const [expanded, setExpanded] = useState(false);
  const typeInfo = ACTION_TYPE_STYLE[packet.action_type];
  const copyText = getCopyText(packet);

  return (
    <div className="action-packet-card">
      <div className="action-packet-card__header">
        <span className={`action-type-badge ${typeInfo.cls}`}>{typeInfo.label}</span>
        <button
          type="button"
          className="action-expand-btn"
          onClick={() => setExpanded((v) => !v)}
          aria-expanded={expanded}
        >
          {expanded ? '▲' : '▼'}
        </button>
      </div>

      <div className="action-packet-card__title">{packet.action_title}</div>

      <div className="action-packet-card__meta">
        <span className="action-meta-label">NEXT:</span>
        <span className="action-meta-value">{packet.recommended_next_step}</span>
      </div>

      <div className="action-packet-card__locks">
        <span className="action-lock action-lock--blocked">⊘ EXEC BLOCKED</span>
        <span className="action-lock action-lock--blocked">⊘ MUTATION BLOCKED</span>
        <span className="action-lock action-lock--blocked">⊘ PROMOTION BLOCKED</span>
        {packet.allowed && (
          <span className="action-lock action-lock--allowed">✓ DISPLAY ALLOWED</span>
        )}
      </div>

      {expanded && (
        <div className="action-packet-card__body">
          <div className="action-packet-card__section-label">CONTENT</div>
          <pre className="action-packet-card__body-text">{copyText}</pre>

          <div className="action-packet-card__section-label" style={{ marginTop: '8px' }}>
            BLOCKED SCOPES
          </div>
          <ul className="action-blocked-list">
            {packet.blocked_scopes.map((scope) => (
              <li key={scope} className="action-blocked-item">
                ⊘ {scope}
              </li>
            ))}
          </ul>

          <div className="action-packet-card__section-label" style={{ marginTop: '8px' }}>
            PROVENANCE
          </div>
          <ul className="action-provenance-list">
            {packet.provenance_refs.map((ref) => (
              <li key={ref} className="action-provenance-item">
                {ref}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="action-packet-card__footer">
        <CopyButton text={copyText} />
      </div>
    </div>
  );
}

export function OperatorActionPacketPanel({
  packetsBundle,
}: OperatorActionPacketPanelProps): JSX.Element {
  const count = packetsBundle?.packets.length ?? 0;

  return (
    <div className="panel-block">
      <div className="panel-header">
        <span className="panel-icon">⊕</span>
        OPERATOR ACTION PACKETS
        <span style={{ marginLeft: 'auto', color: 'var(--clr-violet)', fontSize: '10px' }}>
          {count} PACKETS · COPY ONLY
        </span>
      </div>
      <div className="panel-body">
        {packetsBundle == null ? (
          <div className="empty-state">
            RUN python scripts/build_aal_viz_operator_action_packets.py
          </div>
        ) : packetsBundle.packets.length === 0 ? (
          <div className="empty-state">NO PACKETS — FAIL CLOSED</div>
        ) : (
          <ul className="action-packet-list">
            {packetsBundle.packets.map((pkt) => (
              <li key={pkt.packet_id}>
                <PacketCard packet={pkt} />
              </li>
            ))}
          </ul>
        )}
        <div className="action-footer-notice">
          ⊘ All packets are display/copy only. No auto-apply. No execution. No mutation.
        </div>
      </div>
    </div>
  );
}
