import type { LiveConsoleProjectionBundle, SourceMode } from '../types';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import { validateOperatorPlatformProjection } from './operatorPlatformContract';
import { validateYggdrasilTopologyProjection } from './yggdrasilTopologyContract';
import { validateYggdrasilTopologyIntegrityProjection } from './yggdrasilTopologyIntegrityContract';
import { validateYggdrasilTopologyDeltaIntelligenceProjection } from './yggdrasilTopologyDeltaIntelligenceContract';

export interface LoadResult {
  bundle: LiveConsoleProjectionBundle;
  source_mode: SourceMode;
  fail_closed_reason: string | null;
}

export function validateAuthority(bundle: LiveConsoleProjectionBundle): void {
  const a = bundle.authority;
  if (a.projection_only !== true) {
    throw new Error('authority.projection_only must be true');
  }
  if (a.runtime_mutation_allowed !== false) {
    throw new Error('authority.runtime_mutation_allowed must be false');
  }
  if (a.promotion_allowed !== false) {
    throw new Error('authority.promotion_allowed must be false');
  }
  if (a.production_activation_allowed !== false) {
    throw new Error('authority.production_activation_allowed must be false');
  }
  if (bundle.operator_platform?.projection_only !== true) {
    throw new Error('operator_platform.projection_only must be true');
  }
}

export function failClosed(reason: string): LoadResult {
  return {
    bundle: {
      ...sampleProjectionBundle,
      source_mode: 'FAIL_CLOSED',
      fail_closed_reason: reason,
    },
    source_mode: 'FAIL_CLOSED',
    fail_closed_reason: reason,
  };
}

export function validateProjectionBundle(raw: unknown): LoadResult {
  if (typeof raw !== 'object' || raw === null) {
    return failClosed('projection-bundle.json: not an object');
  }

  const bundle = raw as LiveConsoleProjectionBundle;

  if (bundle.schema_version !== 'AALViz.LiveConsoleProjectionBundle.v0.2') {
    return failClosed(
      `schema_version mismatch: expected AALViz.LiveConsoleProjectionBundle.v0.2, got ${String(bundle.schema_version)}`,
    );
  }

  try {
    validateAuthority(bundle);
  } catch (err) {
    return failClosed(
      `authority validation failed: ${err instanceof Error ? err.message : String(err)}`,
    );
  }

  if (!Array.isArray(bundle.systems) || bundle.systems.length === 0) {
    return failClosed('projection-bundle.json: systems array is empty or missing');
  }

  const platformError = validateOperatorPlatformProjection(bundle.operator_platform);
  if (platformError != null) {
    return failClosed(`projection-bundle.json: ${platformError}`);
  }
  if (bundle.yggdrasil_topology != null) {
    const topologyError = validateYggdrasilTopologyProjection(bundle.yggdrasil_topology);
    if (topologyError != null) {
      return failClosed(`projection-bundle.json: ${topologyError}`);
    }
  }
  if (bundle.yggdrasil_topology_integrity != null) {
    const integrityError = validateYggdrasilTopologyIntegrityProjection(
      bundle.yggdrasil_topology_integrity,
      bundle.yggdrasil_topology,
    );
    if (integrityError != null) {
      return failClosed(`projection-bundle.json: ${integrityError}`);
    }
  }
  if (bundle.yggdrasil_topology_delta_intelligence != null) {
    const deltaError = validateYggdrasilTopologyDeltaIntelligenceProjection(
      bundle.yggdrasil_topology_delta_intelligence,
      bundle.yggdrasil_topology,
    );
    if (deltaError != null) {
      return failClosed(`projection-bundle.json: ${deltaError}`);
    }
  }

  return {
    bundle: { ...bundle, source_mode: 'LIVE_ARTIFACT_BUNDLE', fail_closed_reason: null },
    source_mode: 'LIVE_ARTIFACT_BUNDLE',
    fail_closed_reason: null,
  };
}

export async function loadProjectionBundle(
  sourceMode: SourceMode = 'LIVE_ARTIFACT_BUNDLE',
): Promise<LoadResult> {
  let resp: Response;
  try {
    resp = await fetch('/projection-bundle.json', {
      method: 'GET',
      cache: 'no-cache',
      headers: { Accept: 'application/json' },
    });
  } catch (err) {
    return {
      bundle: { ...sampleProjectionBundle, source_mode: 'SAMPLE_FALLBACK', fail_closed_reason: null },
      source_mode: 'SAMPLE_FALLBACK',
      fail_closed_reason: null,
    };
  }

  if (!resp.ok) {
    return {
      bundle: { ...sampleProjectionBundle, source_mode: 'SAMPLE_FALLBACK', fail_closed_reason: null },
      source_mode: 'SAMPLE_FALLBACK',
      fail_closed_reason: null,
    };
  }

  let raw: unknown;
  try {
    raw = await resp.json();
  } catch {
    return failClosed('projection-bundle.json is not valid JSON');
  }

  const result = validateProjectionBundle(raw);
  if (result.source_mode === 'FAIL_CLOSED') {
    return result;
  }
  return {
    bundle: { ...result.bundle, source_mode: sourceMode, fail_closed_reason: null },
    source_mode: sourceMode,
    fail_closed_reason: null,
  };
}
