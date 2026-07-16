import type {
  YggdrasilDeltaCorrelation,
  YggdrasilDeltaPriority,
  YggdrasilDeltaStructuralClass,
  YggdrasilTopologyProjection,
} from '../types';

type JsonRecord = Record<string, unknown>;

const HASH = /^[0-9a-f]{64}$/;
const TYPED_ID = /^(correlation|structural|path|priority):[0-9a-f]{64}$/;
const STATUS = new Set(['AVAILABLE', 'PARTIAL', 'NOT_COMPUTABLE']);
const PROVENANCE = new Set(['OBSERVED', 'INFERRED']);
const CONFIDENCE = new Set(['VERIFIED', 'SUPPORTED', 'INFERRED', 'NOT_COMPUTABLE']);
const SEVERITIES = new Set(['HIGH', 'MEDIUM', 'LOW', 'INFO', 'NOT_COMPUTABLE']);
const STRUCTURAL_CLASSES = new Set<YggdrasilDeltaStructuralClass>([
  'ISOLATED_NODE_EMERGENCE', 'ORPHANED_CONTRACT', 'VALIDATOR_COVERAGE_LOSS',
  'BROKEN_PRODUCER_CONSUMER_PATH', 'OWNERSHIP_DRIFT', 'STALE_EVIDENCE_CHAIN',
  'TOPOLOGY_FRAGMENTATION', 'UNEXPECTED_CLUSTER_FUSION',
]);
const SEVERITY_ORDER: Record<string, number> = { HIGH: 4, MEDIUM: 3, LOW: 2, INFO: 1 };

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isHashOrNull(value: unknown): boolean {
  return value === null || (typeof value === 'string' && HASH.test(value));
}

function isSortedUnique(values: unknown): values is string[] {
  return Array.isArray(values) && values.every((value) => typeof value === 'string') &&
    values.join('\0') === [...values].sort().join('\0') && new Set(values).size === values.length;
}

function isRelativePath(value: unknown): value is string {
  return typeof value === 'string' && value.length > 0 && !value.startsWith('/') &&
    !/^[A-Za-z]:[\\/]/.test(value) && !value.includes('\\') && !value.split('/').includes('..');
}

function authorityError(value: unknown): string | null {
  if (!isRecord(value)) return 'yggdrasil_topology_delta_intelligence.authority is malformed';
  const expected: Record<string, boolean> = {
    projection_only: true, execution_authority: false, canon_mutation_allowed: false,
    runtime_mutation_allowed: false, graph_driven_execution_allowed: false,
    production_activation_allowed: false, route_receipt_triggering_allowed: false,
    scheduling_allowed: false, alert_delivery_allowed: false,
    acknowledgement_state_allowed: false, browser_persistence_allowed: false,
    automatic_remediation_allowed: false, autonomous_escalation_allowed: false,
  };
  for (const [key, expectedValue] of Object.entries(expected)) {
    if (value[key] !== expectedValue) return `yggdrasil_topology_delta_intelligence.authority.${key} violates projection locks`;
  }
  return null;
}

function validateSection(raw: unknown, name: string): string | null {
  if (!isRecord(raw) || !STATUS.has(String(raw.status)) || !PROVENANCE.has(String(raw.provenance)) ||
      !isSortedUnique(raw.validation_findings)) return `delta intelligence ${name} envelope is malformed`;
  if (raw.status === 'NOT_COMPUTABLE') {
    if (raw.entries !== null || typeof raw.not_computable_reason !== 'string' || raw.not_computable_reason.length === 0) {
      return `delta intelligence ${name} NOT_COMPUTABLE envelope is malformed`;
    }
  } else if (!Array.isArray(raw.entries) || raw.not_computable_reason !== null) {
    return `delta intelligence ${name} available envelope is malformed`;
  }
  return null;
}

