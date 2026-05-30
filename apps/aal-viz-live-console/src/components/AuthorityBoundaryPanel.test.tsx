import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AuthorityBoundaryPanel } from './AuthorityBoundaryPanel';
import type { Authority } from '../types';

const LOCKED_AUTHORITY: Authority = {
  projection_only: true,
  runtime_mutation_allowed: false,
  promotion_allowed: false,
  production_activation_allowed: false,
};

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

describe('AuthorityBoundaryPanel', () => {
  it('renders the panel', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    expect(screen.getByTestId('authority-boundary-panel')).toBeInTheDocument();
  });

  it('shows AUTHORITY BOUNDARY heading', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    const matches = screen.getAllByText(/AUTHORITY BOUNDARY/i);
    expect(matches.length).toBeGreaterThanOrEqual(1);
  });

  it('shows PROJECTION ONLY field', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    expect(screen.getByText('PROJECTION ONLY')).toBeInTheDocument();
  });

  it('shows RUNTIME MUTATION field', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    expect(screen.getByText('RUNTIME MUTATION')).toBeInTheDocument();
  });

  it('shows PROMOTION field', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    expect(screen.getByText('PROMOTION')).toBeInTheDocument();
  });

  it('shows PRODUCTION ACTIVATION field', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    expect(screen.getByText('PRODUCTION ACTIVATION')).toBeInTheDocument();
  });

  it('renders all 10 forbidden control buttons', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    for (const ctrl of FORBIDDEN_CONTROLS) {
      const btn = screen.getByRole('button', { name: new RegExp(ctrl, 'i') });
      expect(btn).toBeInTheDocument();
    }
  });

  it('all forbidden control buttons are disabled', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    for (const ctrl of FORBIDDEN_CONTROLS) {
      const btn = screen.getByRole('button', { name: new RegExp(ctrl, 'i') });
      expect(btn).toBeDisabled();
    }
  });

  it('all forbidden control buttons have aria-disabled="true"', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    for (const ctrl of FORBIDDEN_CONTROLS) {
      const btn = screen.getByRole('button', { name: new RegExp(ctrl, 'i') });
      expect(btn).toHaveAttribute('aria-disabled', 'true');
    }
  });

  it('shows FORBIDDEN CONTROLS header text', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    expect(screen.getByText(/FORBIDDEN CONTROLS/i)).toBeInTheDocument();
  });

  it('has no enabled buttons in the panel', () => {
    render(<AuthorityBoundaryPanel authority={LOCKED_AUTHORITY} />);
    const buttons = screen.getAllByRole('button');
    const enabledButtons = buttons.filter((btn) => !btn.hasAttribute('disabled'));
    expect(enabledButtons).toHaveLength(0);
  });
});
