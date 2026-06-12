import type {
  ABXMetricDashboardFrame,
  CandidateMetricDisplayValue,
  LiveConsoleProjectionBundle,
  MetricDeltaState,
  MetricDeltaValue,
  MetricDisplayValue,
  ProjectionPacket,
  SystemFusionContribution,
} from '../types';

const DASHBOARD_PANELS = [
  'Core ABX Metric Strip',
  'Delta Tracker',
  'Dynamic Metric Expansion Panel',
  'System Fusion Matrix',
  'AFE Run Stream',
  'Oracle Annotation Feed',
  'SHADOW Drift Feed',
  'AAL-Viz Overlay Preview',
  'Non-Filtering Compliance Monitor',
];

const CORE_DEFINITIONS: Record<string, { definition: string; visual_projection: string }> = {
  SDR: {
    definition: 'signal cohesion / density',
    visual_projection: 'cluster density glow',
  },
  MSI: {
    definition: 'manipulation or instability pressure',
    visual_projection: 'drift vectors',
  },
  RFR: {
    definition: 'resonance fidelity / coherence stability',
    visual_projection: 'smooth/jagged stability line',
  },
  ARF: {
    definition: 'attractor retention / loop persistence',
    visual_projection: 'loop thickness',
  },
  NMC: {
    definition: 'normative memory / learned constraint carryover',
    visual_projection: 'persistence trail',
  },
};

const CANDIDATE_DEFINITIONS: Record<
  string,
  { meaning: string; origin: string; visual_projection: string }
> = {
  HCI: {
    meaning: 'Hybrid Collision Index',
    origin: 'Batch 004.1 stack instability',
    visual_projection: 'collision node flare',
  },
  ATI: {
    meaning: 'Authority Tension Index',
    origin: 'authority conflict fields',
    visual_projection: 'authority tension axis',
  },
  MRI: {
    meaning: 'Meme Resonance Index',
    origin: 'meme propagation strength',
    visual_projection: 'meme propagation pulse',
  },
  IPI: {
    meaning: 'Identity Pressure Index',
    origin: 'persona / performance distortion',
    visual_projection: 'identity pressure halo',
  },
  SFI: {
    meaning: 'Scarcity Friction Index',
    origin: 'resource pressure distortion',
    visual_projection: 'scarcity friction bands',
  },
};

const SYSTEM_FUSION_MATRIX: SystemFusionContribution[] = [
  { system: 'AFE', metric_contribution: 'ACS / MDI / SES / SLI / ECI', use: 'behavior traces' },
  { system: 'ABX Core', metric_contribution: 'SDR / MSI / RFR / ARF / NMC', use: 'canonical compression' },
  { system: 'Oracle', metric_contribution: 'labels / symbolic annotations', use: 'interpretive layer' },
  { system: 'Slang Engine', metric_contribution: 'meme drift / slang emergence', use: 'memetic field' },
  { system: 'Neon Genie', metric_contribution: 'ideation pressure / opportunity signals', use: 'product intelligence' },
  { system: 'Level 99', metric_contribution: 'joke density / virality pressure', use: 'content strategy' },
  { system: 'AAL-Viz', metric_contribution: 'projection / overlays', use: 'visibility' },
  { system: 'SHADOW', metric_contribution: 'anomaly / drift / manipulation labels', use: 'detection only' },
];

function clamp01(value: number): number {
  return Math.max(0, Math.min(1, value));
}

function roundMetric(value: number): number {
  return Math.round(clamp01(value) * 100) / 100;
}

function ratio(part: number, total: number): number {
  return total > 0 ? part / total : 0;
}

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

function packetMatches(packet: ProjectionPacket, needles: string[]): boolean {
  const haystack = [
    packet.packet_id,
    packet.packet_type,
    packet.status,
    packet.display_value ?? '',
    packet.authority_source,
  ]
    .join(' ')
    .toLowerCase();
  return needles.some((needle) => haystack.includes(needle));
}

function selectPackets(bundle: LiveConsoleProjectionBundle, needles: string[]): ProjectionPacket[] {
  return bundle.systems
    .flatMap((system) => system.projection_packets)
    .filter((packet) => packet.projection_only === true && packetMatches(packet, needles))
    .slice(0, 8);
}

function deltaState(delta: number, metrics: Record<string, number>): MetricDeltaState {
  if (metrics.MSI >= 0.75 && metrics.RFR <= 0.35) return 'COLLAPSE';
  if (metrics.MSI >= 0.5 && metrics.RFR < 0.55) return 'DRIFT';
  if (metrics.MSI >= 0.45 && metrics.SDR >= 0.55 && metrics.RFR >= 0.45) return 'HYBRID_COLLISION';
  if (delta > 0.04 && metrics.RFR >= 0.5) return 'RECOVERY';
  return 'STABLE';
}

