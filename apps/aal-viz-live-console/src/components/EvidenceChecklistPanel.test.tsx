import { describe, it, expect, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { EvidenceChecklistPanel } from './EvidenceChecklistPanel';
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
      packet_id: 'pkt-checklist-alpha',
      source_frontier_ref: null,
      action_title: 'Alpha Checklist Packet',
      action_type: 'COPY_CHECKLIST',
      operator_id: 'OP-001',
      subsystem_id: 'SYS-A',
      recommended_next_step: 'Review checklist items',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: '',
      validation_checklist: [
        '[ ] 1. Verify gate artifact sealed',
        '[ ] 2. Confirm all constants locked',
        '[ ] 3. Run doctrine validator',
      ],
      blocked_scopes: ['EXECUTION_BLOCKED', 'MUTATION_BLOCKED'],
      provenance_refs: ['gate-001:abc123', 'receipt-001:def456'],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-prompt-beta',
      source_frontier_ref: null,
      action_title: 'Beta Prompt Packet',
      action_type: 'COPY_PROMPT',
      operator_id: 'OP-002',
      subsystem_id: 'SYS-B',
      recommended_next_step: 'Copy prompt and review',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: 'This is the prompt text.',
      validation_checklist: ['[ ] 1. Step one', '[ ] 2. Step two'],
      blocked_scopes: ['PROMOTION_BLOCKED'],
      provenance_refs: [],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-no-checklist',
      source_frontier_ref: null,
      action_title: 'No Checklist Packet',
      action_type: 'REVIEW_REQUIRED',
      operator_id: 'OP-003',
      subsystem_id: 'SYS-C',
      recommended_next_step: 'Manual review',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: 'Review carefully.',
      validation_checklist: [],
      blocked_scopes: [],
      provenance_refs: [],
      fail_closed_reason: null,
    },
  ],
};

