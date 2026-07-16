import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { useState } from 'react';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';
import generatedBundleJson from '../../public/projection-bundle.json';
import type { LiveConsoleProjectionBundle, YggdrasilTopologyIntegrityProjection, YggdrasilTopologyProjection } from '../types';
import { OperatorPlatformGraphViewPanel, type OperatorPlatformGraphState } from './OperatorPlatformViews';
import { OperatorPlatformSimpleViewPanel } from './OperatorPlatformSimpleViews';
import OperatorPlatformChangesView from './OperatorPlatformChangesView';

const graphState: OperatorPlatformGraphState = {
  yggQuery: '',
  yggSelectedNodeClasses: ['CONTRACT', 'PACKET', 'RECEIPT', 'ROUTE', 'RUNE', 'SYSTEM'],
  yggSelectedEdgeClasses: ['RENDER_RELATION'],
  yggSelectedProvenance: ['INFERRED', 'OBSERVED'],
  yggSelectedConfidence: ['INFERRED', 'NOT_COMPUTABLE', 'SUPPORTED', 'VERIFIED'],
  yggSelectedRoles: ['OPERATOR'],
  yggSelectedId: null,
  yggTraversalDepth: 1,
  yggPathTargetId: null,
  yggDiffOverlay: true,
  yggIntegritySeverities: ['HIGH', 'INFO', 'LOW', 'MEDIUM', 'NOT_COMPUTABLE'],
  yggIntegrityTypes: ['GENERATION_MISMATCH', 'INFERRED_LINK', 'MISSING_EVIDENCE', 'SECTION_NOT_COMPUTABLE', 'SOURCE_INTEGRITY_GAP', 'STALE_ENTITY', 'TEMPORAL_REMOVAL', 'TEMPORAL_WEAKENING', 'UNRESOLVED_ENTITY'],
  yggAlertOverlay: true,
  yggSelectedAlertId: null,
  contractQuery: '',
  contractSelectedId: null,
};

function enrichment(): YggdrasilTopologyProjection {
  const source = { id: 'source:test', source_key: 'test', path: 'out/audit/test.json', declared_canonical_hash: null, content_sha256: 'a'.repeat(64), integrity_state: 'VERIFIED' as const };
  return {
    schema_version: 'AALViz.YggdrasilTopology.v1',
    generation: { generated_at: '2026-07-15T00:00:00Z', generated_by: 'LIVE_YGGDRASIL_TOPOLOGY_ENRICHMENT_001', topology_generation_id: 'b'.repeat(64), operator_platform_generation_id: 'c'.repeat(64) },
    status: 'AVAILABLE', provenance: 'OBSERVED', source_artifacts: [source],
    authority: { projection_only: true, runtime_mutation_allowed: false, canon_mutation_allowed: false, execution_authority: false, promotion_allowed: false, production_activation_allowed: false, graph_driven_execution_allowed: false, autonomous_link_creation_allowed: false, alerting_allowed: false, scheduling_allowed: false },
    payload: {
      summary: { node_count: 3, edge_count: 2, evidence_count: 1, unresolved_node_count: 1, stale_entity_count: 0, inferred_edge_count: 1, node_class_counts: { INTERFACE: 1, RUNE: 1, SYSTEM: 1 }, edge_class_counts: { BINDS: 1, EXPOSES: 1 } },
      nodes: [
        { id: 'interface:operator', label: 'Operator interface', node_class: 'INTERFACE', roles: ['OPERATOR'], status: 'OBSERVED', resolution_state: 'RESOLVED', source_ref: 'apps/console', provenance: 'OBSERVED', confidence: 'VERIFIED', freshness: 'CURRENT', evidence_refs: [source.id], temporal_ref: { category: 'TOPOLOGY_NODE', entity_id: 'interface:operator' } },
        { id: 'rune:route', label: 'Route rune', node_class: 'RUNE', roles: [], status: 'UNBOUND', resolution_state: 'UNRESOLVED', source_ref: 'RUNE.ROUTE', provenance: 'OBSERVED', confidence: 'VERIFIED', freshness: 'CURRENT', evidence_refs: [source.id], temporal_ref: { category: 'TOPOLOGY_NODE', entity_id: 'rune:route' } },
        { id: 'system:console', label: 'Console', node_class: 'SYSTEM', roles: [], status: 'OBSERVED', resolution_state: 'RESOLVED', source_ref: 'aal_viz', provenance: 'INFERRED', confidence: 'SUPPORTED', freshness: 'CURRENT', evidence_refs: [source.id], temporal_ref: { category: 'TOPOLOGY_NODE', entity_id: 'system:console' } },
      ],
      edges: [
        { id: 'edge:binds', source: 'rune:route', target: 'system:console', edge_class: 'BINDS', relation: 'BINDS', status: 'OBSERVED', resolution_state: 'RESOLVED', provenance: 'OBSERVED', confidence: 'VERIFIED', freshness: 'CURRENT', evidence_refs: [source.id], temporal_ref: { category: 'TOPOLOGY_EDGE', entity_id: 'edge:binds' } },
        { id: 'edge:exposes', source: 'interface:operator', target: 'system:console', edge_class: 'EXPOSES', relation: 'OPERATOR_ENTRYPOINT', status: 'OBSERVED', resolution_state: 'RESOLVED', provenance: 'INFERRED', confidence: 'SUPPORTED', freshness: 'CURRENT', evidence_refs: [source.id], temporal_ref: { category: 'TOPOLOGY_EDGE', entity_id: 'edge:exposes' } },
      ], evidence: [source],
    },
    not_computable_reason: null, validation_findings: [],
    temporal_linkage: { status: 'NOT_COMPUTABLE', source_path: null, content_sha256: null, prior_generation_id: null, current_generation_id: null }, canonical_hash: 'd'.repeat(64),
  };
}

