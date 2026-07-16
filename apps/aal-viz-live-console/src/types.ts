export type SystemStatus = 'READY' | 'PARTIAL' | 'FAIL_CLOSED' | 'NOT_COMPUTABLE';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type QueueItemStatus = 'PENDING' | 'REVIEWED' | 'DEFERRED';
export type SourceMode = 'LIVE_ARTIFACT_BUNDLE' | 'SAMPLE_FALLBACK' | 'FAIL_CLOSED';
export type ConnectionStatus =
  | 'CONNECTING'
  | 'LIVE_STREAM'
  | 'POLLING_FALLBACK'
  | 'SAMPLE_FALLBACK'
  | 'FAIL_CLOSED';

export type TransportMode = 'WEBSOCKET' | 'POLLING' | 'SAMPLE';

export type FallbackReason =
  | 'WS_URL_UNSET'
  | 'WEBSOCKET_UNAVAILABLE'
  | 'SOCKET_ERROR'
  | 'SOCKET_CLOSED'
  | 'STREAM_MESSAGE_INVALID'
  | 'STREAM_MESSAGE_STALE'
  | 'POLLING_BUNDLE_FAIL_CLOSED'
  | 'POLLING_FETCH_FALLBACK'
  | null;
export type ActionType = 'COPY_PROMPT' | 'COPY_CHECKLIST' | 'REVIEW_REQUIRED';
export type WorkflowItemStatus =
  | 'AVAILABLE'
  | 'COPIED'
  | 'REVIEW_REQUIRED'
  | 'BLOCKED'
  | 'COMPLETED_MANUALLY';

export interface WorkflowItem {
  packet_id: string;
  action_title: string;
  action_type: ActionType;
  status: WorkflowItemStatus;
  prompt_body: string;
  validation_checklist: string[];
  blocked_scopes: string[];
}

export type DecisionOutcomeStatus =
  | 'UNKNOWN'
  | 'MERGED'
  | 'FAILED'
  | 'HELD'
  | 'SUPERSEDED';

export interface DecisionOutcomeAttribution {
  packet_id: string;
  outcome_status: DecisionOutcomeStatus;
  copied_at: string | null;
  manual_result: string;
  linked_pr: string;
  _ui_only: true;
  _non_authoritative: true;
}

export type SuggestionCardType =
  | 'NEXT_SAFE_STEP'
  | 'VALIDATION_REMINDER'
  | 'AUTHORITY_BOUNDARY'
  | 'FRONTIER_PAUSE';

export interface SuggestionCard {
  suggestion_id: string;
  title: string;
  type: SuggestionCardType;
  source_packet_id: string | null;
  rationale: string;
  suggested_manual_action: string;
  authority: 'DISPLAY_ONLY';
  execution_allowed: false;
  runtime_mutation_allowed: false;
  promotion_allowed: false;
}

export interface ProjectionPacket {
  packet_id: string;
  packet_type: string;
  status: string;
  display_value: string | null;
  authority_source: string;
  projection_only: true;
}

export interface LedgerReceipt {
  receipt_id: string;
  event: string;
  timestamp: string;
  canonical_hash: string;
}

export interface OperatorQueueItem {
  action_id: string;
  action_type: string;
  label: string;
  target_system: string;
  status: QueueItemStatus;
  auto_apply_blocked: true;
  requires_operator_review: true;
}

export interface SystemProjection {
  system_id: string;
  display_name: string;
  status: SystemStatus;
  completion_pct: number;
  risk_level: RiskLevel;
  last_updated: string;
  shadow_only: true;
  projection_packets: ProjectionPacket[];
  ledger_receipts: LedgerReceipt[];
}

export interface Authority {
  projection_only: true;
  runtime_mutation_allowed: false;
  promotion_allowed: false;
  production_activation_allowed: false;
}

export interface FusionOverlayNode {
  node_id: string;
  label?: string;
  posture?: string;
  layer_id?: string;
}

export interface FusionOverlayEdge {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  relation?: string;
}

export interface FusionOverlayPacket {
  packet_type: 'AALVizClimateMotifFusionOverlay.v1';
  final_status: string;
  fusion_posture: string;
  overlay_nodes: FusionOverlayNode[];
  overlay_edges: FusionOverlayEdge[];
  governance_flags: {
    advisory_only: true;
    projection_only: true;
  };
}

export interface OperatorNarrativeSectionNav {
  section_id: string;
  title: string;
  status: string;
  index: number;
}

export interface OperatorNarrativeOverlayCard {
  card_id: string;
  title: string;
  status?: string;
  blocker_count?: number;
  blocker_summary?: string[];
  observed_fields?: Record<string, unknown>;
}

export interface OperatorNarrativeReportOverlaySummary {
  report_final_status?: string;
  report_posture?: string;
  audit_final_status?: string;
  audit_posture?: string;
  blocker_count?: number;
  section_count?: number;
}

export interface OperatorNarrativeReportPacket {
  packet_type: 'OperatorNarrativeReportUIOverlay.v1';
  final_status: string;
  overlay_posture: string;
  report_overlay_summary: OperatorNarrativeReportOverlaySummary;
  section_navigation: OperatorNarrativeSectionNav[];
  overlay_cards: OperatorNarrativeOverlayCard[];
  governance_flags: {
    advisory_only: true;
    projection_only: true;
  };
}

export interface MigrationRunnerPosture {
  source_status: 'OBSERVED' | 'MISSING' | 'NOT_COMPUTABLE';
  status: string;
  migration_run_id: string;
  requested_execution_result: 'READY' | 'HELD' | 'NOT_COMPUTABLE';
  requested_execution_reason: string;
  safe_next_surface: string;
  recommended_next_engineering_move: string;
  blocked_action_count: number;
  blocked_action_sample: string[];
  stage_count: number;
  stage_posture_summary: Record<string, number>;
  authority_granted: false;
}

export interface MigrationPreflightPosture {
  source_status: 'READY' | 'READY_WITH_FINDINGS' | 'MISSING' | 'NOT_COMPUTABLE';
  status: string;
  check_count: number;
  pass_count: number;
  held_count: number;
  migration_runner_status: string;
  alias_design_state: string;
  valid_for_implementation: false;
  blocked_action_count: number;
  blocked_action_sample: string[];
  recommended_next_engineering_move: string;
  authority_granted: false;
}

export interface CombinedHealthMigrationArtifactFinding {
  source: 'HEALTH' | 'MIGRATION' | 'ARTIFACT';
  code: string;
  severity: string;
  detail: string;
}

export interface CombinedHealthMigrationArtifactPosture {
  source_status: 'OBSERVED' | 'MISSING' | 'NOT_COMPUTABLE';
  status: string;
  health_status: string;
  migration_runner_status: string;
  artifact_lifecycle_status: string;
  requested_execution_result: 'READY' | 'HELD' | 'NOT_COMPUTABLE';
  requested_execution_reason: string;
  safe_next_surface: string;
  recommended_next_engineering_move: string;
  blocked_action_count: number;
  blocked_action_sample: string[];
  stage_count: number;
  stage_posture_summary: Record<string, number>;
  subsystem_count: number;
  missing_contract_count: number;
  managed_artifact_count: number;
  orphaned_artifact_count: number;
  ambiguous_artifact_count: number;
  blocked_continuity_edge_count: number;
  findings_by_source: {
    health: CombinedHealthMigrationArtifactFinding[];
    migration: CombinedHealthMigrationArtifactFinding[];
    artifact: CombinedHealthMigrationArtifactFinding[];
  };
  authority_granted: false;
}

export type OperatorPlatformSourceStatus = 'OBSERVED' | 'NOT_COMPUTABLE';
export type OperatorPlatformSectionStatus = 'AVAILABLE' | 'PARTIAL' | 'NOT_COMPUTABLE';
export type OperatorPlatformProvenance = 'OBSERVED' | 'INFERRED';
export type OperatorPlatformEntityType =
  | 'SYSTEM'
  | 'RUNE'
  | 'CONTRACT'
  | 'PACKET'
  | 'RECEIPT'
  | 'ROUTE';

export interface OperatorPlatformSourceArtifact {
  source_key: string;
  path: string;
  declared_canonical_hash: string | null;
  content_sha256: string | null;
  integrity_state: 'VERIFIED' | 'NOT_COMPUTABLE';
}

export interface OperatorPlatformSection<T> {
  status: OperatorPlatformSectionStatus;
  provenance: OperatorPlatformProvenance;
  source_artifacts: OperatorPlatformSourceArtifact[];
  payload: T | null;
  not_computable_reason: string | null;
  validation_findings: string[];
}

export interface OperatorPlatformNode {
  id: string;
  label: string;
  entity_type: OperatorPlatformEntityType;
  status: string;
  source_ref: string;
  provenance: string;
}

export interface OperatorPlatformEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
  status: string;
  provenance: string;
}

export interface OperatorPlatformContract {
  id: string;
  language: string;
  version: string;
  owner: string;
  owner_resolved: boolean;
  validation_mode: string;
  production_reachability: string;
  producers: string[];
  validators: string[];
  consumers: string[];
}

export interface OperatorPlatformEvidenceRecord {
  id: string;
  source_status: OperatorPlatformSourceStatus;
  source_path: string;
  canonical_hash: string | null;
  status: string;
  inputs: string[];
  outputs: string[];
  schemas: string[];
  links: string[];
  fail_closed_reason: string | null;
}

export interface OperatorPlatformTemporalChange {
  id: string;
  operation: 'ADDED' | 'REMOVED' | 'CHANGED' | 'NOT_COMPUTABLE';
  category: OperatorPlatformTemporalCategory;
  impact: 'STRENGTHENED' | 'WEAKENED' | 'NEUTRAL' | 'NOT_COMPUTABLE';
  surface: string;
  entity_id: string;
  summary: string;
  severity: string;
  field_path: string;
  prior_value: unknown;
  current_value: unknown;
  provenance: OperatorPlatformProvenance;
  prior_generation_id: string | null;
  current_generation_id: string | null;
  prior_evidence_status: OperatorPlatformSectionStatus;
  current_evidence_status: OperatorPlatformSectionStatus;
  reason_code: string | null;
  source_keys: string[];
}

export type OperatorPlatformTemporalCategory =
  | 'TOPOLOGY_NODE'
  | 'TOPOLOGY_EDGE'
  | 'CONTRACT_FIELD'
  | 'OWNERSHIP'
  | 'VALIDATOR_STATE'
  | 'RECEIPT'
  | 'PACKET'
  | 'SOURCE_INTEGRITY'
  | 'SECTION_STATUS';

