import type { ProjectionPacket, SystemProjection } from '../types';

export interface ForgeInspectProjection {
  schema_version: 'ForgeInspectProjection.v1';
  lane: 'SHADOW';
  specialist_id: 'sigil-forge';
  chips: {
    engine: string;
    construction: string;
    proof: 'commitment' | 'skipped' | 'zk-knowledge' | 'zk-forge';
    authority: 'SHADOW';
  };
  intent_digest_prefix: string | null;
  sigil_root_prefix: string | null;
  authority_visible: true;
  geometry_redrawn: false;
}

const STAMP = '2026-09-16T00:00:00Z';

function packet(
  id: string,
  packetType: string,
  displayValue: string | null,
): ProjectionPacket {
  return {
    packet_id: id,
    packet_type: packetType,
    status: 'RESOLVED',
    display_value: displayValue,
    authority_source: 'SHADOW_LANE',
    projection_only: true,
  };
}

export function buildForgeInspectSystem(
  projection: ForgeInspectProjection,
): SystemProjection {
  return {
    system_id: 'sigil_forge',
    display_name: 'SIGIL-FORGE',
    status: 'READY',
    completion_pct: 70,
    risk_level: 'LOW',
    last_updated: STAMP,
    shadow_only: true,
    projection_packets: [
      packet('sf-pkt-engine', 'FORGE_ENGINE', projection.chips.engine),
      packet('sf-pkt-construction', 'FORGE_CONSTRUCTION', projection.chips.construction),
      packet('sf-pkt-proof', 'FORGE_PROOF', projection.chips.proof),
      packet('sf-pkt-authority', 'FORGE_AUTHORITY', projection.chips.authority),
    ],
    ledger_receipts: [
      {
        receipt_id: 'sf-rcpt-001',
        event: 'FORGE_INSPECT_PROJECTED',
        timestamp: STAMP,
        canonical_hash: 'f7a8b9f7a8b9f7a8b9f7a8b9f7a8b9f7a8b9f7a8b9f7a8b9f7a8b9f7a8b9f7a8',
      },
    ],
  };
}
