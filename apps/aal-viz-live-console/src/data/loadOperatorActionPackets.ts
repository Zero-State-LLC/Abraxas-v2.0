import type { OperatorActionPacketsBundle } from '../types';

function validatePacketsBundle(bundle: OperatorActionPacketsBundle): void {
  if (bundle.schema_version !== 'AALViz.OperatorActionPackets.v0.1') {
    throw new Error(
      `schema_version mismatch: expected AALViz.OperatorActionPackets.v0.1, got ${String(bundle.schema_version)}`,
    );
  }
  const a = bundle.authority;
  if (a.execution_allowed !== false) throw new Error('authority.execution_allowed must be false');
  if (a.runtime_mutation_allowed !== false)
    throw new Error('authority.runtime_mutation_allowed must be false');
  if (a.promotion_allowed !== false) throw new Error('authority.promotion_allowed must be false');
  if (a.production_activation_allowed !== false)
    throw new Error('authority.production_activation_allowed must be false');

  for (const pkt of bundle.packets) {
    if (pkt.execution_allowed !== false) {
      throw new Error(`packet ${pkt.packet_id}: execution_allowed must be false`);
    }
    if (pkt.runtime_mutation_allowed !== false) {
      throw new Error(`packet ${pkt.packet_id}: runtime_mutation_allowed must be false`);
    }
  }
}

export async function loadOperatorActionPackets(): Promise<OperatorActionPacketsBundle | null> {
  let resp: Response;
  try {
    resp = await fetch('/operator-action-packets.json', {
      method: 'GET',
      cache: 'no-cache',
      headers: { Accept: 'application/json' },
    });
  } catch {
    return null;
  }

  if (!resp.ok) return null;

  let raw: unknown;
  try {
    raw = await resp.json();
  } catch {
    return null;
  }

  if (typeof raw !== 'object' || raw === null) return null;
  const bundle = raw as OperatorActionPacketsBundle;

  if (bundle.fail_closed_reason != null) return null;
  if (!Array.isArray(bundle.packets) || bundle.packets.length === 0) return null;

  try {
    validatePacketsBundle(bundle);
  } catch {
    return null;
  }

  return bundle;
}
