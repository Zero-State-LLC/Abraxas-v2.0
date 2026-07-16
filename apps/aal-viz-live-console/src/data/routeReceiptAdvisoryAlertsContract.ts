import type {
  RouteReceiptAdvisoryAlert,
  RouteReceiptAdvisoryAlertsProjection,
  YggdrasilTopologyDeltaIntelligenceProjection,
  YggdrasilTopologyProjection,
} from '../types';

type JsonRecord = Record<string, unknown>;

const HASH = /^[0-9a-f]{64}$/;
const ALERT_ID = /^alert:[0-9a-f]{64}$/;
const RECEIPT_ID = /^receipt:[0-9a-f]{64}$/;
const PRIORITY_ID = /^priority:[0-9a-f]{64}$/;
const ACK_ID = /^ack:[0-9a-f]{64}$/;
const STATUS = new Set(['AVAILABLE', 'PARTIAL', 'NOT_COMPUTABLE']);
const PROVENANCE = new Set(['OBSERVED', 'INFERRED']);
const SEVERITY = new Set(['HIGH', 'MEDIUM', 'LOW', 'INFO', 'NOT_COMPUTABLE']);
const CONFIDENCE = new Set(['VERIFIED', 'SUPPORTED', 'INFERRED', 'NOT_COMPUTABLE']);
const EVENTS = new Set(['FIRST_OBSERVED', 'REFRESHED', 'UPDATED', 'RESOLVED', 'CARRIED_FORWARD']);
const DISPOSITIONS = new Set(['PUBLISH', 'SUPPRESS', 'NOT_COMPUTABLE']);
const TRIGGERS = new Set([
  'NEW_CRITICAL_STRUCTURAL_FINDING', 'SEVERITY_ESCALATION',
  'VALIDATOR_COVERAGE_LOSS', 'BROKEN_PRODUCER_CONSUMER_PATH',
  'OWNERSHIP_DRIFT', 'TOPOLOGY_FRAGMENTATION',
  'UNEXPECTED_CLUSTER_FUSION', 'PERSISTENT_UNRESOLVED_DAMAGE',
]);
const SUPPRESSIONS = new Set([
  'NO_ELIGIBLE_TRIGGER', 'BELOW_SCORE_THRESHOLD', 'BELOW_CONFIDENCE_THRESHOLD',
  'PERSISTENCE_THRESHOLD_NOT_MET', 'INCOMPLETE_EVIDENCE',
  'NO_AFFECTED_OPERATIONAL_SURFACE', 'DUPLICATE_CANDIDATE',
  'UNCHANGED_WITHIN_COOLDOWN',
]);

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isHashOrNull(value: unknown): boolean {
  return value === null || (typeof value === 'string' && HASH.test(value));
}

function isSortedUniqueStrings(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((entry) => typeof entry === 'string') &&
    value.join('\0') === [...value].sort().join('\0') && new Set(value).size === value.length;
}

function isSortedEnum(value: unknown, domain: Set<string>): value is string[] {
  return isSortedUniqueStrings(value) && value.every((entry) => domain.has(entry));
}

function isRelativePath(value: unknown): value is string {
  return typeof value === 'string' && value.length > 0 && !value.startsWith('/') &&
    !/^[A-Za-z]:[\\/]/.test(value) && !value.includes('\\') && !value.split('/').includes('..');
}

function scoreTier(score: number): string {
  if (score <= 49) return 'BASELINE';
  if (score <= 69) return 'ELEVATED';
  if (score <= 84) return 'HIGH';
  return 'CRITICAL';
}

function authorityError(value: unknown): string | null {
  if (!isRecord(value)) return 'route_receipt_advisory_alerts.authority is malformed';
  const expected: Record<string, boolean> = {
    projection_only: true, receipt_advisory_only: true, execution_authority: false,
    canon_mutation_allowed: false, runtime_mutation_allowed: false,
    topology_mutation_allowed: false, graph_driven_execution_allowed: false,
    production_activation_allowed: false, scheduling_allowed: false,
    notification_delivery_allowed: false, acknowledgement_writeback_allowed: false,
    browser_persistence_allowed: false, automatic_remediation_allowed: false,
    autonomous_escalation_allowed: false,
  };
  for (const [key, expectedValue] of Object.entries(expected)) {
    if (value[key] !== expectedValue) return `route_receipt_advisory_alerts.authority.${key} violates projection locks`;
  }
  return null;
}

