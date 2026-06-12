import { useMemo } from 'react';
import { buildPacketBindingFrame } from '../data/buildPacketBindingFrame';
import type { LiveConsoleProjectionBundle } from '../types';

interface PacketBindingLayerPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

export function PacketBindingLayerPanel({
  bundle,
}: PacketBindingLayerPanelProps): JSX.Element {
  const frame = useMemo(() => buildPacketBindingFrame(bundle), [bundle]);
  const boundCount = frame.binding_records.filter((record) => record.binding_state === 'BOUND').length;
  const notComputableLinks = frame.binding_records.filter(
    (record) => record.notion_deep_link_state === 'NOT_COMPUTABLE',
  ).length;
  const previewRecords = frame.binding_records.slice(0, 8);

  return (
    <section
      className="packet-binding-panel"
      data-testid="packet-binding-layer-panel"
      aria-label="AAL-Viz Packet Binding Layer"
    >
      <div className="packet-binding-panel__header">
        <span className="packet-binding-panel__title">PACKET BINDING LAYER</span>
        <span className="packet-binding-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="packet-binding-grid">
        <div className="packet-binding-section packet-binding-section--wide" data-testid="packet-binding-summary">
          <div className="packet-binding-section__label">LIVE STORE BINDINGS</div>
          <div className="packet-binding-summary-row">
            <span>{frame.binding_records.length} PACKETS</span>
            <span>{boundCount} BOUND</span>
            <span>{notComputableLinks} NOTION LINKS NOT_COMPUTABLE</span>
            <span>{frame.relationship_edge_stream.length} RELATIONSHIP STREAM SLOTS</span>
          </div>
          <div className="packet-binding-section__meta">
            {frame.packet_ingest_endpoint} · {frame.websocket_url_env} · source {frame.source_bundle_generated_at}
          </div>
        </div>

        <div className="packet-binding-section" data-testid="packet-binding-records">
          <div className="packet-binding-section__label">PACKET REGISTRY PREVIEW</div>
          <ul className="packet-binding-list">
            {previewRecords.map((record) => (
              <li className={`packet-binding-row packet-binding-row--${record.binding_state}`} key={record.binding_id}>
                <span>{record.live_store_key}</span>
                <span>{record.packet_type}</span>
                <strong>{record.binding_state}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="packet-binding-section" data-testid="packet-binding-notion-map">
          <div className="packet-binding-section__label">NOTION DEEP LINK MAP</div>
          <ul className="packet-binding-list">
            {previewRecords.map((record) => (
              <li className="packet-binding-row" key={`${record.binding_id}-notion`}>
                <span>{record.packet_id}</span>
                {record.canonical_notion_url == null ? (
                  <strong>NOT_COMPUTABLE</strong>
                ) : (
                  <a href={record.canonical_notion_url} target="_blank" rel="noreferrer">OPEN</a>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div className="packet-binding-section" data-testid="packet-binding-stream">
          <div className="packet-binding-section__label">RELATIONSHIP EDGE STREAM</div>
          <div className="packet-binding-chip-list">
            {frame.relationship_edge_stream.slice(0, 10).map((stream) => (
              <span className={`packet-binding-chip packet-binding-chip--${stream.relationship_stream_state}`} key={stream.stream_id}>
                {stream.relationship_stream_state}
              </span>
            ))}
          </div>
          <div className="packet-binding-section__meta">DECLARED LINKS ONLY · SOURCE FIELDS IMMUTABLE</div>
        </div>

        <div className="packet-binding-section" data-testid="packet-binding-locks">
          <div className="packet-binding-section__label">BINDING LOCKS</div>
          <div className="packet-binding-lock-grid">
            <span>NOTION WRITER ENABLED</span><strong>{String(frame.binding_locks.notion_writer_enabled).toUpperCase()}</strong>
            <span>WEBSOCKET BROADCAST ENABLED</span><strong>{String(frame.binding_locks.websocket_broadcast_enabled).toUpperCase()}</strong>
            <span>WS MUTATES SOURCE FIELDS</span><strong>{String(frame.binding_locks.websocket_events_mutate_source_fields).toUpperCase()}</strong>
            <span>SELECTION PROMOTES</span><strong>{String(frame.binding_locks.frontend_selection_promotes).toUpperCase()}</strong>
            <span>SELECTION VALIDATES</span><strong>{String(frame.binding_locks.frontend_selection_validates).toUpperCase()}</strong>
            <span>SELECTION SCORES</span><strong>{String(frame.binding_locks.frontend_selection_scores).toUpperCase()}</strong>
          </div>
          <div className="packet-binding-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}

