import type { SystemProjection } from '../types';

interface SystemSpineGridProps {
  systems: SystemProjection[];
  selectedSystemId: string | null;
  onSelect: (id: string) => void;
}

export function SystemSpineGrid({
  systems,
  selectedSystemId,
  onSelect,
}: SystemSpineGridProps): JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="panel-header">
        <span className="panel-icon">◈</span>
        SYSTEM SPINE
        <span style={{ marginLeft: 'auto', color: 'var(--clr-cyan)', fontSize: '10px' }}>
          {systems.length}
        </span>
      </div>
      <ul className="spine-list" style={{ overflowY: 'auto', flex: 1 }}>
        {systems.map((sys) => (
          <li
            key={sys.system_id}
            className={`spine-item${selectedSystemId === sys.system_id ? ' spine-item--selected' : ''}`}
            onClick={() => onSelect(sys.system_id)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && onSelect(sys.system_id)}
            aria-selected={selectedSystemId === sys.system_id}
          >
            <span
              className={`spine-item__status status-dot--${sys.status}`}
              title={sys.status}
            />
            <span className="spine-item__name">{sys.display_name}</span>
            <span className="spine-item__pct">{sys.completion_pct}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
