import type { OperatorQueueItem } from '../types';

interface OperatorReviewQueueProps {
  queue: OperatorQueueItem[];
}

export function OperatorReviewQueue({ queue }: OperatorReviewQueueProps): JSX.Element {
  return (
    <div className="panel-block">
      <div className="panel-header">
        <span className="panel-icon">⊡</span>
        OPERATOR REVIEW QUEUE
        <span style={{ marginLeft: 'auto', color: 'var(--clr-gold)', fontSize: '10px' }}>
          {queue.filter((q) => q.status === 'PENDING').length} PENDING
        </span>
      </div>
      <div className="panel-body">
        {queue.length === 0 ? (
          <div className="empty-state">NO PENDING ACTIONS</div>
        ) : (
          <ul className="queue-list">
            {queue.map((item) => (
              <li key={item.action_id} className="queue-item">
                <div className="queue-item__label">{item.label}</div>
                <div className="queue-item__meta">
                  <span className="queue-item__target">{item.target_system.toUpperCase()}</span>
                  <span className={`queue-item__status queue-status--${item.status}`}>
                    {item.status}
                  </span>
                  <span className="queue-item__lock">⊘ AUTO-APPLY BLOCKED</span>
                </div>
              </li>
            ))}
          </ul>
        )}
        <div
          style={{
            marginTop: '8px',
            fontSize: '9px',
            color: 'var(--clr-text-muted)',
            borderTop: '1px solid var(--clr-border)',
            paddingTop: '6px',
          }}
        >
          ⊘ Actions are displayed for review only. No action is auto-applied.
        </div>
      </div>
    </div>
  );
}