export interface OperatorPlatformSystemStatusPayload {
    source_status: OperatorPlatformSourceStatus;
    stabilization_status: string;
    production_slice_status: string;
    system_count: number;
    ready_system_count: number;
    work_items: Array<{ id: string; label: string; status: string; target: string }>;
    failures: string[];
    inherited_debt: string[];
    receipt_count: number;
    operator_summary: string[];
}

export interface OperatorPlatformTopologyPayload {
    source_status: OperatorPlatformSourceStatus;
    nodes: OperatorPlatformNode[];
    edges: OperatorPlatformEdge[];
}

export interface OperatorPlatformProductionPayload {
    source_status: OperatorPlatformSourceStatus;
    classification: string;
    entrypoint: string;
    invocation: string;
    orchestration: string[];
    validators: string[];
    execution_flow: string[];
    artifacts: string[];
    receipts: string[];
    excluded_surfaces: string[];
    unresolved_links: string[];
    external_calls: boolean;
    persistence_behavior: string;
}

export interface OperatorPlatformContractPayload {
    source_status: OperatorPlatformSourceStatus;
    contract_count: number;
    unowned_count: number;
    unvalidated_count: number;
    contracts: OperatorPlatformContract[];
}

export interface OperatorPlatformEvidencePayload {
  records: OperatorPlatformEvidenceRecord[];
}

export interface OperatorPlatformTemporalPayload {
    source_status: OperatorPlatformSourceStatus;
    status: string;
    prior_generation_id: string | null;
    current_generation_id: string | null;
    comparison_scope: string[];
    out_of_scope: string[];
    category_counts: Record<OperatorPlatformTemporalCategory, number>;
    total_change_count: number;
    not_computable_count: number;
    topology_change_count: number;
    lineage_shift_count: number;
    queue_delta_count: number;
    transport_delta_count: number;
    operator_summary: string;
    entries: OperatorPlatformTemporalChange[];
    remaining_blockers: string[];
}

export interface OperatorPlatformProjection {
  schema_version: 'AALViz.OperatorPlatformProjection.v0.2';
  generation: {
    generated_at: string;
    generated_by: string;
    source_bundle_schema_version: 'AALViz.LiveConsoleProjectionBundle.v0.2';
  };
  authority: Authority;
  projection_only: true;
  source_artifacts: OperatorPlatformSourceArtifact[];
  system_status: OperatorPlatformSection<OperatorPlatformSystemStatusPayload>;
  topology: OperatorPlatformSection<OperatorPlatformTopologyPayload>;
  production_slice: OperatorPlatformSection<OperatorPlatformProductionPayload>;
  contract_graph: OperatorPlatformSection<OperatorPlatformContractPayload>;
  evidence_index: OperatorPlatformSection<OperatorPlatformEvidencePayload>;
  temporal_diff: OperatorPlatformSection<OperatorPlatformTemporalPayload>;
}

export type YggdrasilNodeClass =
  | 'SYSTEM'
  | 'RUNE'
  | 'CONTRACT'
  | 'PACKET'
  | 'RECEIPT'
  | 'ROUTE'
  | 'INTERFACE';
export type YggdrasilInterfaceRole = 'PRODUCER' | 'VALIDATOR' | 'CONSUMER' | 'OPERATOR';
export type YggdrasilEdgeClass =
  | 'PRODUCES'
  | 'VALIDATES'
  | 'CONSUMES'
  | 'BINDS'
  | 'ROUTES_TO'
  | 'EVIDENCES'
  | 'EXPOSES'
  | 'REFERENCES'
  | 'RENDER_RELATION';
export type YggdrasilConfidence = 'VERIFIED' | 'SUPPORTED' | 'INFERRED' | 'NOT_COMPUTABLE';
export type YggdrasilFreshness = 'CURRENT' | 'STALE' | 'NOT_COMPUTABLE';
export type YggdrasilResolution = 'RESOLVED' | 'UNRESOLVED' | 'NOT_COMPUTABLE';

export interface YggdrasilTopologyEvidence extends OperatorPlatformSourceArtifact {
  id: string;
}

export interface YggdrasilTopologyNode {
  id: string;
  label: string;
  node_class: YggdrasilNodeClass;
  roles: YggdrasilInterfaceRole[];
  status: string;
  resolution_state: YggdrasilResolution;
  source_ref: string;
  provenance: OperatorPlatformProvenance;
  confidence: YggdrasilConfidence;
  freshness: YggdrasilFreshness;
  evidence_refs: string[];
  temporal_ref: { category: 'TOPOLOGY_NODE'; entity_id: string };
}

export interface YggdrasilTopologyEdge {
  id: string;
  source: string;
  target: string;
  edge_class: YggdrasilEdgeClass;
  relation: string;
  status: string;
  resolution_state: YggdrasilResolution;
  provenance: OperatorPlatformProvenance;
  confidence: YggdrasilConfidence;
  freshness: YggdrasilFreshness;
  evidence_refs: string[];
  temporal_ref: { category: 'TOPOLOGY_EDGE'; entity_id: string };
}

export interface YggdrasilTopologyProjection {
  schema_version: 'AALViz.YggdrasilTopology.v1';
  generation: {
    generated_at: string;
    generated_by: 'LIVE_YGGDRASIL_TOPOLOGY_ENRICHMENT_001';
    topology_generation_id: string;
    operator_platform_generation_id: string | null;
  };
  status: OperatorPlatformSectionStatus;
  provenance: OperatorPlatformProvenance;
  source_artifacts: YggdrasilTopologyEvidence[];
  authority: Authority & {
    canon_mutation_allowed: false;
    execution_authority: false;
    graph_driven_execution_allowed: false;
    autonomous_link_creation_allowed: false;
    alerting_allowed: false;
    scheduling_allowed: false;
  };
  payload: {
    summary: {
      node_count: number;
      edge_count: number;
      evidence_count: number;
      unresolved_node_count: number;
      stale_entity_count: number;
      inferred_edge_count: number;
      node_class_counts: Partial<Record<YggdrasilNodeClass, number>>;
      edge_class_counts: Partial<Record<YggdrasilEdgeClass, number>>;
    };
    nodes: YggdrasilTopologyNode[];
    edges: YggdrasilTopologyEdge[];
    evidence: YggdrasilTopologyEvidence[];
  } | null;
  not_computable_reason: string | null;
  validation_findings: string[];
  temporal_linkage: {
    status: 'MATCHED' | 'STALE' | 'NOT_COMPUTABLE';
    source_path: string | null;
    content_sha256: string | null;
    prior_generation_id: string | null;
    current_generation_id: string | null;
  };
  canonical_hash: string;
}

export type YggdrasilIntegrityFindingType =
  | 'GENERATION_MISMATCH'
  | 'INFERRED_LINK'
  | 'MISSING_EVIDENCE'
  | 'SECTION_NOT_COMPUTABLE'
  | 'SOURCE_INTEGRITY_GAP'
  | 'STALE_ENTITY'
  | 'TEMPORAL_REMOVAL'
  | 'TEMPORAL_WEAKENING'
  | 'UNRESOLVED_ENTITY';
export type YggdrasilIntegritySeverity = 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO' | 'NOT_COMPUTABLE';

export interface YggdrasilIntegrityFinding {
  id: string;
  finding_type: YggdrasilIntegrityFindingType;
  severity: YggdrasilIntegritySeverity;
  subject_key: string;
  entity_ref: {
    category: 'TOPOLOGY_NODE' | 'TOPOLOGY_EDGE' | 'SOURCE_ARTIFACT' | 'SECTION';
    entity_id: string;
  } | null;
  evidence_refs: string[];
  provenance: OperatorPlatformProvenance;
  confidence: YggdrasilConfidence;
  reason: string;
  computability: 'COMPUTABLE' | 'NOT_COMPUTABLE';
  generation_binding: {
    topology_generation_id: string;
    operator_platform_generation_id: string | null;
    temporal_diff_generation_id: string | null;
  };
}

export interface YggdrasilTopologyIntegrityProjection {
  schema_version: 'AALViz.YggdrasilTopologyIntegrity.v1';
  generation: {
    generated_at: string;
    generated_by: 'YGGDRASIL_TOPOLOGY_INTEGRITY_FINDINGS_001';
    integrity_generation_id: string;
    topology_generation_id: string | null;
    operator_platform_generation_id: string | null;
    temporal_diff_generation_id: string | null;
  };
  status: OperatorPlatformSectionStatus;
  provenance: OperatorPlatformProvenance;
  source_artifacts: YggdrasilTopologyEvidence[];
  authority: {
    projection_only: true;
    runtime_mutation_allowed: false;
    canon_mutation_allowed: false;
    execution_authority: false;
    production_activation_allowed: false;
    graph_driven_execution_allowed: false;
    alert_delivery_allowed: false;
    acknowledgement_state_allowed: false;
    browser_persistence_allowed: false;
    route_receipt_triggering_allowed: false;
    scheduling_allowed: false;
  };
  payload: {
    summary: {
      finding_count: number;
      affected_entity_count: number;
      non_computable_count: number;
      severity_counts: Partial<Record<YggdrasilIntegritySeverity, number>>;
      type_counts: Partial<Record<YggdrasilIntegrityFindingType, number>>;
    };
    findings: YggdrasilIntegrityFinding[];
  } | null;
  not_computable_reason: string | null;
  validation_findings: string[];
  canonical_hash: string;
}

export type YggdrasilDeltaStructuralClass =
  | 'ISOLATED_NODE_EMERGENCE' | 'ORPHANED_CONTRACT' | 'VALIDATOR_COVERAGE_LOSS'
  | 'BROKEN_PRODUCER_CONSUMER_PATH' | 'OWNERSHIP_DRIFT' | 'STALE_EVIDENCE_CHAIN'
  | 'TOPOLOGY_FRAGMENTATION' | 'UNEXPECTED_CLUSTER_FUSION';

