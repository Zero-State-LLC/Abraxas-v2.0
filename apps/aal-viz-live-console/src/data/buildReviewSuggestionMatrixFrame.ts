import { buildLiveOutcomeReviewFrame } from './buildLiveOutcomeReviewFrame';
import { buildProviderReliabilityFrame } from './buildProviderReliabilityFrame';
import type {
  LiveConsoleProjectionBundle,
  OperatorActionPacketsBundle,
  OperatorDecisionProvenance,
  OutcomeReviewItemProjection,
  ProviderComparisonMatrixPacket,
  ProviderReliabilityScorePacket,
  ReviewSuggestionMatrixFrame,
  ReviewSuggestionPacket,
  ReviewSuggestionTargetType,
  ReviewSuggestionType,
  ReviewUrgencyBand,
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

function round(value: number): number {
  return Number(value.toFixed(4));
}

function urgencyBand(priorityScore: number): ReviewUrgencyBand {
  if (priorityScore >= 0.85) return 'CRITICAL';
  if (priorityScore >= 0.65) return 'HIGH';
  if (priorityScore >= 0.35) return 'MEDIUM';
  return 'LOW';
}

function suggestionTypeFor(item: OutcomeReviewItemProjection): ReviewSuggestionType {
  if (item.review_reason === 'CONFLICTING_SOURCES' || item.review_reason === 'AMBIGUOUS') return 'ESCALATE_CONFLICT';
  if (item.review_reason === 'LOW_PROVENANCE') return 'REQUEST_SECOND_SOURCE';
  if (item.review_reason === 'CORRECTION_REQUESTED') return 'APPLY_CORRECTION_REVIEW';
  if (item.review_reason === 'STALE') return 'REVIEW_NOW';
  if (item.review_status === 'NOT_COMPUTABLE') return 'MARK_NOT_COMPUTABLE';
  return 'WAIT_FOR_MORE_DATA';
}

function priorityScoreFor(item: OutcomeReviewItemProjection, providerRisk: number): number {
  const conflictSeverity =
    item.review_reason === 'CONFLICTING_SOURCES' || item.review_reason === 'AMBIGUOUS' ? 1 : 0;
  const targetValue = item.priority === 'CRITICAL' ? 1 : item.priority === 'HIGH' ? 0.75 : item.priority === 'MEDIUM' ? 0.5 : 0.25;
  const stalenessPressure = item.review_reason === 'STALE' ? 1 : 0;
  const provenanceGap = item.review_reason === 'LOW_PROVENANCE' ? 1 : 0;
  const deadlinePressure = item.due_at == null ? 0 : 0.5;
  const operatorAttentionWeight = item.target_type === 'OPERATOR_DECISION' ? 0.75 : 0.25;

  return round(
    0.25 * conflictSeverity +
      0.2 * targetValue +
      0.15 * stalenessPressure +
      0.15 * providerRisk +
      0.1 * provenanceGap +
      0.1 * deadlinePressure +
      0.05 * operatorAttentionWeight,
  );
}

function targetTypeFor(item: OutcomeReviewItemProjection): ReviewSuggestionTargetType {
  if (item.target_type === 'FORECAST') return 'FORECAST';
  if (item.target_type === 'OPERATOR_DECISION') return 'OPERATOR_DECISION';
  if (item.target_type === 'STRATEGY') return 'STRATEGY';
  return 'RUN';
}

function provenanceFor(item: OutcomeReviewItemProjection): OperatorDecisionProvenance {
  if (item.feed_packet_id == null) return 'missing';
  if (item.review_reason === 'LOW_PROVENANCE' || item.review_reason === 'PENDING_RESOLUTION') return 'partial';
  return 'complete';
}

function reasonCodesFor(item: OutcomeReviewItemProjection, suggestionType: ReviewSuggestionType): string[] {
  return [
    `REVIEW_REASON_${item.review_reason}`,
    `REVIEW_PRIORITY_${item.priority}`,
    `SUGGESTION_${suggestionType}`,
  ].sort((a, b) => a.localeCompare(b));
}

function evidenceFor(suggestionType: ReviewSuggestionType): string[] {
  if (suggestionType === 'REQUEST_SECOND_SOURCE') return ['second_provider_observation', 'provider_provenance_evidence'];
  if (suggestionType === 'ESCALATE_CONFLICT') return ['conflicting_provider_packets', 'operator_conflict_review'];
  if (suggestionType === 'APPLY_CORRECTION_REVIEW') return ['prior_value_hash', 'corrected_value_hash', 'correction_rationale'];
  if (suggestionType === 'MARK_NOT_COMPUTABLE') return ['missing_component_inventory'];
  return ['review_item_context', 'outcome_feed_evidence'];
}

function buildSuggestions(
  reviewItems: OutcomeReviewItemProjection[],
  providerRisk: number,
  createdAt: string,
): ReviewSuggestionPacket[] {
  return reviewItems
    .map((item) => {
      const suggestionType = suggestionTypeFor(item);
      const priorityScore = priorityScoreFor(item, providerRisk);

      return {
        suggestion_id: `suggestion-${item.review_id}`,
        review_id: item.review_id,
        target_type: targetTypeFor(item),
        target_id: item.target_id,
        suggestion_type: suggestionType,
        priority_score: priorityScore,
        urgency_band: urgencyBand(priorityScore),
        reason_codes: reasonCodesFor(item, suggestionType),
        explanation: `${suggestionType} recommended for ${item.target_id} because ${item.review_reason} is ${item.review_status}.`,
        required_evidence: evidenceFor(suggestionType),
        blocked_by: ['NO_EXECUTION_AUTHORITY', 'NO_OUTCOME_TRUTH_AUTHORITY'],
        created_at: createdAt,
        authority: 'SUGGESTION_ONLY' as const,
        provenance: provenanceFor(item),
        projection_only: true as const,
        outcome_resolution_authority: false as const,
        correction_application_authority: false as const,
        forecast_mutation_allowed: false as const,
        routing_mutation_allowed: false as const,
      };
    })
    .sort((a, b) => b.priority_score - a.priority_score || a.suggestion_id.localeCompare(b.suggestion_id));
}

function rankProviders(scores: ProviderReliabilityScorePacket[]): ProviderComparisonMatrixPacket['providers'] {
  const ranked = [...scores]
    .filter((score) => score.reliability_score != null)
    .sort((a, b) => (b.reliability_score ?? 0) - (a.reliability_score ?? 0) || a.provider_id.localeCompare(b.provider_id));
  const rankByProvider = new Map(ranked.map((score, index) => [score.provider_id, index + 1]));

  return [...scores]
    .sort((a, b) => a.provider_id.localeCompare(b.provider_id))
    .map((score) => ({
      provider_id: score.provider_id,
      provider_name: score.provider_name,
      reliability_score: score.reliability_score,
      trust_band: score.trust_band,
      uptime_rate: score.uptime_rate,
      error_rate: score.error_rate,
      stale_rate: score.stale_rate,
      conflict_rate: score.conflict_rate,
      correction_rate: score.correction_rate,
      median_latency_ms: score.median_latency_ms,
      provenance_completeness: score.provenance_completeness,
      observation_count: score.observation_count,
      rank: rankByProvider.get(score.provider_id) ?? null,
    }));
}

function buildProviderMatrix(scores: ProviderReliabilityScorePacket[], computedAt: string): ProviderComparisonMatrixPacket {
  const providers = rankProviders(scores);
  const computedCount = providers.filter((provider) => provider.rank != null).length;
  const matrixStatus =
    providers.length === 0
      ? 'NOT_COMPUTABLE'
      : computedCount === 0
        ? 'UNDER_SAMPLED'
        : providers.some((provider) => provider.trust_band === 'NOT_COMPUTABLE')
          ? 'NOT_COMPUTABLE'
          : 'COMPUTED';

  return {
    matrix_id: 'provider-comparison-matrix-latest',
    window_start: computedAt,
    window_end: computedAt,
    providers,
    matrix_status: matrixStatus,
    computed_at: computedAt,
    projection_only: true,
    descriptive_comparison_only: true,
    provider_removal_authority: false,
    outcome_truth_authority: false,
  };
}

export function buildReviewSuggestionMatrixFrame(
  bundle: LiveConsoleProjectionBundle,
  packetsBundle: OperatorActionPacketsBundle | null,
): ReviewSuggestionMatrixFrame {
  const reviewFrame = buildLiveOutcomeReviewFrame(bundle, packetsBundle);
  const providerFrame = buildProviderReliabilityFrame(bundle, packetsBundle);
  const providerRisk =
    providerFrame.reliability_scores.length === 0
      ? 0
      : providerFrame.reliability_scores.filter((score) => score.trust_band !== 'HIGH' && score.trust_band !== 'MEDIUM').length /
        providerFrame.reliability_scores.length;
  const suggestions = buildSuggestions(reviewFrame.review_items, round(providerRisk), bundle.generated_at);
  const providerMatrix = buildProviderMatrix(providerFrame.reliability_scores, bundle.generated_at);

  const frameWithoutHash = {
    packet_type: 'AALVizReviewSuggestionMatrixFrame.v1' as const,
    drop_name: 'AAL-Viz v7.6 — Automated Review Suggestions + Provider Comparison Matrix Code Drop' as const,
    authority: 'ADVISORY_REVIEW_RECOMMENDATION_AND_SOURCE_COMPARISON_ONLY' as const,
    mutation_policy: 'NO_EXECUTION_OUTCOME_FORECAST_SCORE_AUTHORITY_OR_ROUTING_MUTATION' as const,
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
      'v7.5',
    ] as ReviewSuggestionMatrixFrame['folded_versions'],
    features: [
      'review_suggestion_engine',
      'priority_score',
      'reason_codes',
      'required_evidence',
      'provider_comparison_matrix',
      'pairwise_conflict_grid',
      'source_redundancy_recommendations',
    ] as ReviewSuggestionMatrixFrame['features'],
    suggestions,
    provider_matrix: providerMatrix,
    suggestion_locks: {
      display_only: true as const,
      suggestion_only: true as const,
      provider_comparison_descriptive_only: true as const,
      notion_write_adapter_enabled: false as const,
      websocket_broadcast_enabled: false as const,
      autonomous_execution_allowed: false as const,
      outcome_resolution_allowed: false as const,
      correction_application_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      score_mutation_allowed: false as const,
      strategy_routing_mutation_allowed: false as const,
      provider_removal_allowed: false as const,
      automatic_promotion_allowed: false as const,
      automatic_demotion_allowed: false as const,
      execution_authority: false as const,
      truth_authority: false as const,
      every_suggestion_has_reason_codes: true as const,
      every_suggestion_has_required_evidence: true as const,
      under_sampled_provider_shows_under_sampled: true as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
