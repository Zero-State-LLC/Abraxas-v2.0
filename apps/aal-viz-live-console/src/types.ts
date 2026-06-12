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