function validateCorrelation(value: unknown, index: number, sourceIds: Set<string>): string | null {
  if (!isRecord(value) || !TYPED_ID.test(String(value.id)) || value.id !== value.correlation_key ||
      !['NEW', 'RESOLVED', 'PERSISTENT', 'NOT_COMPUTABLE'].includes(String(value.state)) ||
      !['CHANGE_CORRELATED', 'UNCORRELATED', 'NOT_COMPUTABLE'].includes(String(value.correlation_state)) ||
      !isHashOrNull(typeof value.prior_finding_id === 'string' ? value.prior_finding_id.replace(/^finding:/, '') : value.prior_finding_id) ||
      !isHashOrNull(typeof value.current_finding_id === 'string' ? value.current_finding_id.replace(/^finding:/, '') : value.current_finding_id) ||
      typeof value.subject_key !== 'string' || !SEVERITIES.has(String(value.prior_severity)) && value.prior_severity !== null ||
      !SEVERITIES.has(String(value.current_severity)) && value.current_severity !== null ||
      !['INCREASED', 'DECREASED', 'UNCHANGED', 'NOT_COMPUTABLE'].includes(String(value.severity_change)) ||
      !PROVENANCE.has(String(value.provenance)) || !CONFIDENCE.has(String(value.confidence)) ||
      !isSortedUnique(value.supporting_entity_ids) || !isSortedUnique(value.supporting_temporal_entry_ids) ||
      !Number.isInteger(value.observed_generation_count) || Number(value.observed_generation_count) < 0 || Number(value.observed_generation_count) > 2 ||
      value.true_age_status !== 'NOT_COMPUTABLE' || !isSortedUnique(value.evidence_refs) ||
      !(value.evidence_refs as string[]).every((reference) => sourceIds.has(reference))) {
    return `delta intelligence correlation ${index} is malformed`;
  }
  if (value.entity_ref !== null && (!isRecord(value.entity_ref) || !['TOPOLOGY_NODE', 'TOPOLOGY_EDGE'].includes(String(value.entity_ref.category)) || typeof value.entity_ref.entity_id !== 'string')) {
    return `delta intelligence correlation ${index} has malformed entity reference`;
  }
  if (value.state === 'RESOLVED' && (value.prior_finding_id === null || value.current_finding_id !== null)) return `delta intelligence correlation ${index} has false resolution semantics`;
  if (value.state === 'PERSISTENT' && (value.prior_finding_id === null || value.current_finding_id === null || !Number.isInteger(value.persistence_seconds_lower_bound))) return `delta intelligence correlation ${index} has malformed persistence semantics`;
  return null;
}

function validateStructural(value: unknown, index: number, sourceIds: Set<string>): string | null {
  if (!isRecord(value) || !TYPED_ID.test(String(value.id)) || !STRUCTURAL_CLASSES.has(value.structural_class as YggdrasilDeltaStructuralClass) ||
      !Array.isArray(value.entity_refs) || !PROVENANCE.has(String(value.provenance)) || !CONFIDENCE.has(String(value.confidence)) ||
      typeof value.reason !== 'string' || !['COMPUTABLE', 'NOT_COMPUTABLE'].includes(String(value.computability)) ||
      !isSortedUnique(value.evidence_refs) || !(value.evidence_refs as string[]).every((reference) => sourceIds.has(reference))) {
    return `delta intelligence structural entry ${index} is malformed`;
  }
  if (value.entity_refs.some((reference) => !isRecord(reference) || !['TOPOLOGY_NODE', 'TOPOLOGY_EDGE'].includes(String(reference.category)) || typeof reference.entity_id !== 'string')) return `delta intelligence structural entry ${index} has malformed references`;
  return null;
}

