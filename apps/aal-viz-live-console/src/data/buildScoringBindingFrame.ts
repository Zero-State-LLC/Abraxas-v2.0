import type {
  CalibrationSummaryProjection,
  ForecastOutcomeJoinState,
  LiveConsoleProjectionBundle,
  ProjectionPacket,
  ScoringBindingFrame,
  ScoringBindingRecord,
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

function packetLooksLikeForecast(packet: ProjectionPacket): boolean {
  return packet.packet_type.includes('FORECAST') || packet.packet_type.includes('CLAIM');
}

function packetLooksLikeOutcome(packet: ProjectionPacket): boolean {
  return packet.packet_type.includes('OUTCOME') || packet.packet_type.includes('RESOLUTION');
}

function probabilityFromPacket(packet: ProjectionPacket): number | null {
  if (!packetLooksLikeForecast(packet) || packet.display_value == null) return null;
  const value = Number(packet.display_value);
  return Number.isFinite(value) && value >= 0 && value <= 1 ? value : null;
}

function outcomeFromPacket(packet: ProjectionPacket): 0 | 1 | null {
  if (!packetLooksLikeOutcome(packet) || packet.display_value == null) return null;
  if (packet.display_value === '1' || packet.display_value.toUpperCase() === 'TRUE') return 1;
  if (packet.display_value === '0' || packet.display_value.toUpperCase() === 'FALSE') return 0;
  return null;
}

function joinStateFor(probability: number | null, outcome: 0 | 1 | null): ForecastOutcomeJoinState {
  if (probability == null && outcome == null) return 'NOT_COMPUTABLE';
  if (probability == null) return 'MISSING_FORECAST_PROBABILITY';
  if (outcome == null) return 'MISSING_OUTCOME';
  return 'JOINED';
}

function brierScore(probability: number, outcome: 0 | 1): number {
  return Number(((probability - outcome) ** 2).toFixed(10));
}

function buildRecord(system: SystemProjection, packet: ProjectionPacket): ScoringBindingRecord {
  const probability = probabilityFromPacket(packet);
  const outcome = outcomeFromPacket(packet);
  const joinState = joinStateFor(probability, outcome);
  const score = probability == null || outcome == null ? null : brierScore(probability, outcome);
  const blockers = [
    ...(probability == null ? ['missing_forecast_probability'] : []),
    ...(outcome == null ? ['missing_outcome_resolution'] : []),
  ];

  return {
    score_id: `score-${system.system_id}-${packet.packet_id}`,
    forecast_id: packetLooksLikeForecast(packet) ? packet.packet_id : `NOT_COMPUTABLE:${packet.packet_id}`,
    run_id: system.system_id,
    subject: `${system.display_name}:${packet.packet_type}`,
    probability,
    outcome,
    brier_score: score,
    scoring_status: score == null ? 'NOT_COMPUTABLE' : 'SCORED',
    join_state: joinState,
    blockers,
    source_packet_id: packet.packet_id,
    source_system_id: system.system_id,
    immutable_once_sealed: true,
    projection_only: true,
  };
}

function buildCalibrationSummary(records: ScoringBindingRecord[]): CalibrationSummaryProjection {
  const scored = records.filter((record) => record.brier_score != null);
  const mean =
    scored.length === 0
      ? null
      : Number(
          (scored.reduce((sum, record) => sum + (record.brier_score ?? 0), 0) / scored.length).toFixed(10),
        );

  return {
    summary_id: 'calibration-summary-aal-viz-v6-8',
    run_id: 'aal-viz-live-console',
    bucket_count: scored.length === 0 ? 0 : 10,
    mean_brier: mean,
    calibration_error: null,
    sample_size: scored.length,
    scoring_status: scored.length === 0 ? 'NOT_COMPUTABLE' : 'SCORED',
  };
}

export function buildScoringBindingFrame(bundle: LiveConsoleProjectionBundle): ScoringBindingFrame {
  const records = bundle.systems.flatMap((system) =>
    system.projection_packets.map((packet) => buildRecord(system, packet)),
  );
  const calibrationSummary = buildCalibrationSummary(records);

  const frameWithoutHash = {
    packet_type: 'AALVizScoringBindingFrame.v1' as const,
    drop_name: 'AAL-Viz v6.8 — Run Ledger + Brier Scoring Binding Code Drop' as const,
    authority: 'SCORING_LEDGER_AND_PROJECTION_ONLY' as const,
    promotion_policy: 'NO_AUTOMATIC_PROMOTION_FROM_SCORE_ONLY' as const,
    projection_only: true as const,
    folded_versions: ['v6.1', 'v6.2', 'v6.3', 'v6.4', 'v6.5', 'v6.6', 'v6.7'] as ScoringBindingFrame['folded_versions'],
    bindings: [
      'run_ledger',
      'forecast_outcome_join',
      'brier_score',
      'calibration_summary',
      'notion_score_write',
      'websocket_score_broadcast',
      'aal_viz_score_surface',
    ] as ScoringBindingFrame['bindings'],
    scoring_records: records,
    calibration_summary: calibrationSummary,
    scoring_locks: {
      brier_descriptive_only: true as const,
      automatic_promotion_allowed: false as const,
      execution_authority: false as const,
      truth_authority: false as const,
      model_weight_mutation_allowed: false as const,
      notion_score_write_enabled: false as const,
      websocket_score_broadcast_enabled: false as const,
      missing_outcome_renders_not_computable: true as const,
      missing_probability_renders_not_computable: true as const,
      correction_packet_required_for_score_changes: true as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}