export interface YggdrasilDeltaCorrelation {
  id: string;
  correlation_key: string;
  state: 'NEW' | 'RESOLVED' | 'PERSISTENT' | 'NOT_COMPUTABLE';
  correlation_state: 'CHANGE_CORRELATED' | 'UNCORRELATED' | 'NOT_COMPUTABLE';
  prior_finding_id: string | null;
  current_finding_id: string | null;
  entity_ref: { category: 'TOPOLOGY_NODE' | 'TOPOLOGY_EDGE'; entity_id: string } | null;
  subject_key: string;
  prior_severity: YggdrasilIntegritySeverity | null;
  current_severity: YggdrasilIntegritySeverity | null;
  severity_change: 'INCREASED' | 'DECREASED' | 'UNCHANGED' | 'NOT_COMPUTABLE';
  provenance: OperatorPlatformProvenance;
  confidence: YggdrasilConfidence;
  supporting_entity_ids: string[];
  supporting_temporal_entry_ids: string[];
  observed_generation_count: number;
  persistence_seconds_lower_bound: number | null;
  true_age_status: 'NOT_COMPUTABLE';
  evidence_refs: string[];
}

export interface YggdrasilStructuralDelta {
  id: string;
  structural_class: YggdrasilDeltaStructuralClass;
  entity_refs: Array<{ category: 'TOPOLOGY_NODE' | 'TOPOLOGY_EDGE'; entity_id: string }>;
  prior_value: unknown;
  current_value: unknown;
  provenance: OperatorPlatformProvenance;
  confidence: YggdrasilConfidence;
  reason: string;
  evidence_refs: string[];
  computability: 'COMPUTABLE' | 'NOT_COMPUTABLE';
}

export interface YggdrasilChangedPath {
  id: string;
  source_id: string;
  target_id: string;
  change: 'ADDED' | 'REMOVED' | 'CHANGED' | 'NOT_COMPUTABLE';
  prior_node_ids: string[];
  prior_edge_ids: string[];
  current_node_ids: string[];
  current_edge_ids: string[];
  evidence_refs: string[];
}

export interface YggdrasilDeltaPriority {
  id: string;
  rank: number;
  source_ref: { category: 'INTEGRITY_FINDING' | 'STRUCTURAL_DELTA'; entity_id: string };
  score: number;
  score_breakdown: {
    severity: number;
    structural: number;
    operational_surfaces: number;
    persistence: number;
    confidence: number;
  };
  severity: Exclude<YggdrasilIntegritySeverity, 'NOT_COMPUTABLE'>;
  structural_classes: YggdrasilDeltaStructuralClass[];
  confidence: Exclude<YggdrasilConfidence, 'NOT_COMPUTABLE'>;
  evidence_count: number;
  affected_surface_ids: string[];
  why_this_matters: string;
  evidence_refs: string[];
}

export interface YggdrasilDeltaSection<T> {
  status: OperatorPlatformSectionStatus;
  provenance: OperatorPlatformProvenance;
  not_computable_reason: string | null;
  validation_findings: string[];
  entries: T[] | null;
}

export interface YggdrasilTopologyDeltaIntelligenceProjection {
  schema_version: 'AALViz.YggdrasilTopologyDeltaIntelligence.v1';
  generation: {
    generated_at: string;
    generated_by: 'YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_001';
    delta_generation_id: string;
    prior_topology_generation_id: string;
    current_topology_generation_id: string;
    prior_operator_platform_generation_id: string;
    current_operator_platform_generation_id: string;
    prior_integrity_generation_id: string | null;
    current_integrity_generation_id: string | null;
    temporal_diff_generation_id: string | null;
  };
  status: OperatorPlatformSectionStatus;
  provenance: OperatorPlatformProvenance;
  source_artifacts: YggdrasilTopologyEvidence[];
  sections: {
    finding_correlation: YggdrasilDeltaSection<YggdrasilDeltaCorrelation>;
    structural_deltas: YggdrasilDeltaSection<YggdrasilStructuralDelta>;
    changed_paths: YggdrasilDeltaSection<YggdrasilChangedPath>;
    review_priorities: YggdrasilDeltaSection<YggdrasilDeltaPriority>;
  };
  summary: {
    finding_state_counts: Partial<Record<YggdrasilDeltaCorrelation['state'], number>>;
    structural_class_counts: Partial<Record<YggdrasilDeltaStructuralClass, number>>;
    changed_path_count: number;
    active_priority_count: number;
    not_computable_count: number;
    highest_score: number | null;
  };
  authority: {
    projection_only: true;
    execution_authority: false;
    canon_mutation_allowed: false;
    runtime_mutation_allowed: false;
    graph_driven_execution_allowed: false;
    production_activation_allowed: false;
    alert_delivery_allowed: false;
    acknowledgement_state_allowed: false;
    browser_persistence_allowed: false;
    route_receipt_triggering_allowed: false;
    scheduling_allowed: false;
    automatic_remediation_allowed: false;
    autonomous_escalation_allowed: false;
  };
  validation_findings: string[];
  canonical_hash: string;
}

export interface LiveConsoleProjectionBundle {
  schema_version: 'AALViz.LiveConsoleProjectionBundle.v0.2';
  generated_at: string;
  authority: Authority;
  systems: SystemProjection[];
  operator_queue: OperatorQueueItem[];
  source_mode?: SourceMode;
  source_artifacts?: string[];
  fail_closed_reason?: string | null;
  fusion_overlay?: FusionOverlayPacket;
  operator_narrative_report?: OperatorNarrativeReportPacket;
  migration_runner_posture?: MigrationRunnerPosture;
  migration_preflight_posture?: MigrationPreflightPosture;
  combined_health_migration_artifact_posture?: CombinedHealthMigrationArtifactPosture;
  operator_platform: OperatorPlatformProjection;
  yggdrasil_topology?: YggdrasilTopologyProjection;
  yggdrasil_topology_integrity?: YggdrasilTopologyIntegrityProjection;
  yggdrasil_topology_delta_intelligence?: YggdrasilTopologyDeltaIntelligenceProjection;
}

export type MetricDeltaState =
  | 'STABLE'
  | 'DRIFT'
  | 'COLLAPSE'
  | 'RECOVERY'
  | 'HYBRID_COLLISION';

export interface MetricDisplayValue {
  metric: string;
  value: number;
  label: string;
  definition: string;
  always_visible: true;
  visual_projection: string;
}

export interface CandidateMetricDisplayValue {
  metric: string;
  value: number;
  label: string;
  meaning: string;
  origin: string;
  stabilization_window_required: true;
  canon_promotion_allowed: false;
  visual_projection: string;
}

export interface MetricDeltaValue {
  metric: string;
  value: number;
  state: MetricDeltaState;
}

export interface SystemFusionContribution {
  system: string;
  metric_contribution: string;
  use: string;
}

export interface NonFilteringComplianceMonitor {
  output_preserved: true;
  annotation_only: true;
  filter_calls_detected: false;
  suppression_calls_detected: false;
  rewrite_calls_detected: false;
  panel_hiding_detected: false;
}

export interface DashboardRenderingLocks {
  raw_layer_always_visible: true;
  max_overlay_opacity: 0.6;
  no_panel_hiding: true;
  no_metric_suppression: true;
  no_output_filtering: true;
  no_output_rewrite: true;
  no_canon_mutation: true;
  no_forecast_weight_mutation: true;
}

export interface ABXMetricDashboardFrame {
  packet_type: 'ABXMetricDashboardFrame.v1';
  authority: 'SHADOW_ONLY_TRACE';
  output_effect: 'VISUAL_ANNOTATION_ONLY';
  non_filtering_compliance: true;
  batch_id: string;
  previous_batch_id: string;
  panels: string[];
  core_metrics: MetricDisplayValue[];
  candidate_metrics: CandidateMetricDisplayValue[];
  delta: MetricDeltaValue[];
  system_fusion_matrix: SystemFusionContribution[];
  afe_run_stream: ProjectionPacket[];
  shadow_observation_feed: ProjectionPacket[];
  oracle_annotation_feed: ProjectionPacket[];
  aal_viz_overlay_preview: string[];
  non_filtering_compliance_monitor: NonFilteringComplianceMonitor;
  rendering_locks: DashboardRenderingLocks;
  source_runs: string[];
  provenance_hash: string;
}

export type RelationshipType =
  | 'PROVENANCE_PARENT'
  | 'DERIVED_FROM'
  | 'FORECAST_LINEAGE'
  | 'OUTCOME_RESOLUTION'
  | 'CONTRADICTION'
  | 'MOTIF_RESONANCE'
  | 'STRATEGY_DEPENDENCY'
  | 'OPERATOR_DECISION'
  | 'OBSERVED_LINK_CLAIM'
  | 'INFERRED_LINK_CLAIM'
  | 'SPECULATIVE_LINK_CLAIM';

export type RelationshipLinkKind =
  | 'OBSERVED_LINK'
  | 'INFERRED_LINK'
  | 'SPECULATIVE_LINK'
  | 'NOT_COMPUTABLE_LINK';

export interface LineageOverlayNode {
  node_id: string;
  label: string;
  system_id: string;
  status: SystemStatus;
  authority_tier: 'VISUAL_PROJECTION_ONLY';
  provenance_state: 'OBSERVED' | 'NOT_COMPUTABLE';
  selection_focus_allowed: true;
  packet_count: number;
  receipt_count: number;
}

export interface LineageRelationshipEdge {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  relationship_type: RelationshipType;
  link_kind: RelationshipLinkKind;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW' | 'NOT_COMPUTABLE';
  authority_tier: 'VISUAL_PROJECTION_ONLY';
  provenance_state: 'OBSERVED' | 'INFERRED' | 'SPECULATIVE' | 'NOT_COMPUTABLE';
  renders_dimmed: boolean;
  label: string;
}

export interface LineageRelationshipOverlayFrame {
  packet_type: 'AALVizLineageRelationshipOverlayFrame.v1';
  authority: 'VISUAL_PROJECTION_ONLY';
  relationship_arrow_policy: 'DISPLAY_DECLARED_RELATIONSHIP_ONLY';
  projection_only: true;
  non_filtering_compliance: true;
  nodes: LineageOverlayNode[];
  edges: LineageRelationshipEdge[];
  relationship_types: RelationshipType[];
  link_kind_legend: RelationshipLinkKind[];
  rendering_locks: {
    gpu_simulation_mutates_packets: false;
    selection_highlight_mutates_packets: false;
    selection_highlight_ranks_packets: false;
    scoring_authority: false;
    forecasting_authority: false;
    validation_authority: false;
    promotion_authority: false;
    truth_authority: false;
    missing_source_renders_not_computable: true;
  };
  provenance_hash: string;
}

