import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { InstantiationProjectionPanel } from './InstantiationProjectionPanel';

const AUTHORITY = {
  advisory_only: true,
  projection_only: true,
  non_authoritative: true,
  forecast_authority: false,
  intervention_authority: false,
  execution_authority: false,
  canon_mutation: false,
  runtime_mutation: false,
};

const DIMENSIONS = [
  'symbolic_persistence',
  'cognitive_penetration',
  'behavioral_consequence',
  'network_propagation',
  'executable_embodiment',
  'economic_institutional_embodiment',
  'material_consequence',
  'recursive_reinforcement',
];

function dimensionTiles(observed: string[]): Array<Record<string, unknown>> {
  return DIMENSIONS.map((name) => ({
    name,
    epistemic_status: observed.includes(name) ? 'OBSERVED' : 'NOT_COMPUTABLE',
    evidence_count: observed.includes(name) ? 1 : 0,
    not_computable_reason: observed.includes(name) ? null : 'fixture evidence absent',
  }));
}

const SAMPLE: Record<string, unknown> = {
  schema_version: 'InstantiationProjectionView.v1',
  view_id: 'ipv-test',
  lane: 'PROJECTION',
  dimension_order: DIMENSIONS,
  construct_timelines: [
    {
      construct_ref: { object_id: 'cfar-fixture', canonical_hash: 'a'.repeat(64) },
      states: [
        {
          state_id: 'is-t0',
          state_hash: 'b'.repeat(64),
          observation_window: { start: 'fixture-t0', end: 'fixture-t0' },
          causal_exposure: 'EXOGENOUS',
          aggregate_instantiation_depth: 'NOT_COMPUTABLE',
          dimensions: dimensionTiles(['symbolic_persistence']),
        },
        {
          state_id: 'is-t1',
          state_hash: 'c'.repeat(64),
          observation_window: { start: 'fixture-t1', end: 'fixture-t1' },
          causal_exposure: 'ABX_MEDIATED',
          aggregate_instantiation_depth: 'NOT_COMPUTABLE',
          dimensions: dimensionTiles(['symbolic_persistence', 'network_propagation']),
        },
      ],
    },
  ],
  lineage_edges: [
    {
      transition_id: 'it-test',
      transition_hash: 'd'.repeat(64),
      from_state_id: 'is-t0',
      to_state_id: 'is-t1',
      causal_exposure: 'ABX_MEDIATED',
      feedback_contaminated: true,
      independent_confirmation_eligible: false,
      dimension_changes: [
        {
          dimension: 'network_propagation',
          change_kind: 'INCREASED',
          epistemic_status: 'OBSERVED',
        },
      ],
      linked_refs: { forecast_ref: null, intervention_ref: null, settlement_ref: null },
    },
  ],
  unresolved_state_ids: [],
  shadow_overlay: {
    report_id: 'isr-test',
    report_hash: 'e'.repeat(64),
    findings: [
      {
        code: 'CONTAMINATION_PRESENT',
        severity: 'observation',
        subject_id: 'it-test',
        message: 'Transition it-test is feedback-contaminated.',
      },
      {
        code: 'REINFORCEMENT_WITHOUT_CONSEQUENCE_EVIDENCE',
        severity: 'anomaly',
        subject_id: 'is-t1',
        message: 'anomaly fixture',
      },
    ],
  },
  authority: AUTHORITY,
  view_hash: 'f'.repeat(64),
};

describe('InstantiationProjectionPanel', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('renders timelines, lineage, and shadow overlay from the feed', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: true, json: async () => SAMPLE }),
    );
    render(<InstantiationProjectionPanel />);
    await waitFor(() => {
      expect(screen.getByTestId('instantiation-timeline-cfar-fixture')).toBeInTheDocument();
    });
    expect(screen.getByTestId('instantiation-state-is-t0')).toBeInTheDocument();
    expect(screen.getByTestId('instantiation-edge-it-test')).toBeInTheDocument();
    expect(screen.getByText(/ABX_MEDIATED · CONTAMINATED/)).toBeInTheDocument();
    expect(screen.getByText(/not independent confirmation/)).toBeInTheDocument();
    expect(screen.getByText(/1 anomalies · 1 observations/)).toBeInTheDocument();
    expect(screen.getByTestId('instantiation-authority')).toBeInTheDocument();
  });

  it('falls back to missing state when the feed is absent', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false }));
    render(<InstantiationProjectionPanel />);
    await waitFor(() => {
      expect(
        screen.getByText(/No instantiation-projection.json/),
      ).toBeInTheDocument();
    });
  });

  it('rejects a feed whose authority claims execution', async () => {
    const tampered = {
      ...SAMPLE,
      authority: { ...AUTHORITY, execution_authority: true },
    };
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: true, json: async () => tampered }),
    );
    render(<InstantiationProjectionPanel />);
    await waitFor(() => {
      expect(
        screen.getByText(/No instantiation-projection.json/),
      ).toBeInTheDocument();
    });
  });

  it('rejects a feed that is not PROJECTION lane', async () => {
    const tampered = { ...SAMPLE, lane: 'FORECAST' };
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: true, json: async () => tampered }),
    );
    render(<InstantiationProjectionPanel />);
    await waitFor(() => {
      expect(
        screen.getByText(/No instantiation-projection.json/),
      ).toBeInTheDocument();
    });
  });
});
