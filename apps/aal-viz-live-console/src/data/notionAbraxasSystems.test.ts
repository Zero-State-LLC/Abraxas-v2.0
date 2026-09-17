import { describe, expect, it } from 'vitest';
import { sampleProjectionBundle } from './sampleProjectionBundle';

/** Notion 2026-09-15 model-stack owners + Familiar ownership add. */
const NOTION_STACK_SYSTEMS = [
  'sigil_forge',
  'familiar',
  'hyperlex',
  'athanor',
  'semion',
  'trutina',
] as const;

describe('Notion Abraxas specialist systems on the projection spine', () => {
  it('projects every Notion model-stack specialist without granting execution', () => {
    const ids = sampleProjectionBundle.systems.map((system) => system.system_id);
    for (const id of NOTION_STACK_SYSTEMS) {
      expect(ids).toContain(id);
    }
    for (const id of NOTION_STACK_SYSTEMS) {
      const system = sampleProjectionBundle.systems.find((row) => row.system_id === id);
      expect(system?.shadow_only).toBe(true);
      expect(system?.projection_packets.every((pkt) => pkt.projection_only === true)).toBe(true);
      expect(system?.projection_packets.every((pkt) => pkt.authority_source === 'SHADOW_LANE')).toBe(
        true,
      );
    }
  });

  it('keeps unshared specialist owner pages not-computable instead of inventing READY', () => {
    for (const id of ['athanor', 'semion', 'trutina'] as const) {
      const system = sampleProjectionBundle.systems.find((row) => row.system_id === id);
      expect(system?.status).toBe('NOT_COMPUTABLE');
      expect(system?.projection_packets[0]?.display_value).toBe('SLOT_RESERVED');
    }
  });

  it('does not collapse Sigil-Forge specialist into a generic sigil-output mark', () => {
    const forge = sampleProjectionBundle.systems.find((row) => row.system_id === 'sigil_forge');
    expect(forge?.display_name).toBe('SIGIL-FORGE');
    expect(forge?.system_id).not.toBe('sigil_output');
  });
});
