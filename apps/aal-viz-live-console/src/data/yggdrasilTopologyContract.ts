import type {
  YggdrasilEdgeClass,
  YggdrasilNodeClass,
  YggdrasilTopologyProjection,
} from '../types';

type JsonRecord = Record<string, unknown>;

const HASH = /^[0-9a-f]{64}$/;
const NODE_CLASSES = new Set<YggdrasilNodeClass>([
  'SYSTEM', 'RUNE', 'CONTRACT', 'PACKET', 'RECEIPT', 'ROUTE', 'INTERFACE',
]);
const EDGE_CLASSES = new Set<YggdrasilEdgeClass>([
  'PRODUCES', 'VALIDATES', 'CONSUMES', 'BINDS', 'ROUTES_TO', 'EVIDENCES',
  'EXPOSES', 'REFERENCES', 'RENDER_RELATION',
]);
const ROLES = new Set(['PRODUCER', 'VALIDATOR', 'CONSUMER', 'OPERATOR']);
const PROVENANCE = new Set(['OBSERVED', 'INFERRED']);
const CONFIDENCE = new Set(['VERIFIED', 'SUPPORTED', 'INFERRED', 'NOT_COMPUTABLE']);
const RESOLUTION = new Set(['RESOLVED', 'UNRESOLVED', 'NOT_COMPUTABLE']);
const FRESHNESS = new Set(['CURRENT', 'STALE', 'NOT_COMPUTABLE']);
const SECTION_STATUS = new Set(['AVAILABLE', 'PARTIAL', 'NOT_COMPUTABLE']);

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isRelativePath(value: unknown): value is string {
  return typeof value === 'string' && value.length > 0 && !value.startsWith('/') &&
    !/^[A-Za-z]:[\\/]/.test(value) && !value.includes('\\') &&
    !value.split('/').includes('..');
}

function isSortedUnique(values: unknown, allowed?: Set<string>): values is string[] {
  if (!Array.isArray(values) || !values.every((value) => typeof value === 'string')) return false;
  if (new Set(values).size !== values.length || [...values].sort().join('\0') !== values.join('\0')) return false;
  return allowed == null || values.every((value) => allowed.has(value));
}

function validateEvidence(value: unknown, path: string): string | null {
  if (!isRecord(value)) return `${path} must be an object`;
  if (value.id !== `source:${String(value.source_key)}`) return `${path} has mismatched source identity`;
  if (!isRelativePath(value.path)) return `${path}.path must be repository-relative POSIX`;
  for (const key of ['declared_canonical_hash', 'content_sha256'] as const) {
    if (value[key] !== null && (typeof value[key] !== 'string' || !HASH.test(value[key]))) {
      return `${path}.${key} must be a lowercase SHA-256 hash or null`;
    }
  }
  if (!['VERIFIED', 'NOT_COMPUTABLE'].includes(String(value.integrity_state))) {
    return `${path}.integrity_state is unsupported`;
  }
  return null;
}

function validateAuthority(value: unknown): string | null {
  if (!isRecord(value)) return 'yggdrasil_topology.authority must be an object';
  const expected: Record<string, boolean> = {
    projection_only: true,
    runtime_mutation_allowed: false,
    canon_mutation_allowed: false,
    execution_authority: false,
    promotion_allowed: false,
    production_activation_allowed: false,
    graph_driven_execution_allowed: false,
    autonomous_link_creation_allowed: false,
    alerting_allowed: false,
    scheduling_allowed: false,
  };
  for (const [key, expectedValue] of Object.entries(expected)) {
    if (value[key] !== expectedValue) return `yggdrasil_topology.authority.${key} violates projection locks`;
  }
  return null;
}

