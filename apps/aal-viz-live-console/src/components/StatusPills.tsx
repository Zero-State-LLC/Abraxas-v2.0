import type { ReactNode } from 'react';
import type { Authority, ConnectionStatus, SourceMode } from '../types';

interface StatusPillsProps {
  authority: Authority;
  sourceMode: SourceMode;
  connectionStatus: ConnectionStatus;
}

export type PillVariant = 'cyan' | 'violet' | 'gold' | 'emerald' | 'red' | 'slate';

interface PillDef {
  label: string;
  variant: PillVariant;
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
  FAIL_CLOSED: { label: 'FEED FAIL CLOSED', variant: 'red' },
};

export function formatPostureLabel(value: string | null | undefined): string {
  if (value == null || value === '') {
    return 'NONE';
  }
  return value.split('_').join(' ');
}

export function postureVariant(value: string | null | undefined): PillVariant {
  const upper = (value ?? '').toUpperCase();
  if (upper.includes('FAIL_CLOSED') || upper.includes('FAIL CLOSED')) {
    return 'red';
  }
  if (upper.includes('ADVISORY') || upper.includes('READ ONLY') || upper.includes('PROJECTION')) {
    return 'violet';
  }
  if (upper.includes('MISSING') || upper.includes('NOT_COMPUTABLE') || upper === 'NONE') {
    return 'slate';
  }
  if (
    upper.includes('READY')
    || upper.includes('LIVE')
    || upper.includes('OBSERVED')
    || upper.includes('RESOLVED')
    || upper.includes('ACTIVE')
    || upper.includes('ALIGNED')
  ) {
    return 'emerald';
  }
  if (
    upper.includes('PARTIAL')
    || upper.includes('POLLING')
    || upper.includes('SAMPLE')
    || upper.includes('PENDING')
    || upper.includes('HELD')
    || upper.includes('FINDINGS')
    || upper.includes('BLOCKED')
    || upper.includes('WARNING')
  ) {
    return 'gold';
  }
  return 'cyan';
}

interface PostureBadgeProps {
  label: string;
  variant?: PillVariant;
  subtle?: boolean;
  testId?: string;
  title?: string;
}

export function PostureBadge({
  label,
  variant,
  subtle = false,
  testId,
  title,
}: PostureBadgeProps): JSX.Element {
  const resolvedVariant = variant ?? postureVariant(label);
  return (
    <span
      className={`posture-badge posture-badge--${resolvedVariant}${subtle ? ' posture-badge--subtle' : ''}`}
      data-testid={testId}
      title={title}
    >
      {formatPostureLabel(label)}
    </span>
  );
}

export function AdvisoryNote({ children }: { children: ReactNode }): JSX.Element {
  return (
    <div className="advisory-note">
      <span className="advisory-note__label">ADVISORY ONLY</span>
      <span>{children}</span>
    </div>
  );
}

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
