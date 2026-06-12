import { describe, expect, it } from 'vitest';
import { buildPacketBindingFrame } from './buildPacketBindingFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';

describe('buildPacketBindingFrame', () => {
  it('builds deterministic transport-storage-projection-only binding frames', () => {
    const first = buildPacketBindingFrame(sampleProjectionBundle);
    const second = buildPacketBindingFrame(sampleProjectionBundle);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizPacketBindingFrame.v1');
    expect(first.authority).toBe('TRANSPORT_STORAGE_PROJECTION_ONLY');
    expect(first.mutation_policy).toBe('APPEND_ONLY_DEFAULT');
    expect(first.projection_only).toBe(true);
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('creates one binding record and relationship stream entry per projection packet', () => {
    const frame = buildPacketBindingFrame(sampleProjectionBundle);
    const packetCount = sampleProjectionBundle.systems.reduce(
      (count, system) => count + system.projection_packets.length,
      0,
    );

    expect(frame.binding_records).toHaveLength(packetCount);
    expect(frame.relationship_edge_stream).toHaveLength(packetCount);
    expect(Object.keys(frame.notion_url_map)).toHaveLength(packetCount);
  });

  it('keeps missing Notion URLs not-computable instead of inventing deep links', () => {
    const frame = buildPacketBindingFrame(sampleProjectionBundle);

    expect(frame.binding_records.every((record) => record.canonical_notion_url === null)).toBe(true);
    expect(frame.binding_records.every((record) => record.notion_deep_link_state === 'NOT_COMPUTABLE')).toBe(true);
    expect(Object.values(frame.notion_url_map).every((url) => url === null)).toBe(true);
  });

  it('locks out writer, websocket mutation, and frontend authority behavior', () => {
    const frame = buildPacketBindingFrame(sampleProjectionBundle);

    expect(frame.binding_locks.packet_writes_append_only).toBe(true);
    expect(frame.binding_locks.notion_writer_enabled).toBe(false);
    expect(frame.binding_locks.websocket_broadcast_enabled).toBe(false);
    expect(frame.binding_locks.websocket_events_mutate_source_fields).toBe(false);
    expect(frame.binding_locks.frontend_selection_promotes).toBe(false);
    expect(frame.binding_locks.frontend_selection_validates).toBe(false);
    expect(frame.binding_locks.frontend_selection_scores).toBe(false);
    expect(frame.binding_locks.frontend_selection_resolves_outcomes).toBe(false);
    expect(frame.binding_locks.missing_provenance_renders_not_computable).toBe(true);
  });
});

