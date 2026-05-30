import { describe, it, expect, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import { WorkflowAnalyticsPanel } from './WorkflowAnalyticsPanel';
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
      packet_id: 'pkt-wap-alpha',
      source_frontier_ref: null,
      action_title: 'Alpha Analytics Packet',
      action_type: 'COPY_PROMPT',
      operator_id: 'OP-001',
      subsystem_id: 'SYS-A',
      recommended_next_step: 'Review and copy',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: 'Prompt.',
      validation_checklist: ['[ ] 1. Check A', '[ ] 2. Check B', '[ ] 3. Check C'],
      blocked_scopes: ['EXECUTION_BLOCKED', 'MUTATION_BLOCKED'],
      provenance_refs: [],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-wap-beta',
      source_frontier_ref: null,
      action_title: 'Beta Analytics Packet',
      action_type: 'COPY_CHECKLIST',
      operator_id: 'OP-002',
      subsystem_id: 'SYS-B',
      recommended_next_step: 'Work through checklist',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: '',
      validation_checklist: ['[ ] Step one', '[ ] Step two'],
      blocked_scopes: ['EXECUTION_BLOCKED'],
      provenance_refs: [],
      fail_closed_reason: null,
    },
    {
      packet_id: 'pkt-wap-gamma',
      source_frontier_ref: null,
      action_title: 'Gamma Analytics Packet',
      action_type: 'REVIEW_REQUIRED',
      operator_id: 'OP-003',
      subsystem_id: 'SYS-C',
      recommended_next_step: 'Manual review required',
      authority_required: 'OPERATOR_REVIEW',
      allowed: false,
      execution_allowed: false as const,
      runtime_mutation_allowed: false as const,
      promotion_allowed: false as const,
      prompt_body: 'Review carefully.',
      validation_checklist: [],
      blocked_scopes: [],
      provenance_refs: [],
      fail_closed_reason: 'AUTHORITY_CHECK_FAILED',
    },
  ],
};

