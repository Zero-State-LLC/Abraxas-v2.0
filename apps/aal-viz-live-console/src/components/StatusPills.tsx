import type { Authority, ConnectionStatus, SourceMode } from '../types';

interface StatusPillsProps {
  authority: Authority;
  sourceMode: SourceMode;
  connectionStatus: ConnectionStatus;
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

const CONNECTION_PILL: Record<ConnectionStatus, PillDef> = {
  CONNECTING: { label: 'FEED CONNECTING', variant: 'gold' },
  LIVE_STREAM: { label: 'FEED LIVE STREAM', variant: 'emerald' },
  POLLING_FALLBACK: { label: 'FEED POLLING', variant: 'gold' },
  SAMPLE_FALLBACK: { label: 'FEED SAMPLE', variant: 'gold' },
  FAIL_CLOSED: { label: 'FEED FAIL CLOSED', variant: 'violet' },
};

export function StatusPills({
  authority: _authority,
  sourceMode,
  connectionStatus,
}: StatusPillsProps): JSX.Element {
  const sourcePill = SOURCE_MODE_PILL[sourceMode];
  const connectionPill = CONNECTION_PILL[connectionStatus];
  const pills = [...STATIC_PILLS, sourcePill, connectionPill];

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
