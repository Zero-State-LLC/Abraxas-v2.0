import { buildAnalyticsNarrativeSummaryFrame } from './buildAnalyticsNarrativeSummaryFrame';
import type {
  AnalyticsNarrativeFinding,
  CinematicBriefingCameraMode,
  CinematicBriefingFrame,
  CinematicBriefingStoryBlock,
  LiveConsoleProjectionBundle,
  NarrativeCameraPathSegment,
  OperatorActionPacketsBundle,
  OperatorCoachingSuggestion,
} from '../types';

function stableStringify(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map((item) => stableStringify(item)).join(',')}]`;
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

function cameraModeFor(finding: AnalyticsNarrativeFinding): CinematicBriefingCameraMode {
  if (finding.provenance === 'NOT_COMPUTABLE') return 'LOCKED_GAP';
  if (finding.provenance === 'INFERRED') return 'PAN_GAP';
  return 'FOCUS_FINDING';
}

function storyBlocksFor(findings: AnalyticsNarrativeFinding[]): CinematicBriefingStoryBlock[] {
  return findings
    .map((finding, index) => ({
      block_id: `story-block-${String(index + 1).padStart(2, '0')}`,
      source_finding_id: finding.finding_id,
      title: finding.label,
      narration: finding.claim,
      camera_cue:
        finding.provenance === 'NOT_COMPUTABLE'
          ? `Hold ${finding.label} as an explicit evidence gap.`
          : `Focus ${finding.label} without changing source evidence.`,
      provenance: finding.provenance,
      confidence: finding.confidence,
      source_metric_ids: [...finding.source_metric_ids].sort((a, b) => a.localeCompare(b)),
      severity_band: finding.provenance === 'NOT_COMPUTABLE' ? ('WATCH' as const) : ('INFO' as const),
    }))
    .sort((a, b) => a.block_id.localeCompare(b.block_id));
}

function cameraPathFor(storyBlocks: CinematicBriefingStoryBlock[]): NarrativeCameraPathSegment[] {
  const opening: NarrativeCameraPathSegment = {
    segment_id: 'camera-segment-00',
    target_block_id: storyBlocks[0]?.block_id ?? 'story-block-not-computable',
    camera_mode: 'ESTABLISHING',
    duration_ms: 1600,
    focus_label: 'briefing_context',
    easing: 'EASE_IN_OUT',
    authority: 'VISUAL_PROJECTION_ONLY',
  };

  const blockSegments = storyBlocks.map((block, index) => ({
    segment_id: `camera-segment-${String(index + 1).padStart(2, '0')}`,
    target_block_id: block.block_id,
    camera_mode: cameraModeFor({
      finding_id: block.source_finding_id,
      label: block.title,
      claim: block.narration,
      provenance: block.provenance,
      confidence: block.confidence,
      source_metric_ids: block.source_metric_ids,
      why_it_matters: block.camera_cue,
    }),
    duration_ms: block.provenance === 'NOT_COMPUTABLE' ? 2200 : 1800,
    focus_label: block.title,
    easing: 'EASE_IN_OUT' as const,
    authority: 'VISUAL_PROJECTION_ONLY' as const,
  }));

  return [opening, ...blockSegments].sort((a, b) => a.segment_id.localeCompare(b.segment_id));
}

function coachingSuggestionsFor(storyBlocks: CinematicBriefingStoryBlock[]): OperatorCoachingSuggestion[] {
  return storyBlocks
    .filter((block) => block.provenance === 'NOT_COMPUTABLE' || block.confidence < 0.8)
    .map((block) => ({
      suggestion_id: `coaching-${block.block_id}`,
      source_finding_id: block.source_finding_id,
      prompt:
        block.provenance === 'NOT_COMPUTABLE'
          ? `Review missing evidence for ${block.title}.`
          : `Use ${block.title} as a review prompt, not an action.`,
      rationale: block.camera_cue,
      provenance: block.provenance,
      review_only: true as const,
      rank_authority: false as const,
      execution_allowed: false as const,
    }))
    .sort((a, b) => a.suggestion_id.localeCompare(b.suggestion_id));
}

export function buildCinematicBriefingFrame(
  bundle: LiveConsoleProjectionBundle,
  packetsBundle: OperatorActionPacketsBundle | null,
): CinematicBriefingFrame {
  const narrativeFrame = buildAnalyticsNarrativeSummaryFrame(bundle, packetsBundle);
  const storyBlocks = storyBlocksFor(narrativeFrame.narrative_packet.key_findings);
  const cameraPath = cameraPathFor(storyBlocks);
  const coachingSuggestions = coachingSuggestionsFor(storyBlocks);
  const includedBlockIds = storyBlocks.map((block) => block.block_id).sort((a, b) => a.localeCompare(b));

  const frameWithoutHash = {
    packet_type: 'AALVizCinematicBriefingFrame.v1' as const,
    drop_name: 'AAL-Viz v8.0 — Cinematic Briefing Generator + Narrative Camera Paths' as const,
    authority: 'CINEMATIC_BRIEFING_PROJECTION_ONLY' as const,
    mutation_policy: 'NO_EXECUTION_EXPORT_WRITEBACK_OUTCOME_FORECAST_SCORE_PROVIDER_AUTHORITY_OR_ROUTING_MUTATION' as const,
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
      'v7.6',
      'v7.7',
      'v7.8',
      'v7.9',
    ] as CinematicBriefingFrame['folded_versions'],
    features: [
      'cinematic_briefing_generator',
      'narrative_to_camera_path_compiler',
      'analytics_story_blocks',
      'operator_coaching_suggestions',
      'briefing_export_snapshots',
      'voiceover_script_export_option',
    ] as CinematicBriefingFrame['features'],
    source_narrative_id: narrativeFrame.narrative_packet.narrative_id,
    story_blocks: storyBlocks,
    camera_path: cameraPath,
    operator_coaching_suggestions: coachingSuggestions,
    export_snapshots: [
      {
        snapshot_id: 'snapshot-static-briefing-card',
        label: 'Static briefing card preview',
        included_block_ids: includedBlockIds,
        format: 'STATIC_CARD' as const,
        export_authority: 'DISPLAY_ONLY' as const,
        file_write_allowed: false as const,
      },
      {
        snapshot_id: 'snapshot-script-preview',
        label: 'Voiceover script preview',
        included_block_ids: includedBlockIds,
        format: 'SCRIPT_TEXT' as const,
        export_authority: 'DISPLAY_ONLY' as const,
        file_write_allowed: false as const,
      },
    ].sort((a, b) => a.snapshot_id.localeCompare(b.snapshot_id)),
    voiceover_script_lines: storyBlocks
      .map((block) => `${block.title}: ${block.narration}`)
      .sort((a, b) => a.localeCompare(b)),
    briefing_locks: {
      display_only: true as const,
      source_narrative_required: true as const,
      story_blocks_create_new_facts: false as const,
      camera_paths_visual_projection_only: true as const,
      coaching_suggestions_review_only: true as const,
      snapshot_export_writes_files: false as const,
      voiceover_export_writes_files: false as const,
      notion_write_adapter_enabled: false as const,
      websocket_broadcast_enabled: false as const,
      autonomous_execution_allowed: false as const,
      outcome_resolution_allowed: false as const,
      forecast_probability_mutation_allowed: false as const,
      score_mutation_allowed: false as const,
      provider_authority_mutation_allowed: false as const,
      strategy_routing_mutation_allowed: false as const,
      operator_rank_authority: false as const,
      promotion_allowed: false as const,
      truth_authority: false as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