function validatePath(value: unknown, index: number, sourceIds: Set<string>): string | null {
  if (!isRecord(value) || !TYPED_ID.test(String(value.id)) || typeof value.source_id !== 'string' || typeof value.target_id !== 'string' ||
      !['ADDED', 'REMOVED', 'CHANGED', 'NOT_COMPUTABLE'].includes(String(value.change)) ||
      !isSortedUnique(value.prior_node_ids) || !isSortedUnique(value.prior_edge_ids) ||
      !isSortedUnique(value.current_node_ids) || !isSortedUnique(value.current_edge_ids) ||
      !isSortedUnique(value.evidence_refs) || !(value.evidence_refs as string[]).every((reference) => sourceIds.has(reference))) {
    return `delta intelligence changed path ${index} is malformed`;
  }
  if (value.change === 'REMOVED' && (!(value.prior_node_ids as string[]).length || (value.current_node_ids as string[]).length)) return `delta intelligence changed path ${index} has false removal semantics`;
  return null;
}

function validatePriority(value: unknown, index: number, sourceIds: Set<string>, recordIds: Set<string>): string | null {
  if (!isRecord(value) || !TYPED_ID.test(String(value.id)) || !Number.isInteger(value.rank) || !Number.isInteger(value.score) ||
      Number(value.score) < 0 || Number(value.score) > 100 || !isRecord(value.score_breakdown) ||
      !['HIGH', 'MEDIUM', 'LOW', 'INFO'].includes(String(value.severity)) || !Array.isArray(value.structural_classes) ||
      !(value.structural_classes as unknown[]).every((entry) => STRUCTURAL_CLASSES.has(entry as YggdrasilDeltaStructuralClass)) ||
      !['VERIFIED', 'SUPPORTED', 'INFERRED'].includes(String(value.confidence)) || !Number.isInteger(value.evidence_count) ||
      !isSortedUnique(value.affected_surface_ids) || typeof value.why_this_matters !== 'string' || !isSortedUnique(value.evidence_refs) ||
      !(value.evidence_refs as string[]).every((reference) => sourceIds.has(reference)) || !isRecord(value.source_ref) ||
      !['INTEGRITY_FINDING', 'STRUCTURAL_DELTA'].includes(String(value.source_ref.category)) || !recordIds.has(String(value.source_ref.entity_id))) {
    return `delta intelligence priority ${index} is malformed or dangling`;
  }
  const breakdown = value.score_breakdown;
  const limits: Record<string, number> = { severity: 35, structural: 30, operational_surfaces: 20, persistence: 10, confidence: 5 };
  let total = 0;
  for (const [key, maximum] of Object.entries(limits)) {
    const component = breakdown[key];
    if (!Number.isInteger(component) || Number(component) < 0 || Number(component) > maximum) return `delta intelligence priority ${index} score component is malformed`;
    total += Number(component);
  }
  if (value.score !== Math.min(100, total)) return `delta intelligence priority ${index} score arithmetic is inconsistent`;
  return null;
}