export type PacketBindingState = 'BOUND' | 'PENDING' | 'NOT_COMPUTABLE';
export type NotionDeepLinkState = 'BOUND' | 'NOT_COMPUTABLE';
export type RelationshipStreamState = 'OBSERVED' | 'INFERRED' | 'NOT_COMPUTABLE';

export interface PacketBindingRecord {
  binding_id: string;
  system_id: string;
  packet_id: string;
  packet_type: string;
  packet_status: string;
  live_store_key: string;
  binding_state: PacketBindingState;
  canonical_notion_url: string | null;
  notion_deep_link_state: NotionDeepLinkState;
  relationship_stream_state: RelationshipStreamState;
  append_only_required: true;
  projection_only: true;
}

export interface RelationshipEdgeStreamRecord {
  stream_id: string;
  source_system_id: string;
  target_packet_id: string;
  relationship_stream_state: RelationshipStreamState;
  declared_links_only: true;
  source_fields_mutable: false;
}

export interface PacketBindingFrame {
  packet_type: 'AALVizPacketBindingFrame.v1';
  drop_name: 'AAL-Viz v6.7 — Notion + Live Abraxas Packet Binding Layer Code Drop';
  authority: 'TRANSPORT_STORAGE_PROJECTION_ONLY';
  mutation_policy: 'APPEND_ONLY_DEFAULT';
  projection_only: true;
  bindings: [
    'packet_ingest',
    'notion_writer',
    'websocket_broadcast',
    'frontend_live_store',
    'notion_deep_link',
    'relationship_edge_stream',
  ];
  packet_ingest_endpoint: '/api/packets';
  websocket_url_env: 'AAL_VIZ_WS_URL';
  source_bundle_generated_at: string;
  binding_records: PacketBindingRecord[];
  notion_url_map: Record<string, string | null>;
  relationship_edge_stream: RelationshipEdgeStreamRecord[];
  binding_locks: {
    packet_writes_append_only: true;
    notion_writer_enabled: false;
    websocket_broadcast_enabled: false;
    websocket_events_mutate_source_fields: false;
    frontend_selection_promotes: false;
    frontend_selection_validates: false;
    frontend_selection_scores: false;
    frontend_selection_resolves_outcomes: false;
    missing_provenance_renders_not_computable: true;
  };
  provenance_hash: string;
}

export type ScoringStatus = 'SCORED' | 'NOT_COMPUTABLE' | 'CORRECTED';
export type ForecastOutcomeJoinState =
  | 'JOINED'
  | 'MISSING_FORECAST_PROBABILITY'
  | 'MISSING_OUTCOME'
  | 'NOT_COMPUTABLE';

export interface ScoringBindingRecord {
  score_id: string;
  forecast_id: string;
  run_id: string;
  subject: string;
  probability: number | null;
  outcome: 0 | 1 | null;
  brier_score: number | null;
  scoring_status: ScoringStatus;
  join_state: ForecastOutcomeJoinState;
  blockers: string[];
  source_packet_id: string;
  source_system_id: string;
  immutable_once_sealed: true;
  projection_only: true;
}

export interface CalibrationSummaryProjection {
  summary_id: string;
  run_id: string;
  bucket_count: number;
  mean_brier: number | null;
  calibration_error: number | null;
  sample_size: number;
  scoring_status: ScoringStatus;
}

export interface ScoringBindingFrame {
  packet_type: 'AALVizScoringBindingFrame.v1';
  drop_name: 'AAL-Viz v6.8 — Run Ledger + Brier Scoring Binding Code Drop';
  authority: 'SCORING_LEDGER_AND_PROJECTION_ONLY';
  promotion_policy: 'NO_AUTOMATIC_PROMOTION_FROM_SCORE_ONLY';
  projection_only: true;
  folded_versions: ['v6.1', 'v6.2', 'v6.3', 'v6.4', 'v6.5', 'v6.6', 'v6.7'];
  bindings: [
    'run_ledger',
    'forecast_outcome_join',
    'brier_score',
    'calibration_summary',
    'notion_score_write',
    'websocket_score_broadcast',
    'aal_viz_score_surface',
  ];
  scoring_records: ScoringBindingRecord[];
  calibration_summary: CalibrationSummaryProjection;
  scoring_locks: {
    brier_descriptive_only: true;
    automatic_promotion_allowed: false;
    execution_authority: false;
    truth_authority: false;
    model_weight_mutation_allowed: false;
    notion_score_write_enabled: false;
    websocket_score_broadcast_enabled: false;
    missing_outcome_renders_not_computable: true;
    missing_probability_renders_not_computable: true;
    correction_packet_required_for_score_changes: true;
  };
  provenance_hash: string;
}

export type CalibrationBadge =
  | 'WELL_CALIBRATED'
  | 'UNSTABLE'
  | 'UNDER_SAMPLED'
  | 'CALIBRATION_NOT_COMPUTABLE';

export interface BrierWeightedNodeBehavior {
  behavior_id: string;
  forecast_id: string;
  run_id: string;
  brier_score: number | null;
  mean_brier: number | null;
  calibration_error: number | null;
  sample_size: number;
  scoring_status: ScoringStatus;
  stability_multiplier: number;
  glow_integrity: number;
  jitter_penalty: number;
  halo_distortion: number;
  edge_sharpness: number;
  trust_drag: number;
  calibration_badge: CalibrationBadge;
  projection_only: true;
  source_forecast_probability_mutated: false;
  authority_tier_mutated: false;
}

export interface BrierWeightedNodeBehaviorFrame {
  packet_type: 'AALVizBrierWeightedNodeBehaviorFrame.v1';
  drop_name: 'AAL-Viz v6.9 — Brier-Weighted Node Behavior Code Drop';
  authority: 'VISUAL_CALIBRATION_PROJECTION_ONLY';
  mutation_policy: 'NO_FORECAST_OR_AUTHORITY_MUTATION';
  projection_only: true;
  folded_versions: ['v6.1', 'v6.2', 'v6.3', 'v6.4', 'v6.5', 'v6.6', 'v6.7', 'v6.8'];
  features: [
    'brier_visual_weight',
    'calibration_badge',
    'halo_distortion',
    'stability_multiplier',
    'sample_size_gate',
    'calibration_not_computable_state',
  ];
  behaviors: BrierWeightedNodeBehavior[];
  behavior_locks: {
    display_only: true;
    scoring_mutation_allowed: false;
    forecast_probability_mutation_allowed: false;
    authority_tier_mutation_allowed: false;
    automatic_promotion_allowed: false;
    automatic_demotion_allowed: false;
    execution_authority: false;
    truth_authority: false;
    low_sample_size_damps_trust_effects: true;
    missing_scoring_renders_calibration_not_computable: true;
    corrected_scores_show_correction_provenance: true;
  };
  provenance_hash: string;
}

export type ClusterType = 'DOMAIN' | 'STRATEGY' | 'SUBSYSTEM' | 'SIGNAL_FAMILY' | 'RUN_GROUP';
export type ClusterScoringStatus = 'SCORED' | 'UNDER_SAMPLED' | 'MIXED' | 'NOT_COMPUTABLE';
export type ClusterCalibrationWeather = 'CLEAR' | 'NOISY' | 'TURBULENT' | 'UNDER_SAMPLED' | 'NOT_COMPUTABLE';

export interface BrierWeightedClusterBehavior {
  cluster_id: string;
  cluster_type: ClusterType;
  member_count: number;
  scored_member_count: number;
  mean_brier: number | null;
  median_brier: number | null;
  calibration_error: number | null;
  score_variance: number | null;
  sample_size: number;
  window_start: string;
  window_end: string;
  scoring_status: ClusterScoringStatus;
  cohesion_multiplier: number;
  boundary_sharpness: number;
  cluster_jitter: number;
  turbulence: number;
  trust_halo: number;
  shear_force: number;
  warning_ring_opacity: number;
  calibration_weather: ClusterCalibrationWeather;
  projection_only: true;
  source_forecast_probability_mutated: false;
  source_score_mutated: false;
  authority_tier_mutated: false;
}

export interface BrierWeightedClusterBehaviorFrame {
  packet_type: 'AALVizBrierWeightedClusterBehaviorFrame.v1';
  drop_name: 'AAL-Viz v7.0 — Brier-Weighted Cluster Behavior Code Drop';
  authority: 'VISUAL_CALIBRATION_PROJECTION_ONLY';
  mutation_policy: 'NO_FORECAST_SCORE_OR_AUTHORITY_MUTATION';
  projection_only: true;
  folded_versions: ['v6.1', 'v6.2', 'v6.3', 'v6.4', 'v6.5', 'v6.6', 'v6.7', 'v6.8', 'v6.9'];
  features: [
    'cluster_brier_weight',
    'calibration_weather',
    'cohesion_multiplier',
    'cluster_turbulence',
    'internal_shear',
    'sample_size_gate',
    'cluster_not_computable_state',
  ];
  clusters: BrierWeightedClusterBehavior[];
  cluster_locks: {
    display_only: true;
    cluster_weather_static_mode_available: true;
    scoring_mutation_allowed: false;
    forecast_probability_mutation_allowed: false;
    score_mutation_allowed: false;
    authority_tier_mutation_allowed: false;
    automatic_promotion_allowed: false;
    automatic_demotion_allowed: false;
    execution_authority: false;
    truth_authority: false;
    low_sample_size_damps_trust_effects: true;
    missing_scoring_renders_cluster_calibration_not_computable: true;
    mixed_clusters_show_variance_and_shear: true;
    corrected_scores_show_correction_provenance: true;
  };
  provenance_hash: string;
}

export type TemporalCalibrationEntityType = 'NODE' | 'CLUSTER' | 'DOMAIN' | 'STRATEGY' | 'SUBSYSTEM';
export type TemporalCalibrationSmoothing = 'NONE' | 'LINEAR' | 'EASED';
export type TemporalCalibrationMode = 'SNAPSHOT' | 'TRAIL' | 'MORPH' | 'CHRONOSCOPE';
export type TemporalCalibrationAnimationBadge =
  | 'IMPROVING'
  | 'DECAYING'
  | 'VOLATILE'
  | 'STABLE'
  | 'UNDER_SAMPLED'
  | 'NOT_COMPUTABLE';

export interface TemporalCalibrationWindow {
  window_id: string;
  start_at: string;
  end_at: string;
  mean_brier: number | null;
  calibration_error: number | null;
  score_variance: number | null;
  sample_size: number;
  scoring_status: ClusterScoringStatus;
}

