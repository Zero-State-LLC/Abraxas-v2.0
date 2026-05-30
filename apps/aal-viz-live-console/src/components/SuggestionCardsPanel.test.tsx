import { describe, it, expect, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { SuggestionCardsPanel } from './SuggestionCardsPanel';
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
      packet_id: 'pkt-scp-alpha',
      source_frontier_ref: null,
      action_title: 'Alpha Suggestion Packet',
      action_type: 'COPY_PROMPT',
      operator_id: 'OP-001',
      subsystem_id: 'SYS-A',
      recommended_next_step: 'Copy prompt and review with team',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: 'Prompt text here.',
      validation_checklist: ['[ ] 1. Check A', '[ ] 2. Check B'],
      blocked_scopes: ['EXECUTION_BLOCKED', 'MUTATION_BLOCKED'],
      provenance_refs: [],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-scp-beta',
      source_frontier_ref: null,
      action_title: 'Beta Review Packet',
      action_type: 'REVIEW_REQUIRED',
      operator_id: 'OP-002',
      subsystem_id: 'SYS-B',
      recommended_next_step: 'Perform manual operator review',
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
    {
      packet_id: 'pkt-scp-gamma',
      source_frontier_ref: null,
      action_title: 'Gamma Checklist Packet',
      action_type: 'COPY_CHECKLIST',
      operator_id: 'OP-003',
      subsystem_id: 'SYS-C',
      recommended_next_step: 'Copy and work through checklist',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: '',
      validation_checklist: ['[ ] Step one'],
      blocked_scopes: [],
      provenance_refs: [],
      fail_closed_reason: null,
    },
  ],
};

