export type SystemStatus = 'READY' | 'PARTIAL' | 'FAIL_CLOSED' | 'NOT_COMPUTABLE';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type QueueItemStatus = 'PENDING' | 'REVIEWED' | 'DEFERRED';

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
}

export interface SignalWeatherMetrics {
  ready_count: number;
  partial_count: number;
  fail_closed_count: number;
  not_computable_count: number;
  average_completion: number;
  high_risk_count: number;
}
