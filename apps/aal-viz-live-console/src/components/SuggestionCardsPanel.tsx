import { useState, useMemo } from 'react';
import type {
  OperatorActionPacketsBundle,
  SuggestionCard,
  SuggestionCardType,
} from '../types';

interface SuggestionCardsPanelProps {
  packetsBundle: OperatorActionPacketsBundle | null;
}

function generateSuggestions(
  bundle: OperatorActionPacketsBundle,
): SuggestionCard[] {
  const cards: SuggestionCard[] = [];

  for (const pkt of bundle.packets) {
    cards.push({
      suggestion_id: `NEXT_SAFE_STEP-${pkt.packet_id}`,
      title: `Next safe step: ${pkt.action_title}`,
      type: 'NEXT_SAFE_STEP',
      source_packet_id: pkt.packet_id,
      rationale: `Packet "${pkt.action_title}" has recommended next step available for operator review.`,
      suggested_manual_action: pkt.recommended_next_step,
      authority: 'DISPLAY_ONLY',
      execution_allowed: false,
      runtime_mutation_allowed: false,
      promotion_allowed: false,
    });

    if (pkt.validation_checklist.length > 0) {
      cards.push({
        suggestion_id: `VALIDATION_REMINDER-${pkt.packet_id}`,
        title: `Validation reminder: ${pkt.action_title}`,
        type: 'VALIDATION_REMINDER',
        source_packet_id: pkt.packet_id,
        rationale: `Packet has ${pkt.validation_checklist.length} checklist item(s) that require operator review before proceeding.`,
        suggested_manual_action:
          'Open Evidence Checklist Panel and review all items before marking complete.',
        authority: 'DISPLAY_ONLY',
        execution_allowed: false,
        runtime_mutation_allowed: false,
        promotion_allowed: false,
      });
    }

    if (pkt.blocked_scopes.length > 0) {
      cards.push({
        suggestion_id: `AUTHORITY_BOUNDARY-${pkt.packet_id}`,
        title: `Authority boundary: ${pkt.blocked_scopes.length} scope(s) blocked`,
        type: 'AUTHORITY_BOUNDARY',
        source_packet_id: pkt.packet_id,
        rationale: `Blocked scopes on this packet: ${pkt.blocked_scopes.join(', ')}. No automated action may cross these boundaries.`,
        suggested_manual_action:
          'Review blocked scopes. Do not attempt to bypass authority boundary. Proceed only via governance-authorized path.',
        authority: 'DISPLAY_ONLY',
        execution_allowed: false,
        runtime_mutation_allowed: false,
        promotion_allowed: false,
      });
    }

    if (pkt.action_type === 'REVIEW_REQUIRED') {
      cards.push({
        suggestion_id: `FRONTIER_PAUSE-${pkt.packet_id}`,
        title: `Frontier pause required: ${pkt.action_title}`,
        type: 'FRONTIER_PAUSE',
        source_packet_id: pkt.packet_id,
        rationale: `Packet requires explicit operator review before the frontier can advance. No auto-apply permitted.`,
        suggested_manual_action:
          'Read packet contents carefully. Mark reviewed in Workflow Panel only after full manual review.',
        authority: 'DISPLAY_ONLY',
        execution_allowed: false,
        runtime_mutation_allowed: false,
        promotion_allowed: false,
      });
    }
  }

  return cards;
}

const TYPE_LABEL: Record<SuggestionCardType, string> = {
  NEXT_SAFE_STEP: 'NEXT SAFE STEP',
  VALIDATION_REMINDER: 'VALIDATION REMINDER',
  AUTHORITY_BOUNDARY: 'AUTHORITY BOUNDARY',
  FRONTIER_PAUSE: 'FRONTIER PAUSE',
};

