import { buildOperatorDecisionOutcomeFrame } from './buildOperatorDecisionOutcomeFrame';
import type {
  LiveConsoleProjectionBundle,
  LiveOutcomeFeedPacket,
  LiveOutcomeReviewFrame,
  OperatorActionPacketsBundle,
  OutcomeReviewItemProjection,
  ProjectionPacket,
  SystemProjection,
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

function packetHash(value: unknown): string {
  return stableUiHash(value);
}

function outcomeCandidatePackets(bundle: LiveConsoleProjectionBundle): Array<{ system: SystemProjection; packet: ProjectionPacket }> {
  return bundle.systems
    .flatMap((system) =>
      system.projection_packets.map((packet) => ({
        system,
        packet,
      })),
    )
    .filter(({ packet }) => {
      const type = packet.packet_type.toUpperCase();
      const status = packet.status.toUpperCase();
      return type.includes('OUTCOME') || type.includes('RESOLUTION') || status.includes('RESOLVED');
    })
    .sort((a, b) => a.packet.packet_id.localeCompare(b.packet.packet_id));
}

function normalizeResult(packet: ProjectionPacket): 0 | 1 | null {
  if (packet.display_value === '0') return 0;
  if (packet.display_value === '1') return 1;
  return null;
}

function normalizeStatus(packet: ProjectionPacket): LiveOutcomeFeedPacket['normalized_status'] {
  const status = packet.status.toUpperCase();
  if (status.includes('ERROR')) return 'ERROR';
  if (status.includes('CANCEL')) return 'CANCELLED';
  if (status.includes('AMBIGUOUS') || status.includes('CONFLICT')) return 'AMBIGUOUS';
  if (status.includes('RESOLVED') || normalizeResult(packet) != null) return 'RESOLVED';
  return 'OPEN';
}

function buildFeedPacket(system: SystemProjection, packet: ProjectionPacket, capturedAt: string): LiveOutcomeFeedPacket {
  const normalizedStatus = normalizeStatus(packet);
  const normalizedResult = normalizedStatus === 'RESOLVED' ? normalizeResult(packet) : null;
  const provenance = packet.authority_source === '' || packet.authority_source === 'NOT_COMPUTABLE' ? 'missing' : 'partial';

  return {
    feed_packet_id: `feed-${packet.packet_id}`,
    provider: `AAL_VIZ_${system.system_id}`,
    provider_event_id: packet.packet_id,
    captured_at: capturedAt,
    source_url: null,
    raw_status: packet.status,
    raw_payload_hash: packetHash(packet),
    normalized_status: normalizedStatus,
    normalized_result: normalizedResult,
    confidence: normalizedStatus === 'RESOLVED' && provenance !== 'missing' ? 0.5 : 0,
    provenance,
    projection_only: true,
    candidate_resolution_only: true,
    final_truth_authority: false,
    source_forecast_probability_mutated: false,
    source_score_mutated: false,
    strategy_routing_mutated: false,
  };
}

function reviewReasonFor(feedPacket: LiveOutcomeFeedPacket | null): OutcomeReviewItemProjection['review_reason'] {
  if (feedPacket == null) return 'PENDING_RESOLUTION';
  if (feedPacket.provenance !== 'complete') return 'LOW_PROVENANCE';
  if (feedPacket.normalized_status === 'AMBIGUOUS') return 'AMBIGUOUS';
  if (feedPacket.normalized_status === 'ERROR') return 'CONFLICTING_SOURCES';
  return 'PENDING_RESOLUTION';
}

function priorityFor(reason: OutcomeReviewItemProjection['review_reason']): OutcomeReviewItemProjection['priority'] {
  if (reason === 'CONFLICTING_SOURCES' || reason === 'CORRECTION_REQUESTED') return 'CRITICAL';
  if (reason === 'AMBIGUOUS' || reason === 'LOW_PROVENANCE') return 'HIGH';
  if (reason === 'STALE') return 'MEDIUM';
  return 'LOW';
}

function buildReviewItem(
  targetType: OutcomeReviewItemProjection['target_type'],
  targetId: string,
  feedPacket: LiveOutcomeFeedPacket | null,
  createdAt: string,
): OutcomeReviewItemProjection {
  const reason = reviewReasonFor(feedPacket);

  return {
    review_id: `review-${targetType.toLowerCase()}-${targetId}`,
    target_type: targetType,
    target_id: targetId,
    feed_packet_id: feedPacket?.feed_packet_id ?? null,
    review_reason: reason,
    review_status: feedPacket?.normalized_status === 'RESOLVED' && feedPacket.provenance === 'complete' ? 'RESOLVED' : 'OPEN',
    priority: priorityFor(reason),
    created_at: createdAt,
    due_at: null,
    projection_only: true,
    review_decision_descriptive_only: true,
    outcome_resolution_authority: false,
  };
}

export function buildLiveOutcomeReviewFrame(
  bundle: LiveConsoleProjectionBundle,
  packetsBundle: OperatorActionPacketsBundle | null,
): LiveOutcomeReviewFrame {
  const computedAt = bundle.generated_at;
  const feedPackets = outcomeCandidatePackets(bundle).map(({ system, packet }) =>
    buildFeedPacket(system, packet, computedAt),
  );
  const feedByProviderEvent = new Map(feedPackets.map((packet) => [packet.provider_event_id, packet]));
  const decisionFrame = buildOperatorDecisionOutcomeFrame(packetsBundle);

  const forecastReviewItems = feedPackets.map((feedPacket) =>
    buildReviewItem('FORECAST', feedPacket.provider_event_id, feedPacket, computedAt),
  );
  const decisionReviewItems = decisionFrame.decision_packets.map((decision) =>
    buildReviewItem('OPERATOR_DECISION', decision.decision_id, feedByProviderEvent.get(decision.target_id) ?? null, computedAt),
  );
  const reviewItems = [...forecastReviewItems, ...decisionReviewItems].sort((a, b) =>
    a.review_id.localeCompare(b.review_id),
  );

  const frameWithoutHash = {
    packet_type: 'AALVizLiveOutcomeReviewFrame.v1' as const,
    drop_name: 'AAL-Viz v7.4 — Live Outcome Feeds + Decision Review Queue Code Drop' as const,
    authority: 'OUTCOME_INTAKE_REVIEW_AND_PROJECTION_ONLY' as const,
    mutation_policy: 'APPEND_ONLY_WITH_CORRECTION_PACKETS' as const,
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
      'v7.3',
    ] as LiveOutcomeReviewFrame['folded_versions'],
    features: [
      'live_outcome_adapter_interface',
      'forecast_outcome_resolver',
      'decision_review_queue',
      'pending_resolution_tracker',
      'stale_outcome_detector',
      'correction_packet_workflow',
      'outcome_feed_overlay',
    ] as LiveOutcomeReviewFrame['features'],
    feed_packets: feedPackets,
    review_items: reviewItems,
    correction_packets: [],
    review_locks: {
      display_only: true as const,
      candidate_resolution_only: true as const,
      append_only_with_correction_packets: true as const,
      provider_polling_enabled: false as const,
      notion_write_adapter_enabled: false as const,
      websocket_broadcast_enabled: false as const,
      autonomous_execution_allowed: false as const,
      outcome_resolution_without_review_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      score_mutation_allowed: false as const,
      authority_tier_mutation_allowed: false as const,
      strategy_routing_mutation_allowed: false as const,
      automatic_promotion_allowed: false as const,
      execution_authority: false as const,
      truth_authority: false as const,
      ambiguous_or_conflicting_routes_to_review: true as const,
      low_provenance_routes_to_review: true as const,
      stale_pending_routes_to_review: true as const,
      corrections_preserve_previous_and_corrected_hashes: true as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
