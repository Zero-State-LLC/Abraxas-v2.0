import type { Authority } from '../types';

interface StatusPillsProps {
  authority: Authority;
}

interface PillDef {
  label: string;
  variant: 'cyan' | 'violet' | 'gold' | 'emerald';
}

const PILLS: PillDef[] = [
  { label: 'CANON ACTIVE', variant: 'cyan' },
  { label: 'SHADOW ONLINE', variant: 'cyan' },
  { label: 'FORECAST GATED', variant: 'gold' },
  { label: 'PROJECTION ONLY', variant: 'violet' },
  { label: 'LEDGER SAFE', variant: 'emerald' },
  { label: 'RUNTIME MUTATION OFF', variant: 'emerald' },
  { label: 'PROMOTION LOCKED', variant: 'gold' },
];

export function StatusPills({ authority: _authority }: StatusPillsProps): JSX.Element {
  return (
    <ul className="pills-list" aria-label="System status pills">
      {PILLS.map((pill) => (
        <li key={pill.label} className={`pill pill--${pill.variant}`}>
          <span className="pill-dot" />
          {pill.label}
        </li>
      ))}
    </ul>
  );
}
