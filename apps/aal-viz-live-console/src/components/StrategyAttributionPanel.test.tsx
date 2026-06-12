import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { StrategyAttributionPanel } from './StrategyAttributionPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

afterEach(cleanup);

describe('StrategyAttributionPanel', () => {
  it('renders summary, attribution packets, drift timeline, score badge, and locks', () => {
    render(<StrategyAttributionPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('strategy-attribution-panel')).toBeInTheDocument();
    expect(screen.getByTestId('strategy-attribution-summary')).toBeInTheDocument();
    expect(screen.getByTestId('strategy-attribution-packets')).toBeInTheDocument();
    expect(screen.getByTestId('domain-drift-timeline')).toBeInTheDocument();
    expect(screen.getByTestId('contribution-score-badge')).toBeInTheDocument();
    expect(screen.getByTestId('strategy-attribution-locks')).toBeInTheDocument();
  });

  it('shows not-computable attribution and explicit missing baseline state', () => {
    render(<StrategyAttributionPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('strategy-attribution-summary').textContent).toContain('NOT_COMPUTABLE');
    expect(screen.getByTestId('strategy-attribution-packets').textContent).toContain('NOT_COMPUTABLE');
    expect(screen.getByTestId('domain-drift-timeline').textContent).toContain('NOT_COMPUTABLE');
    expect(screen.getByTestId('contribution-score-badge').textContent).toContain('BASELINENOT_COMPUTABLE');
    expect(screen.getByTestId('contribution-score-badge').textContent).toContain('CONTRIBUTIONNOT_COMPUTABLE');
  });

  it('does not expose attribution controls or authority-bearing locks as true', () => {
    render(<StrategyAttributionPanel bundle={sampleProjectionBundle} />);

    expect(screen.queryAllByRole('button')).toHaveLength(0);
    const locks = screen.getByTestId('strategy-attribution-locks');
    expect(locks.textContent).toContain('NOTION WRITEFALSE');
    expect(locks.textContent).toContain('WEBSOCKETFALSE');
    expect(locks.textContent).toContain('ROUTING MUTATIONFALSE');
    expect(locks.textContent).toContain('FORECAST MUTATIONFALSE');
    expect(locks.textContent).toContain('SCORE MUTATIONFALSE');
    expect(locks.textContent).toContain('AUTHORITY MUTATIONFALSE');
  });
});