export interface TemporalCalibrationPlayback {
  speed: number;
  loop: false;
  smoothing: TemporalCalibrationSmoothing;
  mode: TemporalCalibrationMode;
}

export interface TemporalCalibrationAnimation {
  timeline_id: string;
  entity_id: string;
  entity_type: TemporalCalibrationEntityType;
  windows: TemporalCalibrationWindow[];
  playback: TemporalCalibrationPlayback;
  temporal_cohesion_curve: number[];
  turbulence_curve: number[];
  trust_halo_curve: number[];
  boundary_integrity_curve: number[];
  gap_markers: string[];
  animation_badge: TemporalCalibrationAnimationBadge;
  projection_only: true;
  source_forecast_probability_mutated: false;
  source_score_mutated: false;
  authority_tier_mutated: false;
}

export interface TemporalCalibrationAnimationFrame {
  packet_type: 'AALVizTemporalCalibrationAnimationFrame.v1';
  drop_name: 'AAL-Viz v7.1 — Temporal Calibration Animation Code Drop';
  authority: 'VISUAL_TEMPORAL_CALIBRATION_PROJECTION_ONLY';
  mutation_policy: 'NO_FORECAST_SCORE_OR_AUTHORITY_MUTATION';
  projection_only: true;
  folded_versions: ['v6.1', 'v6.2', 'v6.3', 'v6.4', 'v6.5', 'v6.6', 'v6.7', 'v6.8', 'v6.9', 'v7.0'];
  features: [
    'calibration_timeline',
    'chronoscope_scrubber',
    'temporal_trails',
    'morph_animation',
    'temporal_gap_markers',
    'accessibility_static_summary',
  ];
  timelines: TemporalCalibrationAnimation[];
  animation_locks: {
    display_only: true;
    static_timeline_table_available: true;
    animated_playback_controls_enabled: false;
    scoring_mutation_allowed: false;
    forecast_probability_mutation_allowed: false;
    score_mutation_allowed: false;
    authority_tier_mutation_allowed: false;
    automatic_promotion_allowed: false;
    automatic_demotion_allowed: false;
    execution_authority: false;
    truth_authority: false;
    missing_windows_render_temporal_gaps: true;
    missing_windows_interpolated_as_certainty: false;
    low_sample_windows_render_under_sampled: true;
    corrected_windows_show_correction_provenance: true;
  };
  provenance_hash: string;
}

export type StrategyAttributionStatus = 'ATTRIBUTED' | 'UNDER_SAMPLED' | 'NOT_COMPUTABLE';
export type DriftDirection = 'IMPROVING' | 'DECAYING' | 'STABLE' | 'VOLATILE' | 'UNDER_SAMPLED' | 'NOT_COMPUTABLE';

export interface StrategyAttributionPacket {
  attribution_id: string;
  run_id: string;
  strategy_id: string;
  strategy_name: string;
  domain: string;
  signal_family: string;
  forecast_ids: string[];
  scored_forecast_count: number;
  mean_brier: number | null;
  baseline_mean_brier: number | null;
  brier_delta: number | null;
  calibration_error_delta: number | null;
  contribution_score: number | null;
  attribution_status: StrategyAttributionStatus;
  computed_at: string;
  lineage_join_state: 'JOINED' | 'MISSING_STRATEGY_LINEAGE' | 'MISSING_OUTCOME_DATA';
  projection_only: true;
  source_forecast_probability_mutated: false;
  source_score_mutated: false;
  authority_tier_mutated: false;
  strategy_routing_mutated: false;
}

export interface DomainScoreDriftPacket {
  drift_id: string;
  domain: string;
  window_start: string;
  window_end: string;
  mean_brier: number | null;
  previous_mean_brier: number | null;
  brier_delta: number | null;
  calibration_error: number | null;
  sample_size: number;
  drift_direction: DriftDirection;
  computed_at: string;
  projection_only: true;
  source_forecast_probability_mutated: false;
  source_score_mutated: false;
  authority_tier_mutated: false;
  strategy_routing_mutated: false;
}

export interface StrategyAttributionDriftFrame {
  packet_type: 'AALVizStrategyAttributionDriftFrame.v1';
  drop_name: 'AAL-Viz v7.2 — Strategy Attribution + Domain Score Drift Timeline Code Drop';
  authority: 'DESCRIPTIVE_ATTRIBUTION_AND_PROJECTION_ONLY';
  mutation_policy: 'NO_FORECAST_SCORE_AUTHORITY_OR_ROUTING_MUTATION';
  projection_only: true;
  folded_versions: ['v6.1', 'v6.2', 'v6.3', 'v6.4', 'v6.5', 'v6.6', 'v6.7', 'v6.8', 'v6.9', 'v7.0', 'v7.1'];
  features: [
    'strategy_attribution_ledger',
    'domain_score_drift_timeline',
    'contribution_score',
    'rolling_brier_windows',
    'attribution_visual_weight',
    'under_sampled_guard',
    'not_computable_guard',
  ];
  attribution_packets: StrategyAttributionPacket[];
  drift_packets: DomainScoreDriftPacket[];
  attribution_locks: {
    display_only: true;
    descriptive_attribution_only: true;
    notion_write_adapter_enabled: false;
    websocket_broadcast_enabled: false;
    contribution_score_promotes_or_demotes: false;
    scoring_mutation_allowed: false;
    forecast_probability_mutation_allowed: false;
    score_mutation_allowed: false;
    authority_tier_mutation_allowed: false;
    strategy_routing_mutation_allowed: false;
    automatic_promotion_allowed: false;
    automatic_demotion_allowed: false;
    execution_authority: false;
    truth_authority: false;
    low_sample_size_renders_under_sampled: true;
    missing_strategy_lineage_renders_not_computable: true;
    missing_outcome_data_renders_not_computable: true;
    baseline_comparison_required: true;
    corrected_scores_show_correction_provenance: true;
  };
  provenance_hash: string;
}

export type OperatorDecisionType =
  | 'SELECT'
  | 'REJECT'
  | 'HOLD'
  | 'ESCALATE'
  | 'WATCH'
  | 'OVERRIDE'
  | 'ANNOTATE'
  | 'CORRECT';

export type OperatorDecisionTargetType =
  | 'FORECAST'
  | 'STRATEGY'
  | 'DOMAIN'
  | 'SIGNAL'
  | 'RUN'
  | 'OUTCOME'
  | 'CLUSTER';

export type OperatorDecisionProvenance = 'complete' | 'partial' | 'missing';
export type DecisionEffect = 'HELPED' | 'HURT' | 'NEUTRAL' | 'MIXED' | 'UNDER_SAMPLED' | 'NOT_COMPUTABLE';
export type DecisionAttributionStatus = 'ATTRIBUTED' | 'PENDING' | 'UNDER_SAMPLED' | 'NOT_COMPUTABLE';

export interface OperatorDecisionPacketProjection {
  decision_id: string;
  operator_id: string;
  created_at: string;
  decision_type: OperatorDecisionType;
  target_type: OperatorDecisionTargetType;
  target_id: string;
  linked_forecast_ids: string[];
  linked_strategy_ids: string[];
  linked_signal_ids: string[];
  rationale: string;
  confidence_at_decision: number | null;
  expected_result: string | null;
  review_deadline: string | null;
  authority: 'OPERATOR_LOG_ONLY';
  provenance: OperatorDecisionProvenance;
  projection_only: true;
  autonomous_execution_triggered: false;
  source_forecast_probability_mutated: false;
  source_score_mutated: false;
  authority_tier_mutated: false;
  strategy_routing_mutated: false;
}

export interface DecisionOutcomeAttributionPacket {
  attribution_id: string;
  decision_id: string;
  target_id: string;
  outcome_id: string | null;
  evaluation_window_start: string;
  evaluation_window_end: string;
  observed_result: string | null;
  decision_effect: DecisionEffect;
  confidence_delta: number | null;
  brier_delta: number | null;
  contribution_score: number | null;
  attribution_status: DecisionAttributionStatus;
  computed_at: string;
  projection_only: true;
  decision_quality_score: number | null;
  source_forecast_probability_mutated: false;
  source_score_mutated: false;
  authority_tier_mutated: false;
  strategy_routing_mutated: false;
}

export interface OperatorDecisionOutcomeFrame {
  packet_type: 'AALVizOperatorDecisionOutcomeFrame.v1';
  drop_name: 'AAL-Viz v7.3 — Operator Decision Packets + Outcome Attribution Code Drop';
  authority: 'DESCRIPTIVE_DECISION_LOGGING_AND_PROJECTION_ONLY';
  mutation_policy: 'NO_EXECUTION_FORECAST_SCORE_AUTHORITY_OR_ROUTING_MUTATION';
  projection_only: true;
  folded_versions: [
    'v6.1',
    'v6.2',
    'v6.3',
    'v6.4',
    'v6.5',
    'v6.6',
    'v6.7',
    'v6.8',
    'v6.9',
    'v7.0',
    'v7.1',
    'v7.2',
  ];
  features: [
    'operator_decision_packet',
    'decision_outcome_attribution',
    'decision_quality_score',
    'operator_feedback_timeline',
    'decision_overlay_layer',
    'review_queue_panel',
    'correction_decision_support',
  ];
  decision_packets: OperatorDecisionPacketProjection[];
  outcome_attributions: DecisionOutcomeAttributionPacket[];
  decision_locks: {
    display_only: true;
    descriptive_decision_logging_only: true;
    operator_log_only: true;
    notion_write_adapter_enabled: false;
    websocket_broadcast_enabled: false;
    autonomous_execution_allowed: false;
    forecast_probability_mutation_allowed: false;
    score_mutation_allowed: false;
    authority_tier_mutation_allowed: false;
    strategy_routing_mutation_allowed: false;
    automatic_promotion_allowed: false;
    automatic_demotion_allowed: false;
    execution_authority: false;
    truth_authority: false;
    rationale_is_context_not_proof: true;
    correction_decisions_preserve_provenance: true;
    missing_outcome_renders_pending_or_not_computable: true;
    low_sample_size_renders_under_sampled: true;
    decision_quality_score_promotes_or_demotes: false;
  };
  provenance_hash: string;
}