describe('SuggestionCardsPanel', () => {
  describe('null bundle (empty state)', () => {
    it('renders the panel', () => {
      render(<SuggestionCardsPanel packetsBundle={null} />);
      expect(screen.getByTestId('suggestion-cards-panel')).toBeInTheDocument();
    });

    it('shows fail-closed empty state', () => {
      render(<SuggestionCardsPanel packetsBundle={null} />);
      expect(screen.getByTestId('scp-empty').textContent).toMatch(/FAIL CLOSED/i);
    });
  });

  describe('suggestions generated from packets', () => {
    it('renders the panel with cards', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('suggestion-cards-panel')).toBeInTheDocument();
      expect(screen.queryByTestId('scp-empty')).toBeNull();
    });

    it('generates NEXT_SAFE_STEP for each packet', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('scp-card-NEXT_SAFE_STEP-pkt-scp-alpha')).toBeInTheDocument();
      expect(screen.getByTestId('scp-card-NEXT_SAFE_STEP-pkt-scp-beta')).toBeInTheDocument();
      expect(screen.getByTestId('scp-card-NEXT_SAFE_STEP-pkt-scp-gamma')).toBeInTheDocument();
    });

    it('generates VALIDATION_REMINDER for packets with checklists', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('scp-card-VALIDATION_REMINDER-pkt-scp-alpha')).toBeInTheDocument();
      expect(screen.getByTestId('scp-card-VALIDATION_REMINDER-pkt-scp-gamma')).toBeInTheDocument();
      expect(screen.queryByTestId('scp-card-VALIDATION_REMINDER-pkt-scp-beta')).toBeNull();
    });

    it('generates AUTHORITY_BOUNDARY for packets with blocked scopes', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('scp-card-AUTHORITY_BOUNDARY-pkt-scp-alpha')).toBeInTheDocument();
      expect(screen.queryByTestId('scp-card-AUTHORITY_BOUNDARY-pkt-scp-beta')).toBeNull();
    });

    it('generates FRONTIER_PAUSE for REVIEW_REQUIRED packets', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('scp-card-FRONTIER_PAUSE-pkt-scp-beta')).toBeInTheDocument();
      expect(screen.queryByTestId('scp-card-FRONTIER_PAUSE-pkt-scp-alpha')).toBeNull();
    });

    it('shows total suggestion count', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const total = screen.getByTestId('scp-count-total');
      expect(total.textContent).toContain('7');
    });

    it('shows reviewed count starting at 0', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('scp-count-reviewed').textContent).toContain('0');
    });
  });

  describe('display-only authority', () => {
    it('shows DISPLAY_ONLY · NON_AUTHORITATIVE in panel header', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('suggestion-cards-panel');
      expect(panel.textContent).toMatch(/DISPLAY_ONLY/);
      expect(panel.textContent).toMatch(/NON_AUTHORITATIVE/);
    });

    it('shows authority locks when card is expanded', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const id = 'NEXT_SAFE_STEP-pkt-scp-alpha';
      fireEvent.click(screen.getByTestId(`scp-card-header-${id}`));
      const authorityRow = screen.getByTestId(`scp-authority-${id}`);
      expect(authorityRow.textContent).toMatch(/AUTHORITY: DISPLAY_ONLY/);
      expect(authorityRow.textContent).toMatch(/EXEC: false/);
      expect(authorityRow.textContent).toMatch(/MUTATION: false/);
      expect(authorityRow.textContent).toMatch(/PROMOTION: false/);
    });

    it('shows NO_AUTO_APPLY in footer', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('suggestion-cards-panel');
      expect(panel.textContent).toMatch(/NO_AUTO_APPLY/);
      expect(panel.textContent).toMatch(/NO_EXECUTION/);
      expect(panel.textContent).toMatch(/NO_BACKEND_WRITES/);
    });
  });

  describe('collapse / expand behavior', () => {
    it('cards start collapsed (body not visible)', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const id = 'NEXT_SAFE_STEP-pkt-scp-alpha';
      expect(screen.queryByTestId(`scp-card-body-${id}`)).toBeNull();
    });

    it('clicking card header expands it', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const id = 'NEXT_SAFE_STEP-pkt-scp-alpha';
      fireEvent.click(screen.getByTestId(`scp-card-header-${id}`));
      expect(screen.getByTestId(`scp-card-body-${id}`)).toBeInTheDocument();
    });

    it('clicking expanded card collapses it', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const id = 'NEXT_SAFE_STEP-pkt-scp-alpha';
      fireEvent.click(screen.getByTestId(`scp-card-header-${id}`));
      fireEvent.click(screen.getByTestId(`scp-card-header-${id}`));
      expect(screen.queryByTestId(`scp-card-body-${id}`)).toBeNull();
    });

    it('suggestion_id shown in expanded body', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const id = 'NEXT_SAFE_STEP-pkt-scp-alpha';
      fireEvent.click(screen.getByTestId(`scp-card-header-${id}`));
      expect(screen.getByTestId(`scp-suggestion-id-${id}`).textContent).toBe(id);
    });
  });

  describe('local reviewed toggle (UI_ONLY)', () => {
    it('mark reviewed button appears when card is expanded', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const id = 'NEXT_SAFE_STEP-pkt-scp-alpha';
      fireEvent.click(screen.getByTestId(`scp-card-header-${id}`));
      expect(screen.getByTestId(`scp-reviewed-btn-${id}`)).toBeInTheDocument();
    });

    it('clicking mark reviewed shows REVIEWED badge on card header', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const id = 'NEXT_SAFE_STEP-pkt-scp-alpha';
      fireEvent.click(screen.getByTestId(`scp-card-header-${id}`));
      fireEvent.click(screen.getByTestId(`scp-reviewed-btn-${id}`));
      expect(screen.getByTestId(`scp-reviewed-badge-${id}`)).toBeInTheDocument();
    });

    it('reviewed count increments after marking', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const id = 'NEXT_SAFE_STEP-pkt-scp-alpha';
      fireEvent.click(screen.getByTestId(`scp-card-header-${id}`));
      fireEvent.click(screen.getByTestId(`scp-reviewed-btn-${id}`));
      expect(screen.getByTestId('scp-count-reviewed').textContent).toContain('1');
    });

    it('clicking reviewed again un-marks it', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const id = 'NEXT_SAFE_STEP-pkt-scp-alpha';
      fireEvent.click(screen.getByTestId(`scp-card-header-${id}`));
      fireEvent.click(screen.getByTestId(`scp-reviewed-btn-${id}`));
      fireEvent.click(screen.getByTestId(`scp-reviewed-btn-${id}`));
      expect(screen.queryByTestId(`scp-reviewed-badge-${id}`)).toBeNull();
      expect(screen.getByTestId('scp-count-reviewed').textContent).toContain('0');
    });
  });

  describe('no execution controls', () => {
    it('has no enabled execute/promote/mutate/activate buttons', () => {
      render(<SuggestionCardsPanel packetsBundle={sampleBundle} />);
      const buttons = document.querySelectorAll('button:not([disabled])');
      const forbidden = /execute|promote|mutate|activate|publish|runtime|force/i;
      buttons.forEach((btn) => {
        expect(btn.textContent ?? '').not.toMatch(forbidden);
      });
    });
  });
});
