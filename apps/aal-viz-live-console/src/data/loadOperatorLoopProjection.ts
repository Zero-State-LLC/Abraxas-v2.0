export interface OperatorLoopTruthSurface {
  role: string;
  truth_claim: string;
  glyph: string;
  status: string;
  source: string;
  items: Array<Record<string, unknown>>;
  notes: string[];
  authority_implication: string;
  can_assign: boolean;
  can_approve: boolean;
  can_merge: boolean;
  can_deploy: boolean;
}

export interface OperatorLoopProjection {
  schema_version: string;
  summary: {
    work_packet_count: number;
    handoff_count: number;
    file_overlap_count: number;
    github_item_count?: number;
    notion_item_count?: number;
    ci_item_count?: number;
    validation_error_count?: number;
    by_producer?: Record<string, number>;
    by_work_state?: Record<string, number>;
  };
  work_packets: Array<{
    work_packet_id: string;
    goal: string;
    producer_system: string;
    work_state: string;
    authority_implication: string;
  }>;
  handoffs: Array<{
    handoff_id: string;
    work_packet_id: string;
    status: string;
    authority_implication: string;
  }>;
  file_overlaps: Array<{
    conflict_class: string;
    detail: string;
    subject_ids: string[];
  }>;
  truth_surfaces?: {
    github: OperatorLoopTruthSurface;
    notion: OperatorLoopTruthSurface;
    ci: OperatorLoopTruthSurface;
    lineage_rule?: string;
  };
  authority: {
    projection_only: boolean;
    assignment_authority: boolean;
    approval_authority: boolean;
    producer_identity_grants_authority: boolean;
    runtime_mutation_allowed?: boolean;
    promotion_allowed?: boolean;
    production_activation_allowed?: boolean;
  };
  notes?: string[];
}

function validateAuthority(projection: OperatorLoopProjection): void {
  const a = projection.authority;
  if (a.projection_only !== true) {
    throw new Error('authority.projection_only must be true');
  }
  if (a.assignment_authority !== false) {
    throw new Error('authority.assignment_authority must be false');
  }
  if (a.approval_authority !== false) {
    throw new Error('authority.approval_authority must be false');
  }
  if (a.producer_identity_grants_authority !== false) {
    throw new Error('authority.producer_identity_grants_authority must be false');
  }
}

export async function loadOperatorLoopProjection(): Promise<OperatorLoopProjection | null> {
  let resp: Response;
  try {
    resp = await fetch('/operator-loop-projection.json', {
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
  const projection = raw as OperatorLoopProjection;
  if (projection.schema_version !== 'OperatorLoopProjection.v1') return null;
  try {
    validateAuthority(projection);
  } catch {
    return null;
  }
  return projection;
}
