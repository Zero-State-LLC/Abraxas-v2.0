import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { OperatorLoopProjectionPanel } from './OperatorLoopProjectionPanel';

const SAMPLE: Record<string, unknown> = {
  schema_version: 'OperatorLoopProjection.v1',
  summary: {
    work_packet_count: 1,
    handoff_count: 0,
    file_overlap_count: 0,
    github_item_count: 2,
    notion_item_count: 1,
    ci_item_count: 1,
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
      items: [
        { kind: 'git_tip', sha: 'abc1234567', branch: 'main' },
        {
          kind: 'open_pr',
          number: 42,
          title: 'feat: example',
          is_draft: false,
          mergeable: 'MERGEABLE',
          primary: undefined,
        },
      ],
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
      status: 'PRESENT',
      source: 'fixture',
      items: [
        {
          kind: 'pr_checks_summary',
          pr_number: 42,
          pass: 3,
          fail: 0,
          pending: 0,
          primary: 'pass',
        },
      ],
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

  it('renders open PR title for status glance', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => SAMPLE,
      }),
    );

    render(<OperatorLoopProjectionPanel />);

    await waitFor(() => {
      // Formatted glance rows (not raw JSON); #42 appears on open_pr and CI summary
      expect(screen.getByText(/#42 feat: example/)).toBeInTheDocument();
      expect(screen.getByText(/feat: example · ready · MERGEABLE/)).toBeInTheDocument();
      expect(screen.getByText(/PR #42 checks · pass/)).toBeInTheDocument();
      expect(screen.getByText(/tip abc1234 @ main/)).toBeInTheDocument();
    });
  });
});