export type LiveOutcomeNormalizedStatus = 'OPEN' | 'RESOLVED' | 'CANCELLED' | 'AMBIGUOUS' | 'ERROR';
export type OutcomeReviewTargetType = 'FORECAST' | 'OPERATOR_DECISION' | 'STRATEGY' | 'RUN';
export type OutcomeReviewReason =
  | 'PENDING_RESOLUTION'
  | 'STALE'
  | 'AMBIGUOUS'
  | 'CONFLICTING_SOURCES'
  | 'LOW_PROVENANCE'
  | 'CORRECTION_REQUESTED';
export type OutcomeReviewStatus = 'OPEN' | 'IN_REVIEW' | 'RESOLVED' | 'DISMISSED' | 'NOT_COMPUTABLE';
export type OutcomeReviewPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type OutcomeCorrectionType =
  | 'RESULT_CHANGE'
  | 'SOURCE_CHANGE'
  | 'TIMESTAMP_CHANGE'
  | 'PROVENANCE_CHANGE'
  | 'DUPLICATE_MERGE';

export interface LiveOutcomeFeedPacket {
  feed_packet_id: string;
  provider: string;
  provider_event_id: string;
  captured_at: string;
  source_url: string | null;
  raw_status: string;
  raw_payload_hash: string;
  normalized_status: LiveOutcomeNormalizedStatus;
  normalized_result: 0 | 1 | null;
  confidence: number;
  provenance: OperatorDecisionProvenance;
  projection_only: true;
  candidate_resolution_only: true;
  final_truth_authority: false;
  source_forecast_probability_mutated: false;
  source_score_mutated: false;
  strategy_routing_mutated: false;
}

export interface OutcomeReviewItemProjection {
  review_id: string;
  target_type: OutcomeReviewTargetType;
  target_id: string;
  feed_packet_id: string | null;
  review_reason: OutcomeReviewReason;
  review_status: OutcomeReviewStatus;
  priority: OutcomeReviewPriority;
  created_at: string;
  due_at: string | null;
  projection_only: true;
  review_decision_descriptive_only: true;
  outcome_resolution_authority: false;
}

export interface OutcomeCorrectionPacketProjection {
  correction_id: string;
  target_outcome_id: string;
  correction_type: OutcomeCorrectionType;
  previous_value_hash: string;
  corrected_value_hash: string;
  rationale: string;
  source_url: string | null;
  created_at: string;
  provenance: OperatorDecisionProvenance;
  projection_only: true;
  append_only_correction: true;
  prior_value_preserved: true;
  outcome_resolution_authority: false;
}

export interface LiveOutcomeReviewFrame {
  packet_type: 'AALVizLiveOutcomeReviewFrame.v1';
  drop_name: 'AAL-Viz v7.4 — Live Outcome Feeds + Decision Review Queue Code Drop';
  authority: 'OUTCOME_INTAKE_REVIEW_AND_PROJECTION_ONLY';
  mutation_policy: 'APPEND_ONLY_WITH_CORRECTION_PACKETS';
  projection_only: true;
  folded_versions: [
    'v6.1',
    'v6.2',
    'v6.3',
    'v6.4',
    'v6.5',
    'v6.6',
    'v6.7',
    'v6.8',
    'v6.9',
    'v7.0',
    'v7.1',
    'v7.2',
    'v7.3',
  ];
  features: [
    'live_outcome_adapter_interface',
    'forecast_outcome_resolver',
    'decision_review_queue',
    'pending_resolution_tracker',
    'stale_outcome_detector',
    'correction_packet_workflow',
    'outcome_feed_overlay',
  ];
  feed_packets: LiveOutcomeFeedPacket[];
  review_items: OutcomeReviewItemProjection[];
  correction_packets: OutcomeCorrectionPacketProjection[];
  review_locks: {
    display_only: true;
    candidate_resolution_only: true;
    append_only_with_correction_packets: true;
    provider_polling_enabled: false;
    notion_write_adapter_enabled: false;
    websocket_broadcast_enabled: false;
    autonomous_execution_allowed: false;
    outcome_resolution_without_review_allowed: false;
    forecast_probability_mutation_allowed: false;
    score_mutation_allowed: false;
    authority_tier_mutation_allowed: false;
    strategy_routing_mutation_allowed: false;
    automatic_promotion_allowed: false;
    execution_authority: false;
    truth_authority: false;
    ambiguous_or_conflicting_routes_to_review: true;
    low_provenance_routes_to_review: true;
    stale_pending_routes_to_review: true;
    corrections_preserve_previous_and_corrected_hashes: true;
  };
  provenance_hash: string;
}

export type ProviderObservationStatus = 'OK' | 'ERROR' | 'STALE' | 'AMBIGUOUS' | 'CONFLICTING' | 'RATE_LIMITED';
export type ProviderTrustBand = 'HIGH' | 'MEDIUM' | 'LOW' | 'UNDER_SAMPLED' | 'NOT_COMPUTABLE';
export type ProviderConflictType =
  | 'RESULT_MISMATCH'
  | 'TIMESTAMP_MISMATCH'
  | 'STATUS_MISMATCH'
  | 'SOURCE_MISSING'
  | 'PAYLOAD_DIVERGENCE';

export interface ProviderObservationPacket {
  observation_id: string;
  provider_id: string;
  provider_name: string;
  captured_at: string;
  endpoint: string | null;
  event_id: string | null;
  status: ProviderObservationStatus;
  latency_ms: number | null;
  payload_hash: string | null;
  provenance: OperatorDecisionProvenance;
  projection_only: true;
  provider_score_only: true;
  forecast_mutation_allowed: false;
  outcome_truth_authority: false;
}

export interface ProviderReliabilityScorePacket {
  score_id: string;
  provider_id: string;
  provider_name: string;
  window_start: string;
  window_end: string;
  observation_count: number;
  uptime_rate: number | null;
  error_rate: number | null;
  stale_rate: number | null;
  conflict_rate: number | null;
  correction_rate: number | null;
  median_latency_ms: number | null;
  provenance_completeness: number | null;
  reliability_score: number | null;
  trust_band: ProviderTrustBand;
  computed_at: string;
  projection_only: true;
  review_priority_influence_only: true;
  forecast_probability_mutated: false;
  brier_score_mutated: false;
  outcome_truth_mutated: false;
}

export interface ProviderConflictPacket {
  conflict_id: string;
  provider_ids: string[];
  target_event_id: string;
  conflict_type: ProviderConflictType;
  detected_at: string;
  review_item_id: string | null;
  provenance: OperatorDecisionProvenance;
  projection_only: true;
  creates_review_item_only: true;
  outcome_truth_authority: false;
}

export interface ProviderReliabilityFrame {
  packet_type: 'AALVizProviderReliabilityFrame.v1';
  drop_name: 'AAL-Viz v7.5 — Provider Reliability Scoring Code Drop';
  authority: 'SOURCE_RELIABILITY_SCORING_AND_PROJECTION_ONLY';
  mutation_policy: 'NO_FORECAST_OUTCOME_SCORE_AUTHORITY_OR_ROUTING_MUTATION';
  projection_only: true;
  folded_versions: [
    'v6.1',
    'v6.2',
    'v6.3',
    'v6.4',
    'v6.5',
    'v6.6',
    'v6.7',
    'v6.8',
    'v6.9',
    'v7.0',
    'v7.1',
    'v7.2',
    'v7.3',
    'v7.4',
  ];
  features: [
    'provider_reliability_ledger',
    'provider_healthcheck',
    'freshness_score',
    'consistency_score',
    'conflict_rate',
    'correction_rate',
    'latency_score',
    'trust_band',
    'source_reliability_overlay',
  ];
  minimum_window_count: number;
  observations: ProviderObservationPacket[];
  reliability_scores: ProviderReliabilityScorePacket[];
  conflicts: ProviderConflictPacket[];
  reliability_locks: {
    display_only: true;
    source_reliability_projection_only: true;
    provider_healthcheck_enabled: false;
    notion_write_adapter_enabled: false;
    websocket_broadcast_enabled: false;
    autonomous_execution_allowed: false;
    forecast_probability_mutation_allowed: false;
    brier_score_mutation_allowed: false;
    outcome_truth_mutation_allowed: false;
    strategy_routing_mutation_allowed: false;
    automatic_promotion_allowed: false;
    automatic_demotion_allowed: false;
    execution_authority: false;
    truth_authority: false;
    low_trust_routes_to_review: true;
    under_sampled_routes_to_review_unless_corroborated: true;
    provider_reliability_visual_trust_only: true;
    corrections_preserve_previous_and_corrected_hashes: true;
  };
  provenance_hash: string;
}

export type ReviewSuggestionTargetType = 'FORECAST' | 'OUTCOME' | 'PROVIDER' | 'OPERATOR_DECISION' | 'STRATEGY' | 'RUN';
export type ReviewSuggestionType =
  | 'REVIEW_NOW'
  | 'WAIT_FOR_MORE_DATA'
  | 'REQUEST_SECOND_SOURCE'
  | 'APPLY_CORRECTION_REVIEW'
  | 'DISMISS_LOW_PRIORITY'
  | 'ESCALATE_CONFLICT'
  | 'MARK_NOT_COMPUTABLE';
export type ReviewUrgencyBand = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type ProviderComparisonMatrixStatus = 'COMPUTED' | 'UNDER_SAMPLED' | 'NOT_COMPUTABLE';

export interface ReviewSuggestionPacket {
  suggestion_id: string;
  review_id: string;
  target_type: ReviewSuggestionTargetType;
  target_id: string;
  suggestion_type: ReviewSuggestionType;
  priority_score: number;
  urgency_band: ReviewUrgencyBand;
  reason_codes: string[];
  explanation: string;
  required_evidence: string[];
  blocked_by: string[];
  created_at: string;
  authority: 'SUGGESTION_ONLY';
  provenance: OperatorDecisionProvenance;
  projection_only: true;
  outcome_resolution_authority: false;
  correction_application_authority: false;
  forecast_mutation_allowed: false;
  routing_mutation_allowed: false;
}

export interface ProviderComparisonMatrixProvider {
  provider_id: string;
  provider_name: string;
  reliability_score: number | null;
  trust_band: ProviderTrustBand;
  uptime_rate: number | null;
  error_rate: number | null;
  stale_rate: number | null;
  conflict_rate: number | null;
  correction_rate: number | null;
  median_latency_ms: number | null;
  provenance_completeness: number | null;
  observation_count: number;
  rank: number | null;
}

export interface ProviderComparisonMatrixPacket {
  matrix_id: string;
  window_start: string;
  window_end: string;
  providers: ProviderComparisonMatrixProvider[];
  matrix_status: ProviderComparisonMatrixStatus;
  computed_at: string;
  projection_only: true;
  descriptive_comparison_only: true;
  provider_removal_authority: false;
  outcome_truth_authority: false;
}

