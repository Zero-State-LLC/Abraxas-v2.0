import type { SystemProjection } from '../types';

interface ProjectionPacketInspectorProps {
  system: SystemProjection | null;
}

export function ProjectionPacketInspector({
  system,
}: ProjectionPacketInspectorProps): JSX.Element {
  return (
    <div className="panel-block">
      <div className="panel-header">
        <span className="panel-icon">◧</span>
        PROJECTION PACKET INSPECTOR
        {system != null && (
          <span style={{ marginLeft: 'auto', color: 'var(--clr-text-muted)', fontSize: '10px' }}>
            {system.display_name}
          </span>
        )}
      </div>
      <div className="panel-body">
        {system == null ? (
          <div className="empty-state">SELECT A SYSTEM TO INSPECT PACKETS</div>
        ) : system.projection_packets.length === 0 ? (
          <div className="empty-state">NO PROJECTION PACKETS</div>
        ) : (
          <ul className="packet-list">
            {system.projection_packets.map((pkt) => (
              <li key={pkt.packet_id} className="packet-item">
                <span className="packet-item__type uppercase">{pkt.packet_type}</span>
                <span className="packet-item__status">{pkt.status}</span>
                <span className="packet-item__value">
                  {pkt.display_value ?? <span className="text-muted">—</span>}
                </span>
                <span className="packet-item__authority">
                  src: {pkt.authority_source} · projection_only: {String(pkt.projection_only)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
