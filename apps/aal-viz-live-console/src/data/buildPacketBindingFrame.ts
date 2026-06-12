import type {
  LiveConsoleProjectionBundle,
  NotionDeepLinkState,
  PacketBindingFrame,
  PacketBindingRecord,
  PacketBindingState,
  ProjectionPacket,
  RelationshipEdgeStreamRecord,
  RelationshipStreamState,
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

function bindingStateFor(system: SystemProjection, packet: ProjectionPacket): PacketBindingState {
  if (system.status === 'NOT_COMPUTABLE' || packet.status === 'NOT_COMPUTABLE') {
    return 'NOT_COMPUTABLE';
  }
  if (system.ledger_receipts.length === 0) return 'NOT_COMPUTABLE';
  return packet.projection_only === true ? 'BOUND' : 'PENDING';
}

function notionStateFor(url: string | null): NotionDeepLinkState {
  return url == null ? 'NOT_COMPUTABLE' : 'BOUND';
}

function relationshipStateFor(
  system: SystemProjection,
  bindingState: PacketBindingState,
): RelationshipStreamState {
  if (bindingState === 'NOT_COMPUTABLE') return 'NOT_COMPUTABLE';
  if (system.status === 'PARTIAL' || system.status === 'FAIL_CLOSED') return 'INFERRED';
  return 'OBSERVED';
}

function buildRecord(system: SystemProjection, packet: ProjectionPacket): PacketBindingRecord {
  const canonicalUrl = null;
  const bindingState = bindingStateFor(system, packet);
  return {
    binding_id: `binding-${system.system_id}-${packet.packet_id}`,
    system_id: system.system_id,
    packet_id: packet.packet_id,
    packet_type: packet.packet_type,
    packet_status: packet.status,
    live_store_key: `${system.system_id}:${packet.packet_id}`,
    binding_state: bindingState,
    canonical_notion_url: canonicalUrl,
    notion_deep_link_state: notionStateFor(canonicalUrl),
    relationship_stream_state: relationshipStateFor(system, bindingState),
    append_only_required: true,
    projection_only: true,
  };
}

function buildBindingRecords(bundle: LiveConsoleProjectionBundle): PacketBindingRecord[] {
  return bundle.systems.flatMap((system) => system.projection_packets.map((packet) => buildRecord(system, packet)));
}

function buildRelationshipEdgeStream(records: PacketBindingRecord[]): RelationshipEdgeStreamRecord[] {
  return records.map((record, index) => ({
    stream_id: `relationship-stream-${String(index + 1).padStart(3, '0')}`,
    source_system_id: record.system_id,
    target_packet_id: record.packet_id,
    relationship_stream_state: record.relationship_stream_state,
    declared_links_only: true,
    source_fields_mutable: false,
  }));
}

export function buildPacketBindingFrame(bundle: LiveConsoleProjectionBundle): PacketBindingFrame {
  const bindingRecords = buildBindingRecords(bundle);
  const relationshipEdgeStream = buildRelationshipEdgeStream(bindingRecords);
  const notionUrlMap = Object.fromEntries(
    bindingRecords.map((record) => [record.live_store_key, record.canonical_notion_url]),
  );

  const frameWithoutHash = {
    packet_type: 'AALVizPacketBindingFrame.v1' as const,
    drop_name: 'AAL-Viz v6.7 — Notion + Live Abraxas Packet Binding Layer Code Drop' as const,
    authority: 'TRANSPORT_STORAGE_PROJECTION_ONLY' as const,
    mutation_policy: 'APPEND_ONLY_DEFAULT' as const,
    projection_only: true as const,
    bindings: [
      'packet_ingest',
      'notion_writer',
      'websocket_broadcast',
      'frontend_live_store',
      'notion_deep_link',
      'relationship_edge_stream',
    ] as PacketBindingFrame['bindings'],
    packet_ingest_endpoint: '/api/packets' as const,
    websocket_url_env: 'AAL_VIZ_WS_URL' as const,
    source_bundle_generated_at: bundle.generated_at,
    binding_records: bindingRecords,
    notion_url_map: notionUrlMap,
    relationship_edge_stream: relationshipEdgeStream,
    binding_locks: {
      packet_writes_append_only: true as const,
      notion_writer_enabled: false as const,
      websocket_broadcast_enabled: false as const,
      websocket_events_mutate_source_fields: false as const,
      frontend_selection_promotes: false as const,
      frontend_selection_validates: false as const,
      frontend_selection_scores: false as const,
      frontend_selection_resolves_outcomes: false as const,
      missing_provenance_renders_not_computable: true as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}

