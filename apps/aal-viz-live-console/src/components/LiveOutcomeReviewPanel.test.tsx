import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { LiveOutcomeReviewPanel } from './LiveOutcomeReviewPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';
import type { LiveConsoleProjectionBundle, OperatorActionPacketsBundle } from '../types';

const LOCKED_PACKET_AUTHORITY = {
  execution_allowed: false as const,
  runtime_mutation_allowed: false as const,
  promotion_allowed: false as const,
  production_activation_allowed: false as const,
  metric_emission_allowed: false as const,
  forecast_influence_allowed: false as const,
  p43_lanes_allowed: false as const,
};

const SAMPLE_PACKETS: OperatorActionPacketsBundle = {
  schema_version: 'AALViz.OperatorActionPackets.v0.1',
  generated_at: '2026-05-30T00:00:00Z',
  authority: LOCKED_PACKET_AUTHORITY,
  source_projection_bundle_hash: null,
  fail_closed_reason: null,
  packets: [
    {
      packet_id: 'review-pkt-001',
      source_frontier_ref: 'forecast-outcome-pkt-001',
      action_title: 'REVIEW DECISION',
      action_type: 'REVIEW_REQUIRED',
      recommended_next_step: 'REVIEW_LOW_PROVENANCE',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false,
      runtime_mutation_allowed: false,
      promotion_allowed: false,
      prompt_body: 'Review the low-provenance outcome candidate.',
      validation_checklist: ['confirm outcome'],
      blocked_scopes: ['EXECUTION', 'FORECAST_MUTATION'],
      provenance_refs: ['forecast-outcome-pkt-001'],
      fail_closed_reason: null,
    },
  ],
};

function bundleWithOutcome(): LiveConsoleProjectionBundle {
  return {
    ...sampleProjectionBundle,
    systems: [
      {
        ...sampleProjectionBundle.systems[0],
        projection_packets: [
          {
            packet_id: 'forecast-outcome-pkt-001',
            packet_type: 'FORECAST_OUTCOME_RESOLUTION',
            status: 'RESOLVED',
            display_value: '1',
            authority_source: 'SHADOW_LANE',
            projection_only: true,
          },
        ],
      },
      ...sampleProjectionBundle.systems.slice(1),
    ],
  };
}

afterEach(cleanup);

describe('LiveOutcomeReviewPanel', () => {
  it('renders live feed, review queue, pending tracker, correction workflow, and locks', () => {
    render(<LiveOutcomeReviewPanel bundle={bundleWithOutcome()} packetsBundle={SAMPLE_PACKETS} />);

    expect(screen.getByTestId('live-outcome-review-panel')).toBeInTheDocument();
    expect(screen.getByTestId('live-outcome-summary')).toBeInTheDocument();
    expect(screen.getByTestId('live-outcome-feed')).toBeInTheDocument();
    expect(screen.getByTestId('decision-review-queue')).toBeInTheDocument();
    expect(screen.getByTestId('pending-resolution-tracker')).toBeInTheDocument();
    expect(screen.getByTestId('correction-workflow-panel')).toBeInTheDocument();
    expect(screen.getByTestId('live-outcome-locks')).toBeInTheDocument();
  });

  it('shows candidate outcomes and low-provenance review state without resolution authority', () => {
    render(<LiveOutcomeReviewPanel bundle={bundleWithOutcome()} packetsBundle={SAMPLE_PACKETS} />);

    expect(screen.getByTestId('live-outcome-summary').textContent).toContain('FEED PACKETS');
    expect(screen.getByTestId('live-outcome-feed').textContent).toContain('RESOLVED');
    expect(screen.getByTestId('decision-review-queue').textContent).toContain('LOW_PROVENANCE');
    expect(screen.getByTestId('correction-workflow-panel').textContent).toContain('RESOLUTION AUTHORITYFALSE');
  });

  it('does not expose controls or authority-bearing locks as true', () => {
    render(<LiveOutcomeReviewPanel bundle={bundleWithOutcome()} packetsBundle={SAMPLE_PACKETS} />);

    expect(screen.queryAllByRole('button')).toHaveLength(0);
    const locks = screen.getByTestId('live-outcome-locks');
    expect(locks.textContent).toContain('PROVIDER POLLINGFALSE');
    expect(locks.textContent).toContain('NOTION WRITEFALSE');
    expect(locks.textContent).toContain('WEBSOCKETFALSE');
    expect(locks.textContent).toContain('AUTO EXECUTIONFALSE');
    expect(locks.textContent).toContain('FORECAST MUTATIONFALSE');
    expect(locks.textContent).toContain('SCORE MUTATIONFALSE');
    expect(locks.textContent).toContain('ROUTING MUTATIONFALSE');
    expect(locks.textContent).toContain('TRUTH AUTHORITYFALSE');
  });
});
