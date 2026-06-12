import { useMemo, useState } from 'react';
import { buildLineageRelationshipOverlayFrame } from '../data/buildLineageRelationshipOverlayFrame';
import type { LiveConsoleProjectionBundle } from '../types';

interface LineageRelationshipOverlayPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

export function LineageRelationshipOverlayPanel({
  bundle,
}: LineageRelationshipOverlayPanelProps): JSX.Element {
  const frame = useMemo(() => buildLineageRelationshipOverlayFrame(bundle), [bundle]);
  const [selectedNodeId, setSelectedNodeId] = useState(frame.nodes[0]?.node_id ?? '');

  const selectedEdges = frame.edges.filter(
    (edge) => edge.source_node_id === selectedNodeId || edge.target_node_id === selectedNodeId,
  );

  return (
    <section
      className="lineage-overlay-panel"
      data-testid="lineage-relationship-overlay-panel"
      aria-label="AAL-Viz Lineage Relationship Overlay"
    >
      <div className="lineage-overlay-panel__header">
        <span className="lineage-overlay-panel__title">LINEAGE RELATIONSHIP OVERLAY</span>
        <span className="lineage-overlay-panel__notice">
          {frame.authority} · {frame.relationship_arrow_policy}
        </span>
      </div>

      <div className="lineage-overlay-grid">
        <div className="lineage-section lineage-section--wide" data-testid="lineage-node-field">
          <div className="lineage-section__label">DECLARED NODE FIELD</div>
          <div className="lineage-node-row">
            {frame.nodes.map((node) => (
              <button
                key={node.node_id}
                type="button"
                className={`lineage-node lineage-node--${node.status}${selectedNodeId === node.node_id ? ' lineage-node--selected' : ''}`}
                onClick={() => setSelectedNodeId(node.node_id)}
                data-testid={`lineage-node-${node.node_id}`}
                aria-pressed={selectedNodeId === node.node_id}
              >
                <span className="lineage-node__label">{node.label}</span>
                <span className="lineage-node__meta">{node.provenance_state}</span>
              </button>
            ))}
          </div>
          <div className="lineage-section__meta">
            Selection highlighting is display-only and cannot mutate packets or rank nodes.
          </div>
        </div>

        <div className="lineage-section" data-testid="lineage-edge-list">
          <div className="lineage-section__label">RELATIONSHIP ARROWS</div>
          <ul className="lineage-edge-list">
            {frame.edges.map((edge) => (
              <li
                key={edge.edge_id}
                className={`lineage-edge lineage-edge--${edge.link_kind}`}
                data-testid={`lineage-edge-${edge.edge_id}`}
              >
                <span className="lineage-edge__path">{edge.source_node_id} → {edge.target_node_id}</span>
                <span className="lineage-edge__type">{edge.relationship_type}</span>
                <span className="lineage-edge__kind">{edge.link_kind}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="lineage-section" data-testid="lineage-selected-focus">
          <div className="lineage-section__label">SELECTION FOCUS</div>
          <div className="lineage-focus-label">{selectedNodeId || 'NOT_COMPUTABLE'}</div>
          <ul className="lineage-edge-list">
            {selectedEdges.length === 0 ? (
              <li className="lineage-edge lineage-edge--NOT_COMPUTABLE_LINK">
                <span className="lineage-edge__path">NO DECLARED EDGES</span>
                <span className="lineage-edge__kind">NOT_COMPUTABLE_LINK</span>
              </li>
            ) : (
              selectedEdges.map((edge) => (
                <li key={edge.edge_id} className={`lineage-edge lineage-edge--${edge.link_kind}`}>
                  <span className="lineage-edge__path">{edge.edge_id}</span>
                  <span className="lineage-edge__kind">{edge.confidence}</span>
                </li>
              ))
            )}
          </ul>
        </div>

        <div className="lineage-section" data-testid="lineage-link-legend">
          <div className="lineage-section__label">LINK KIND LEGEND</div>
          <div className="lineage-chip-list">
            {frame.link_kind_legend.map((kind) => (
              <span className={`lineage-chip lineage-chip--${kind}`} key={kind}>{kind}</span>
            ))}
          </div>
        </div>

        <div className="lineage-section" data-testid="lineage-authority-locks">
          <div className="lineage-section__label">AUTHORITY LOCKS</div>
          <div className="lineage-lock-grid">
            <span>SCORING AUTHORITY</span><strong>{String(frame.rendering_locks.scoring_authority).toUpperCase()}</strong>
            <span>FORECASTING AUTHORITY</span><strong>{String(frame.rendering_locks.forecasting_authority).toUpperCase()}</strong>
            <span>VALIDATION AUTHORITY</span><strong>{String(frame.rendering_locks.validation_authority).toUpperCase()}</strong>
            <span>PROMOTION AUTHORITY</span><strong>{String(frame.rendering_locks.promotion_authority).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(frame.rendering_locks.truth_authority).toUpperCase()}</strong>
            <span>MISSING SOURCE DIMMED</span><strong>{String(frame.rendering_locks.missing_source_renders_not_computable).toUpperCase()}</strong>
          </div>
          <div className="lineage-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