function buildCoreMetrics(bundle: LiveConsoleProjectionBundle): MetricDisplayValue[] {
  const total = bundle.systems.length;
  const ready = bundle.systems.filter((system) => system.status === 'READY').length;
  const partial = bundle.systems.filter((system) => system.status === 'PARTIAL').length;
  const notComputable = bundle.systems.filter((system) => system.status === 'NOT_COMPUTABLE').length;
  const highRisk = bundle.systems.filter((system) => system.risk_level === 'HIGH').length;
  const averageCompletion = ratio(
    bundle.systems.reduce((sum, system) => sum + system.completion_pct, 0),
    total * 100,
  );
  const reviewedQueue = ratio(
    bundle.operator_queue.filter((item) => item.status === 'REVIEWED').length,
    bundle.operator_queue.length,
  );
  const authorityMemory =
    bundle.authority.projection_only === true &&
    bundle.authority.runtime_mutation_allowed === false &&
    bundle.authority.promotion_allowed === false &&
    bundle.authority.production_activation_allowed === false
      ? 1
      : 0;

  const values: Record<string, number> = {
    SDR: averageCompletion,
    MSI: ratio(highRisk + notComputable, Math.max(1, total)),
    RFR: ratio(ready, Math.max(1, total)),
    ARF: Math.max(reviewedQueue, ratio(partial + ready, Math.max(1, total))),
    NMC: authorityMemory,
  };

  return ['SDR', 'MSI', 'RFR', 'ARF', 'NMC'].map((metric) => ({
    metric,
    value: roundMetric(values[metric]),
    label: `${metric}: ${roundMetric(values[metric]).toFixed(2)}`,
    definition: CORE_DEFINITIONS[metric].definition,
    always_visible: true,
    visual_projection: CORE_DEFINITIONS[metric].visual_projection,
  }));
}

function buildCandidateMetrics(bundle: LiveConsoleProjectionBundle): CandidateMetricDisplayValue[] {
  const total = Math.max(1, bundle.systems.length);
  const partial = bundle.systems.filter((system) => system.status === 'PARTIAL').length;
  const notComputable = bundle.systems.filter((system) => system.status === 'NOT_COMPUTABLE').length;
  const highRisk = bundle.systems.filter((system) => system.risk_level === 'HIGH').length;
  const lowRisk = bundle.systems.filter((system) => system.risk_level === 'LOW').length;
  const packetCount = bundle.systems.reduce((sum, system) => sum + system.projection_packets.length, 0);
  const values: Record<string, number> = {
    HCI: ratio(partial + notComputable, total),
    ATI: bundle.authority.projection_only ? 0 : 1,
    MRI: ratio(packetCount, total * 4),
    IPI: ratio(highRisk, total),
    SFI: 1 - ratio(lowRisk, total),
  };

  return ['HCI', 'ATI', 'MRI', 'IPI', 'SFI'].map((metric) => ({
    metric,
    value: roundMetric(values[metric]),
    label: `${metric}: ${roundMetric(values[metric]).toFixed(2)}`,
    meaning: CANDIDATE_DEFINITIONS[metric].meaning,
    origin: CANDIDATE_DEFINITIONS[metric].origin,
    stabilization_window_required: true,
    canon_promotion_allowed: false,
    visual_projection: CANDIDATE_DEFINITIONS[metric].visual_projection,
  }));
}

function buildDelta(coreMetrics: MetricDisplayValue[]): MetricDeltaValue[] {
  const metricMap = Object.fromEntries(coreMetrics.map((metric) => [metric.metric, metric.value]));
  const baseline: Record<string, number> = {
    SDR: 0.5,
    MSI: 0.25,
    RFR: 0.5,
    ARF: 0.5,
    NMC: 1,
  };
  return coreMetrics.map((metric) => {
    const value = Math.round((metric.value - baseline[metric.metric]) * 100) / 100;
    return {
      metric: metric.metric,
      value,
      state: deltaState(value, metricMap),
    };
  });
}

export function buildMetricDashboardFrame(
  bundle: LiveConsoleProjectionBundle,
): ABXMetricDashboardFrame {
  const coreMetrics = buildCoreMetrics(bundle);
  const candidateMetrics = buildCandidateMetrics(bundle);
  const frameWithoutHash = {
    packet_type: 'ABXMetricDashboardFrame.v1' as const,
    authority: 'SHADOW_ONLY_TRACE' as const,
    output_effect: 'VISUAL_ANNOTATION_ONLY' as const,
    non_filtering_compliance: true as const,
    batch_id: 'AFE-BATCH-004.1',
    previous_batch_id: 'AFE-BATCH-004',
    panels: DASHBOARD_PANELS,
    core_metrics: coreMetrics,
    candidate_metrics: candidateMetrics,
    delta: buildDelta(coreMetrics),
    system_fusion_matrix: SYSTEM_FUSION_MATRIX,
    afe_run_stream: selectPackets(bundle, ['afe', 'trace', 'metric_posture']),
    shadow_observation_feed: selectPackets(bundle, ['shadow', 'risk', 'not_computable', 'blocked', 'partial']),
    oracle_annotation_feed: selectPackets(bundle, ['oracle', 'annotation']),
    aal_viz_overlay_preview: [
      'cluster density glow',
      'drift vectors',
      'smooth/jagged stability line',
      'loop thickness',
      'persistence trail',
      'collision node flare',
      'authority tension axis',
      'meme propagation pulse',
      'identity pressure halo',
      'scarcity friction bands',
    ],
    non_filtering_compliance_monitor: {
      output_preserved: true as const,
      annotation_only: true as const,
      filter_calls_detected: false as const,
      suppression_calls_detected: false as const,
      rewrite_calls_detected: false as const,
      panel_hiding_detected: false as const,
    },
    rendering_locks: {
      raw_layer_always_visible: true as const,
      max_overlay_opacity: 0.6 as const,
      no_panel_hiding: true as const,
      no_metric_suppression: true as const,
      no_output_filtering: true as const,
      no_output_rewrite: true as const,
      no_canon_mutation: true as const,
      no_forecast_weight_mutation: true as const,
    },
    source_runs: bundle.systems.map((system) => system.system_id).sort(),
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
