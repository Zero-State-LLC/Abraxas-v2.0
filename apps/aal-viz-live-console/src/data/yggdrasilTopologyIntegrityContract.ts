import type {
  YggdrasilIntegrityFindingType,
  YggdrasilIntegritySeverity,
  YggdrasilTopologyIntegrityProjection,
  YggdrasilTopologyProjection,
} from '../types';

type JsonRecord = Record<string, unknown>;

const HASH = /^[0-9a-f]{64}$/;
const FINDING_ID = /^finding:[0-9a-f]{64}$/;
const STATUS = new Set(['AVAILABLE', 'PARTIAL', 'NOT_COMPUTABLE']);
const PROVENANCE = new Set(['OBSERVED', 'INFERRED']);
const CONFIDENCE = new Set(['VERIFIED', 'SUPPORTED', 'INFERRED', 'NOT_COMPUTABLE']);
const ENTITY_CATEGORIES = new Set(['TOPOLOGY_NODE', 'TOPOLOGY_EDGE', 'SOURCE_ARTIFACT', 'SECTION']);
const SEVERITY_BY_TYPE: Record<YggdrasilIntegrityFindingType, YggdrasilIntegritySeverity> = {
  GENERATION_MISMATCH: 'HIGH',
  INFERRED_LINK: 'INFO',
  MISSING_EVIDENCE: 'LOW',
  SECTION_NOT_COMPUTABLE: 'NOT_COMPUTABLE',
  SOURCE_INTEGRITY_GAP: 'HIGH',
  STALE_ENTITY: 'MEDIUM',
  TEMPORAL_REMOVAL: 'MEDIUM',
  TEMPORAL_WEAKENING: 'MEDIUM',
  UNRESOLVED_ENTITY: 'MEDIUM',
};
const FINDING_TYPES = new Set(Object.keys(SEVERITY_BY_TYPE));

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

function validateAuthority(value: unknown): string | null {
  if (!isRecord(value)) return 'yggdrasil_topology_integrity.authority must be an object';
  const expected: Record<string, boolean> = {
    projection_only: true,
    runtime_mutation_allowed: false,
    canon_mutation_allowed: false,
    execution_authority: false,
    production_activation_allowed: false,
    graph_driven_execution_allowed: false,
    alert_delivery_allowed: false,
    acknowledgement_state_allowed: false,
    browser_persistence_allowed: false,
    route_receipt_triggering_allowed: false,
    scheduling_allowed: false,
  };
  for (const [key, expectedValue] of Object.entries(expected)) {
    if (value[key] !== expectedValue) return `yggdrasil_topology_integrity.authority.${key} violates projection locks`;
  }
  return null;
}

