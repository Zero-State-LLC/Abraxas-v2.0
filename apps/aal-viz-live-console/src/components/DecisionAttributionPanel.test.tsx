import { describe, it, expect, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { DecisionAttributionPanel } from './DecisionAttributionPanel';
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
      packet_id: 'pkt-alpha-dap',
      source_frontier_ref: null,
      action_title: 'Alpha Attribution Packet',
      action_type: 'COPY_PROMPT',
      operator_id: 'OP-001',
      subsystem_id: 'SYS-A',
      recommended_next_step: 'Review and attribute',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: 'Prompt text.',
      validation_checklist: ['[ ] 1. Check A'],
      blocked_scopes: ['EXECUTION_BLOCKED'],
      provenance_refs: [],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-beta-dap',
      source_frontier_ref: null,
      action_title: 'Beta Attribution Packet',
      action_type: 'COPY_CHECKLIST',
      operator_id: 'OP-002',
      subsystem_id: 'SYS-B',
      recommended_next_step: 'Review checklist',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: '',
      validation_checklist: ['[ ] 1. Step one', '[ ] 2. Step two'],
      blocked_scopes: [],
      provenance_refs: [],
      fail_closed_reason: null,
    },
  ],
};

describe('DecisionAttributionPanel', () => {
  describe('null bundle (empty state)', () => {
    it('renders the panel', () => {
      render(<DecisionAttributionPanel packetsBundle={null} />);
      expect(screen.getByTestId('decision-attribution-panel')).toBeInTheDocument();
    });

    it('shows fail-closed empty state', () => {
      render(<DecisionAttributionPanel packetsBundle={null} />);
      expect(screen.getByTestId('dap-empty').textContent).toMatch(/FAIL CLOSED/i);
    });

    it('shows UI_ONLY warning even when no bundle', () => {
      render(<DecisionAttributionPanel packetsBundle={null} />);
      expect(screen.getByTestId('dap-warning').textContent).toMatch(/UI_ONLY/);
      expect(screen.getByTestId('dap-warning').textContent).toMatch(/DOES NOT UPDATE REPO/i);
    });
  });

  describe('panel renders with bundle', () => {
    it('renders the panel', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('decision-attribution-panel')).toBeInTheDocument();
    });

    it('shows UI_ONLY · NON_AUTHORITATIVE header notice', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('decision-attribution-panel');
      expect(panel.textContent).toMatch(/UI_ONLY/);
      expect(panel.textContent).toMatch(/NON_AUTHORITATIVE/);
    });

    it('shows warning banner', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('dap-warning').textContent).toMatch(/DOES NOT UPDATE REPO/i);
    });
  });

  describe('packet selector', () => {
    it('shows dropdown with all packets', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      const select = screen.getByTestId('dap-packet-select') as HTMLSelectElement;
      expect(select.options.length).toBe(2);
      expect(select.options[0].text).toBe('Alpha Attribution Packet');
      expect(select.options[1].text).toBe('Beta Attribution Packet');
    });

    it('defaults to first packet', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      const select = screen.getByTestId('dap-packet-select') as HTMLSelectElement;
      expect(select.value).toBe('pkt-alpha-dap');
    });

    it('shows packet_id of selected packet', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('dap-packet-id').textContent).toBe('pkt-alpha-dap');
    });

    it('switching packet updates packet_id display', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      const select = screen.getByTestId('dap-packet-select');
      fireEvent.change(select, { target: { value: 'pkt-beta-dap' } });
      expect(screen.getByTestId('dap-packet-id').textContent).toBe('pkt-beta-dap');
    });

    it('switching packet preserves independent attribution state per packet', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('dap-outcome-btn-MERGED'));
      const select = screen.getByTestId('dap-packet-select');
      fireEvent.change(select, { target: { value: 'pkt-beta-dap' } });
      expect(screen.getByTestId('dap-current-outcome').textContent).toBe('UNKNOWN');
      fireEvent.change(select, { target: { value: 'pkt-alpha-dap' } });
      expect(screen.getByTestId('dap-current-outcome').textContent).toBe('MERGED');
    });
  });

  describe('default outcome', () => {
    it('defaults outcome to UNKNOWN for all packets', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('dap-current-outcome').textContent).toBe('UNKNOWN');
    });

    it('UNKNOWN outcome button is active by default', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      expect(
        screen.getByTestId('dap-outcome-btn-UNKNOWN').className,
      ).toContain('dap-outcome-btn--active');
    });

    it('all 5 outcome buttons are rendered', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      for (const status of ['UNKNOWN', 'MERGED', 'FAILED', 'HELD', 'SUPERSEDED']) {
        expect(screen.getByTestId(`dap-outcome-btn-${status}`)).toBeInTheDocument();
      }
    });
  });

  describe('local outcome changes', () => {
    it('clicking MERGED sets outcome to MERGED', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('dap-outcome-btn-MERGED'));
      expect(screen.getByTestId('dap-current-outcome').textContent).toBe('MERGED');
    });

    it('clicking FAILED sets outcome to FAILED', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('dap-outcome-btn-FAILED'));
      expect(screen.getByTestId('dap-current-outcome').textContent).toBe('FAILED');
    });

    it('clicking HELD sets outcome to HELD', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('dap-outcome-btn-HELD'));
      expect(screen.getByTestId('dap-current-outcome').textContent).toBe('HELD');
    });

    it('clicking SUPERSEDED sets outcome to SUPERSEDED', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('dap-outcome-btn-SUPERSEDED'));
      expect(screen.getByTestId('dap-current-outcome').textContent).toBe('SUPERSEDED');
    });

    it('active outcome button updates to newly clicked status', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('dap-outcome-btn-HELD'));
      expect(screen.getByTestId('dap-outcome-btn-HELD').className).toContain(
        'dap-outcome-btn--active',
      );
      expect(screen.getByTestId('dap-outcome-btn-UNKNOWN').className).not.toContain(
        'dap-outcome-btn--active',
      );
    });
  });

  describe('local text fields', () => {
    it('linked PR input starts empty', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      const input = screen.getByTestId('dap-linked-pr') as HTMLInputElement;
      expect(input.value).toBe('');
    });

    it('typing in linked PR input updates value', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      const input = screen.getByTestId('dap-linked-pr') as HTMLInputElement;
      fireEvent.change(input, { target: { value: '#380' } });
      expect(input.value).toBe('#380');
    });

    it('linked PR appears in current summary after typing', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      fireEvent.change(screen.getByTestId('dap-linked-pr'), {
        target: { value: '#380' },
      });
      expect(screen.getByTestId('dap-summary-pr').textContent).toContain('#380');
    });

    it('manual result textarea starts empty', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      const ta = screen.getByTestId('dap-manual-result') as HTMLTextAreaElement;
      expect(ta.value).toBe('');
    });

    it('typing in manual result updates value', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      const ta = screen.getByTestId('dap-manual-result') as HTMLTextAreaElement;
      fireEvent.change(ta, { target: { value: 'Merged at 2026-05-30' } });
      expect(ta.value).toBe('Merged at 2026-05-30');
    });
  });

  describe('authority boundary', () => {
    it('shows NO_EXECUTION footer', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('decision-attribution-panel');
      expect(panel.textContent).toMatch(/NO_EXECUTION/);
      expect(panel.textContent).toMatch(/NO_BACKEND_WRITES/);
      expect(panel.textContent).toMatch(/NO_PERSISTENCE/);
    });

    it('has no enabled execute/promote/mutate buttons', () => {
      render(<DecisionAttributionPanel packetsBundle={sampleBundle} />);
      const buttons = document.querySelectorAll('button:not([disabled])');
      const forbidden = /execute|promote|mutate|activate|publish|runtime|force/i;
      buttons.forEach((btn) => {
        expect(btn.textContent ?? '').not.toMatch(forbidden);
      });
    });
  });
});
