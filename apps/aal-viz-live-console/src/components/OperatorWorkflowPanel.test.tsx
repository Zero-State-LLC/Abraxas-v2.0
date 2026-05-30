import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';
import { OperatorWorkflowPanel } from './OperatorWorkflowPanel';
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
      packet_id: 'pkt-copy-prompt-001',
      source_frontier_ref: null,
      action_title: 'Test Copy Prompt Packet',
      action_type: 'COPY_PROMPT',
      operator_id: 'OP-001',
      subsystem_id: 'SYS-A',
      recommended_next_step: 'Copy prompt and review',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: 'This is the prompt body text.',
      validation_checklist: ['Check A', 'Check B'],
      blocked_scopes: ['EXECUTION_BLOCKED'],
      provenance_refs: [],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-copy-checklist-001',
      source_frontier_ref: null,
      action_title: 'Test Copy Checklist Packet',
      action_type: 'COPY_CHECKLIST',
      operator_id: 'OP-002',
      subsystem_id: 'SYS-B',
      recommended_next_step: 'Copy checklist and review',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: '',
      validation_checklist: ['Step 1', 'Step 2', 'Step 3'],
      blocked_scopes: [],
      provenance_refs: [],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-review-required-001',
      source_frontier_ref: null,
      action_title: 'Test Review Required Packet',
      action_type: 'REVIEW_REQUIRED',
      operator_id: 'OP-003',
      subsystem_id: 'SYS-C',
      recommended_next_step: 'Manual operator review required',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: 'Review this carefully.',
      validation_checklist: [],
      blocked_scopes: ['MUTATION_BLOCKED'],
      provenance_refs: [],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-blocked-001',
      source_frontier_ref: null,
      action_title: 'Test Blocked Packet',
      action_type: 'COPY_PROMPT',
      operator_id: 'OP-004',
      subsystem_id: 'SYS-D',
      recommended_next_step: 'Cannot proceed — blocked by authority',
      authority_required: 'OPERATOR_REVIEW',
      allowed: false,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: '',
      validation_checklist: [],
      blocked_scopes: ['ALL'],
      provenance_refs: [],
      fail_closed_reason: 'AUTHORITY_CHECK_FAILED',
    },
  ],
};

describe('OperatorWorkflowPanel', () => {
  describe('null bundle', () => {
    it('renders the panel with no items', () => {
      render(<OperatorWorkflowPanel packetsBundle={null} />);
      expect(screen.getByTestId('operator-workflow-panel')).toBeInTheDocument();
      expect(screen.getByTestId('workflow-empty')).toBeInTheDocument();
    });

    it('shows zero counts for all status types', () => {
      render(<OperatorWorkflowPanel packetsBundle={null} />);
      expect(screen.getByTestId('wf-count-available').textContent).toContain('0');
      expect(screen.getByTestId('wf-count-copied').textContent).toContain('0');
      expect(screen.getByTestId('wf-count-review').textContent).toContain('0');
      expect(screen.getByTestId('wf-count-blocked').textContent).toContain('0');
      expect(screen.getByTestId('wf-count-completed').textContent).toContain('0');
    });
  });

  describe('packet → workflow item mapping', () => {
    it('renders all 4 workflow items from bundle', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('workflow-item-pkt-copy-prompt-001')).toBeInTheDocument();
      expect(screen.getByTestId('workflow-item-pkt-copy-checklist-001')).toBeInTheDocument();
      expect(screen.getByTestId('workflow-item-pkt-review-required-001')).toBeInTheDocument();
      expect(screen.getByTestId('workflow-item-pkt-blocked-001')).toBeInTheDocument();
    });

    it('COPY_PROMPT → initial status AVAILABLE', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('workflow-status-pkt-copy-prompt-001').textContent).toBe('AVAILABLE');
    });

    it('COPY_CHECKLIST → initial status AVAILABLE', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('workflow-status-pkt-copy-checklist-001').textContent).toBe('AVAILABLE');
    });

    it('REVIEW_REQUIRED (allowed=true) → initial status REVIEW_REQUIRED', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('workflow-status-pkt-review-required-001').textContent).toBe('REVIEW_REQUIRED');
    });

    it('allowed=false → initial status BLOCKED regardless of action_type', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('workflow-status-pkt-blocked-001').textContent).toBe('BLOCKED');
    });
  });

  describe('counts', () => {
    it('counts match derived initial statuses', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wf-count-available').textContent).toContain('2');
      expect(screen.getByTestId('wf-count-review').textContent).toContain('1');
      expect(screen.getByTestId('wf-count-blocked').textContent).toContain('1');
      expect(screen.getByTestId('wf-count-copied').textContent).toContain('0');
      expect(screen.getByTestId('wf-count-completed').textContent).toContain('0');
    });
  });

  describe('local state transitions', () => {
    beforeEach(() => {
      Object.assign(navigator, {
        clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
      });
    });

    it('clicking COPY button transitions status to COPIED', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('wf-copy-btn-pkt-copy-prompt-001'));
      expect(screen.getByTestId('workflow-status-pkt-copy-prompt-001').textContent).toBe('COPIED');
    });

    it('COPIED count increments after copy', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('wf-copy-btn-pkt-copy-prompt-001'));
      expect(screen.getByTestId('wf-count-copied').textContent).toContain('1');
      expect(screen.getByTestId('wf-count-available').textContent).toContain('1');
    });

    it('clicking REVIEW_REQUIRED button transitions status', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('wf-review-btn-pkt-copy-prompt-001'));
      expect(screen.getByTestId('workflow-status-pkt-copy-prompt-001').textContent).toBe('REVIEW_REQUIRED');
    });

    it('clicking COMPLETED_MANUALLY button transitions status', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('wf-complete-btn-pkt-copy-prompt-001'));
      expect(screen.getByTestId('workflow-status-pkt-copy-prompt-001').textContent).toBe('COMPLETED_MANUALLY');
    });

    it('clicking BLOCKED button transitions status', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('wf-block-btn-pkt-copy-prompt-001'));
      expect(screen.getByTestId('workflow-status-pkt-copy-prompt-001').textContent).toBe('BLOCKED');
    });

    it('COMPLETED_MANUALLY count increments after manual completion', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      fireEvent.click(screen.getByTestId('wf-complete-btn-pkt-copy-checklist-001'));
      expect(screen.getByTestId('wf-count-completed').textContent).toContain('1');
    });
  });

  describe('authority boundaries', () => {
    it('shows UI_ONLY · NON_AUTHORITATIVE notice', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('operator-workflow-panel');
      expect(panel.textContent).toMatch(/UI_ONLY/);
      expect(panel.textContent).toMatch(/NON_AUTHORITATIVE/);
    });

    it('shows NO_EXECUTION footer notice', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('operator-workflow-panel');
      expect(panel.textContent).toMatch(/NO_EXECUTION/);
      expect(panel.textContent).toMatch(/NO_RUNTIME_MUTATION/);
      expect(panel.textContent).toMatch(/NO_BACKEND_WRITES/);
    });

    it('has no enabled execute/promote/mutate/activate buttons', () => {
      render(<OperatorWorkflowPanel packetsBundle={sampleBundle} />);
      const buttons = document.querySelectorAll('button:not([disabled])');
      const forbidden = /execute|promote|mutate|activate|publish|runtime|force/i;
      buttons.forEach((btn) => {
        expect(btn.textContent ?? '').not.toMatch(forbidden);
      });
    });
  });
});
