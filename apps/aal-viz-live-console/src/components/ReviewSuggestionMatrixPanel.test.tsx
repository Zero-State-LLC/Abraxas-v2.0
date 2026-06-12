import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { ReviewSuggestionMatrixPanel } from './ReviewSuggestionMatrixPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

afterEach(cleanup);

describe('ReviewSuggestionMatrixPanel', () => {
  it('renders suggestions, matrix, reason codes, redundancy, and locks', () => {
    render(<ReviewSuggestionMatrixPanel bundle={sampleProjectionBundle} packetsBundle={null} />);

    expect(screen.getByTestId('review-suggestion-matrix-panel')).toBeInTheDocument();
    expect(screen.getByTestId('review-suggestion-summary')).toBeInTheDocument();
    expect(screen.getByTestId('automated-review-suggestions')).toBeInTheDocument();
    expect(screen.getByTestId('provider-comparison-matrix')).toBeInTheDocument();
    expect(screen.getByTestId('suggestion-reason-codes')).toBeInTheDocument();
    expect(screen.getByTestId('source-redundancy-recommendations')).toBeInTheDocument();
    expect(screen.getByTestId('review-suggestion-locks')).toBeInTheDocument();
  });

  it('shows evidence-bearing advisory suggestions and descriptive matrix status', () => {
    render(<ReviewSuggestionMatrixPanel bundle={sampleProjectionBundle} packetsBundle={null} />);

    expect(screen.getByTestId('review-suggestion-summary').textContent).toContain('SUGGESTIONS');
    expect(screen.getByTestId('suggestion-reason-codes').textContent).toContain('REASON CODESTRUE');
    expect(screen.getByTestId('suggestion-reason-codes').textContent).toContain('REQUIRED EVIDENCETRUE');
    expect(screen.getByTestId('source-redundancy-recommendations').textContent).toContain('COMPARISON ONLYTRUE');
  });

  it('does not expose controls or authority-bearing locks as true', () => {
    render(<ReviewSuggestionMatrixPanel bundle={sampleProjectionBundle} packetsBundle={null} />);

    expect(screen.queryAllByRole('button')).toHaveLength(0);
    const locks = screen.getByTestId('review-suggestion-locks');
    expect(locks.textContent).toContain('NOTION WRITEFALSE');
    expect(locks.textContent).toContain('WEBSOCKETFALSE');
    expect(locks.textContent).toContain('AUTO EXECUTIONFALSE');
    expect(locks.textContent).toContain('OUTCOME RESOLVEFALSE');
    expect(locks.textContent).toContain('CORRECTION APPLYFALSE');
    expect(locks.textContent).toContain('FORECAST MUTATIONFALSE');
    expect(locks.textContent).toContain('SCORE MUTATIONFALSE');
    expect(locks.textContent).toContain('ROUTING MUTATIONFALSE');
  });
});
