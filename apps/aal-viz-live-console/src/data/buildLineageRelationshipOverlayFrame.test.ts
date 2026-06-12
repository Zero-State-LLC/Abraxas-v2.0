import { describe, expect, it } from 'vitest';
import { buildLineageRelationshipOverlayFrame } from './buildLineageRelationshipOverlayFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';

describe('buildLineageRelationshipOverlayFrame', () => {
  it('builds deterministic visual-only lineage frames', () => {
    const first = buildLineageRelationshipOverlayFrame(sampleProjectionBundle);
    const second = buildLineageRelationshipOverlayFrame(sampleProjectionBundle);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizLineageRelationshipOverlayFrame.v1');
    expect(first.authority).toBe('VISUAL_PROJECTION_ONLY');
    expect(first.relationship_arrow_policy).toBe('DISPLAY_DECLARED_RELATIONSHIP_ONLY');
    expect(first.projection_only).toBe(true);
    expect(first.non_filtering_compliance).toBe(true);
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('creates nodes for every system and root-to-system relationship arrows', () => {
    const frame = buildLineageRelationshipOverlayFrame(sampleProjectionBundle);

    expect(frame.nodes).toHaveLength(sampleProjectionBundle.systems.length);
    expect(frame.edges).toHaveLength(sampleProjectionBundle.systems.length - 1);
    expect(frame.nodes.every((node) => node.authority_tier === 'VISUAL_PROJECTION_ONLY')).toBe(true);
    expect(frame.edges.every((edge) => edge.authority_tier === 'VISUAL_PROJECTION_ONLY')).toBe(true);
  });

  it('distinguishes observed, inferred, speculative, and not-computable links', () => {
    const frame = buildLineageRelationshipOverlayFrame(sampleProjectionBundle);
    const kinds = new Set(frame.edges.map((edge) => edge.link_kind));

    expect(kinds.has('OBSERVED_LINK')).toBe(true);
    expect(kinds.has('INFERRED_LINK')).toBe(true);
    expect(kinds.has('SPECULATIVE_LINK')).toBe(true);
    expect(kinds.has('NOT_COMPUTABLE_LINK')).toBe(true);
    expect(frame.edges.some((edge) => edge.renders_dimmed && edge.link_kind === 'NOT_COMPUTABLE_LINK')).toBe(true);
  });

  it('locks relationship overlays out of authority-bearing behavior', () => {
    const frame = buildLineageRelationshipOverlayFrame(sampleProjectionBundle);

    expect(frame.rendering_locks.gpu_simulation_mutates_packets).toBe(false);
    expect(frame.rendering_locks.selection_highlight_mutates_packets).toBe(false);
    expect(frame.rendering_locks.selection_highlight_ranks_packets).toBe(false);
    expect(frame.rendering_locks.scoring_authority).toBe(false);
    expect(frame.rendering_locks.forecasting_authority).toBe(false);
    expect(frame.rendering_locks.validation_authority).toBe(false);
    expect(frame.rendering_locks.promotion_authority).toBe(false);
    expect(frame.rendering_locks.truth_authority).toBe(false);
    expect(frame.rendering_locks.missing_source_renders_not_computable).toBe(true);
  });
});
