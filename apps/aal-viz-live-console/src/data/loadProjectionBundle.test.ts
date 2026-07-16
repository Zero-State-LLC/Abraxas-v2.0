import { describe, expect, it } from 'vitest';
import generatedBundle from '../../public/projection-bundle.json';
import type { LiveConsoleProjectionBundle } from '../types';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import { validateProjectionBundle } from './loadProjectionBundle';

describe('validateProjectionBundle v0.2', () => {
  it('accepts a complete projection-only operator platform bundle', () => {
    const result = validateProjectionBundle(sampleProjectionBundle);
    expect(result.source_mode).toBe('LIVE_ARTIFACT_BUNDLE');
    expect(result.bundle.operator_platform.projection_only).toBe(true);
  });

  it('accepts section-level NOT_COMPUTABLE states', () => {
    const bundle = structuredClone(sampleProjectionBundle);
    bundle.operator_platform.production_slice = {
      ...bundle.operator_platform.production_slice,
      status: 'NOT_COMPUTABLE',
      payload: null,
      not_computable_reason: 'Missing source.',
    };
    bundle.operator_platform.contract_graph = {
      ...bundle.operator_platform.contract_graph,
      status: 'NOT_COMPUTABLE',
      payload: null,
      not_computable_reason: 'Missing source.',
    };
    const result = validateProjectionBundle(bundle);
    expect(result.source_mode).toBe('LIVE_ARTIFACT_BUNDLE');
  });

  it('fails closed for legacy schema versions', () => {
    const bundle = { ...sampleProjectionBundle, schema_version: 'AALViz.LiveConsoleProjectionBundle.v0.1' };
    const result = validateProjectionBundle(bundle);
    expect(result.source_mode).toBe('FAIL_CLOSED');
    expect(result.fail_closed_reason).toMatch(/schema_version mismatch/);
  });

  it('fails closed when the operator platform grants authority', () => {
    const bundle = structuredClone(sampleProjectionBundle);
    (bundle.operator_platform as { projection_only: boolean }).projection_only = false;
    const result = validateProjectionBundle(bundle);
    expect(result.source_mode).toBe('FAIL_CLOSED');
    expect(result.fail_closed_reason).toMatch(/operator_platform\.projection_only/);
  });

  it('fails closed for malformed topology arrays', () => {
    const bundle = structuredClone(sampleProjectionBundle);
    if (bundle.operator_platform.topology.payload != null) {
      (bundle.operator_platform.topology.payload as { nodes: unknown }).nodes = null;
    }
    const result = validateProjectionBundle(bundle);
    expect(result.source_mode).toBe('FAIL_CLOSED');
    expect(result.fail_closed_reason).toMatch(/topology payload/);
  });

  it('fails closed for duplicate topology node IDs', () => {
    const bundle = structuredClone(sampleProjectionBundle);
    const nodes = bundle.operator_platform.topology.payload?.nodes;
    expect(nodes).toBeDefined();
    nodes?.push(structuredClone(nodes[0]));
    const result = validateProjectionBundle(bundle);
    expect(result.source_mode).toBe('FAIL_CLOSED');
    expect(result.fail_closed_reason).toMatch(/duplicate node id/i);
  });

  it('fails closed for dangling topology endpoints', () => {
    const bundle = structuredClone(sampleProjectionBundle);
    const edges = bundle.operator_platform.topology.payload?.edges;
    expect(edges).toBeDefined();
    if (edges?.[0] != null) edges[0].target = 'missing-node';
    const result = validateProjectionBundle(bundle);
    expect(result.source_mode).toBe('FAIL_CLOSED');
    expect(result.fail_closed_reason).toMatch(/dangling edge/i);
  });

  it('rejects a malformed optional integrity sidecar', () => {
    const malformed = structuredClone(sampleProjectionBundle);
    (malformed as unknown as { yggdrasil_topology_integrity: unknown }).yggdrasil_topology_integrity = {};
    const result = validateProjectionBundle(malformed);
    expect(result.source_mode).toBe('FAIL_CLOSED');
    expect(result.fail_closed_reason).toMatch(/integrity schema/);
  });

  it('accepts current delta intelligence and rejects malformed or stale sidecars', () => {
    const current = structuredClone(generatedBundle) as unknown as LiveConsoleProjectionBundle;
    expect(validateProjectionBundle(current).source_mode).toBe('LIVE_ARTIFACT_BUNDLE');

    const malformed = structuredClone(current);
    (malformed as unknown as { yggdrasil_topology_delta_intelligence: unknown }).yggdrasil_topology_delta_intelligence = {};
    expect(validateProjectionBundle(malformed).fail_closed_reason).toMatch(/delta_intelligence schema/);

    const stale = structuredClone(current);
    if (stale.yggdrasil_topology_delta_intelligence != null) {
      stale.yggdrasil_topology_delta_intelligence.generation.current_topology_generation_id = 'f'.repeat(64);
    }
    expect(validateProjectionBundle(stale).fail_closed_reason).toMatch(/current generation is stale/);
  });

  it('accepts current advisory alerts and rejects malformed or stale sidecars', () => {
    const current = structuredClone(generatedBundle) as unknown as LiveConsoleProjectionBundle;
    expect(validateProjectionBundle(current).source_mode).toBe('LIVE_ARTIFACT_BUNDLE');

    const malformed = structuredClone(current);
    (malformed as unknown as { route_receipt_advisory_alerts: unknown }).route_receipt_advisory_alerts = {};
    expect(validateProjectionBundle(malformed).fail_closed_reason).toMatch(/advisory_alerts schema/);

    const stale = structuredClone(current);
    if (stale.route_receipt_advisory_alerts != null) {
      stale.route_receipt_advisory_alerts.generation.delta_generation_id = 'f'.repeat(64);
    }
    expect(validateProjectionBundle(stale).fail_closed_reason).toMatch(/delta generation is stale/);
  });

  it('rejects absolute source artifact paths', () => {
    const bundle = structuredClone(sampleProjectionBundle);
    bundle.operator_platform.source_artifacts.push({
      source_key: 'invalid',
      path: '/private/evidence.json',
      declared_canonical_hash: null,
      content_sha256: null,
      integrity_state: 'NOT_COMPUTABLE',
    });
    const result = validateProjectionBundle(bundle);
    expect(result.source_mode).toBe('FAIL_CLOSED');
    expect(result.fail_closed_reason).toMatch(/repository-relative/i);
  });
});