export function validateYggdrasilTopologyProjection(raw: unknown): string | null {
  if (!isRecord(raw)) return 'yggdrasil_topology must be an object';
  if (raw.schema_version !== 'AALViz.YggdrasilTopology.v1') return 'yggdrasil_topology schema is unsupported';
  const authorityError = validateAuthority(raw.authority);
  if (authorityError != null) return authorityError;
  if (!isRecord(raw.generation) || raw.generation.generated_by !== 'LIVE_YGGDRASIL_TOPOLOGY_ENRICHMENT_001' ||
      typeof raw.generation.generated_at !== 'string' || !HASH.test(String(raw.generation.topology_generation_id)) ||
      (raw.generation.operator_platform_generation_id !== null && !HASH.test(String(raw.generation.operator_platform_generation_id)))) {
    return 'yggdrasil_topology generation is malformed';
  }
  if (!SECTION_STATUS.has(String(raw.status)) || !PROVENANCE.has(String(raw.provenance))) {
    return 'yggdrasil_topology status or provenance is unsupported';
  }
  if (!HASH.test(String(raw.canonical_hash))) return 'yggdrasil_topology canonical hash is malformed';
  if (!Array.isArray(raw.source_artifacts)) return 'yggdrasil_topology source artifacts must be an array';
  const sourceIds: string[] = [];
  for (const [index, source] of raw.source_artifacts.entries()) {
    const error = validateEvidence(source, `yggdrasil_topology.source_artifacts[${index}]`);
    if (error != null) return error;
    sourceIds.push(String((source as JsonRecord).id));
  }
  if (sourceIds.join('\0') !== [...sourceIds].sort().join('\0') || new Set(sourceIds).size !== sourceIds.length) {
    return 'yggdrasil_topology source artifacts are not canonically ordered';
  }
  if (!isSortedUnique(raw.validation_findings)) return 'yggdrasil_topology findings are not canonically ordered';
  if (!isRecord(raw.temporal_linkage)) return 'yggdrasil_topology temporal linkage is malformed';
  const linkage = raw.temporal_linkage;
  if (!['MATCHED', 'STALE', 'NOT_COMPUTABLE'].includes(String(linkage.status))) return 'yggdrasil_topology temporal linkage status is unsupported';
  for (const key of ['content_sha256', 'prior_generation_id', 'current_generation_id'] as const) {
    if (linkage[key] !== null && !HASH.test(String(linkage[key]))) return `yggdrasil_topology temporal ${key} is malformed`;
  }
  if (linkage.source_path !== null && !isRelativePath(linkage.source_path)) return 'yggdrasil_topology temporal source path is invalid';
  const operatorId = raw.generation.operator_platform_generation_id;
  if (linkage.status === 'MATCHED' && linkage.current_generation_id !== operatorId) return 'yggdrasil_topology matched temporal generation is inconsistent';
  if (linkage.status === 'STALE' && (linkage.current_generation_id === null || linkage.current_generation_id === operatorId)) return 'yggdrasil_topology stale temporal generation is inconsistent';
  if (linkage.status === 'NOT_COMPUTABLE' && [linkage.source_path, linkage.content_sha256, linkage.prior_generation_id, linkage.current_generation_id].some((value) => value !== null)) {
    return 'yggdrasil_topology non-computable temporal linkage must be empty';
  }
  if (raw.status === 'NOT_COMPUTABLE') {
    if (raw.payload !== null || typeof raw.not_computable_reason !== 'string' || raw.not_computable_reason.length === 0) {
      return 'yggdrasil_topology NOT_COMPUTABLE payload is malformed';
    }
    return null;
  }
  if (!isRecord(raw.payload) || raw.not_computable_reason !== null) return 'yggdrasil_topology available payload is malformed';
  const payload = raw.payload;
  if (!Array.isArray(payload.nodes) || !Array.isArray(payload.edges) || !Array.isArray(payload.evidence) || !isRecord(payload.summary)) {
    return 'yggdrasil_topology payload collections are malformed';
  }
  const evidenceIds: string[] = [];
  for (const [index, evidence] of payload.evidence.entries()) {
    const error = validateEvidence(evidence, `yggdrasil_topology.payload.evidence[${index}]`);
    if (error != null) return error;
    evidenceIds.push(String((evidence as JsonRecord).id));
  }
  if (evidenceIds.join('\0') !== [...evidenceIds].sort().join('\0') || new Set(evidenceIds).size !== evidenceIds.length) return 'yggdrasil_topology evidence is not canonically ordered';
  const evidenceSet = new Set(evidenceIds);
  const nodeIds: string[] = [];
  for (const [index, node] of payload.nodes.entries()) {
    if (!isRecord(node) || typeof node.id !== 'string' || !NODE_CLASSES.has(node.node_class as YggdrasilNodeClass)) return `yggdrasil_topology node ${index} is malformed`;
    if (!isSortedUnique(node.roles, ROLES) || !isSortedUnique(node.evidence_refs) || !(node.evidence_refs as string[]).every((id) => evidenceSet.has(id))) return `yggdrasil_topology node ${index} has invalid roles or evidence`;
    if (!PROVENANCE.has(String(node.provenance)) || !CONFIDENCE.has(String(node.confidence)) || !RESOLUTION.has(String(node.resolution_state)) || !FRESHNESS.has(String(node.freshness))) return `yggdrasil_topology node ${index} has unsupported evidence state`;
    if (!isRecord(node.temporal_ref) || node.temporal_ref.category !== 'TOPOLOGY_NODE' || node.temporal_ref.entity_id !== node.id) return `yggdrasil_topology node ${index} has invalid temporal reference`;
    nodeIds.push(node.id);
  }
  if (nodeIds.join('\0') !== [...nodeIds].sort().join('\0') || new Set(nodeIds).size !== nodeIds.length) return 'yggdrasil_topology nodes are not canonically ordered';
  const nodeSet = new Set(nodeIds);
  const edgeIds: string[] = [];
  for (const [index, edge] of payload.edges.entries()) {
    if (!isRecord(edge) || typeof edge.id !== 'string' || !EDGE_CLASSES.has(edge.edge_class as YggdrasilEdgeClass) || !nodeSet.has(String(edge.source)) || !nodeSet.has(String(edge.target))) return `yggdrasil_topology edge ${index} is malformed or dangling`;
    if (!isSortedUnique(edge.evidence_refs) || !(edge.evidence_refs as string[]).every((id) => evidenceSet.has(id))) return `yggdrasil_topology edge ${index} has invalid evidence`;
    if (!PROVENANCE.has(String(edge.provenance)) || !CONFIDENCE.has(String(edge.confidence)) || !RESOLUTION.has(String(edge.resolution_state)) || !FRESHNESS.has(String(edge.freshness))) return `yggdrasil_topology edge ${index} has unsupported evidence state`;
    if (!isRecord(edge.temporal_ref) || edge.temporal_ref.category !== 'TOPOLOGY_EDGE' || edge.temporal_ref.entity_id !== edge.id) return `yggdrasil_topology edge ${index} has invalid temporal reference`;
    edgeIds.push(edge.id);
  }
  if (edgeIds.join('\0') !== [...edgeIds].sort().join('\0') || new Set(edgeIds).size !== edgeIds.length) return 'yggdrasil_topology edges are not canonically ordered';
  if (payload.summary.node_count !== nodeIds.length || payload.summary.edge_count !== edgeIds.length || payload.summary.evidence_count !== evidenceIds.length) return 'yggdrasil_topology summary counts are inconsistent';
  return null;
}

export function asYggdrasilTopologyProjection(raw: unknown): YggdrasilTopologyProjection {
  const error = validateYggdrasilTopologyProjection(raw);
  if (error != null) throw new Error(error);
  return raw as YggdrasilTopologyProjection;
}