function integrity(): YggdrasilTopologyIntegrityProjection {
  const generation = {
    topology_generation_id: 'b'.repeat(64),
    operator_platform_generation_id: 'c'.repeat(64),
    temporal_diff_generation_id: null,
  };
  return {
    schema_version: 'AALViz.YggdrasilTopologyIntegrity.v1',
    generation: { generated_at: '2026-07-15T00:00:00Z', generated_by: 'YGGDRASIL_TOPOLOGY_INTEGRITY_FINDINGS_001', integrity_generation_id: 'e'.repeat(64), ...generation },
    status: 'PARTIAL', provenance: 'OBSERVED', source_artifacts: [],
    authority: { projection_only: true, runtime_mutation_allowed: false, canon_mutation_allowed: false, execution_authority: false, production_activation_allowed: false, graph_driven_execution_allowed: false, alert_delivery_allowed: false, acknowledgement_state_allowed: false, browser_persistence_allowed: false, route_receipt_triggering_allowed: false, scheduling_allowed: false },
    payload: {
      summary: { finding_count: 1, affected_entity_count: 1, non_computable_count: 0, severity_counts: { MEDIUM: 1 }, type_counts: { UNRESOLVED_ENTITY: 1 } },
      findings: [{ id: `finding:${'f'.repeat(64)}`, finding_type: 'UNRESOLVED_ENTITY', severity: 'MEDIUM', subject_key: 'rune:route', entity_ref: { category: 'TOPOLOGY_NODE', entity_id: 'rune:route' }, evidence_refs: ['source:test'], provenance: 'OBSERVED', confidence: 'VERIFIED', reason: 'Route rune is unresolved.', computability: 'COMPUTABLE', generation_binding: generation }],
    },
    not_computable_reason: null, validation_findings: [], canonical_hash: '1'.repeat(64),
  };
}

function TestGraph({ view, enriched = false, withIntegrity = false }: { view: 'yggdrasil' | 'contracts'; enriched?: boolean; withIntegrity?: boolean }): JSX.Element {
  const [state, setState] = useState(graphState);
  return <OperatorPlatformGraphViewPanel view={view} platform={sampleProjectionBundle.operator_platform} topologyProjection={enriched ? enrichment() : undefined} integrityProjection={withIntegrity ? integrity() : undefined} graphState={state} onGraphStateChange={setState} />;
}

