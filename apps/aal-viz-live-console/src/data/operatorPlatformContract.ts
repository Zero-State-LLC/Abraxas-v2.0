import type { OperatorPlatformProjection } from '../types';

const SECTION_STATUSES = new Set(['AVAILABLE', 'PARTIAL', 'NOT_COMPUTABLE']);
const PROVENANCE = new Set(['OBSERVED', 'INFERRED']);
const ENTITY_TYPES = new Set(['SYSTEM', 'RUNE', 'CONTRACT', 'PACKET', 'RECEIPT', 'ROUTE']);
const TEMPORAL_OPERATIONS = new Set([
  'ADDED',
  'REMOVED',
  'CHANGED',
  'NOT_COMPUTABLE',
]);
const TEMPORAL_CATEGORIES = new Set([
  'TOPOLOGY_NODE',
  'TOPOLOGY_EDGE',
  'CONTRACT_FIELD',
  'OWNERSHIP',
  'VALIDATOR_STATE',
  'RECEIPT',
  'PACKET',
  'SOURCE_INTEGRITY',
  'SECTION_STATUS',
]);
const TEMPORAL_IMPACTS = new Set(['STRENGTHENED', 'WEAKENED', 'NEUTRAL', 'NOT_COMPUTABLE']);
const HASH_PATTERN = /^[0-9a-f]{64}$/;
const JSON_POINTER_PATTERN = /^(?:\/(?:[^~/]|~[01])*)*$/;

type JsonRecord = Record<string, unknown>;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string');
}

function isRelativePath(value: unknown): value is string {
  return (
    typeof value === 'string' &&
    value.length > 0 &&
    !value.startsWith('/') &&
    !/^[A-Za-z]:[\\/]/.test(value)
  );
}

function validateAuthority(value: unknown, path: string): string | null {
  if (!isRecord(value)) return `${path} must be an object`;
  if (value.projection_only !== true) return `${path}.projection_only must be true`;
  if (value.runtime_mutation_allowed !== false) return `${path}.runtime_mutation_allowed must be false`;
  if (value.promotion_allowed !== false) return `${path}.promotion_allowed must be false`;
  if (value.production_activation_allowed !== false) return `${path}.production_activation_allowed must be false`;
  return null;
}

function validateSources(value: unknown, path: string): string | null {
  if (!Array.isArray(value)) return `${path} must be an array`;
  for (const [index, source] of value.entries()) {
    if (!isRecord(source)) return `${path}[${index}] must be an object`;
    if (typeof source.source_key !== 'string' || source.source_key.length === 0) {
      return `${path}[${index}].source_key is required`;
    }
    if (!isRelativePath(source.path)) return `${path}[${index}].path must be repository-relative`;
    if (source.integrity_state !== 'VERIFIED' && source.integrity_state !== 'NOT_COMPUTABLE') {
      return `${path}[${index}].integrity_state is unsupported`;
    }
    if (source.content_sha256 !== null && !/^[0-9a-f]{64}$/.test(String(source.content_sha256))) {
      return `${path}[${index}].content_sha256 is malformed`;
    }
  }
  return null;
}

function validateSection(value: unknown, path: string): string | null {
  if (!isRecord(value)) return `${path} must be an object`;
  if (!SECTION_STATUSES.has(String(value.status))) return `${path}.status is unsupported`;
  if (!PROVENANCE.has(String(value.provenance))) return `${path}.provenance is unsupported`;
  const sourceError = validateSources(value.source_artifacts, `${path}.source_artifacts`);
  if (sourceError != null) return sourceError;
  if (!isStringArray(value.validation_findings)) return `${path}.validation_findings must be strings`;
  if (value.status === 'NOT_COMPUTABLE') {
    if (value.payload !== null) return `${path}.payload must be null when NOT_COMPUTABLE`;
    if (typeof value.not_computable_reason !== 'string' || value.not_computable_reason.length === 0) {
      return `${path}.not_computable_reason is required when NOT_COMPUTABLE`;
    }
  } else {
    if (!isRecord(value.payload)) return `${path}.payload must be an object when available`;
    if (value.not_computable_reason !== null) return `${path}.not_computable_reason must be null when available`;
  }
  return null;
}

function payloadOf(section: JsonRecord): JsonRecord | null {
  return isRecord(section.payload) ? section.payload : null;
}

