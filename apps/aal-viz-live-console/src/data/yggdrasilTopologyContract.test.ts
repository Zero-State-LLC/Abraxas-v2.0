import { describe, expect, it } from 'vitest';
import type { YggdrasilTopologyProjection } from '../types';
import { validateYggdrasilTopologyProjection } from './yggdrasilTopologyContract';

function topology(): YggdrasilTopologyProjection {
  const evidence = {
    id: 'source:yggdrasil',
    source_key: 'yggdrasil',
    path: 'out/audit/yggdrasil.json',
    declared_canonical_hash: null,
    content_sha256: 'a'.repeat(64),
    integrity_state: 'VERIFIED' as const,
  };
  return {
    schema_version: 'AALViz.YggdrasilTopology.v1',
    generation: {
      generated_at: '2026-07-15T00:00:00Z',
      generated_by: 'LIVE_YGGDRASIL_TOPOLOGY_ENRICHMENT_001',
      topology_generation_id: 'b'.repeat(64),
      operator_platform_generation_id: 'c'.repeat(64),
    },
    status: 'AVAILABLE',
    provenance: 'OBSERVED',
    source_artifacts: [evidence],
    authority: {
      projection_only: true,
      runtime_mutation_allowed: false,
      canon_mutation_allowed: false,
      execution_authority: false,
      promotion_allowed: false,
      production_activation_allowed: false,
      graph_driven_execution_allowed: false,
      autonomous_link_creation_allowed: false,
      alerting_allowed: false,
      scheduling_allowed: false,
    },
    payload: {
      summary: {
        node_count: 2,
        edge_count: 1,
        evidence_count: 1,
        unresolved_node_count: 0,
        stale_entity_count: 0,
        inferred_edge_count: 0,
        node_class_counts: { RUNE: 1, SYSTEM: 1 },
        edge_class_counts: { BINDS: 1 },
      },
      nodes: [
        {
          id: 'rune:validate', label: 'validate', node_class: 'RUNE', roles: [], status: 'BOUND',
          resolution_state: 'RESOLVED', source_ref: 'validate', provenance: 'OBSERVED', confidence: 'VERIFIED',
          freshness: 'CURRENT', evidence_refs: [evidence.id], temporal_ref: { category: 'TOPOLOGY_NODE', entity_id: 'rune:validate' },
        },
        {
          id: 'system:console', label: 'console', node_class: 'SYSTEM', roles: [], status: 'OBSERVED',
          resolution_state: 'RESOLVED', source_ref: 'console', provenance: 'OBSERVED', confidence: 'VERIFIED',
          freshness: 'CURRENT', evidence_refs: [evidence.id], temporal_ref: { category: 'TOPOLOGY_NODE', entity_id: 'system:console' },
        },
      ],
      edges: [
        {
          id: 'binding:validate:console', source: 'rune:validate', target: 'system:console', edge_class: 'BINDS', relation: 'BINDS',
          status: 'OBSERVED', resolution_state: 'RESOLVED', provenance: 'OBSERVED', confidence: 'VERIFIED', freshness: 'CURRENT',
          evidence_refs: [evidence.id], temporal_ref: { category: 'TOPOLOGY_EDGE', entity_id: 'binding:validate:console' },
        },
      ],
      evidence: [evidence],
    },
    not_computable_reason: null,
    validation_findings: [],
    temporal_linkage: {
      status: 'NOT_COMPUTABLE', source_path: null, content_sha256: null,
      prior_generation_id: null, current_generation_id: null,
    },
    canonical_hash: 'd'.repeat(64),
  };
}

describe('YGGDRASIL topology runtime contract', () => {
  it('accepts a complete projection and deterministic stale linkage', () => {
    const complete = topology();
    expect(validateYggdrasilTopologyProjection(complete)).toBeNull();
    complete.temporal_linkage = {
      status: 'STALE', source_path: 'out/projections/diff.json', content_sha256: 'e'.repeat(64),
      prior_generation_id: 'f'.repeat(64), current_generation_id: '9'.repeat(64),
    };
    expect(validateYggdrasilTopologyProjection(complete)).toBeNull();
  });

  it('rejects authority violations and dangling endpoints', () => {
    const authority = topology();
    authority.authority.runtime_mutation_allowed = true as false;
    expect(validateYggdrasilTopologyProjection(authority)).toMatch(/authority/);
    const dangling = topology();
    if (dangling.payload != null) dangling.payload.edges[0].target = 'system:missing';
    expect(validateYggdrasilTopologyProjection(dangling)).toMatch(/dangling/);
  });

  it('accepts explicit NOT_COMPUTABLE and rejects future versions', () => {
    const missing = topology();
    missing.status = 'NOT_COMPUTABLE';
    missing.payload = null;
    missing.not_computable_reason = 'No usable topology evidence was supplied.';
    expect(validateYggdrasilTopologyProjection(missing)).toBeNull();
    const future = topology() as unknown as Record<string, unknown>;
    future.schema_version = 'AALViz.YggdrasilTopology.v2';
    expect(validateYggdrasilTopologyProjection(future)).toMatch(/unsupported/);
  });
});
