import { describe, expect, it } from 'vitest';
import { buildCinematicBriefingFrame } from './buildCinematicBriefingFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { OperatorActionPacketsBundle } from '../types';

const SAMPLE_PACKETS: OperatorActionPacketsBundle = {
  schema_version: 'AALViz.OperatorActionPackets.v0.1',
  generated_at: '2026-05-30T00:00:00Z',
  authority: {
    execution_allowed: false,
    runtime_mutation_allowed: false,
    promotion_allowed: false,
    production_activation_allowed: false,
    metric_emission_allowed: false,
    forecast_influence_allowed: false,
    p43_lanes_allowed: false,
  },
  source_projection_bundle_hash: null,
  fail_closed_reason: null,
  packets: [],
};

describe('buildCinematicBriefingFrame', () => {
  it('builds a deterministic v8 cinematic briefing frame from the v7.9 narrative packet', () => {
    const frame = buildCinematicBriefingFrame(sampleProjectionBundle, SAMPLE_PACKETS);
    const repeat = buildCinematicBriefingFrame(sampleProjectionBundle, SAMPLE_PACKETS);

    expect(frame).toEqual(repeat);
    expect(frame.packet_type).toBe('AALVizCinematicBriefingFrame.v1');
    expect(frame.drop_name).toBe('AAL-Viz v8.0 — Cinematic Briefing Generator + Narrative Camera Paths');
    expect(frame.authority).toBe('CINEMATIC_BRIEFING_PROJECTION_ONLY');
    expect(frame.folded_versions).toContain('v7.9');
    expect(frame.features).toContain('cinematic_briefing_generator');
    expect(frame.features).toContain('narrative_to_camera_path_compiler');
    expect(frame.features).toContain('voiceover_script_export_option');
    expect(frame.source_narrative_id).toBe('analytics-narrative-latest');
    expect(frame.provenance_hash).toMatch(/^[0-9a-f]{8}$/);
  });

  it('derives story blocks, camera path segments, coaching prompts, and snapshot previews without side effects', () => {
    const frame = buildCinematicBriefingFrame(sampleProjectionBundle, SAMPLE_PACKETS);

    expect(frame.story_blocks.length).toBeGreaterThan(0);
    expect(frame.camera_path.length).toBe(frame.story_blocks.length + 1);
    expect(frame.camera_path[0].camera_mode).toBe('ESTABLISHING');
    expect(frame.camera_path.every((segment) => segment.authority === 'VISUAL_PROJECTION_ONLY')).toBe(true);
    expect(frame.operator_coaching_suggestions.length).toBeGreaterThan(0);
    expect(frame.operator_coaching_suggestions.every((suggestion) => suggestion.review_only)).toBe(true);
    expect(frame.operator_coaching_suggestions.every((suggestion) => !suggestion.execution_allowed)).toBe(true);
    expect(frame.export_snapshots).toHaveLength(2);
    expect(frame.export_snapshots.every((snapshot) => !snapshot.file_write_allowed)).toBe(true);
    expect(frame.voiceover_script_lines.length).toBe(frame.story_blocks.length);
  });

  it('keeps cinematic briefing locks fail-closed', () => {
    const frame = buildCinematicBriefingFrame(sampleProjectionBundle, SAMPLE_PACKETS);

    expect(frame.briefing_locks.display_only).toBe(true);
    expect(frame.briefing_locks.source_narrative_required).toBe(true);
    expect(frame.briefing_locks.story_blocks_create_new_facts).toBe(false);
    expect(frame.briefing_locks.camera_paths_visual_projection_only).toBe(true);
    expect(frame.briefing_locks.coaching_suggestions_review_only).toBe(true);
    expect(frame.briefing_locks.snapshot_export_writes_files).toBe(false);
    expect(frame.briefing_locks.voiceover_export_writes_files).toBe(false);
    expect(frame.briefing_locks.notion_write_adapter_enabled).toBe(false);
    expect(frame.briefing_locks.websocket_broadcast_enabled).toBe(false);
    expect(frame.briefing_locks.autonomous_execution_allowed).toBe(false);
    expect(frame.briefing_locks.outcome_resolution_allowed).toBe(false);
    expect(frame.briefing_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.briefing_locks.score_mutation_allowed).toBe(false);
    expect(frame.briefing_locks.provider_authority_mutation_allowed).toBe(false);
    expect(frame.briefing_locks.strategy_routing_mutation_allowed).toBe(false);
    expect(frame.briefing_locks.operator_rank_authority).toBe(false);
    expect(frame.briefing_locks.promotion_allowed).toBe(false);
    expect(frame.briefing_locks.truth_authority).toBe(false);
  });
});
