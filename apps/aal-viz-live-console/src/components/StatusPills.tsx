import type { Authority, SourceMode } from '../types';

interface StatusPillsProps {
  authority: Authority;
  sourceMode: SourceMode;
}

interface PillDef {
  label: string;
  variant: 'cyan' | 'violet' | 'gold' | 'emerald';
}

const STATIC_PILLS: PillDef[] = [
  { label: 'CANON ACTIVE', variant: 'cyan' },
  { label: 'SHADOW ONLINE', variant: 'cyan' },
  { label: 'FORECAST GATED', variant: 'gold' },
  { label: 'PROJECTION ONLY', variant: 'violet' },
  { label: 'LEDGER SAFE', variant: 'emerald' },
  { label: 'RUNTIME MUTATION OFF', variant: 'emerald' },
  { label: 'PROMOTION LOCKED', variant: 'gold' },
];

const SOURCE_MODE_PILL: Record<SourceMode, PillDef> = {
  LIVE_ARTIFACT_BUNDLE: { label: 'LIVE ARTIFACT BUNDLE', variant: 'emerald' },
  SAMPLE_FALLBACK: { label: 'SAMPLE FALLBACK', variant: 'gold' },
  FAIL_CLOSED: { label: 'FAIL CLOSED', variant: 'violet' },
};

export function StatusPills({ authority: _authority, sourceMode }: StatusPillsProps): JSX.Element {
  const sourcePill = SOURCE_MODE_PILL[sourceMode];
  const pills = [...STATIC_PILLS, sourcePill];

  return (
    <ul className="pills-list" aria-label="System status pills">
      {pills.map((pill) => (
        <li key={pill.label} className={`pill pill--${pill.variant}`}>
          <span className="pill-dot" />
          {pill.label}
        </li>
      ))}
    </ul>
  );
}