function validateTopology(section: JsonRecord): string | null {
  const payload = payloadOf(section);
  if (payload == null) return null;
  if (!Array.isArray(payload.nodes) || !Array.isArray(payload.edges)) {
    return 'operator_platform.topology payload must contain node and edge arrays';
  }
  const nodeIds = new Set<string>();
  for (const [index, node] of payload.nodes.entries()) {
    if (!isRecord(node) || typeof node.id !== 'string' || node.id.length === 0) {
      return `operator_platform.topology.payload.nodes[${index}] has no stable id`;
    }
    if (nodeIds.has(node.id)) return `operator_platform topology duplicate node id: ${node.id}`;
    if (!ENTITY_TYPES.has(String(node.entity_type))) {
      return `operator_platform topology unsupported node kind: ${String(node.entity_type)}`;
    }
    nodeIds.add(node.id);
  }
  const edgeIds = new Set<string>();
  for (const [index, edge] of payload.edges.entries()) {
    if (!isRecord(edge) || typeof edge.id !== 'string' || edge.id.length === 0) {
      return `operator_platform.topology.payload.edges[${index}] has no stable id`;
    }
    if (edgeIds.has(edge.id)) return `operator_platform topology duplicate edge id: ${edge.id}`;
    if (!nodeIds.has(String(edge.source)) || !nodeIds.has(String(edge.target))) {
      return `operator_platform topology dangling edge: ${edge.id}`;
    }
    edgeIds.add(edge.id);
  }
  return null;
}

function validateTemporal(section: JsonRecord): string | null {
  const payload = payloadOf(section);
  if (payload == null) return null;
  if (!Array.isArray(payload.entries)) return 'operator_platform.temporal_diff.payload.entries must be an array';
  const isV1 = payload.comparison_scope !== undefined || payload.category_counts !== undefined;
  if (!isV1) {
    for (const [index, entry] of payload.entries.entries()) {
      if (!isRecord(entry)) return `operator_platform temporal entry ${index} must be an object`;
      if (!new Set([...TEMPORAL_OPERATIONS, 'UNCHANGED']).has(String(entry.operation))) {
        return `operator_platform temporal entry ${index} has an unsupported legacy operation`;
      }
      if (!PROVENANCE.has(String(entry.provenance))) return `operator_platform temporal entry ${index} has unsupported provenance`;
      if (entry.operation === 'REMOVED' && entry.prior_generation_id == null) return `operator_platform temporal removal ${index} lacks prior evidence`;
    }
    return null;
  }
  if (!isStringArray(payload.comparison_scope) || !isStringArray(payload.out_of_scope)) {
    return 'operator_platform temporal comparison scope is malformed';
  }
  if ([...payload.comparison_scope].sort().join('\0') !== payload.comparison_scope.join('\0')) {
    return 'operator_platform temporal comparison scope is not canonically ordered';
  }
  if (!isRecord(payload.category_counts)) return 'operator_platform temporal category counts are malformed';
  for (const category of TEMPORAL_CATEGORIES) {
    if (!Number.isInteger(payload.category_counts[category]) || Number(payload.category_counts[category]) < 0) {
      return `operator_platform temporal category count is malformed: ${category}`;
    }
  }
  for (const field of ['prior_generation_id', 'current_generation_id']) {
    const value = payload[field];
    if (value !== null && !HASH_PATTERN.test(String(value))) return `operator_platform temporal ${field} is malformed`;
  }
  const ids = new Set<string>();
  let priorOrderKey = '';
  for (const [index, entry] of payload.entries.entries()) {
    if (!isRecord(entry)) return `operator_platform temporal entry ${index} must be an object`;
    if (!HASH_PATTERN.test(String(entry.id))) return `operator_platform temporal entry ${index} has malformed id`;
    if (ids.has(String(entry.id))) return `operator_platform temporal duplicate entry id: ${String(entry.id)}`;
    ids.add(String(entry.id));
    if (!TEMPORAL_OPERATIONS.has(String(entry.operation))) {
      return `operator_platform temporal entry ${index} has an unsupported operation`;
    }
    if (!TEMPORAL_CATEGORIES.has(String(entry.category))) return `operator_platform temporal entry ${index} has an unsupported category`;
    if (!TEMPORAL_IMPACTS.has(String(entry.impact))) return `operator_platform temporal entry ${index} has an unsupported impact`;
    if (!PROVENANCE.has(String(entry.provenance))) {
      return `operator_platform temporal entry ${index} has unsupported provenance`;
    }
    if (typeof entry.entity_id !== 'string' || entry.entity_id.length === 0) return `operator_platform temporal entry ${index} lacks entity id`;
    if (typeof entry.field_path !== 'string' || !JSON_POINTER_PATTERN.test(entry.field_path)) return `operator_platform temporal entry ${index} has malformed JSON Pointer`;
    if (!SECTION_STATUSES.has(String(entry.prior_evidence_status)) || !SECTION_STATUSES.has(String(entry.current_evidence_status))) return `operator_platform temporal entry ${index} has unsupported evidence status`;
    if (!isStringArray(entry.source_keys) || [...entry.source_keys].sort().join('\0') !== entry.source_keys.join('\0')) return `operator_platform temporal entry ${index} source keys are not canonically ordered`;
    if (entry.prior_generation_id !== payload.prior_generation_id || entry.current_generation_id !== payload.current_generation_id) return `operator_platform temporal entry ${index} generation reference mismatch`;
    if (entry.operation === 'REMOVED') {
      if (entry.prior_evidence_status !== 'AVAILABLE' || entry.current_evidence_status !== 'AVAILABLE') return `operator_platform temporal removal ${index} lacks complete evidence`;
      if (entry.prior_value == null || entry.current_value !== null) return `operator_platform temporal removal ${index} has invalid value semantics`;
    }
    if (entry.operation === 'ADDED' && (entry.prior_value !== null || entry.current_value == null)) return `operator_platform temporal addition ${index} has invalid value semantics`;
    if (entry.operation === 'NOT_COMPUTABLE' && (entry.impact !== 'NOT_COMPUTABLE' || typeof entry.reason_code !== 'string')) return `operator_platform temporal non-computable entry ${index} lacks reason`;
    if (entry.operation !== 'NOT_COMPUTABLE' && entry.reason_code !== null) return `operator_platform temporal entry ${index} has an unexpected reason`;
    const orderKey = [entry.category, entry.surface, entry.entity_id, entry.field_path, entry.operation, entry.id].join('\0');
    if (orderKey < priorOrderKey) return `operator_platform temporal entries are not canonically ordered at ${index}`;
    priorOrderKey = orderKey;
    if (typeof entry.prior_generation_id === 'string' && !HASH_PATTERN.test(entry.prior_generation_id)) {
      return `operator_platform temporal entry ${index} has malformed prior generation id`;
    }
  }
  return null;
}

