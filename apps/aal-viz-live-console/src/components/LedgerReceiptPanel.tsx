import type { SystemProjection } from '../types';

interface LedgerReceiptPanelProps {
  system: SystemProjection | null;
}

export function LedgerReceiptPanel({ system }: LedgerReceiptPanelProps): JSX.Element {
  return (
    <div className="panel-block">
      <div className="panel-header">
        <span className="panel-icon">▣</span>
        LEDGER RECEIPT PANEL
        {system != null && (
          <span style={{ marginLeft: 'auto', color: 'var(--clr-text-muted)', fontSize: '10px' }}>
            {system.ledger_receipts.length} receipt{system.ledger_receipts.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>
      <div className="panel-body">
        {system == null ? (
          <div className="empty-state">SELECT A SYSTEM TO VIEW RECEIPTS</div>
        ) : system.ledger_receipts.length === 0 ? (
          <div className="empty-state">NO LEDGER RECEIPTS</div>
        ) : (
          <ul className="receipt-list">
            {system.ledger_receipts.map((rcpt) => (
              <li key={rcpt.receipt_id} className="receipt-item">
                <div className="receipt-item__event">{rcpt.event}</div>
                <div className="receipt-item__hash">⊞ {rcpt.canonical_hash}</div>
                <div className="receipt-item__time">{rcpt.timestamp}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
