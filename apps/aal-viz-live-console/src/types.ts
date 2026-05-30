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
