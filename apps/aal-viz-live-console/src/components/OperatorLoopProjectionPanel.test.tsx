import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { OperatorLoopProjectionPanel } from './OperatorLoopProjectionPanel';

const SAMPLE: Record<string, unknown> = {
  schema_version: 'OperatorLoopProjection.v1',
  summary: {
    work_packet_count: 1,
    handoff_count: 0,
    file_overlap_count: 0,
    github_item_count: 1,
    notion_item_count: 1,
    ci_item_count: 0,
  },
  work_packets: [
    {
      work_packet_id: 'WP-test',
      goal: 'Test packet',
      producer_system: 'CODEX',
      work_state: 'ACTIVE',
      authority_implication: 'none',
    },
  ],
  handoffs: [],
  file_overlaps: [],
  truth_surfaces: {
    github: {
      role: 'implementation_truth',
      truth_claim: 'GitHub is implementation truth.',
      glyph: 'github_implementation_truth',
      status: 'PRESENT',
      source: 'fixture',
      items: [{ kind: 'git_tip', sha: 'abc123' }],
      notes: [],
      authority_implication: 'none',
      can_assign: false,
      can_approve: false,
      can_merge: false,
      can_deploy: false,
    },
    notion: {
      role: 'architecture_truth',
      truth_claim: 'Notion is architecture truth.',
      glyph: 'notion_architecture_truth',
      status: 'PRESENT',
      source: 'fixture',
      items: [{ title: 'Master System' }],
      notes: [],
      authority_implication: 'none',
      can_assign: false,
      can_approve: false,
      can_merge: false,
      can_deploy: false,
    },
    ci: {
      role: 'deterministic_evidence',
      truth_claim: 'CI is evidence only.',
      glyph: 'ci_validator',
      status: 'NOT_COMPUTABLE',
      source: 'none',
      items: [],
      notes: [],
      authority_implication: 'none',
      can_assign: false,
      can_approve: false,
      can_merge: false,
      can_deploy: false,
    },
    lineage_rule: 'Lineage is projection only.',
  },
  authority: {
    projection_only: true,
    assignment_authority: false,
    approval_authority: false,
    producer_identity_grants_authority: false,
  },
};

describe('OperatorLoopProjectionPanel', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('renders truth surfaces from operator-loop projection', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => SAMPLE,
      }),
    );

    render(<OperatorLoopProjectionPanel />);

    await waitFor(() => {
      expect(screen.getByTestId('operator-loop-projection-panel')).toBeInTheDocument();
      expect(screen.getByTestId('operator-loop-truth-surfaces')).toBeInTheDocument();
    });
    expect(screen.getByText(/WP-test/)).toBeInTheDocument();
    expect(screen.getByText(/DISPLAY ONLY/)).toBeInTheDocument();
    expect(screen.getByTestId('operator-loop-surface-github')).toBeInTheDocument();
  });

  it('rejects authority escalation payloads', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          ...SAMPLE,
          authority: {
            projection_only: true,
            assignment_authority: true,
            approval_authority: false,
            producer_identity_grants_authority: false,
          },
        }),
      }),
    );

    render(<OperatorLoopProjectionPanel />);

    await waitFor(() => {
      expect(screen.getByText(/No operator-loop-projection/i)).toBeInTheDocument();
    });
  });
});
