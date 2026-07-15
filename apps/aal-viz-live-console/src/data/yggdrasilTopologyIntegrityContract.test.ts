import { describe, expect, it } from 'vitest';
import type { YggdrasilTopologyIntegrityProjection } from '../types';
import { validateYggdrasilTopologyIntegrityProjection } from './yggdrasilTopologyIntegrityContract';

export function integrityProjectionFixture(): YggdrasilTopologyIntegrityProjection {
  return {
    schema_version: 'AALViz.YggdrasilTopologyIntegrity.v1',
    generation: {
      generated_at: '2026-07-15T00:00:00Z',
      generated_by: 'YGGDRASIL_TOPOLOGY_INTEGRITY_FINDINGS_001',
      integrity_generation_id: 'a'.repeat(64),
      topology_generation_id: 'b'.repeat(64),
      operator_platform_generation_id: 'c'.repeat(64),
      temporal_diff_generation_id: null,
    },
    status: 'AVAILABLE',
    provenance: 'OBSERVED',
    source_artifacts: [{
      id: 'source:topology', source_key: 'topology', path: 'out/topology.json',
      declared_canonical_hash: 'd'.repeat(64), content_sha256: 'e'.repeat(64),
      integrity_state: 'VERIFIED',
    }],
    authority: {
      projection_only: true, runtime_mutation_allowed: false, canon_mutation_allowed: false,
      execution_authority: false, production_activation_allowed: false,
      graph_driven_execution_allowed: false, alert_delivery_allowed: false,
      acknowledgement_state_allowed: false, browser_persistence_allowed: false,
      route_receipt_triggering_allowed: false, scheduling_allowed: false,
    },
    payload: { summary: { finding_count: 0, affected_entity_count: 0, non_computable_count: 0, severity_counts: {}, type_counts: {} }, findings: [] },
    not_computable_reason: null,
    validation_findings: [],
    canonical_hash: 'f'.repeat(64),
  };
}

describe('YGGDRASIL topology integrity runtime contract', () => {
  it('accepts a canonical projection-only sidecar', () => {
    expect(validateYggdrasilTopologyIntegrityProjection(integrityProjectionFixture())).toBeNull();
  });

  it('rejects authority escalation and absolute paths', () => {
    const authority = structuredClone(integrityProjectionFixture());
    (authority.authority as { alert_delivery_allowed: boolean }).alert_delivery_allowed = true;
    expect(validateYggdrasilTopologyIntegrityProjection(authority)).toMatch(/projection locks/);
    const path = structuredClone(integrityProjectionFixture());
    path.source_artifacts[0].path = '/tmp/topology.json';
    expect(validateYggdrasilTopologyIntegrityProjection(path)).toMatch(/source artifact/);
  });

  it('rejects false temporal conclusions and inconsistent summaries', () => {
    const artifact = integrityProjectionFixture();
    artifact.payload!.findings = [{
      id: `finding:${'1'.repeat(64)}`, finding_type: 'TEMPORAL_REMOVAL', severity: 'MEDIUM',
      subject_key: 'edge:old', entity_ref: { category: 'TOPOLOGY_EDGE', entity_id: 'edge:old' },
      evidence_refs: ['source:topology'], provenance: 'OBSERVED', confidence: 'VERIFIED',
      reason: 'Removed.', computability: 'COMPUTABLE', generation_binding: {
        topology_generation_id: 'b'.repeat(64), operator_platform_generation_id: 'c'.repeat(64), temporal_diff_generation_id: null,
      },
    }];
    expect(validateYggdrasilTopologyIntegrityProjection(artifact)).toMatch(/without matching evidence/);
    const summary = integrityProjectionFixture();
    summary.payload!.summary.finding_count = 1;
    expect(validateYggdrasilTopologyIntegrityProjection(summary)).toMatch(/summary/);
  });
});
