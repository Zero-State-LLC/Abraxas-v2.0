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
