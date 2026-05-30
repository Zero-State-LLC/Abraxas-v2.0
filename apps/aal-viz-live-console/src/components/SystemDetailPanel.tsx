import type { SystemProjection } from '../types';

interface SystemDetailPanelProps {
  system: SystemProjection | null;
}

export function SystemDetailPanel({ system }: SystemDetailPanelProps): JSX.Element {
  return (
    <div className="panel-block">
      <div className="panel-header">
        <span className="panel-icon">◈</span>
        SYSTEM DETAIL
        {system != null && (
          <span style={{ marginLeft: 'auto', color: 'var(--clr-cyan)', fontSize: '10px', fontWeight: 700 }}>
            {system.display_name}
          </span>
        )}
      </div>
      <div className="panel-body">
        {system == null ? (
          <div className="empty-state">SELECT A SYSTEM FROM THE SPINE</div>
        ) : (
          <>
            <div className="detail-grid">
              <span className="detail-label">SYSTEM ID</span>
              <span className="detail-value text-cyan">{system.system_id}</span>

              <span className="detail-label">STATUS</span>
              <span className="detail-value">
                <span className={`status-badge status-badge--${system.status}`}>
                  {system.status.replace('_', ' ')}
                </span>
              </span>

              <span className="detail-label">COMPLETION</span>
              <span className="detail-value">
                <span style={{ color: 'var(--clr-cyan)' }}>{system.completion_pct}%</span>
              </span>

              <span className="detail-label">RISK LEVEL</span>
              <span className={`detail-value risk-badge--${system.risk_level} font-bold`}>
                {system.risk_level}
              </span>

              <span className="detail-label">SHADOW ONLY</span>
              <span className="detail-value" style={{ color: 'var(--clr-emerald)' }}>
                {String(system.shadow_only).toUpperCase()}
              </span>

              <span className="detail-label">LAST UPDATED</span>
              <span className="detail-value text-muted">{system.last_updated}</span>

              <span className="detail-label">PACKETS</span>
              <span className="detail-value">{system.projection_packets.length}</span>

              <span className="detail-label">RECEIPTS</span>
              <span className="detail-value">{system.ledger_receipts.length}</span>
            </div>

            <div className="progress-bar" style={{ marginTop: '10px' }}>
              <div
                className="progress-bar__fill"
                style={{ width: `${system.completion_pct}%` }}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
