export type SystemStatus = 'READY' | 'PARTIAL' | 'FAIL_CLOSED' | 'NOT_COMPUTABLE';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type QueueItemStatus = 'PENDING' | 'REVIEWED' | 'DEFERRED';
export type SourceMode = 'LIVE_ARTIFACT_BUNDLE' | 'SAMPLE_FALLBACK' | 'FAIL_CLOSED';
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

export interface LiveConsoleProjectionBundle {
  schema_version: 'AALViz.LiveConsoleProjectionBundle.v0.1';
  generated_at: string;
  authority: Authority;
  systems: SystemProjection[];
  operator_queue: OperatorQueueItem[];
  source_mode?: SourceMode;
  source_artifacts?: string[];
  fail_closed_reason?: string | null;
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