export interface ReviewSuggestionMatrixFrame {
  packet_type: 'AALVizReviewSuggestionMatrixFrame.v1';
  drop_name: 'AAL-Viz v7.6 — Automated Review Suggestions + Provider Comparison Matrix Code Drop';
  authority: 'ADVISORY_REVIEW_RECOMMENDATION_AND_SOURCE_COMPARISON_ONLY';
  mutation_policy: 'NO_EXECUTION_OUTCOME_FORECAST_SCORE_AUTHORITY_OR_ROUTING_MUTATION';
  projection_only: true;
  folded_versions: [
    'v6.1',
    'v6.2',
    'v6.3',
    'v6.4',
    'v6.5',
    'v6.6',
    'v6.7',
    'v6.8',
    'v6.9',
    'v7.0',
    'v7.1',
    'v7.2',
    'v7.3',
    'v7.4',
    'v7.5',
  ];
  features: [
    'review_suggestion_engine',
    'priority_score',
    'reason_codes',
    'required_evidence',
    'provider_comparison_matrix',
    'pairwise_conflict_grid',
    'source_redundancy_recommendations',
  ];
  suggestions: ReviewSuggestionPacket[];
  provider_matrix: ProviderComparisonMatrixPacket;
  suggestion_locks: {
    display_only: true;
    suggestion_only: true;
    provider_comparison_descriptive_only: true;
    notion_write_adapter_enabled: false;
    websocket_broadcast_enabled: false;
    autonomous_execution_allowed: false;
    outcome_resolution_allowed: false;
    correction_application_allowed: false;
    forecast_probability_mutation_allowed: false;
    score_mutation_allowed: false;
    strategy_routing_mutation_allowed: false;
    provider_removal_allowed: false;
    automatic_promotion_allowed: false;
    automatic_demotion_allowed: false;
    execution_authority: false;
    truth_authority: false;
    every_suggestion_has_reason_codes: true;
    every_suggestion_has_required_evidence: true;
    under_sampled_provider_shows_under_sampled: true;
  };
  provenance_hash: string;
}

export type OperatorWorkflowTargetType = ReviewSuggestionTargetType;
export type OperatorWorkflowStatus =
  | 'NEW'
  | 'TRIAGED'
  | 'EVIDENCE_REQUESTED'
  | 'READY_FOR_DECISION'
  | 'DECISION_DRAFTED'
  | 'COMMITTED'
  | 'ARCHIVED'
  | 'DISMISSED'
  | 'BLOCKED'
  | 'NOT_COMPUTABLE';
export type OperatorWorkflowActiveStep = 'TRIAGE' | 'EVIDENCE' | 'COMPARE' | 'DECIDE' | 'CORRECT' | 'COMMIT' | 'ARCHIVE';
export type OperatorWorkflowActionType =
  | 'OPEN'
  | 'TRIAGE'
  | 'REQUEST_EVIDENCE'
  | 'MARK_EVIDENCE_COMPLETE'
  | 'DRAFT_DECISION'
  | 'DRAFT_CORRECTION'
  | 'COMMIT_DECISION'
  | 'DISMISS'
  | 'BLOCK'
  | 'UNBLOCK'
  | 'ANNOTATE';

export interface OperatorWorkflowStatePacket {
  workflow_id: string;
  review_id: string;
  target_type: OperatorWorkflowTargetType;
  target_id: string;
  status: OperatorWorkflowStatus;
  active_step: OperatorWorkflowActiveStep;
  assigned_operator_id: string | null;
  priority_score: number;
  urgency_band: ReviewUrgencyBand;
  blockers: string[];
  required_evidence: string[];
  completed_evidence: string[];
  last_updated_at: string;
  provenance: OperatorDecisionProvenance;
  projection_only: true;
  review_state_management_only: true;
  commit_authority: false;
  outcome_mutation_allowed: false;
  forecast_mutation_allowed: false;
  score_mutation_allowed: false;
  routing_mutation_allowed: false;
}

export interface OperatorWorkflowActionPacket {
  action_id: string;
  workflow_id: string;
  operator_id: string;
  action_type: OperatorWorkflowActionType;
  created_at: string;
  payload_hash: string;
  rationale: string | null;
  authority: 'OPERATOR_WORKFLOW_LOG_ONLY';
  provenance: OperatorDecisionProvenance;
  append_only: true;
  external_execution_allowed: false;
  notion_write_allowed: false;
}

export interface OperatorWorkflowCommandCenterFrame {
  packet_type: 'AALVizOperatorWorkflowCommandCenterFrame.v1';
  drop_name: 'AAL-Viz v7.7 — Operator Workflow UI Code Drop';
  authority: 'WORKFLOW_GUIDANCE_REVIEW_STATE_AND_PROJECTION_ONLY';
  mutation_policy: 'NO_EXECUTION_OUTCOME_FORECAST_SCORE_PROVIDER_AUTHORITY_OR_ROUTING_MUTATION';
  projection_only: true;
  folded_versions: [
    'v6.1',
    'v6.2',
    'v6.3',
    'v6.4',
    'v6.5',
    'v6.6',
    'v6.7',
    'v6.8',
    'v6.9',
    'v7.0',
    'v7.1',
    'v7.2',
    'v7.3',
    'v7.4',
    'v7.5',
    'v7.6',
  ];
  features: [
    'workflow_inbox',
    'workflow_state_machine',
    'evidence_checklist',
    'provider_side_panel',
    'decision_composer',
    'correction_composer',
    'audit_preview',
    'workflow_timeline',
    'keyboard_command_bar',
    'notion_context_panel',
  ];
  workflows: OperatorWorkflowStatePacket[];
  actions: OperatorWorkflowActionPacket[];
  status_transitions: Record<OperatorWorkflowStatus, OperatorWorkflowStatus[]>;
  ui_zones: {
    left_rail: string;
    center_panel: string;
    right_panel: string;
    bottom_timeline: string;
    command_bar: string;
    field_overlay: string;
  };
  workflow_locks: {
    display_only: true;
    workflow_guidance_only: true;
    review_state_management_only: true;
    append_only_actions: true;
    audit_preview_required_before_commit: true;
    evidence_completion_is_not_truth_validation: true;
    notion_deep_links_context_only: true;
    accessibility_static_review_mode: true;
    notion_write_adapter_enabled: false;
    websocket_live_updates_enabled: false;
    autonomous_execution_allowed: false;
    external_action_execution_allowed: false;
    outcome_mutation_allowed: false;
    correction_application_allowed: false;
    forecast_probability_mutation_allowed: false;
    score_mutation_allowed: false;
    provider_authority_mutation_allowed: false;
    strategy_routing_mutation_allowed: false;
    truth_authority: false;
  };
  provenance_hash: string;
}

export type WorkflowAnalyticsStatus = 'COMPUTED' | 'UNDER_SAMPLED' | 'NOT_COMPUTABLE';
export type WorkflowBottleneckStep = OperatorWorkflowActiveStep | 'NONE' | 'NOT_COMPUTABLE';

export interface WorkflowAnalyticsPacket {
  analytics_id: string;
  window_start: string;
  window_end: string;
  workflow_count: number;
  completed_count: number;
  blocked_count: number;
  dismissed_count: number;
  not_computable_count: number;
  mean_time_to_triage_ms: number | null;
  mean_time_to_decision_ms: number | null;
  mean_time_to_commit_ms: number | null;
  bottleneck_step: WorkflowBottleneckStep;
  suggestion_acceptance_rate: number | null;
  correction_rate: number | null;
  stale_review_rate: number | null;
  analytics_status: WorkflowAnalyticsStatus;
  computed_at: string;
  projection_only: true;
  descriptive_only: true;
  promotion_authority: false;
  routing_mutation_allowed: false;
}

export interface OperatorPerformancePacket {
  performance_id: string;
  operator_id: string;
  window_start: string;
  window_end: string;
  decision_count: number;
  reviewed_count: number;
  override_count: number;
  correction_count: number;
  mean_decision_quality_score: number | null;
  positive_decision_rate: number | null;
  negative_decision_rate: number | null;
  neutral_decision_rate: number | null;
  pending_decision_rate: number | null;
  evidence_completion_rate: number | null;
  mean_review_latency_ms: number | null;
  operator_calibration_error: number | null;
  performance_status: WorkflowAnalyticsStatus;
  computed_at: string;
  feedback_only: true;
  rank_authority: false;
  truth_authority: false;
}

export interface WorkflowOperatorAnalyticsFrame {
  packet_type: 'AALVizWorkflowOperatorAnalyticsFrame.v1';
  drop_name: 'AAL-Viz v7.8 — Workflow Analytics + Operator Performance Tracking Code Drop';
  authority: 'DESCRIPTIVE_WORKFLOW_AND_OPERATOR_FEEDBACK_ONLY';
  mutation_policy: 'NO_EXECUTION_OUTCOME_FORECAST_SCORE_PROVIDER_AUTHORITY_OR_ROUTING_MUTATION';
  projection_only: true;
  folded_versions: [
    'v6.1',
    'v6.2',
    'v6.3',
    'v6.4',
    'v6.5',
    'v6.6',
    'v6.7',
    'v6.8',
    'v6.9',
    'v7.0',
    'v7.1',
    'v7.2',
    'v7.3',
    'v7.4',
    'v7.5',
    'v7.6',
    'v7.7',
  ];
  features: [
    'workflow_analytics',
    'workflow_bottleneck_detection',
    'review_aging',
    'suggestion_effectiveness',
    'operator_performance_tracking',
    'operator_calibration_profile',
    'override_outcome_tracking',
    'correction_quality_tracking',
  ];
  workflow_analytics: WorkflowAnalyticsPacket;
  operator_performance: OperatorPerformancePacket[];
  visual_mapping: {
    workflow_bottleneck: string;
    stale_review_growth: string;
    high_suggestion_acceptance: string;
    low_suggestion_acceptance: string;
    positive_operator_trend: string;
    negative_operator_trend: string;
    under_sampled_operator: string;
    not_computable_operator: string;
  };
  analytics_locks: {
    display_only: true;
    descriptive_analytics_only: true;
    operator_feedback_only: true;
    windowed_and_timestamped: true;
    pending_decisions_not_scored_positive_or_negative: true;
    low_sample_size_renders_under_sampled: true;
    missing_outcomes_render_not_computable: true;
    prior_and_corrected_hashes_preserved: true;
    notion_write_adapter_enabled: false;
    websocket_broadcast_enabled: false;
    autonomous_execution_allowed: false;
    promotion_allowed: false;
    outcome_mutation_allowed: false;
    forecast_probability_mutation_allowed: false;
    score_mutation_allowed: false;
    provider_authority_mutation_allowed: false;
    strategy_routing_mutation_allowed: false;
    operator_rank_authority: false;
    truth_authority: false;
  };
  provenance_hash: string;
}

