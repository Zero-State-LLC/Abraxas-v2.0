import type {
  ActionType,
  DecisionAttributionStatus,
  DecisionEffect,
  OperatorActionPacket,
  OperatorActionPacketsBundle,
  OperatorDecisionOutcomeFrame,
  OperatorDecisionPacketProjection,
  OperatorDecisionProvenance,
  OperatorDecisionType,
} from '../types';

function stableStringify(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(',')}]`;
  }
  if (value !== null && typeof value === 'object') {
    return `{${Object.entries(value)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, item]) => `${JSON.stringify(key)}:${stableStringify(item)}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}

function stableUiHash(value: unknown): string {
  const input = stableStringify(value);
  let hash = 0x811c9dc5;
  for (let index = 0; index < input.length; index++) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return (hash >>> 0).toString(16).padStart(8, '0');
}

const DECISION_TYPE_BY_ACTION: Record<ActionType, OperatorDecisionType> = {
  COPY_PROMPT: 'WATCH',
  COPY_CHECKLIST: 'ANNOTATE',
  REVIEW_REQUIRED: 'ESCALATE',
};

function provenanceFor(packet: OperatorActionPacket): OperatorDecisionProvenance {
  if (!packet.allowed || packet.fail_closed_reason != null) return 'missing';
  if (packet.provenance_refs.length === 0) return 'partial';
  return 'partial';
}

function linkedIds(packet: OperatorActionPacket, marker: string): string[] {
  const markerUpper = marker.toUpperCase();
  return packet.provenance_refs
    .filter((ref) => ref.toUpperCase().includes(markerUpper))
    .sort((a, b) => a.localeCompare(b));
}

function buildDecision(packet: OperatorActionPacket, createdAt: string): OperatorDecisionPacketProjection {
  return {
    decision_id: `decision-${packet.packet_id}`,
    operator_id: packet.operator_id ?? 'OPERATOR_NOT_COMPUTABLE',
    created_at: createdAt,
    decision_type: DECISION_TYPE_BY_ACTION[packet.action_type],
    target_type: 'RUN',
    target_id: packet.source_frontier_ref ?? packet.subsystem_id ?? packet.packet_id,
    linked_forecast_ids: linkedIds(packet, 'forecast'),
    linked_strategy_ids: linkedIds(packet, 'strategy'),
    linked_signal_ids: linkedIds(packet, 'signal'),
    rationale: packet.prompt_body,
    confidence_at_decision: null,
    expected_result: packet.recommended_next_step,
    review_deadline: null,
    authority: 'OPERATOR_LOG_ONLY',
    provenance: provenanceFor(packet),
    projection_only: true,
    autonomous_execution_triggered: false,
    source_forecast_probability_mutated: false,
    source_score_mutated: false,
    authority_tier_mutated: false,
    strategy_routing_mutated: false,
  };
}

function buildOutcomeAttribution(
  decision: OperatorDecisionPacketProjection,
  computedAt: string,
): OperatorDecisionOutcomeFrame['outcome_attributions'][number] {
  const attributionStatus: DecisionAttributionStatus = 'PENDING';
  const decisionEffect: DecisionEffect = 'NOT_COMPUTABLE';

  return {
    attribution_id: `decision-outcome-${decision.decision_id}`,
    decision_id: decision.decision_id,
    target_id: decision.target_id,
    outcome_id: null,
    evaluation_window_start: decision.created_at,
    evaluation_window_end: computedAt,
    observed_result: null,
    decision_effect: decisionEffect,
    confidence_delta: null,
    brier_delta: null,
    contribution_score: null,
    attribution_status: attributionStatus,
    computed_at: computedAt,
    projection_only: true,
    decision_quality_score: null,
    source_forecast_probability_mutated: false,
    source_score_mutated: false,
    authority_tier_mutated: false,
    strategy_routing_mutated: false,
  };
}

export function buildOperatorDecisionOutcomeFrame(
  packetsBundle: OperatorActionPacketsBundle | null,
): OperatorDecisionOutcomeFrame {
  const computedAt = packetsBundle?.generated_at ?? 'NOT_COMPUTABLE';
  const packets = [...(packetsBundle?.packets ?? [])].sort((a, b) => a.packet_id.localeCompare(b.packet_id));
  const decisionPackets = packets.map((packet) => buildDecision(packet, computedAt));
  const outcomeAttributions = decisionPackets.map((decision) => buildOutcomeAttribution(decision, computedAt));

  const frameWithoutHash = {
    packet_type: 'AALVizOperatorDecisionOutcomeFrame.v1' as const,
    drop_name: 'AAL-Viz v7.3 — Operator Decision Packets + Outcome Attribution Code Drop' as const,
    authority: 'DESCRIPTIVE_DECISION_LOGGING_AND_PROJECTION_ONLY' as const,
    mutation_policy: 'NO_EXECUTION_FORECAST_SCORE_AUTHORITY_OR_ROUTING_MUTATION' as const,
    projection_only: true as const,
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
    ] as OperatorDecisionOutcomeFrame['folded_versions'],
    features: [
      'operator_decision_packet',
      'decision_outcome_attribution',
      'decision_quality_score',
      'operator_feedback_timeline',
      'decision_overlay_layer',
      'review_queue_panel',
      'correction_decision_support',
    ] as OperatorDecisionOutcomeFrame['features'],
    decision_packets: decisionPackets,
    outcome_attributions: outcomeAttributions,
    decision_locks: {
      display_only: true as const,
      descriptive_decision_logging_only: true as const,
      operator_log_only: true as const,
      notion_write_adapter_enabled: false as const,
      websocket_broadcast_enabled: false as const,
      autonomous_execution_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      score_mutation_allowed: false as const,
      authority_tier_mutation_allowed: false as const,
      strategy_routing_mutation_allowed: false as const,
      automatic_promotion_allowed: false as const,
      automatic_demotion_allowed: false as const,
      execution_authority: false as const,
      truth_authority: false as const,
      rationale_is_context_not_proof: true as const,
      correction_decisions_preserve_provenance: true as const,
      missing_outcome_renders_pending_or_not_computable: true as const,
      low_sample_size_renders_under_sampled: true as const,
      decision_quality_score_promotes_or_demotes: false as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