function validateRecord(
  value: unknown,
  name: string,
  index: number,
  sourceIds: Set<string>,
): string | null {
  if (!isRecord(value) || !RECEIPT_ID.test(String(value.receipt_id)) ||
      value.receipt_kind !== 'ROUTE_RECEIPT_ADVISORY_ALERT' || !ALERT_ID.test(String(value.alert_id)) ||
      value.priority_id !== null && !PRIORITY_ID.test(String(value.priority_id)) ||
      !isRecord(value.source_ref) || !['INTEGRITY_FINDING', 'STRUCTURAL_DELTA'].includes(String(value.source_ref.category)) ||
      typeof value.source_ref.entity_id !== 'string' || !isSortedEnum(value.trigger_types, TRIGGERS) ||
      !EVENTS.has(String(value.event_type)) || !DISPOSITIONS.has(String(value.receipt_disposition)) ||
      !['ACTIVE', 'RESOLVED'].includes(String(value.lifecycle)) || !Number.isInteger(value.score) ||
      Number(value.score) < 0 || Number(value.score) > 100 || value.score_tier !== scoreTier(Number(value.score)) ||
      !SEVERITY.has(String(value.severity)) || !CONFIDENCE.has(String(value.confidence)) ||
      value.persistence_seconds_lower_bound !== null && (!Number.isInteger(value.persistence_seconds_lower_bound) || Number(value.persistence_seconds_lower_bound) < 0) ||
      !isSortedUniqueStrings(value.affected_surface_ids) || !isSortedUniqueStrings(value.evidence_refs) ||
      !(value.evidence_refs as string[]).every((entry) => sourceIds.has(entry)) ||
      !isSortedUniqueStrings(value.resolution_evidence_refs) ||
      !(value.resolution_evidence_refs as string[]).every((entry) => sourceIds.has(entry)) ||
      !isSortedEnum(value.suppression_reasons, SUPPRESSIONS) || typeof value.why_this_fired !== 'string' ||
      ![true, false, null].includes(value.acknowledged as boolean | null) ||
      value.acknowledgement_ref !== null && !ACK_ID.test(String(value.acknowledgement_ref)) ||
      value.delivery_state !== 'NOT_DELIVERED') return `advisory alert ${name} record ${index} is malformed`;
  if (name === 'resolved_alerts' && (value.lifecycle !== 'RESOLVED' || value.event_type !== 'RESOLVED' ||
      value.receipt_disposition !== 'PUBLISH' || !(value.resolution_evidence_refs as string[]).length)) return `advisory alert ${name} record ${index} has false resolution semantics`;
  if (name === 'suppressed_candidates' && (value.lifecycle !== 'ACTIVE' || value.receipt_disposition !== 'SUPPRESS' ||
      !(value.suppression_reasons as string[]).length)) return `advisory alert ${name} record ${index} has invalid suppression semantics`;
  if ((value.suppression_reasons as string[]).includes('UNCHANGED_WITHIN_COOLDOWN') && value.event_type !== 'CARRIED_FORWARD') return `advisory alert ${name} record ${index} has invalid cooldown semantics`;
  return null;
}

