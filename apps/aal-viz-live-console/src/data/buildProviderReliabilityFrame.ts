import { buildLiveOutcomeReviewFrame } from './buildLiveOutcomeReviewFrame';
import type {
  LiveConsoleProjectionBundle,
  LiveOutcomeFeedPacket,
  OperatorActionPacketsBundle,
  OperatorDecisionProvenance,
  OutcomeReviewItemProjection,
  ProviderConflictPacket,
  ProviderObservationPacket,
  ProviderObservationStatus,
  ProviderReliabilityFrame,
  ProviderReliabilityScorePacket,
  ProviderTrustBand,
} from '../types';

const MINIMUM_WINDOW_COUNT = 3;

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

function round(value: number): number {
  return Number(value.toFixed(4));
}

function observationStatus(packet: LiveOutcomeFeedPacket): ProviderObservationStatus {
  if (packet.normalized_status === 'ERROR') return 'ERROR';
  if (packet.normalized_status === 'AMBIGUOUS') return 'AMBIGUOUS';
  if (packet.normalized_status === 'CANCELLED') return 'STALE';
  if (packet.provenance === 'missing') return 'STALE';
  return 'OK';
}

function buildObservation(packet: LiveOutcomeFeedPacket): ProviderObservationPacket {
  return {
    observation_id: `provider-observation-${packet.provider}-${packet.provider_event_id}`,
    provider_id: packet.provider,
    provider_name: packet.provider,
    captured_at: packet.captured_at,
    endpoint: packet.source_url,
    event_id: packet.provider_event_id,
    status: observationStatus(packet),
    latency_ms: null,
    payload_hash: packet.raw_payload_hash,
    provenance: packet.provenance,
    projection_only: true,
    provider_score_only: true,
    forecast_mutation_allowed: false,
    outcome_truth_authority: false,
  };
}

function rate(count: number, total: number): number | null {
  return total === 0 ? null : round(count / total);
}

function trustBand(observationCount: number, reliabilityScore: number | null): ProviderTrustBand {
  if (observationCount < MINIMUM_WINDOW_COUNT) return 'UNDER_SAMPLED';
  if (reliabilityScore == null) return 'NOT_COMPUTABLE';
  if (reliabilityScore >= 0.85) return 'HIGH';
  if (reliabilityScore >= 0.65) return 'MEDIUM';
  return 'LOW';
}

function reliabilityScoreFor(
  uptimeRate: number | null,
  provenanceCompleteness: number | null,
  staleRate: number | null,
  conflictRate: number | null,
  correctionRate: number | null,
): number | null {
  if (
    uptimeRate == null ||
    provenanceCompleteness == null ||
    staleRate == null ||
    conflictRate == null ||
    correctionRate == null
  ) {
    return null;
  }
  const freshnessScore = 1 - staleRate;
  const consistencyScore = 1 - conflictRate;
  const latencyScore = 0.5;
  const correctionStabilityScore = 1 - correctionRate;
  const conflictStabilityScore = 1 - conflictRate;

  return round(
    0.25 * uptimeRate +
      0.2 * provenanceCompleteness +
      0.15 * freshnessScore +
      0.15 * consistencyScore +
      0.1 * latencyScore +
      0.1 * correctionStabilityScore +
      0.05 * conflictStabilityScore,
  );
}

function buildReliabilityScores(
  observations: ProviderObservationPacket[],
  conflicts: ProviderConflictPacket[],
  computedAt: string,
): ProviderReliabilityScorePacket[] {
  const observationsByProvider = new Map<string, ProviderObservationPacket[]>();
  for (const observation of observations) {
    const existing = observationsByProvider.get(observation.provider_id) ?? [];
    existing.push(observation);
    observationsByProvider.set(observation.provider_id, existing);
  }

  return [...observationsByProvider.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([providerId, providerObservations]) => {
      const total = providerObservations.length;
      const errorCount = providerObservations.filter((observation) => observation.status === 'ERROR').length;
      const staleCount = providerObservations.filter((observation) => observation.status === 'STALE').length;
      const completeCount = providerObservations.filter((observation) => observation.provenance === 'complete').length;
      const providerConflictCount = conflicts.filter((conflict) => conflict.provider_ids.includes(providerId)).length;
      const uptimeRate = rate(total - errorCount, total);
      const errorRate = rate(errorCount, total);
      const staleRate = rate(staleCount, total);
      const conflictRate = rate(providerConflictCount, total);
      const correctionRate = 0;
      const provenanceCompleteness = rate(completeCount, total);
      const reliabilityScore = reliabilityScoreFor(
        uptimeRate,
        provenanceCompleteness,
        staleRate,
        conflictRate,
        correctionRate,
      );

      return {
        score_id: `provider-score-${providerId}`,
        provider_id: providerId,
        provider_name: providerObservations[0]?.provider_name ?? providerId,
        window_start: providerObservations[0]?.captured_at ?? computedAt,
        window_end: providerObservations[providerObservations.length - 1]?.captured_at ?? computedAt,
        observation_count: total,
        uptime_rate: uptimeRate,
        error_rate: errorRate,
        stale_rate: staleRate,
        conflict_rate: conflictRate,
        correction_rate: correctionRate,
        median_latency_ms: null,
        provenance_completeness: provenanceCompleteness,
        reliability_score: total < MINIMUM_WINDOW_COUNT ? null : reliabilityScore,
        trust_band: trustBand(total, reliabilityScore),
        computed_at: computedAt,
        projection_only: true,
        review_priority_influence_only: true,
        forecast_probability_mutated: false,
        brier_score_mutated: false,
        outcome_truth_mutated: false,
      };
    });
}