export function validateOperatorPlatformProjection(raw: unknown): string | null {
  if (!isRecord(raw)) return 'operator_platform must be an object';
  if (raw.schema_version !== 'AALViz.OperatorPlatformProjection.v0.2') {
    return 'operator_platform schema is missing or unsupported';
  }
  if (raw.projection_only !== true) return 'operator_platform.projection_only must be true';
  const authorityError = validateAuthority(raw.authority, 'operator_platform.authority');
  if (authorityError != null) return authorityError;
  if (!isRecord(raw.generation) || typeof raw.generation.generated_at !== 'string') {
    return 'operator_platform.generation is malformed';
  }
  const sourcesError = validateSources(raw.source_artifacts, 'operator_platform.source_artifacts');
  if (sourcesError != null) return sourcesError;

  const sectionNames = [
    'system_status',
    'topology',
    'production_slice',
    'contract_graph',
    'evidence_index',
    'temporal_diff',
  ] as const;
  for (const sectionName of sectionNames) {
    const error = validateSection(raw[sectionName], `operator_platform.${sectionName}`);
    if (error != null) return error;
  }

  const topologyError = validateTopology(raw.topology as JsonRecord);
  if (topologyError != null) return topologyError;
  const temporalError = validateTemporal(raw.temporal_diff as JsonRecord);
  if (temporalError != null) return temporalError;

  const evidence = payloadOf(raw.evidence_index as JsonRecord);
  if (evidence != null && !Array.isArray(evidence.records)) {
    return 'operator_platform.evidence_index.payload.records must be an array';
  }
  if (evidence != null) {
    for (const [index, record] of (evidence.records as unknown[]).entries()) {
      if (!isRecord(record)) return `operator_platform evidence record ${index} must be an object`;
      if (record.canonical_hash !== null && typeof record.canonical_hash !== 'string') {
        return `operator_platform evidence record ${index} has a non-scalar canonical hash`;
      }
    }
  }
  const contracts = payloadOf(raw.contract_graph as JsonRecord);
  if (contracts != null && !Array.isArray(contracts.contracts)) {
    return 'operator_platform.contract_graph.payload.contracts must be an array';
  }
  return null;
}

export function asOperatorPlatformProjection(raw: unknown): OperatorPlatformProjection {
  const error = validateOperatorPlatformProjection(raw);
  if (error != null) throw new Error(error);
  return raw as OperatorPlatformProjection;
}