export function validateRouteReceiptAdvisoryAlertsProjection(
  raw: unknown,
  delta?: YggdrasilTopologyDeltaIntelligenceProjection,
  topology?: YggdrasilTopologyProjection,
): string | null {
  if (!isRecord(raw) || raw.schema_version !== 'AALViz.RouteReceiptAdvisoryAlerts.v1') return 'route_receipt_advisory_alerts schema is unsupported';
  const lockError = authorityError(raw.authority); if (lockError != null) return lockError;
  if (!isRecord(raw.generation) || raw.generation.generated_by !== 'ROUTE_RECEIPT_ADVISORY_ALERTS_001' ||
      typeof raw.generation.generated_at !== 'string' || !HASH.test(String(raw.generation.alert_generation_id)) ||
      !HASH.test(String(raw.generation.delta_generation_id)) || !HASH.test(String(raw.generation.prior_topology_generation_id)) ||
      !HASH.test(String(raw.generation.current_topology_generation_id)) || !HASH.test(String(raw.generation.prior_operator_platform_generation_id)) ||
      !HASH.test(String(raw.generation.current_operator_platform_generation_id)) || !isHashOrNull(raw.generation.prior_alert_generation_id) ||
      !isHashOrNull(raw.generation.acknowledgement_generation_id) || !HASH.test(String(raw.canonical_hash)) ||
      !STATUS.has(String(raw.status)) || !PROVENANCE.has(String(raw.provenance))) return 'route_receipt_advisory_alerts metadata is malformed';
  if (delta != null && raw.generation.delta_generation_id !== delta.generation.delta_generation_id) return 'route_receipt_advisory_alerts delta generation is stale';
  if (topology != null && raw.generation.current_topology_generation_id !== topology.generation.topology_generation_id) return 'route_receipt_advisory_alerts topology generation is stale';
  if (topology != null && raw.generation.current_operator_platform_generation_id !== topology.generation.operator_platform_generation_id) return 'route_receipt_advisory_alerts operator generation is stale';
  if (!isRecord(raw.policy) || raw.policy.policy_version !== 'ROUTE_RECEIPT_ADVISORY_ALERTS_POLICY.v1' ||
      raw.policy.cooldown_seconds !== 86400 || raw.policy.persistence_seconds !== 86400 ||
      JSON.stringify(raw.policy.score_tiers) !== '[49,69,84,100]') return 'route_receipt_advisory_alerts policy is malformed';
  if (!Array.isArray(raw.source_artifacts) || !isSortedUniqueStrings(raw.validation_findings)) return 'route_receipt_advisory_alerts sources are malformed';
  const sourceIds: string[] = [];
  for (const [index, source] of raw.source_artifacts.entries()) {
    if (!isRecord(source) || source.id !== `source:${String(source.source_key)}` ||
        !['delta_intelligence', 'prior_alerts', 'acknowledgements'].includes(String(source.source_key)) ||
        !isRelativePath(source.path) || !isHashOrNull(source.declared_canonical_hash) ||
        !isHashOrNull(source.content_sha256) || !['VERIFIED', 'NOT_COMPUTABLE'].includes(String(source.integrity_state))) return `advisory alert source ${index} is malformed`;
    sourceIds.push(String(source.id));
  }
  if (!isSortedUniqueStrings(sourceIds) || !isRecord(raw.sections)) return 'route_receipt_advisory_alerts sources or sections are not canonical';
  const sourceDomain = new Set(sourceIds);
  const names = ['eligibility_decisions', 'active_alerts', 'resolved_alerts', 'suppressed_candidates', 'not_computable'] as const;
  const records: RouteReceiptAdvisoryAlert[] = [];
  for (const name of names) {
    const section = raw.sections[name];
    if (!isRecord(section) || !STATUS.has(String(section.status)) || !PROVENANCE.has(String(section.provenance)) ||
        !isSortedUniqueStrings(section.validation_findings)) return `advisory alert ${name} envelope is malformed`;
    if (section.status === 'NOT_COMPUTABLE') {
      if (section.entries !== null || typeof section.not_computable_reason !== 'string' || section.not_computable_reason.length === 0) return `advisory alert ${name} NOT_COMPUTABLE envelope is malformed`;
      continue;
    }
    if (!Array.isArray(section.entries) || section.not_computable_reason !== null) return `advisory alert ${name} available envelope is malformed`;
    const ids = section.entries.map((entry) => isRecord(entry) ? String(entry.receipt_id) : '');
    if (!isSortedUniqueStrings(ids)) return `advisory alert ${name} records are not canonical`;
    for (const [index, entry] of section.entries.entries()) {
      const error = validateRecord(entry, name, index, sourceDomain); if (error != null) return error;
      records.push(entry as RouteReceiptAdvisoryAlert);
    }
  }
  if (new Set(records.map((entry) => entry.receipt_id)).size !== records.length) return 'route_receipt_advisory_alerts contains duplicate receipt ids';
  if (records.some((entry) => entry.acknowledgement_ref != null) && raw.generation.acknowledgement_generation_id === null) return 'route_receipt_advisory_alerts has a dangling acknowledgement reference';
  if (records.some((entry) => entry.acknowledged === true && entry.acknowledgement_ref == null)) return 'route_receipt_advisory_alerts acknowledgement metadata is inconsistent';
  if (!isRecord(raw.summary)) return 'route_receipt_advisory_alerts summary is malformed';
  const sections = raw.sections as RouteReceiptAdvisoryAlertsProjection['sections'];
  const active = sections.active_alerts.entries ?? [];
  const resolved = sections.resolved_alerts.entries ?? [];
  const suppressed = sections.suppressed_candidates.entries ?? [];
  const notComputableCount = names.filter((name) => sections[name].status === 'NOT_COMPUTABLE').length;
  const publishedCount = records.filter((entry) => entry.receipt_disposition === 'PUBLISH').length;
  const highestActiveScore = active.length === 0 ? null : Math.max(...active.map((entry) => entry.score));
  if (raw.summary.candidate_count !== active.length + suppressed.length ||
      raw.summary.active_count !== active.length || raw.summary.resolved_count !== resolved.length ||
      raw.summary.suppressed_count !== suppressed.length || raw.summary.not_computable_count !== notComputableCount ||
      raw.summary.published_receipt_count !== publishedCount || raw.summary.highest_active_score !== highestActiveScore) return 'route_receipt_advisory_alerts summary is inconsistent';
  return null;
}
