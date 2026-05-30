import type { Authority } from '../types';

interface AuthorityBoundaryPanelProps {
  authority: Authority;
}

const AUTHORITY_FIELDS: { key: keyof Authority; label: string }[] = [
  { key: 'projection_only', label: 'PROJECTION ONLY' },
  { key: 'runtime_mutation_allowed', label: 'RUNTIME MUTATION' },
  { key: 'promotion_allowed', label: 'PROMOTION' },
  { key: 'production_activation_allowed', label: 'PRODUCTION ACTIVATION' },
];

const FORBIDDEN_CONTROLS = [
  'Promote',
  'Activate Production',
  'Mutate Runtime',
  'Place Bet',
  'Publish',
  'Mint',
  'Transfer Wallet',
  'Control Hardware',
  'Control DAW',
  'Execute Live Patch',
];

export function AuthorityBoundaryPanel({ authority }: AuthorityBoundaryPanelProps): JSX.Element {
  return (
    <div className="panel-block">
      <div className="panel-header">
        <span className="panel-icon">⊘</span>
        AUTHORITY BOUNDARY
      </div>
      <div className="panel-body">
        <div className="authority-table">
          {AUTHORITY_FIELDS.map(({ key, label }) => {
            const val = authority[key] as boolean;
            return (
              <>
                <span key={`${key}-label`} className="authority-table__key">{label}</span>
                <span
                  key={`${key}-val`}
                  className={`authority-table__val authority-table__val--${String(val)}`}
                >
                  {String(val).toUpperCase()}
                </span>
              </>
            );
          })}
        </div>

        <div className="forbidden-controls">
          <div className="forbidden-controls__header">
            ⊘ FORBIDDEN CONTROLS — DISABLED BY AUTHORITY BOUNDARY
          </div>
          {FORBIDDEN_CONTROLS.map((ctrl) => (
            <button
              key={ctrl}
              className="forbidden-btn"
              disabled
              aria-disabled="true"
              aria-label={`${ctrl} — FORBIDDEN_BY_AUTHORITY_BOUNDARY`}
            >
              {ctrl}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
