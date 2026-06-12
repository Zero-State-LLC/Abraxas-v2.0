import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { OperatorDecisionOutcomePanel } from './OperatorDecisionOutcomePanel';
import type { OperatorActionPacketsBundle } from '../types';

const LOCKED_PACKET_AUTHORITY = {
  execution_allowed: false as const,
  runtime_mutation_allowed: false as const,
  promotion_allowed: false as const,
  production_activation_allowed: false as const,
  metric_emission_allowed: false as const,
  forecast_influence_allowed: false as const,
  p43_lanes_allowed: false as const,
};

const SAMPLE_BUNDLE: OperatorActionPacketsBundle = {
  schema_version: 'AALViz.OperatorActionPackets.v0.1',
  generated_at: '2026-05-30T00:00:00Z',
  authority: LOCKED_PACKET_AUTHORITY,
  source_projection_bundle_hash: null,
  fail_closed_reason: null,
  packets: [
    {
      packet_id: 'test-pkt-001',
      source_frontier_ref: 'run-001',
      action_title: 'TEST ACTION PACKET',
      action_type: 'COPY_CHECKLIST',
      recommended_next_step: 'ANNOTATE_REVIEW',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false,
      runtime_mutation_allowed: false,
      promotion_allowed: false,
      prompt_body: 'Test prompt body content.',
      validation_checklist: ['step-1', 'step-2'],
      blocked_scopes: ['EXECUTION', 'MUTATION', 'PROMOTION'],
      provenance_refs: ['forecast-001', 'strategy-001'],
      fail_closed_reason: null,
    },
  ],
};

afterEach(cleanup);

describe('OperatorDecisionOutcomePanel', () => {
  it('renders summary, decision packets, outcome attribution, quality badge, and locks', () => {
    render(<OperatorDecisionOutcomePanel packetsBundle={SAMPLE_BUNDLE} />);

    expect(screen.getByTestId('operator-decision-outcome-panel')).toBeInTheDocument();
    expect(screen.getByTestId('operator-decision-summary')).toBeInTheDocument();
    expect(screen.getByTestId('operator-decision-packets')).toBeInTheDocument();
    expect(screen.getByTestId('decision-outcome-attributions')).toBeInTheDocument();
    expect(screen.getByTestId('decision-quality-badge')).toBeInTheDocument();
    expect(screen.getByTestId('operator-decision-locks')).toBeInTheDocument();
  });

  it('shows pending, not-computable attribution with explicit missing quality score', () => {
    render(<OperatorDecisionOutcomePanel packetsBundle={SAMPLE_BUNDLE} />);

    expect(screen.getByTestId('operator-decision-summary').textContent).toContain('PENDING');
    expect(screen.getByTestId('operator-decision-summary').textContent).toContain('NOT_COMPUTABLE');
    expect(screen.getByTestId('decision-outcome-attributions').textContent).toContain('PENDING');
    expect(screen.getByTestId('decision-outcome-attributions').textContent).toContain('NOT_COMPUTABLE');
    expect(screen.getByTestId('decision-quality-badge').textContent).toContain('QUALITY SCORENOT_COMPUTABLE');
  });

  it('does not expose decision controls or authority-bearing locks as true', () => {
    render(<OperatorDecisionOutcomePanel packetsBundle={SAMPLE_BUNDLE} />);

    expect(screen.queryAllByRole('button')).toHaveLength(0);
    const locks = screen.getByTestId('operator-decision-locks');
    expect(locks.textContent).toContain('NOTION WRITEFALSE');
    expect(locks.textContent).toContain('WEBSOCKETFALSE');
    expect(locks.textContent).toContain('AUTO EXECUTIONFALSE');
    expect(locks.textContent).toContain('FORECAST MUTATIONFALSE');
    expect(locks.textContent).toContain('SCORE MUTATIONFALSE');
    expect(locks.textContent).toContain('ROUTING MUTATIONFALSE');
    expect(locks.textContent).toContain('AUTHORITY MUTATIONFALSE');
  });

  it('renders a closed empty projection without a loaded operator action bundle', () => {
    render(<OperatorDecisionOutcomePanel packetsBundle={null} />);

    expect(screen.getByTestId('operator-decision-summary').textContent).toContain('0 DECISIONS');
    expect(screen.getByTestId('operator-decision-packets').textContent).toContain('NO OPERATOR DECISION PACKETS');
    expect(screen.getByTestId('decision-outcome-attributions').textContent).toContain('NO OUTCOME JOINS');
  });
});