export function validateYggdrasilTopologyDeltaIntelligenceProjection(
  raw: unknown,
  topology?: YggdrasilTopologyProjection,
): string | null {
  if (!isRecord(raw) || raw.schema_version !== 'AALViz.YggdrasilTopologyDeltaIntelligence.v1') return 'yggdrasil_topology_delta_intelligence schema is unsupported';
  const lockError = authorityError(raw.authority);
  if (lockError != null) return lockError;
  if (!isRecord(raw.generation) || raw.generation.generated_by !== 'YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_001' ||
      typeof raw.generation.generated_at !== 'string' || !HASH.test(String(raw.generation.delta_generation_id)) ||
      !HASH.test(String(raw.generation.prior_topology_generation_id)) || !HASH.test(String(raw.generation.current_topology_generation_id)) ||
      !HASH.test(String(raw.generation.prior_operator_platform_generation_id)) || !HASH.test(String(raw.generation.current_operator_platform_generation_id)) ||
      !isHashOrNull(raw.generation.prior_integrity_generation_id) || !isHashOrNull(raw.generation.current_integrity_generation_id) ||
      !isHashOrNull(raw.generation.temporal_diff_generation_id) || !HASH.test(String(raw.canonical_hash)) ||
      !STATUS.has(String(raw.status)) || !PROVENANCE.has(String(raw.provenance))) return 'yggdrasil_topology_delta_intelligence metadata is malformed';
  if (topology != null && raw.generation.current_topology_generation_id !== topology.generation.topology_generation_id) return 'yggdrasil_topology_delta_intelligence current generation is stale';
  if (!Array.isArray(raw.source_artifacts) || !isSortedUnique(raw.validation_findings)) return 'delta intelligence source metadata is malformed';
  const sourceIds: string[] = [];
  for (const [index, source] of raw.source_artifacts.entries()) {
    if (!isRecord(source) || source.id !== `source:${String(source.source_key)}` || !isRelativePath(source.path) ||
        !isHashOrNull(source.declared_canonical_hash) || !isHashOrNull(source.content_sha256) ||
        !['VERIFIED', 'NOT_COMPUTABLE'].includes(String(source.integrity_state))) return `delta intelligence source ${index} is malformed`;
    sourceIds.push(String(source.id));
  }
  if (!isSortedUnique(sourceIds) || !isRecord(raw.sections)) return 'delta intelligence sources or sections are not canonically ordered';
  const sourceDomain = new Set(sourceIds);
  const names = ['finding_correlation', 'structural_deltas', 'changed_paths', 'review_priorities'] as const;
  for (const name of names) {
    const error = validateSection(raw.sections[name], name);
    if (error != null) return error;
  }
  const correlations = (raw.sections.finding_correlation as JsonRecord).entries as unknown[] | null;
  const structural = (raw.sections.structural_deltas as JsonRecord).entries as unknown[] | null;
  const paths = (raw.sections.changed_paths as JsonRecord).entries as unknown[] | null;
  const priorities = (raw.sections.review_priorities as JsonRecord).entries as unknown[] | null;
  const recordIds = new Set<string>();
  for (const [index, entry] of (correlations ?? []).entries()) {
    const error = validateCorrelation(entry, index, sourceDomain); if (error != null) return error;
    recordIds.add(String((entry as JsonRecord).id));
  }
  for (const [index, entry] of (structural ?? []).entries()) {
    const error = validateStructural(entry, index, sourceDomain); if (error != null) return error;
    recordIds.add(String((entry as JsonRecord).id));
  }
  for (const [index, entry] of (paths ?? []).entries()) {
    const error = validatePath(entry, index, sourceDomain); if (error != null) return error;
    recordIds.add(String((entry as JsonRecord).id));
  }
  const priorityRecords: YggdrasilDeltaPriority[] = [];
  for (const [index, entry] of (priorities ?? []).entries()) {
    const error = validatePriority(entry, index, sourceDomain, recordIds); if (error != null) return error;
    priorityRecords.push(entry as YggdrasilDeltaPriority);
  }
  const ordered = [...priorityRecords].sort((left, right) => right.score - left.score || SEVERITY_ORDER[right.severity] - SEVERITY_ORDER[left.severity] || right.evidence_count - left.evidence_count || left.id.localeCompare(right.id));
  if (priorityRecords.some((entry, index) => entry !== ordered[index] || entry.rank !== index + 1)) return 'delta intelligence priorities are not canonically ordered';
  if (!isRecord(raw.summary)) return 'delta intelligence summary is malformed';
  const stateCounts: Record<string, number> = {};
  for (const entry of (correlations ?? []) as YggdrasilDeltaCorrelation[]) stateCounts[entry.state] = (stateCounts[entry.state] ?? 0) + 1;
  if (JSON.stringify(raw.summary.finding_state_counts) !== JSON.stringify(Object.fromEntries(Object.entries(stateCounts).sort())) ||
      raw.summary.changed_path_count !== (paths ?? []).length || raw.summary.active_priority_count !== priorityRecords.length ||
      raw.summary.highest_score !== (priorityRecords[0]?.score ?? null)) return 'delta intelligence summary is inconsistent';
  return null;
}
