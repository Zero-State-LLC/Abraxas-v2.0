import { describe, it, expect, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { PacketDiffViewerPanel } from './PacketDiffViewerPanel';
import type { OperatorActionPacketsBundle } from '../types';

afterEach(cleanup);

const AUTHORITY = {
  execution_allowed: false as const,
  runtime_mutation_allowed: false as const,
  promotion_allowed: false as const,
  production_activation_allowed: false as const,
  metric_emission_allowed: false as const,
  forecast_influence_allowed: false as const,
  p43_lanes_allowed: false as const,
};

const sampleBundle: OperatorActionPacketsBundle = {
  schema_version: 'AALViz.OperatorActionPackets.v0.1',
  generated_at: '2026-05-30T00:00:00Z',
  authority: AUTHORITY,
  source_projection_bundle_hash: null,
  fail_closed_reason: null,
  packets: [
    {
      packet_id: 'pkt-pdv-alpha',
      source_frontier_ref: null,
      action_title: 'Alpha Diff Packet',
      action_type: 'COPY_PROMPT',
      operator_id: 'OP-001',
      subsystem_id: 'SYS-A',
      recommended_next_step: 'Copy prompt and review',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: 'Alpha prompt body text.',
      validation_checklist: ['[ ] 1. Check A', '[ ] 2. Check B', '[ ] 3. Check C'],
      blocked_scopes: ['EXECUTION_BLOCKED', 'MUTATION_BLOCKED'],
      provenance_refs: ['ref-001:abc', 'ref-002:def'],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-pdv-beta',
      source_frontier_ref: null,
      action_title: 'Beta Diff Packet',
      action_type: 'COPY_CHECKLIST',
      operator_id: 'OP-002',
      subsystem_id: 'SYS-B',
      recommended_next_step: 'Copy checklist and verify steps',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: '',
      validation_checklist: ['[ ] Step one', '[ ] Step two'],
      blocked_scopes: ['PROMOTION_BLOCKED'],
      provenance_refs: [],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-pdv-gamma',
      source_frontier_ref: null,
      action_title: 'Gamma Diff Packet',
      action_type: 'REVIEW_REQUIRED',
      operator_id: 'OP-003',
      subsystem_id: 'SYS-C',
      recommended_next_step: 'Manual operator review',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: 'Gamma prompt body text.',
      validation_checklist: [],
      blocked_scopes: [],
      provenance_refs: ['ref-003:xyz'],
      fail_closed_reason: null,
    },
  ],
};

describe('PacketDiffViewerPanel', () => {
  describe('null bundle (empty state)', () => {
    it('renders the panel', () => {
      render(<PacketDiffViewerPanel packetsBundle={null} />);
      expect(screen.getByTestId('packet-diff-viewer-panel')).toBeInTheDocument();
    });

    it('shows fail-closed empty state', () => {
      render(<PacketDiffViewerPanel packetsBundle={null} />);
      expect(screen.getByTestId('pdv-empty').textContent).toMatch(/FAIL CLOSED/i);
    });
  });

  describe('panel renders with bundle', () => {
    it('renders the panel', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('packet-diff-viewer-panel')).toBeInTheDocument();
      expect(screen.queryByTestId('pdv-empty')).toBeNull();
    });

    it('shows READ_ONLY · DISPLAY_ONLY notice', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('packet-diff-viewer-panel');
      expect(panel.textContent).toMatch(/READ_ONLY/);
      expect(panel.textContent).toMatch(/DISPLAY_ONLY/);
    });
  });

  describe('packet selectors', () => {
    it('renders left and right selectors', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('pdv-left-select')).toBeInTheDocument();
      expect(screen.getByTestId('pdv-right-select')).toBeInTheDocument();
    });

    it('left selector defaults to first packet', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      const left = screen.getByTestId('pdv-left-select') as HTMLSelectElement;
      expect(left.value).toBe('pkt-pdv-alpha');
    });

    it('right selector defaults to second packet', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      const right = screen.getByTestId('pdv-right-select') as HTMLSelectElement;
      expect(right.value).toBe('pkt-pdv-beta');
    });

    it('both selectors show all 3 packets as options', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      const left = screen.getByTestId('pdv-left-select') as HTMLSelectElement;
      expect(left.options.length).toBe(3);
    });
  });

  describe('same packet state', () => {
    it('shows same-packet message when both selectors point to same packet', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      const right = screen.getByTestId('pdv-right-select');
      fireEvent.change(right, { target: { value: 'pkt-pdv-alpha' } });
      expect(screen.getByTestId('pdv-same-packet')).toBeInTheDocument();
      expect(screen.getByTestId('pdv-same-packet').textContent).toMatch(/SAME PACKET SELECTED/);
    });

    it('hides diff table when same packet selected', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      fireEvent.change(screen.getByTestId('pdv-right-select'), {
        target: { value: 'pkt-pdv-alpha' },
      });
      expect(screen.queryByTestId('pdv-diff-table')).toBeNull();
    });
  });

  describe('different packet comparison', () => {
    it('renders diff table when two different packets selected', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('pdv-diff-table')).toBeInTheDocument();
    });

    it('action_type row shows DIFFERENT for alpha vs beta', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      const statusEl = screen.getByTestId('pdv-diff-status-action_type');
      expect(statusEl.textContent).toBe('≠');
    });

    it('left action_type shows COPY_PROMPT', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('pdv-left-val-action_type').textContent).toBe('COPY_PROMPT');
    });

    it('right action_type shows COPY_CHECKLIST', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('pdv-right-val-action_type').textContent).toBe('COPY_CHECKLIST');
    });

    it('execution_allowed row shows SAME (both false)', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('pdv-diff-status-execution_allowed').textContent).toBe('=');
    });

    it('validation_checklist_count row: left=3, right=2, DIFFERENT', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('pdv-left-val-validation_checklist_count').textContent).toBe('3');
      expect(screen.getByTestId('pdv-right-val-validation_checklist_count').textContent).toBe('2');
      expect(screen.getByTestId('pdv-diff-status-validation_checklist_count').textContent).toBe('≠');
    });

    it('provenance_ref_count row: left=2, right=0, DIFFERENT', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('pdv-left-val-provenance_ref_count').textContent).toBe('2');
      expect(screen.getByTestId('pdv-right-val-provenance_ref_count').textContent).toBe('0');
    });

    it('shows legend', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('pdv-legend')).toBeInTheDocument();
    });

    it('switching right selector updates diff', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      fireEvent.change(screen.getByTestId('pdv-right-select'), {
        target: { value: 'pkt-pdv-gamma' },
      });
      expect(screen.getByTestId('pdv-right-val-action_type').textContent).toBe('REVIEW_REQUIRED');
    });
  });

  describe('authority clean', () => {
    it('shows AUTHORITY_CLEAN when both packets have all flags false', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('pdv-authority-clean')).toBeInTheDocument();
      expect(screen.getByTestId('pdv-authority-clean').textContent).toMatch(/AUTHORITY_CLEAN/);
    });

    it('no authority-violation banner shown on clean packets', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      expect(screen.queryByTestId('pdv-authority-violation')).toBeNull();
    });
  });

  describe('authority violation', () => {
    it('shows FAIL_CLOSED when left packet has execution_allowed=true', () => {
      const violatingBundle = {
        ...sampleBundle,
        packets: [
          { ...sampleBundle.packets[0], execution_allowed: true as unknown as false },
          ...sampleBundle.packets.slice(1),
        ],
      } as OperatorActionPacketsBundle;
      render(<PacketDiffViewerPanel packetsBundle={violatingBundle} />);
      expect(screen.getByTestId('pdv-authority-violation')).toBeInTheDocument();
      expect(screen.getByTestId('pdv-authority-violation').textContent).toMatch(
        /AUTHORITY_DIFF_VIOLATION/,
      );
    });

    it('hides AUTHORITY_CLEAN when violation present', () => {
      const violatingBundle = {
        ...sampleBundle,
        packets: [
          { ...sampleBundle.packets[0], execution_allowed: true as unknown as false },
          ...sampleBundle.packets.slice(1),
        ],
      } as OperatorActionPacketsBundle;
      render(<PacketDiffViewerPanel packetsBundle={violatingBundle} />);
      expect(screen.queryByTestId('pdv-authority-clean')).toBeNull();
    });
  });

  describe('authority boundary display', () => {
    it('shows NO_BACKEND_WRITES in footer', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('packet-diff-viewer-panel');
      expect(panel.textContent).toMatch(/NO_BACKEND_WRITES/);
      expect(panel.textContent).toMatch(/NO_PERSISTENCE/);
    });

    it('has no enabled execute/promote/mutate buttons', () => {
      render(<PacketDiffViewerPanel packetsBundle={sampleBundle} />);
      const buttons = document.querySelectorAll('button:not([disabled])');
      const forbidden = /execute|promote|mutate|activate|publish|runtime|force/i;
      buttons.forEach((btn) => {
        expect(btn.textContent ?? '').not.toMatch(forbidden);
      });
    });
  });
});