export type AnalyticsNarrativeType =
  | 'DAILY_BRIEF'
  | 'WEEKLY_REVIEW'
  | 'WORKFLOW_SUMMARY'
  | 'OPERATOR_SUMMARY'
  | 'PROVIDER_SUMMARY'
  | 'CALIBRATION_SUMMARY'
  | 'ATTRIBUTION_SUMMARY'
  | 'ALERT_SUMMARY';
export type AnalyticsNarrativeProvenance = 'OBSERVED' | 'INFERRED' | 'NOT_COMPUTABLE';
export type AnalyticsNarrativeSeverityBand = 'INFO' | 'WATCH' | 'WARNING' | 'CRITICAL';
export type NarrativeTemplateInputMetricType =
  | 'WORKFLOW'
  | 'OPERATOR'
  | 'PROVIDER'
  | 'CALIBRATION'
  | 'ATTRIBUTION'
  | 'REVIEW'
  | 'OUTCOME';
export type NarrativeTemplateOutputBlockType = 'HEADLINE' | 'FINDING' | 'WARNING' | 'GAP' | 'REVIEW_PROMPT' | 'SUMMARY';

export interface AnalyticsNarrativeFinding {
  finding_id: string;
  label: string;
  claim: string;
  provenance: AnalyticsNarrativeProvenance;
  confidence: number;
  source_metric_ids: string[];
  why_it_matters: string;
}

export interface AnalyticsNarrativePacket {
  narrative_id: string;
  window_start: string;
  window_end: string;
  source_packet_ids: string[];
  narrative_type: AnalyticsNarrativeType;
  headline: string;
  summary: string;
  key_findings: AnalyticsNarrativeFinding[];
  recommended_review_items: string[];
  not_computable_items: string[];
  severity_band: AnalyticsNarrativeSeverityBand;
  generated_at: string;
  authority: 'NARRATIVE_COMPRESSION_ONLY';
  projection_only: true;
  creates_new_facts: false;
  recommendations_review_prompts_only: true;
  execution_allowed: false;
  outcome_resolution_allowed: false;
  forecast_mutation_allowed: false;
  promotion_allowed: false;
}

export interface NarrativeTemplateRule {
  template_id: string;
  input_metric_type: NarrativeTemplateInputMetricType;
  trigger_condition: string;
  output_block_type: NarrativeTemplateOutputBlockType;
  wording_rule: string;
  provenance_rule: AnalyticsNarrativeProvenance;
  confidence_rule: string;
}

export interface AnalyticsNarrativeSummaryFrame {
  packet_type: 'AALVizAnalyticsNarrativeSummaryFrame.v1';
  drop_name: 'AAL-Viz v7.9 — Analytics Narrative Summary Engine Code Drop';
  authority: 'NARRATIVE_COMPRESSION_AND_PROJECTION_ONLY';
  mutation_policy: 'NO_EXECUTION_OUTCOME_FORECAST_SCORE_PROVIDER_AUTHORITY_OR_ROUTING_MUTATION';
  projection_only: true;
  folded_versions: [
    'v6.1',
    'v6.2',
    'v6.3',
    'v6.4',
    'v6.5',
    'v6.6',
    'v6.7',
    'v6.8',
    'v6.9',
    'v7.0',
    'v7.1',
    'v7.2',
    'v7.3',
    'v7.4',
    'v7.5',
    'v7.6',
    'v7.7',
    'v7.8',
  ];
  features: [
    'analytics_narrative_packet',
    'metric_to_story_compiler',
    'deterministic_insight_templates',
    'provenance_labeled_findings',
    'narrative_gap_detection',
    'review_prompt_selection',
    'briefing_card_surface',
  ];
  narrative_packet: AnalyticsNarrativePacket;
  template_rules: NarrativeTemplateRule[];
  generation_flow: [
    'analytics_packets',
    'metric_normalization',
    'template_rule_matching',
    'finding_generation',
    'provenance_labeling',
    'confidence_severity_assignment',
    'gap_detection',
    'narrative_packet_creation',
    'projection_only_briefing_surface',
  ];
  narrative_locks: {
    display_only: true;
    narrative_compression_only: true;
    no_new_facts_created: true;
    every_finding_has_source_metric_ids: true;
    unsupported_claims_render_not_computable: true;
    inferred_claims_labeled_inferred: true;
    confidence_capped_by_evidence_class: true;
    recommendations_review_prompts_only: true;
    missing_metrics_render_as_gaps: true;
    operator_summaries_descriptive_only: true;
    notion_write_adapter_enabled: false;
    websocket_broadcast_enabled: false;
    autonomous_execution_allowed: false;
    outcome_resolution_allowed: false;
    forecast_probability_mutation_allowed: false;
    score_mutation_allowed: false;
    provider_authority_mutation_allowed: false;
    strategy_routing_mutation_allowed: false;
    promotion_allowed: false;
    truth_authority: false;
  };
  provenance_hash: string;
}

export type CinematicBriefingCameraMode =
  | 'ESTABLISHING'
  | 'FOCUS_FINDING'
  | 'PAN_GAP'
  | 'REVIEW_PROMPT'
  | 'LOCKED_GAP';

export interface CinematicBriefingStoryBlock {
  block_id: string;
  source_finding_id: string;
  title: string;
  narration: string;
  camera_cue: string;
  provenance: AnalyticsNarrativeProvenance;
  confidence: number;
  source_metric_ids: string[];
  severity_band: AnalyticsNarrativeSeverityBand;
}

export interface NarrativeCameraPathSegment {
  segment_id: string;
  target_block_id: string;
  camera_mode: CinematicBriefingCameraMode;
  duration_ms: number;
  focus_label: string;
  easing: 'LINEAR' | 'EASE_IN_OUT';
  authority: 'VISUAL_PROJECTION_ONLY';
}

export interface OperatorCoachingSuggestion {
  suggestion_id: string;
  source_finding_id: string;
  prompt: string;
  rationale: string;
  provenance: AnalyticsNarrativeProvenance;
  review_only: true;
  rank_authority: false;
  execution_allowed: false;
}

export interface BriefingExportSnapshot {
  snapshot_id: string;
  label: string;
  included_block_ids: string[];
  format: 'STATIC_CARD' | 'JSON_PREVIEW' | 'SCRIPT_TEXT';
  export_authority: 'DISPLAY_ONLY';
  file_write_allowed: false;
}

export interface CinematicBriefingFrame {
  packet_type: 'AALVizCinematicBriefingFrame.v1';
  drop_name: 'AAL-Viz v8.0 — Cinematic Briefing Generator + Narrative Camera Paths';
  authority: 'CINEMATIC_BRIEFING_PROJECTION_ONLY';
  mutation_policy: 'NO_EXECUTION_EXPORT_WRITEBACK_OUTCOME_FORECAST_SCORE_PROVIDER_AUTHORITY_OR_ROUTING_MUTATION';
  projection_only: true;
  folded_versions: [
    'v6.1',
    'v6.2',
    'v6.3',
    'v6.4',
    'v6.5',
    'v6.6',
    'v6.7',
    'v6.8',
    'v6.9',
    'v7.0',
    'v7.1',
    'v7.2',
    'v7.3',
    'v7.4',
    'v7.5',
    'v7.6',
    'v7.7',
    'v7.8',
    'v7.9',
  ];
  features: [
    'cinematic_briefing_generator',
    'narrative_to_camera_path_compiler',
    'analytics_story_blocks',
    'operator_coaching_suggestions',
    'briefing_export_snapshots',
    'voiceover_script_export_option',
  ];
  source_narrative_id: string;
  story_blocks: CinematicBriefingStoryBlock[];
  camera_path: NarrativeCameraPathSegment[];
  operator_coaching_suggestions: OperatorCoachingSuggestion[];
  export_snapshots: BriefingExportSnapshot[];
  voiceover_script_lines: string[];
  briefing_locks: {
    display_only: true;
    source_narrative_required: true;
    story_blocks_create_new_facts: false;
    camera_paths_visual_projection_only: true;
    coaching_suggestions_review_only: true;
    snapshot_export_writes_files: false;
    voiceover_export_writes_files: false;
    notion_write_adapter_enabled: false;
    websocket_broadcast_enabled: false;
    autonomous_execution_allowed: false;
    outcome_resolution_allowed: false;
    forecast_probability_mutation_allowed: false;
    score_mutation_allowed: false;
    provider_authority_mutation_allowed: false;
    strategy_routing_mutation_allowed: false;
    operator_rank_authority: false;
    promotion_allowed: false;
    truth_authority: false;
  };
  provenance_hash: string;
}

export interface SignalWeatherMetrics {
  ready_count: number;
  partial_count: number;
  fail_closed_count: number;
  not_computable_count: number;
  average_completion: number;
  high_risk_count: number;
}

export interface PacketAuthority {
  execution_allowed: false;
  runtime_mutation_allowed: false;
  promotion_allowed: false;
  production_activation_allowed: false;
  metric_emission_allowed: false;
  forecast_influence_allowed: false;
  p43_lanes_allowed: false;
}

export interface OperatorActionPacket {
  packet_id: string;
  source_frontier_ref: string | null;
  action_title: string;
  action_type: ActionType;
  operator_id?: string;
  subsystem_id?: string;
  recommended_next_step: string;
  authority_required: string;
  allowed: boolean;
  execution_allowed: false;
  runtime_mutation_allowed: false;
  promotion_allowed: false;
  prompt_body: string;
  validation_checklist: string[];
  blocked_scopes: string[];
  provenance_refs: string[];
  fail_closed_reason: string | null;
}

export interface OperatorActionPacketsBundle {
  schema_version: 'AALViz.OperatorActionPackets.v0.1';
  generated_at: string;
  authority: PacketAuthority;
  source_projection_bundle_hash: string | null;
  packets: OperatorActionPacket[];
  fail_closed_reason: string | null;
}