describe('WorkflowAnalyticsPanel', () => {
  describe('null bundle (empty state)', () => {
    it('renders the panel', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={null} />);
      expect(screen.getByTestId('workflow-analytics-panel')).toBeInTheDocument();
    });

    it('shows fail-closed empty state', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={null} />);
      expect(screen.getByTestId('wap-empty').textContent).toMatch(/FAIL CLOSED/i);
    });
  });

  describe('metrics computation', () => {
    it('renders analytics sections', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-metrics')).toBeInTheDocument();
      expect(screen.getByTestId('wap-type-distribution')).toBeInTheDocument();
      expect(screen.getByTestId('wap-blocked-scopes')).toBeInTheDocument();
      expect(screen.getByTestId('wap-authority-health')).toBeInTheDocument();
    });

    it('total_packets = 3', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-metric-total').textContent).toContain('3');
    });

    it('copy_prompt_count = 1', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-metric-copy-prompt').textContent).toContain('1');
    });

    it('copy_checklist_count = 1', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-metric-copy-checklist').textContent).toContain('1');
    });

    it('review_required_count = 1', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-metric-review-required').textContent).toContain('1');
    });

    it('blocked_packet_count = 1 (allowed=false)', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-metric-blocked').textContent).toContain('1');
    });

    it('packets_with_validation_checklist_count = 2', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-metric-with-checklist').textContent).toContain('2');
    });

    it('packets_with_blocked_scopes_count = 2', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-metric-with-blocked-scopes').textContent).toContain('2');
    });

    it('total_validation_checklist_items = 5 (3+2+0)', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-metric-total-checklist-items').textContent).toContain('5');
    });

    it('total_blocked_scope_refs = 3 (2+1+0)', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-metric-total-scope-refs').textContent).toContain('3');
    });
  });

  describe('packet type distribution', () => {
    it('renders all three distribution bars', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-dist-copy-prompt')).toBeInTheDocument();
      expect(screen.getByTestId('wap-dist-copy-checklist')).toBeInTheDocument();
      expect(screen.getByTestId('wap-dist-review-required')).toBeInTheDocument();
    });

    it('COPY_PROMPT bar row shows count 1', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-dist-copy-prompt').textContent).toContain('1');
    });

    it('REVIEW_REQUIRED bar row shows count 1', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-dist-review-required').textContent).toContain('1');
    });
  });

  describe('blocked scope aggregation', () => {
    it('shows EXECUTION_BLOCKED scope with count 2', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      const el = screen.getByTestId('wap-scope-EXECUTION_BLOCKED');
      expect(el.textContent).toContain('EXECUTION_BLOCKED');
      expect(el.textContent).toContain('2');
    });

    it('shows MUTATION_BLOCKED scope with count 1', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      const el = screen.getByTestId('wap-scope-MUTATION_BLOCKED');
      expect(el.textContent).toContain('MUTATION_BLOCKED');
      expect(el.textContent).toContain('1');
    });

    it('shows no-scopes message when bundle has no blocked scopes', () => {
      const emptyBundle: OperatorActionPacketsBundle = {
        ...sampleBundle,
        packets: sampleBundle.packets.map((p) => ({ ...p, blocked_scopes: [] })),
      };
      render(<WorkflowAnalyticsPanel packetsBundle={emptyBundle} />);
      expect(screen.getByTestId('wap-no-scopes').textContent).toMatch(
        /No blocked scopes reported by packets/i,
      );
    });
  });

  describe('authority health — clean', () => {
    it('shows AUTHORITY_CLEAN when all forbidden flags are false', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      const status = screen.getByTestId('wap-authority-status');
      expect(status.textContent).toMatch(/AUTHORITY_CLEAN/);
    });

    it('execution_allowed_count = 0 shown in health checks', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-auth-execution').textContent).toContain('0');
    });

    it('runtime_mutation_allowed_count = 0 shown', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-auth-mutation').textContent).toContain('0');
    });

    it('promotion_allowed_count = 0 shown', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.getByTestId('wap-auth-promotion').textContent).toContain('0');
    });

    it('no authority-violation banner shown', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      expect(screen.queryByTestId('wap-authority-violation')).toBeNull();
    });
  });

  describe('authority health — fail-closed on violation', () => {
    it('shows FAIL_CLOSED when a packet has execution_allowed=true', () => {
      const violatingBundle = {
        ...sampleBundle,
        packets: [
          {
            ...sampleBundle.packets[0],
            execution_allowed: true as unknown as false,
          },
          ...sampleBundle.packets.slice(1),
        ],
      } as OperatorActionPacketsBundle;
      render(<WorkflowAnalyticsPanel packetsBundle={violatingBundle} />);
      expect(screen.getByTestId('wap-authority-status').textContent).toMatch(/FAIL_CLOSED/);
    });

    it('shows authority-violation banner on violation', () => {
      const violatingBundle = {
        ...sampleBundle,
        packets: [
          {
            ...sampleBundle.packets[0],
            execution_allowed: true as unknown as false,
          },
          ...sampleBundle.packets.slice(1),
        ],
      } as OperatorActionPacketsBundle;
      render(<WorkflowAnalyticsPanel packetsBundle={violatingBundle} />);
      expect(screen.getByTestId('wap-authority-violation')).toBeInTheDocument();
      expect(screen.getByTestId('wap-authority-violation').textContent).toMatch(
        /AUTHORITY_VIOLATION_DETECTED/,
      );
    });
  });

  describe('authority boundary display', () => {
    it('shows READ_ONLY · DISPLAY_ONLY notice', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('workflow-analytics-panel');
      expect(panel.textContent).toMatch(/READ_ONLY/);
      expect(panel.textContent).toMatch(/DISPLAY_ONLY/);
    });

    it('shows NO_BACKEND_WRITES in footer', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      const panel = screen.getByTestId('workflow-analytics-panel');
      expect(panel.textContent).toMatch(/NO_BACKEND_WRITES/);
      expect(panel.textContent).toMatch(/NO_PERSISTENCE/);
    });

    it('has no enabled execute/promote/mutate buttons', () => {
      render(<WorkflowAnalyticsPanel packetsBundle={sampleBundle} />);
      const buttons = document.querySelectorAll('button:not([disabled])');
      const forbidden = /execute|promote|mutate|activate|publish|runtime|force/i;
      buttons.forEach((btn) => {
        expect(btn.textContent ?? '').not.toMatch(forbidden);
      });
    });
  });
});