export function validateYggdrasilTopologyIntegrityProjection(
  raw: unknown,
  topology?: YggdrasilTopologyProjection,
): string | null {
  if (!isRecord(raw)) return 'yggdrasil_topology_integrity must be an object';
  if (raw.schema_version !== 'AALViz.YggdrasilTopologyIntegrity.v1') return 'yggdrasil_topology_integrity schema is unsupported';
  const authorityError = validateAuthority(raw.authority);
  if (authorityError != null) return authorityError;
  if (!isRecord(raw.generation) || raw.generation.generated_by !== 'YGGDRASIL_TOPOLOGY_INTEGRITY_FINDINGS_001' ||
      typeof raw.generation.generated_at !== 'string' || !HASH.test(String(raw.generation.integrity_generation_id)) ||
      !isHashOrNull(raw.generation.topology_generation_id) || !isHashOrNull(raw.generation.operator_platform_generation_id) ||
      !isHashOrNull(raw.generation.temporal_diff_generation_id)) return 'yggdrasil_topology_integrity generation is malformed';
  if (!STATUS.has(String(raw.status)) || !PROVENANCE.has(String(raw.provenance)) || !HASH.test(String(raw.canonical_hash))) {
    return 'yggdrasil_topology_integrity status, provenance, or canonical hash is malformed';
  }
  if (!Array.isArray(raw.source_artifacts)) return 'yggdrasil_topology_integrity source artifacts must be an array';
  const sourceIds: string[] = [];
  for (const [index, source] of raw.source_artifacts.entries()) {
    if (!isRecord(source) || source.id !== `source:${String(source.source_key)}` ||
        !['topology', 'temporal_diff'].includes(String(source.source_key)) || !isRelativePath(source.path) ||
        !isHashOrNull(source.declared_canonical_hash) || !isHashOrNull(source.content_sha256) ||
        !['VERIFIED', 'NOT_COMPUTABLE'].includes(String(source.integrity_state))) {
      return `yggdrasil_topology_integrity source artifact ${index} is malformed`;
    }
    sourceIds.push(String(source.id));
  }
  if (!isSortedUnique(sourceIds) || !isSortedUnique(raw.validation_findings)) return 'yggdrasil_topology_integrity metadata is not canonically ordered';
  if (topology != null && (raw.generation.topology_generation_id !== topology.generation.topology_generation_id ||
      raw.generation.operator_platform_generation_id !== topology.generation.operator_platform_generation_id)) {
    return 'yggdrasil_topology_integrity topology generation binding is stale';
  }
  if (raw.status === 'NOT_COMPUTABLE') {
    if (raw.payload !== null || typeof raw.not_computable_reason !== 'string' || raw.not_computable_reason.length === 0) return 'yggdrasil_topology_integrity NOT_COMPUTABLE payload is malformed';
    return null;
  }
  if (!isRecord(raw.payload) || !isRecord(raw.payload.summary) || !Array.isArray(raw.payload.findings) || raw.not_computable_reason !== null) {
    return 'yggdrasil_topology_integrity available payload is malformed';
  }
  const evidenceDomain = new Set(sourceIds);
  topology?.payload?.evidence.forEach((record) => evidenceDomain.add(record.id));
  const ids: string[] = [];
  const severityCounts: Record<string, number> = {};
  const typeCounts: Record<string, number> = {};
  const affected = new Set<string>();
  let nonComputable = 0;
  for (const [index, finding] of raw.payload.findings.entries()) {
    if (!isRecord(finding) || typeof finding.id !== 'string' || !FINDING_ID.test(finding.id) ||
        !FINDING_TYPES.has(String(finding.finding_type)) || finding.severity !== SEVERITY_BY_TYPE[finding.finding_type as YggdrasilIntegrityFindingType] ||
        typeof finding.subject_key !== 'string' || finding.subject_key.length === 0 || !isSortedUnique(finding.evidence_refs) ||
        !(finding.evidence_refs as string[]).every((reference) => evidenceDomain.has(reference)) ||
        !PROVENANCE.has(String(finding.provenance)) || !CONFIDENCE.has(String(finding.confidence)) ||
        typeof finding.reason !== 'string' || finding.reason.length === 0 || !['COMPUTABLE', 'NOT_COMPUTABLE'].includes(String(finding.computability)) ||
        !isRecord(finding.generation_binding)) return `yggdrasil_topology_integrity finding ${index} is malformed`;
    const binding = finding.generation_binding;
    if (binding.topology_generation_id !== raw.generation.topology_generation_id || binding.operator_platform_generation_id !== raw.generation.operator_platform_generation_id || binding.temporal_diff_generation_id !== raw.generation.temporal_diff_generation_id) return `yggdrasil_topology_integrity finding ${index} has stale generation binding`;
    if (['TEMPORAL_REMOVAL', 'TEMPORAL_WEAKENING'].includes(String(finding.finding_type)) &&
        (raw.generation.temporal_diff_generation_id === null || raw.generation.temporal_diff_generation_id !== raw.generation.operator_platform_generation_id)) return 'yggdrasil_topology_integrity contains a temporal conclusion without matching evidence';
    if (finding.entity_ref !== null) {
      if (!isRecord(finding.entity_ref) || !ENTITY_CATEGORIES.has(String(finding.entity_ref.category)) || typeof finding.entity_ref.entity_id !== 'string' || finding.entity_ref.entity_id.length === 0) return `yggdrasil_topology_integrity finding ${index} has malformed entity reference`;
      affected.add(`${String(finding.entity_ref.category)}:${finding.entity_ref.entity_id}`);
    }
    ids.push(finding.id);
    severityCounts[String(finding.severity)] = (severityCounts[String(finding.severity)] ?? 0) + 1;
    typeCounts[String(finding.finding_type)] = (typeCounts[String(finding.finding_type)] ?? 0) + 1;
    if (finding.computability === 'NOT_COMPUTABLE') nonComputable += 1;
  }
  if (!isSortedUnique(ids) || raw.payload.summary.finding_count !== ids.length ||
      raw.payload.summary.affected_entity_count !== affected.size || raw.payload.summary.non_computable_count !== nonComputable ||
      JSON.stringify(raw.payload.summary.severity_counts) !== JSON.stringify(Object.fromEntries(Object.entries(severityCounts).sort())) ||
      JSON.stringify(raw.payload.summary.type_counts) !== JSON.stringify(Object.fromEntries(Object.entries(typeCounts).sort()))) {
    return 'yggdrasil_topology_integrity summary or finding order is inconsistent';
  }
  return null;
}

export function asYggdrasilTopologyIntegrityProjection(raw: unknown): YggdrasilTopologyIntegrityProjection {
  const error = validateYggdrasilTopologyIntegrityProjection(raw);
  if (error != null) throw new Error(error);
  return raw as YggdrasilTopologyIntegrityProjection;
}
