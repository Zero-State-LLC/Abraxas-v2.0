import { describe, expect, it } from 'vitest';
import { buildForgeInspectSystem } from './buildForgeInspectFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';

const projection = {
  schema_version: 'ForgeInspectProjection.v1' as const,
  lane: 'SHADOW' as const,
  specialist_id: 'sigil-forge' as const,
  chips: {
    engine: 'sigil-forge',
    construction: 'spare.letter_monogram',
    proof: 'commitment' as const,
    authority: 'SHADOW' as const,
  },
  intent_digest_prefix: '14a878a7d0fdf477',
  sigil_root_prefix: '301e83cfd89e6cd1',
  authority_visible: true as const,
  geometry_redrawn: false as const,
};

describe('buildForgeInspectSystem', () => {
  it('projects SHADOW inspect chips without granting authority', () => {
    const system = buildForgeInspectSystem(projection);
    expect(system.system_id).toBe('sigil_forge');
    expect(system.shadow_only).toBe(true);
    expect(system.projection_packets.every((pkt) => pkt.projection_only === true)).toBe(true);
    expect(system.projection_packets.map((pkt) => pkt.packet_type)).toEqual([
      'FORGE_ENGINE',
      'FORGE_CONSTRUCTION',
      'FORGE_PROOF',
      'FORGE_AUTHORITY',
    ]);
    expect(system.projection_packets.find((pkt) => pkt.packet_type === 'FORGE_PROOF')?.display_value).toBe(
      'commitment',
    );
    expect(system.projection_packets.find((pkt) => pkt.packet_type === 'FORGE_AUTHORITY')?.display_value).toBe(
      'SHADOW',
    );
  });

  it('keeps sample bundle aligned with inspect chip types', () => {
    const sample = sampleProjectionBundle.systems.find((system) => system.system_id === 'sigil_forge');
    const built = buildForgeInspectSystem(projection);
    expect(sample).toBeDefined();
    expect(sample?.projection_packets.map((pkt) => pkt.packet_type)).toEqual(
      built.projection_packets.map((pkt) => pkt.packet_type),
    );
    expect(sample?.shadow_only).toBe(true);
  });
});