function conflictProvenance(feedPackets: LiveOutcomeFeedPacket[]): OperatorDecisionProvenance {
  if (feedPackets.every((packet) => packet.provenance === 'complete')) return 'complete';
  if (feedPackets.every((packet) => packet.provenance === 'missing')) return 'missing';
  return 'partial';
}

function buildConflicts(
  feedPackets: LiveOutcomeFeedPacket[],
  reviewItems: OutcomeReviewItemProjection[],
  detectedAt: string,
): ProviderConflictPacket[] {
  const byEvent = new Map<string, LiveOutcomeFeedPacket[]>();
  for (const packet of feedPackets) {
    const existing = byEvent.get(packet.provider_event_id) ?? [];
    existing.push(packet);
    byEvent.set(packet.provider_event_id, existing);
  }

  return [...byEvent.entries()]
    .filter(([, packets]) => packets.length > 1)
    .filter(([, packets]) => {
      const resultSet = new Set(packets.map((packet) => String(packet.normalized_result)));
      const statusSet = new Set(packets.map((packet) => packet.normalized_status));
      return resultSet.size > 1 || statusSet.size > 1;
    })
    .map(([eventId, packets]): ProviderConflictPacket => {
      const conflictType: ProviderConflictPacket['conflict_type'] =
        new Set(packets.map((packet) => String(packet.normalized_result))).size > 1
          ? 'RESULT_MISMATCH'
          : 'STATUS_MISMATCH';

      return {
        conflict_id: `provider-conflict-${eventId}`,
        provider_ids: packets.map((packet) => packet.provider).sort((a, b) => a.localeCompare(b)),
        target_event_id: eventId,
        conflict_type: conflictType,
        detected_at: detectedAt,
        review_item_id:
          reviewItems.find((item) => item.target_id === eventId && item.review_reason === 'CONFLICTING_SOURCES')
            ?.review_id ?? null,
        provenance: conflictProvenance(packets),
        projection_only: true,
        creates_review_item_only: true,
        outcome_truth_authority: false,
      };
    })
    .sort((a, b) => a.conflict_id.localeCompare(b.conflict_id));
}

export function buildProviderReliabilityFrame(
  bundle: LiveConsoleProjectionBundle,
  packetsBundle: OperatorActionPacketsBundle | null,
): ProviderReliabilityFrame {
  const outcomeFrame = buildLiveOutcomeReviewFrame(bundle, packetsBundle);
  const observations = outcomeFrame.feed_packets.map((packet) => buildObservation(packet));
  const conflicts = buildConflicts(outcomeFrame.feed_packets, outcomeFrame.review_items, bundle.generated_at);
  const reliabilityScores = buildReliabilityScores(observations, conflicts, bundle.generated_at);

  const frameWithoutHash = {
    packet_type: 'AALVizProviderReliabilityFrame.v1' as const,
    drop_name: 'AAL-Viz v7.5 — Provider Reliability Scoring Code Drop' as const,
    authority: 'SOURCE_RELIABILITY_SCORING_AND_PROJECTION_ONLY' as const,
    mutation_policy: 'NO_FORECAST_OUTCOME_SCORE_AUTHORITY_OR_ROUTING_MUTATION' as const,
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
      'v7.4',
    ] as ProviderReliabilityFrame['folded_versions'],
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
    ] as ProviderReliabilityFrame['features'],
    minimum_window_count: MINIMUM_WINDOW_COUNT,
    observations,
    reliability_scores: reliabilityScores,
    conflicts,
    reliability_locks: {
      display_only: true as const,
      source_reliability_projection_only: true as const,
      provider_healthcheck_enabled: false as const,
      notion_write_adapter_enabled: false as const,
      websocket_broadcast_enabled: false as const,
      autonomous_execution_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      brier_score_mutation_allowed: false as const,
      outcome_truth_mutation_allowed: false as const,
      strategy_routing_mutation_allowed: false as const,
      automatic_promotion_allowed: false as const,
      automatic_demotion_allowed: false as const,
      execution_authority: false as const,
      truth_authority: false as const,
      low_trust_routes_to_review: true as const,
      under_sampled_routes_to_review_unless_corroborated: true as const,
      provider_reliability_visual_trust_only: true as const,
      corrections_preserve_previous_and_corrected_hashes: true as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
