import { describe, expect, it } from 'vitest';
import bundleJson from '../../public/projection-bundle.json';
import type { LiveConsoleProjectionBundle } from '../types';
import { validateYggdrasilTopologyDeltaIntelligenceProjection } from './yggdrasilTopologyDeltaIntelligenceContract';

const bundle = bundleJson as unknown as LiveConsoleProjectionBundle;

function fixture() {
  const value = bundle.yggdrasil_topology_delta_intelligence;
  if (value == null) throw new Error('generated delta intelligence fixture is missing');
  return structuredClone(value);
}

describe('YGGDRASIL topology delta intelligence runtime contract', () => {
  it('accepts the generated current-corpus sidecar', () => {
    expect(validateYggdrasilTopologyDeltaIntelligenceProjection(
      fixture(), bundle.yggdrasil_topology,
    )).toBeNull();
  });

  it('rejects authority, stale generation, and unsafe source paths', () => {
    const authority = fixture();
    authority.authority.automatic_remediation_allowed = true as false;
    expect(validateYggdrasilTopologyDeltaIntelligenceProjection(authority)).toMatch(/projection locks/);

    const stale = fixture();
    stale.generation.current_topology_generation_id = 'f'.repeat(64);
    expect(validateYggdrasilTopologyDeltaIntelligenceProjection(stale, bundle.yggdrasil_topology)).toMatch(/stale/);

    const path = fixture();
    path.source_artifacts[0].path = '/tmp/input.json';
    expect(validateYggdrasilTopologyDeltaIntelligenceProjection(path)).toMatch(/source/);
  });

  it('rejects score tampering, dangling priorities, and false resolution', () => {
    const score = fixture();
    const priority = score.sections.review_priorities.entries?.[0];
    if (priority == null) throw new Error('priority fixture is missing');
    priority.score -= 1;
    expect(validateYggdrasilTopologyDeltaIntelligenceProjection(score)).toMatch(/score arithmetic/);

    const dangling = fixture();
    const danglingPriority = dangling.sections.review_priorities.entries?.[0];
    if (danglingPriority == null) throw new Error('priority fixture is missing');
    danglingPriority.source_ref.entity_id = `correlation:${'0'.repeat(64)}`;
    expect(validateYggdrasilTopologyDeltaIntelligenceProjection(dangling)).toMatch(/dangling/);

    const resolution = fixture();
    const correlation = resolution.sections.finding_correlation.entries?.[0];
    if (correlation == null) throw new Error('correlation fixture is missing');
    correlation.state = 'RESOLVED';
    correlation.current_finding_id = `finding:${'1'.repeat(64)}`;
    expect(validateYggdrasilTopologyDeltaIntelligenceProjection(resolution)).toMatch(/false resolution/);
  });
});