export function SuggestionCardsPanel({
  packetsBundle,
}: SuggestionCardsPanelProps): JSX.Element {
  const cards = useMemo(
    () => (packetsBundle ? generateSuggestions(packetsBundle) : []),
    [packetsBundle],
  );

  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [reviewed, setReviewed] = useState<Set<string>>(new Set());

  const toggleExpand = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleReviewed = (id: string) => {
    setReviewed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const reviewedCount = reviewed.size;

  return (
    <section
      className="scp-panel"
      data-testid="suggestion-cards-panel"
      aria-label="Suggestion Cards Panel"
    >
      <div className="scp-panel__header">
        <span className="scp-panel__title">◈ INTERVENTION SUGGESTIONS</span>
        <span className="scp-panel__notice">DISPLAY_ONLY · NON_AUTHORITATIVE</span>
      </div>

      {cards.length === 0 ? (
        <div className="scp-panel__empty" data-testid="scp-empty">
          NO PACKETS LOADED — FAIL CLOSED
        </div>
      ) : (
        <>
          <div className="scp-summary">
            <span className="scp-count scp-count--total" data-testid="scp-count-total">
              SUGGESTIONS {cards.length}
            </span>
            <span className="scp-count scp-count--reviewed" data-testid="scp-count-reviewed">
              REVIEWED {reviewedCount}
            </span>
          </div>

          <ul className="scp-card-list">
            {cards.map((card) => {
              const isExpanded = expanded.has(card.suggestion_id);
              const isReviewed = reviewed.has(card.suggestion_id);
              return (
                <li
                  key={card.suggestion_id}
                  className="scp-card"
                  data-testid={`scp-card-${card.suggestion_id}`}
                >
                  <div
                    className="scp-card__header"
                    onClick={() => toggleExpand(card.suggestion_id)}
                    data-testid={`scp-card-header-${card.suggestion_id}`}
                    role="button"
                    aria-expanded={isExpanded}
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') toggleExpand(card.suggestion_id);
                    }}
                  >
                    <span className="scp-card__chevron">
                      {isExpanded ? '▾' : '▸'}
                    </span>
                    <span
                      className={`scp-card__type-badge scp-badge--${card.type}`}
                      data-testid={`scp-type-badge-${card.suggestion_id}`}
                    >
                      {TYPE_LABEL[card.type]}
                    </span>
                    <span className="scp-card__title">{card.title}</span>
                    {isReviewed && (
                      <span
                        className="scp-card__reviewed-badge"
                        data-testid={`scp-reviewed-badge-${card.suggestion_id}`}
                      >
                        REVIEWED [UI_ONLY]
                      </span>
                    )}
                  </div>

                  {isExpanded && (
                    <div className="scp-card__body" data-testid={`scp-card-body-${card.suggestion_id}`}>
                      <div className="scp-card__field">
                        <span className="scp-card__field-label">SUGGESTION ID</span>
                        <span className="scp-card__field-value scp-card__field-value--mono" data-testid={`scp-suggestion-id-${card.suggestion_id}`}>
                          {card.suggestion_id}
                        </span>
                      </div>

                      {card.source_packet_id && (
                        <div className="scp-card__field">
                          <span className="scp-card__field-label">SOURCE PACKET</span>
                          <span className="scp-card__field-value scp-card__field-value--mono">
                            {card.source_packet_id}
                          </span>
                        </div>
                      )}

                      <div className="scp-card__field">
                        <span className="scp-card__field-label">RATIONALE</span>
                        <span className="scp-card__field-value">{card.rationale}</span>
                      </div>

                      <div className="scp-card__field">
                        <span className="scp-card__field-label">SUGGESTED MANUAL ACTION</span>
                        <span className="scp-card__field-value">{card.suggested_manual_action}</span>
                      </div>

                      <div className="scp-card__authority-row" data-testid={`scp-authority-${card.suggestion_id}`}>
                        <span className="scp-authority-display">AUTHORITY: {card.authority}</span>
                        <span className="scp-authority-lock">EXEC: {String(card.execution_allowed)}</span>
                        <span className="scp-authority-lock">MUTATION: {String(card.runtime_mutation_allowed)}</span>
                        <span className="scp-authority-lock">PROMOTION: {String(card.promotion_allowed)}</span>
                      </div>

                      <div className="scp-card__actions">
                        <button
                          className={`scp-btn--reviewed${isReviewed ? ' scp-btn--reviewed-active' : ''}`}
                          data-testid={`scp-reviewed-btn-${card.suggestion_id}`}
                          onClick={() => toggleReviewed(card.suggestion_id)}
                        >
                          {isReviewed ? '✓ REVIEWED [UI_ONLY]' : 'MARK REVIEWED [UI_ONLY]'}
                        </button>
                      </div>
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        </>
      )}

      <div className="scp-panel__footer">
        DISPLAY_ONLY · NO_AUTO_APPLY · NO_AUTO_RESPONSE · NO_EXECUTION · NO_BACKEND_WRITES · NO_PERSISTENCE
      </div>
    </section>
  );
}