describe('OperatorPlatformViewPanel', () => {
  it('filters topology entity types into an explicit empty state', async () => {
    const user = userEvent.setup();
    render(
      <TestGraph view="yggdrasil" />,
    );
    expect(screen.getByTestId('topology-canvas')).toBeInTheDocument();
    for (const checkbox of screen.getAllByRole('checkbox').slice(0, 7)) await user.click(checkbox);
    expect(screen.getByText('No matching topology')).toBeInTheDocument();
  });

  it('renders the production flow in deterministic stage order', () => {
    render(
      <OperatorPlatformSimpleViewPanel
        view="production"
        platform={sampleProjectionBundle.operator_platform}
      />,
    );
    expect(screen.getByRole('heading', { name: 'Entry' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Receipts' })).toBeInTheDocument();
  });

  it('renders enriched evidence state and supports keyboard selection', async () => {
    const user = userEvent.setup();
    render(<TestGraph view="yggdrasil" enriched />);
    expect(screen.getByText(/1 unresolved; 0 stale; 1 inferred edges/)).toBeInTheDocument();
    const canvas = screen.getByTestId('topology-canvas');
    canvas.focus();
    await user.keyboard('{ArrowRight}');
    expect(screen.getByText('Route rune')).toBeInTheDocument();
    expect(screen.getByText('source:test')).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText('Neighborhood depth'), '3');
    expect(screen.getByLabelText('Neighborhood depth')).toHaveValue('3');
  });

  it('filters and inspects advisory integrity findings', async () => {
    const user = userEvent.setup();
    render(<TestGraph view="yggdrasil" enriched withIntegrity />);
    expect(screen.getByText(/1 integrity findings visible/)).toBeInTheDocument();
    const canvas = screen.getByTestId('topology-canvas');
    canvas.focus();
    await user.keyboard('{ArrowRight}');
    expect(screen.getByText('Route rune is unresolved.')).toBeInTheDocument();
    await user.click(screen.getByText('Integrity severity'));
    await user.click(screen.getByRole('checkbox', { name: 'MEDIUM' }));
    expect(screen.getByText(/0 integrity findings visible/)).toBeInTheDocument();
  });

  it('renders contract missing-evidence state', () => {
    render(
      <TestGraph view="contracts" />,
    );
    expect(screen.getByText('No contracts')).toBeInTheDocument();
  });

  it('searches evidence records', async () => {
    const user = userEvent.setup();
    render(
      <OperatorPlatformSimpleViewPanel
        view="evidence"
        platform={sampleProjectionBundle.operator_platform}
      />,
    );
    await user.type(screen.getByLabelText('Search evidence'), 'not-present');
    expect(screen.getByText('No matching evidence')).toBeInTheDocument();
  });

  it('renders a stable zero-change generation', () => {
    render(
      <OperatorPlatformChangesView platform={sampleProjectionBundle.operator_platform} />,
    );
    expect(screen.getByText('No changes observed')).toBeInTheDocument();
  });

  it('groups typed changes and renders generation labels', () => {
    const bundle = structuredClone(sampleProjectionBundle);
    const diff = bundle.operator_platform.temporal_diff.payload;
    if (diff == null) throw new Error('sample temporal payload is required');
    diff.prior_generation_id = 'a'.repeat(64);
    diff.current_generation_id = 'b'.repeat(64);
    diff.total_change_count = 1;
    diff.category_counts.OWNERSHIP = 1;
    diff.entries = [{
      id: 'c'.repeat(64),
      operation: 'CHANGED',
      category: 'OWNERSHIP',
      impact: 'STRENGTHENED',
      surface: 'contract_graph',
      entity_id: 'contract:1',
      summary: 'Ownership evidence resolved.',
      severity: 'INFO',
      field_path: '/contract_graph/payload/contracts/contract:1/owner',
      prior_value: 'UNRESOLVED',
      current_value: 'core.owner',
      provenance: 'OBSERVED',
      prior_generation_id: 'a'.repeat(64),
      current_generation_id: 'b'.repeat(64),
      prior_evidence_status: 'AVAILABLE',
      current_evidence_status: 'AVAILABLE',
      reason_code: null,
      source_keys: ['contract_inventory'],
    }];
    render(<OperatorPlatformChangesView platform={bundle.operator_platform} />);
    expect(screen.getByRole('heading', { name: 'OWNERSHIP' })).toBeInTheDocument();
    expect(screen.getByText('STRENGTHENED')).toBeInTheDocument();
    expect(screen.getByText('aaaaaaaaaaaa')).toBeInTheDocument();
    expect(screen.getByText('bbbbbbbbbbbb')).toBeInTheDocument();
  });

  it('renders ranked delta intelligence when temporal diff is not computable', async () => {
    const user = userEvent.setup();
    const bundle = generatedBundleJson as unknown as LiveConsoleProjectionBundle;
    render(<OperatorPlatformChangesView
      platform={bundle.operator_platform}
      deltaIntelligence={bundle.yggdrasil_topology_delta_intelligence}
    />);
    expect(screen.getByRole('heading', { name: 'Topology delta intelligence' })).toBeInTheDocument();
    expect(screen.getByLabelText('Recommended review order')).toBeInTheDocument();
    expect(screen.getByText('162', { selector: '.metric-strip strong' })).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText('Severity'), 'HIGH');
    expect(screen.getByText('No active priorities match these filters.')).toBeInTheDocument();
  });
});
