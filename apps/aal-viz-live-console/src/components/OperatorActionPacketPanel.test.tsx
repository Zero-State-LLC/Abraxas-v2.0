import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OperatorActionPacketPanel } from './OperatorActionPacketPanel';
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
      source_frontier_ref: null,
      action_title: 'TEST ACTION PACKET',
      action_type: 'COPY_PROMPT',
      recommended_next_step: 'REVIEW_AND_COPY',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false,
      runtime_mutation_allowed: false,
      promotion_allowed: false,
      prompt_body: 'Test prompt body content.',
      validation_checklist: ['step-1', 'step-2'],
      blocked_scopes: ['EXECUTION', 'MUTATION', 'PROMOTION'],
      provenance_refs: ['ref-001'],
      fail_closed_reason: null,
    },
  ],
};

describe('OperatorActionPacketPanel — null bundle', () => {
  it('renders the panel with null bundle', () => {
    render(<OperatorActionPacketPanel packetsBundle={null} />);
    expect(screen.getByTestId('operator-action-packet-panel')).toBeInTheDocument();
  });

  it('shows empty state message when bundle is null', () => {
    render(<OperatorActionPacketPanel packetsBundle={null} />);
    expect(screen.getByText(/build_aal_viz_operator_action_packets/i)).toBeInTheDocument();
  });

  it('shows display/copy only notice', () => {
    render(<OperatorActionPacketPanel packetsBundle={null} />);
    expect(screen.getByText(/display\/copy only/i)).toBeInTheDocument();
  });
});

describe('OperatorActionPacketPanel — with bundle', () => {
  it('renders the panel with a bundle', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    expect(screen.getByTestId('operator-action-packet-panel')).toBeInTheDocument();
  });

  it('renders the packet action title', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    expect(screen.getByText('TEST ACTION PACKET')).toBeInTheDocument();
  });

  it('shows COPY ONLY badge in header', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    const matches = screen.getAllByText(/COPY ONLY/i);
    expect(matches.length).toBeGreaterThanOrEqual(1);
  });

  it('shows display/copy only notice', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    expect(screen.getByText(/display\/copy only/i)).toBeInTheDocument();
  });

  it('shows no auto-apply notice', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    expect(screen.getByText(/No auto-apply/i)).toBeInTheDocument();
  });

  it('shows exec blocked lock indicator', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    expect(screen.getByText(/EXEC BLOCKED/i)).toBeInTheDocument();
  });

  it('shows mutation blocked lock indicator', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    expect(screen.getByText(/MUTATION BLOCKED/i)).toBeInTheDocument();
  });

  it('shows promotion blocked lock indicator', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    expect(screen.getByText(/PROMOTION BLOCKED/i)).toBeInTheDocument();
  });

  it('has no enabled execution buttons', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    const allButtons = screen.getAllByRole('button');
    const execLabels = ['execute', 'activate', 'promote', 'mutate'];
    const enabledExec = allButtons.filter((btn) => {
      const label = (btn.textContent ?? '').toLowerCase();
      return execLabels.some((d) => label.includes(d)) && !btn.hasAttribute('disabled');
    });
    expect(enabledExec).toHaveLength(0);
  });

  it('copy button is enabled (display action only)', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    const copyBtn = screen.getByRole('button', { name: /COPY/i });
    expect(copyBtn).not.toBeDisabled();
  });

  it('copy button is not an execute action', () => {
    render(<OperatorActionPacketPanel packetsBundle={SAMPLE_BUNDLE} />);
    const copyBtn = screen.getByRole('button', { name: /COPY/i });
    expect(copyBtn.textContent).toMatch(/COPY/i);
    expect(copyBtn.textContent).not.toMatch(/execute|activate|promote|mutate/i);
  });
});
