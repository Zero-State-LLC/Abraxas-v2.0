export interface InstantiationDimensionTile {
  name: string;
  epistemic_status: string;
  evidence_count: number;
  not_computable_reason: string | null;
}

export interface InstantiationStateTile {
  state_id: string;
  state_hash: string;
  observation_window: { start: string; end: string };
  causal_exposure: string;
  aggregate_instantiation_depth: string;
  dimensions: InstantiationDimensionTile[];
}

export interface InstantiationLineageEdge {
  transition_id: string;
  transition_hash: string;
  from_state_id: string;
  to_state_id: string;
  causal_exposure: string;
  feedback_contaminated: boolean;
  independent_confirmation_eligible: boolean;
  dimension_changes: Array<{
    dimension: string;
    change_kind: string;
    epistemic_status: string;
  }>;
  linked_refs: Record<string, { object_id: string; canonical_hash: string } | null>;
}

export interface InstantiationShadowFinding {
  code: string;
  severity: string;
  subject_id: string;
  message: string;
}

export interface InstantiationProjectionView {
  schema_version: string;
  view_id: string;
  lane: string;
  dimension_order: string[];
  construct_timelines: Array<{
    construct_ref: { object_id: string; canonical_hash: string };
    states: InstantiationStateTile[];
  }>;
  lineage_edges: InstantiationLineageEdge[];
  unresolved_state_ids: string[];
  shadow_overlay: {
    report_id: string;
    report_hash: string;
    findings: InstantiationShadowFinding[];
  } | null;
  authority: {
    advisory_only: boolean;
    projection_only: boolean;
    non_authoritative: boolean;
    forecast_authority: boolean;
    intervention_authority: boolean;
    execution_authority: boolean;
    canon_mutation: boolean;
    runtime_mutation: boolean;
  };
  view_hash: string;
}

/** Fail closed on any authority drift: display requires a projection-only view. */
function validateAuthority(view: InstantiationProjectionView): void {
  const a = view.authority;
  if (a.projection_only !== true || a.advisory_only !== true || a.non_authoritative !== true) {
    throw new Error('instantiation projection must be projection-only/advisory');
  }
  for (const key of [
    'forecast_authority',
    'intervention_authority',
    'execution_authority',
    'canon_mutation',
    'runtime_mutation',
  ] as const) {
    if (a[key] !== false) {
      throw new Error(`instantiation projection authority.${key} must be false`);
    }
  }
}

export async function loadInstantiationProjection(): Promise<InstantiationProjectionView | null> {
  let resp: Response;
  try {
    resp = await fetch('/instantiation-projection.json', {
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
  const view = raw as InstantiationProjectionView;
  if (view.schema_version !== 'InstantiationProjectionView.v1') return null;
  if (view.lane !== 'PROJECTION') return null;
  try {
    validateAuthority(view);
  } catch {
    return null;
  }
  return view;
}
