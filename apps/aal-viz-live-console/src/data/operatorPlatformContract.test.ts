import { describe, expect, it } from 'vitest';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import { validateOperatorPlatformProjection } from './operatorPlatformContract';

const HASH_A = 'a'.repeat(64);
const HASH_B = 'b'.repeat(64);

function v1Projection(): Record<string, unknown> {
  const platform = structuredClone(sampleProjectionBundle.operator_platform) as unknown as Record<string, unknown>;
  const temporal = platform.temporal_diff as Record<string, unknown>;
  const payload = temporal.payload as Record<string, unknown>;
  payload.prior_generation_id = HASH_A;
  payload.current_generation_id = HASH_B;
  payload.status = 'CHANGED';
  payload.total_change_count = 1;
  payload.category_counts = {
    TOPOLOGY_NODE: 1,
    TOPOLOGY_EDGE: 0,
    CONTRACT_FIELD: 0,
    OWNERSHIP: 0,
    VALIDATOR_STATE: 0,
    RECEIPT: 0,
    PACKET: 0,
    SOURCE_INTEGRITY: 0,
    SECTION_STATUS: 0,
  };
  payload.entries = [{
    id: 'c'.repeat(64),
    operation: 'ADDED',
    category: 'TOPOLOGY_NODE',
    impact: 'NEUTRAL',
    surface: 'topology',
    entity_id: 'node:2',
    summary: 'ADDED topology node: node:2',
    severity: 'INFO',
    field_path: '/topology/payload/nodes/node:2',
    prior_value: null,
    current_value: { id: 'node:2' },
    provenance: 'OBSERVED',
    prior_generation_id: HASH_A,
    current_generation_id: HASH_B,
    prior_evidence_status: 'AVAILABLE',
    current_evidence_status: 'AVAILABLE',
    reason_code: null,
    source_keys: ['graph_render'],
  }];
  return platform;
}

describe('validateOperatorPlatformProjection temporal diff v1', () => {
  it('accepts a complete additive v1 payload', () => {
    expect(validateOperatorPlatformProjection(v1Projection())).toBeNull();
  });

  it('preserves legacy v0.2 compatibility', () => {
    const platform = v1Projection();
    const payload = (platform.temporal_diff as Record<string, unknown>).payload as Record<string, unknown>;
    for (const field of ['prior_generation_id', 'current_generation_id', 'comparison_scope', 'out_of_scope', 'category_counts', 'not_computable_count']) delete payload[field];
    payload.entries = [];
    expect(validateOperatorPlatformProjection(platform)).toBeNull();
  });

  it('rejects malformed JSON Pointer paths', () => {
    const platform = v1Projection();
    const payload = (platform.temporal_diff as Record<string, unknown>).payload as Record<string, unknown>;
    (payload.entries as Array<Record<string, unknown>>)[0].field_path = 'topology/nodes';
    expect(validateOperatorPlatformProjection(platform)).toContain('malformed JSON Pointer');
  });

  it('rejects false removals under partial evidence', () => {
    const platform = v1Projection();
    const payload = (platform.temporal_diff as Record<string, unknown>).payload as Record<string, unknown>;
    const entry = (payload.entries as Array<Record<string, unknown>>)[0];
    entry.operation = 'REMOVED';
    entry.prior_value = { id: 'node:2' };
    entry.current_value = null;
    entry.current_evidence_status = 'PARTIAL';
    expect(validateOperatorPlatformProjection(platform)).toContain('lacks complete evidence');
  });

  it('rejects generation reference mismatches and unsupported categories', () => {
    const platform = v1Projection();
    const payload = (platform.temporal_diff as Record<string, unknown>).payload as Record<string, unknown>;
    const entry = (payload.entries as Array<Record<string, unknown>>)[0];
    entry.current_generation_id = HASH_A;
    expect(validateOperatorPlatformProjection(platform)).toContain('generation reference mismatch');
    entry.current_generation_id = HASH_B;
    entry.category = 'QUEUE';
    expect(validateOperatorPlatformProjection(platform)).toContain('unsupported category');
  });
});
