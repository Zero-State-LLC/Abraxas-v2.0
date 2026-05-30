import { useState, useCallback } from 'react';
import type { OperatorActionPacketsBundle, WorkflowItem, WorkflowItemStatus } from '../types';

interface OperatorWorkflowPanelProps {
  packetsBundle: OperatorActionPacketsBundle | null;
}

function deriveInitialStatus(
  actionType: string,
  allowed: boolean,
): WorkflowItemStatus {
  if (!allowed) return 'BLOCKED';
  if (actionType === 'COPY_PROMPT') return 'AVAILABLE';
  if (actionType === 'COPY_CHECKLIST') return 'AVAILABLE';
  if (actionType === 'REVIEW_REQUIRED') return 'REVIEW_REQUIRED';
  return 'BLOCKED';
}

function deriveWorkflowItems(bundle: OperatorActionPacketsBundle): WorkflowItem[] {
  return bundle.packets.map((pkt) => ({
    packet_id: pkt.packet_id,
    action_title: pkt.action_title,
    action_type: pkt.action_type,
    status: deriveInitialStatus(pkt.action_type, pkt.allowed),
    prompt_body: pkt.prompt_body,
    validation_checklist: pkt.validation_checklist,
    blocked_scopes: pkt.blocked_scopes,
  }));
}

const STATUS_COLORS: Record<WorkflowItemStatus, string> = {
  AVAILABLE: 'var(--clr-emerald)',
  COPIED: 'var(--clr-cyan)',
  REVIEW_REQUIRED: 'var(--clr-gold)',
  BLOCKED: 'var(--clr-red)',
  COMPLETED_MANUALLY: 'var(--clr-violet)',
};

export function OperatorWorkflowPanel({
  packetsBundle,
}: OperatorWorkflowPanelProps): JSX.Element {
  const [items, setItems] = useState<WorkflowItem[]>(() =>
    packetsBundle ? deriveWorkflowItems(packetsBundle) : [],
  );

  const setStatus = useCallback((packet_id: string, status: WorkflowItemStatus) => {
    setItems((prev) =>
      prev.map((item) => (item.packet_id === packet_id ? { ...item, status } : item)),
    );
  }, []);

  const handleCopy = useCallback(
    (item: WorkflowItem) => {
      const text =
        item.action_type === 'COPY_CHECKLIST'
          ? item.validation_checklist.map((s, i) => `${i + 1}. ${s}`).join('\n')
          : item.prompt_body;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).catch(() => undefined);
      }
      setStatus(item.packet_id, 'COPIED');
    },
    [setStatus],
  );

  const available_count = items.filter((i) => i.status === 'AVAILABLE').length;
  const copied_count = items.filter((i) => i.status === 'COPIED').length;
  const review_required_count = items.filter((i) => i.status === 'REVIEW_REQUIRED').length;
  const blocked_count = items.filter((i) => i.status === 'BLOCKED').length;
  const completed_manually_count = items.filter((i) => i.status === 'COMPLETED_MANUALLY').length;

  return (
    <section
      className="workflow-panel"
      data-testid="operator-workflow-panel"
      aria-label="Operator Workflow Panel"
    >
      <div className="workflow-panel__header">
        <span className="workflow-panel__title">◈ OPERATOR WORKFLOW</span>
        <span className="workflow-panel__notice">UI_ONLY · NON_AUTHORITATIVE</span>
      </div>

      <div className="workflow-panel__counts">
        <span className="wf-count wf-count--available" data-testid="wf-count-available">
          AVAILABLE {available_count}
        </span>
        <span className="wf-count wf-count--copied" data-testid="wf-count-copied">
          COPIED {copied_count}
        </span>
        <span className="wf-count wf-count--review" data-testid="wf-count-review">
          REVIEW_REQUIRED {review_required_count}
        </span>
        <span className="wf-count wf-count--blocked" data-testid="wf-count-blocked">
          BLOCKED {blocked_count}
        </span>
        <span className="wf-count wf-count--completed" data-testid="wf-count-completed">
          COMPLETED_MANUALLY {completed_manually_count}
        </span>
      </div>

      {items.length === 0 && (
        <div className="workflow-panel__empty" data-testid="workflow-empty">
          NO PACKETS LOADED
        </div>
      )}

      <ul className="workflow-item-list">
        {items.map((item) => (
          <li key={item.packet_id} className="workflow-item" data-testid={`workflow-item-${item.packet_id}`}>
            <div className="workflow-item__header">
              <span className="workflow-item__title">{item.action_title}</span>
              <span className="workflow-item__type">{item.action_type}</span>
              <span
                className="workflow-item__status"
                data-testid={`workflow-status-${item.packet_id}`}
                style={{ color: STATUS_COLORS[item.status] }}
              >
                {item.status}
              </span>
            </div>

            <div className="workflow-item__actions">
              {(item.action_type === 'COPY_PROMPT' || item.action_type === 'COPY_CHECKLIST') && (
                <button
                  className="wf-btn wf-btn--copy"
                  data-testid={`wf-copy-btn-${item.packet_id}`}
                  onClick={() => handleCopy(item)}
                  title="Copy to clipboard — UI_ONLY"
                >
                  COPY [UI_ONLY]
                </button>
              )}

              <span className="workflow-item__manual-label">MANUAL STATUS [UI_ONLY]:</span>

              <button
                className="wf-btn wf-btn--review"
                data-testid={`wf-review-btn-${item.packet_id}`}
                onClick={() => setStatus(item.packet_id, 'REVIEW_REQUIRED')}
              >
                REVIEW_REQUIRED
              </button>
              <button
                className="wf-btn wf-btn--complete"
                data-testid={`wf-complete-btn-${item.packet_id}`}
                onClick={() => setStatus(item.packet_id, 'COMPLETED_MANUALLY')}
              >
                COMPLETED_MANUALLY
              </button>
              <button
                className="wf-btn wf-btn--block"
                data-testid={`wf-block-btn-${item.packet_id}`}
                onClick={() => setStatus(item.packet_id, 'BLOCKED')}
              >
                BLOCKED
              </button>
            </div>

            {item.blocked_scopes.length > 0 && (
              <div className="workflow-item__blocked-scopes">
                {item.blocked_scopes.map((s) => (
                  <span key={s} className="wf-scope-tag">
                    {s}
                  </span>
                ))}
              </div>
            )}
          </li>
        ))}
      </ul>

      <div className="workflow-panel__footer">
        NO_EXECUTION · NO_RUNTIME_MUTATION · NO_BACKEND_WRITES · NO_PERSISTENCE · REVIEW_ONLY
      </div>
    </section>
  );
}