describe('EvidenceChecklistPanel', () => {
  describe('null bundle (empty state)', () => {
    it('renders the panel', () => {
      render(<EvidenceChecklistPanel packetsBundle={null} />);
      expect(screen.getByTestId('evidence-checklist-panel')).toBeInTheDocument();
    });

    it('shows fail-closed empty state when no bundle', () => {
      render(<EvidenceChecklistPanel packetsBundle={null} />);
      expect(screen.getByTestId('ecl-empty').textContent).toMatch(/FAIL CLOSED/i);
    });
  });

  describe('panel renders with bundle', () => {
    it('renders the panel with a bundle', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('evidence-checklist-panel')).toBeInTheDocument();
    });

    it('shows packet selector dropdown with all packets', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const select = screen.getByTestId('ecl-packet-select') as HTMLSelectElement;
      expect(select.options.length).toBe(3);
      expect(select.options[0].text).toBe('Alpha Checklist Packet');
      expect(select.options[1].text).toBe('Beta Prompt Packet');
    });

    it('defaults to first packet', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const select = screen.getByTestId('ecl-packet-select') as HTMLSelectElement;
      expect(select.value).toBe('pkt-checklist-alpha');
    });

    it('shows UI_ONLY · NON_AUTHORITATIVE notice', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('evidence-checklist-panel');
      expect(panel.textContent).toMatch(/UI_ONLY/);
      expect(panel.textContent).toMatch(/NON_AUTHORITATIVE/);
    });
  });

  describe('checklist items', () => {
    it('renders all 3 checklist items for first packet', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('ecl-item-0')).toBeInTheDocument();
      expect(screen.getByTestId('ecl-item-1')).toBeInTheDocument();
      expect(screen.getByTestId('ecl-item-2')).toBeInTheDocument();
    });

    it('strips [ ] prefix from checklist item text', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const item0 = screen.getByTestId('ecl-item-0');
      expect(item0.textContent).not.toMatch(/^\[\s*\]/);
      expect(item0.textContent).toContain('Verify gate artifact sealed');
    });

    it('shows checklist progress counter', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const progress = screen.getByTestId('ecl-progress');
      expect(progress.textContent).toContain('0');
      expect(progress.textContent).toContain('3');
    });

    it('shows fail-closed when selected packet has no checklist', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const select = screen.getByTestId('ecl-packet-select');
      fireEvent.change(select, { target: { value: 'pkt-no-checklist' } });
      expect(screen.getByTestId('ecl-no-checklist').textContent).toMatch(/FAIL CLOSED/i);
    });
  });

  describe('local toggle behavior', () => {
    it('all checkboxes start unchecked', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const cb0 = screen.getByTestId('ecl-checkbox-0') as HTMLInputElement;
      const cb1 = screen.getByTestId('ecl-checkbox-1') as HTMLInputElement;
      const cb2 = screen.getByTestId('ecl-checkbox-2') as HTMLInputElement;
      expect(cb0.checked).toBe(false);
      expect(cb1.checked).toBe(false);
      expect(cb2.checked).toBe(false);
    });

    it('clicking checkbox toggles it checked', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const cb0 = screen.getByTestId('ecl-checkbox-0') as HTMLInputElement;
      fireEvent.click(cb0);
      expect(cb0.checked).toBe(true);
    });

    it('clicking checkbox twice returns it to unchecked', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const cb0 = screen.getByTestId('ecl-checkbox-0') as HTMLInputElement;
      fireEvent.click(cb0);
      fireEvent.click(cb0);
      expect(cb0.checked).toBe(false);
    });

    it('progress counter increments when items checked', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('ecl-checkbox-0'));
      fireEvent.click(screen.getByTestId('ecl-checkbox-2'));
      const progress = screen.getByTestId('ecl-progress');
      expect(progress.textContent).toContain('2');
      expect(progress.textContent).toContain('3');
    });

    it('switching packet resets all toggles', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('ecl-checkbox-0'));
      const select = screen.getByTestId('ecl-packet-select');
      fireEvent.change(select, { target: { value: 'pkt-prompt-beta' } });
      const cb0 = screen.getByTestId('ecl-checkbox-0') as HTMLInputElement;
      expect(cb0.checked).toBe(false);
    });

    it('progress shows [UI_ONLY] label', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('ecl-progress').textContent).toMatch(/\[UI_ONLY\]/);
    });
  });

  describe('authority locks', () => {
    it('shows EXEC BLOCKED lock', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('ecl-lock-execution').textContent).toMatch(/EXEC BLOCKED/);
    });

    it('shows MUTATION BLOCKED lock', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('ecl-lock-mutation').textContent).toMatch(/MUTATION BLOCKED/);
    });

    it('shows PROMOTION BLOCKED lock', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('ecl-lock-promotion').textContent).toMatch(/PROMOTION BLOCKED/);
    });
  });

  describe('blocked scopes', () => {
    it('shows blocked scopes for first packet', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const scopes = screen.getByTestId('ecl-blocked-scopes');
      expect(scopes.textContent).toContain('EXECUTION_BLOCKED');
      expect(scopes.textContent).toContain('MUTATION_BLOCKED');
    });

    it('shows different scopes after switching packet', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const select = screen.getByTestId('ecl-packet-select');
      fireEvent.change(select, { target: { value: 'pkt-prompt-beta' } });
      const scopes = screen.getByTestId('ecl-blocked-scopes');
      expect(scopes.textContent).toContain('PROMOTION_BLOCKED');
    });

    it('hides blocked-scopes section when packet has none', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const select = screen.getByTestId('ecl-packet-select');
      fireEvent.change(select, { target: { value: 'pkt-no-checklist' } });
      expect(screen.queryByTestId('ecl-blocked-scopes')).toBeNull();
    });
  });

  describe('provenance refs', () => {
    it('shows provenance refs for first packet', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const prov = screen.getByTestId('ecl-provenance-refs');
      expect(prov.textContent).toContain('gate-001:abc123');
      expect(prov.textContent).toContain('receipt-001:def456');
    });

    it('hides provenance refs section when packet has none', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const select = screen.getByTestId('ecl-packet-select');
      fireEvent.change(select, { target: { value: 'pkt-prompt-beta' } });
      expect(screen.queryByTestId('ecl-provenance-refs')).toBeNull();
    });
  });

  describe('authority boundary', () => {
    it('shows NO_EXECUTION footer', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('evidence-checklist-panel');
      expect(panel.textContent).toMatch(/NO_EXECUTION/);
      expect(panel.textContent).toMatch(/NO_BACKEND_WRITES/);
      expect(panel.textContent).toMatch(/NO_PERSISTENCE/);
    });

    it('has no enabled execute/promote/mutate buttons', () => {
      render(<EvidenceChecklistPanel packetsBundle={sampleBundle} />);
      const buttons = document.querySelectorAll('button:not([disabled])');
      const forbidden = /execute|promote|mutate|activate|publish|runtime|force/i;
      buttons.forEach((btn) => {
        expect(btn.textContent ?? '').not.toMatch(forbidden);
      });
    });
  });
});
