import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type KeyboardEvent } from 'react';
import cytoscape, { type Core, type ElementDefinition } from 'cytoscape';
import type {
  OperatorPlatformContract,
  OperatorPlatformEntityType,
  OperatorPlatformProjection,
  OperatorPlatformProvenance,
  YggdrasilConfidence,
  YggdrasilEdgeClass,
  YggdrasilInterfaceRole,
  YggdrasilNodeClass,
  YggdrasilTopologyEdge,
  YggdrasilTopologyNode,
  YggdrasilTopologyProjection,
} from '../types';

export type OperatorPlatformView =
  | 'status'
  | 'yggdrasil'
  | 'production'
  | 'contracts'
  | 'evidence'
  | 'changes';

export const OPERATOR_PLATFORM_VIEWS: Array<{
  id: OperatorPlatformView;
  label: string;
}> = [
  { id: 'status', label: 'Status' },
  { id: 'yggdrasil', label: 'YGGDRASIL' },
  { id: 'production', label: 'Production' },
  { id: 'contracts', label: 'Contracts' },
  { id: 'evidence', label: 'Evidence' },
  { id: 'changes', label: 'Changes' },
];

const ENTITY_COLORS: Record<OperatorPlatformEntityType, string> = {
  SYSTEM: '#2dd4bf',
  RUNE: '#f2c14e',
  CONTRACT: '#7dd3fc',
  PACKET: '#c4b5fd',
  RECEIPT: '#86efac',
  ROUTE: '#fb7185',
};

const NODE_COLORS: Record<YggdrasilNodeClass, string> = {
  ...ENTITY_COLORS,
  INTERFACE: '#f8fafc',
};

const EDGE_CLASSES: YggdrasilEdgeClass[] = [
  'BINDS', 'CONSUMES', 'EVIDENCES', 'EXPOSES', 'PRODUCES', 'REFERENCES',
  'RENDER_RELATION', 'ROUTES_TO', 'VALIDATES',
];
const NODE_CLASSES = Object.keys(NODE_COLORS).sort() as YggdrasilNodeClass[];
const CONFIDENCE_LEVELS: YggdrasilConfidence[] = ['INFERRED', 'NOT_COMPUTABLE', 'SUPPORTED', 'VERIFIED'];
const PROVENANCE_LEVELS: OperatorPlatformProvenance[] = ['INFERRED', 'OBSERVED'];
const INTERFACE_ROLES: YggdrasilInterfaceRole[] = ['CONSUMER', 'OPERATOR', 'PRODUCER', 'VALIDATOR'];

function SourceState({ state }: { state: string }): JSX.Element {
  return <span className={`source-state source-state--${state.toLowerCase()}`}>{state}</span>;
}

function EmptyState({ title, detail }: { title: string; detail: string }): JSX.Element {
  return (
    <div className="operator-empty" role="status">
      <strong>{title}</strong>
      <span>{detail}</span>
    </div>
  );
}

function SectionFindings({ findings }: { findings: string[] }): JSX.Element | null {
  if (findings.length === 0) return null;
  return (
    <div className="section-findings" role="status">
      <strong>Projection findings</strong>
      {findings.map((finding) => <span key={finding}>{finding}</span>)}
    </div>
  );
}

interface TopologyCanvasProps {
  elements: ElementDefinition[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onReady?: (core: Core) => void;
  layoutName?: 'cose' | 'breadthfirst';
}

function TopologyCanvas({
  elements,
  selectedId,
  onSelect,
  onReady,
  layoutName = 'cose',
}: TopologyCanvasProps): JSX.Element {
  const hostRef = useRef<HTMLDivElement>(null);
  const coreRef = useRef<Core | null>(null);
  const [tooltip, setTooltip] = useState<{ label: string; x: number; y: number } | null>(null);

  useEffect(() => {
    if (hostRef.current == null) return undefined;
    const isHeadless =
      typeof navigator !== 'undefined' && navigator.userAgent.toLowerCase().includes('jsdom');
    const core = cytoscape({
      container: isHeadless ? undefined : hostRef.current,
      headless: isHeadless,
      styleEnabled: !isHeadless,
      elements,
      minZoom: 0.2,
      maxZoom: 2.5,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(color)',
            'border-color': '#071013',
            'border-width': 2,
            color: '#e7f0f2',
            label: 'data(label)',
            'font-size': 9,
            'text-wrap': 'ellipsis',
            'text-max-width': '120px',
            'text-valign': 'bottom',
            'text-margin-y': 8,
            width: 26,
            height: 26,
          },
        },
        {
          selector: 'edge',
          style: {
            width: 1.5,
            'line-color': '#46606a',
            'target-arrow-color': '#46606a',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            opacity: 0.72,
          },
        },
        {
          selector: ':selected',
          style: {
            'border-color': '#ffffff',
            'border-width': 4,
            'line-color': '#f2c14e',
            'target-arrow-color': '#f2c14e',
            opacity: 1,
          },
        },
        { selector: '.dimmed', style: { opacity: 0.12 } },
        { selector: '.unresolved', style: { 'border-color': '#f2c14e', 'border-style': 'dashed' } },
        { selector: '.stale', style: { 'border-color': '#fb7185', 'line-style': 'dashed' } },
        { selector: '.inferred', style: { 'border-color': '#7dd3fc', 'line-style': 'dotted' } },
        { selector: '.diff-added', style: { 'border-color': '#86efac', 'border-width': 4 } },
        { selector: '.diff-removed', style: { opacity: 0.48, 'border-color': '#fb7185', 'border-style': 'dashed', 'line-style': 'dashed' } },
        { selector: '.path-highlight', style: { opacity: 1, 'line-color': '#f2c14e', 'target-arrow-color': '#f2c14e', 'border-color': '#f2c14e' } },
      ],
      layout: {
        name: layoutName,
        animate: false,
        fit: true,
        padding: 42,
        nodeDimensionsIncludeLabels: true,
      },
    });
    core.on('tap', 'node', (event) => onSelect(event.target.id()));
    core.on('mouseover', 'node', (event) => {
      const position = event.target.renderedPosition();
      setTooltip({ label: String(event.target.data('tooltip') ?? event.target.data('label')), x: position.x, y: position.y });
    });
    core.on('mouseout', 'node', () => setTooltip(null));
    coreRef.current = core;
    onReady?.(core);
    return () => {
      core.destroy();
      coreRef.current = null;
    };
  }, [elements, layoutName, onReady, onSelect]);

  useEffect(() => {
    const core = coreRef.current;
    if (core == null) return;
    core.elements().unselect();
    if (selectedId != null) core.getElementById(selectedId).select();
  }, [selectedId]);

  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>): void => {
    const nodeIds = elements
      .filter((element) => element.data.source == null && element.data.target == null)
      .map((element) => String(element.data.id))
      .sort();
    if (event.key === 'Escape') {
      onSelect(null);
      return;
    }
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Enter'].includes(event.key) || nodeIds.length === 0) return;
    event.preventDefault();
    const currentIndex = selectedId == null ? -1 : nodeIds.indexOf(selectedId);
    const direction = event.key === 'ArrowLeft' || event.key === 'ArrowUp' ? -1 : 1;
    const nextIndex = event.key === 'Enter' && currentIndex >= 0
      ? currentIndex
      : (currentIndex + direction + nodeIds.length) % nodeIds.length;
    onSelect(nodeIds[nextIndex]);
  };

  return (
    <div className="topology-canvas-wrap">
      <div
        aria-label={`Interactive projection graph with ${elements.filter((element) => element.data.source == null).length} nodes. Use arrow keys to select nodes and Escape to clear selection.`}
        className="topology-canvas"
        data-testid="topology-canvas"
        onKeyDown={onKeyDown}
        ref={hostRef}
        role="application"
        tabIndex={0}
      />
      {tooltip != null && <div className="graph-tooltip" role="tooltip" style={{ left: tooltip.x, top: tooltip.y }}>{tooltip.label}</div>}
    </div>
  );
}

export interface OperatorPlatformGraphState {
  yggQuery: string;
  yggSelectedNodeClasses: YggdrasilNodeClass[];
  yggSelectedEdgeClasses: YggdrasilEdgeClass[];
  yggSelectedProvenance: OperatorPlatformProvenance[];
  yggSelectedConfidence: YggdrasilConfidence[];
  yggSelectedRoles: YggdrasilInterfaceRole[];
  yggSelectedId: string | null;
  yggTraversalDepth: 1 | 2 | 3;
  yggPathTargetId: string | null;
  yggDiffOverlay: boolean;
  contractQuery: string;
  contractSelectedId: string | null;
}

interface GraphStateProps {
  graphState: OperatorPlatformGraphState;
  onGraphStateChange: (state: OperatorPlatformGraphState) => void;
}

function fallbackTopology(platform: OperatorPlatformProjection): { nodes: YggdrasilTopologyNode[]; edges: YggdrasilTopologyEdge[] } {
  const topology = platform.topology.payload;
  return {
    nodes: (topology?.nodes ?? []).map((node) => ({
      id: node.id, label: node.label, node_class: node.entity_type, roles: [], status: node.status,
      resolution_state: 'RESOLVED', source_ref: node.source_ref,
      provenance: node.provenance === 'OBSERVED' ? 'OBSERVED' : 'INFERRED',
      confidence: node.provenance === 'OBSERVED' ? 'VERIFIED' : 'SUPPORTED', freshness: 'CURRENT',
      evidence_refs: [], temporal_ref: { category: 'TOPOLOGY_NODE', entity_id: node.id },
    })),
    edges: (topology?.edges ?? []).map((edge) => ({
      id: edge.id, source: edge.source, target: edge.target, edge_class: 'RENDER_RELATION',
      relation: edge.relation, status: edge.status, resolution_state: 'RESOLVED',
      provenance: edge.provenance === 'OBSERVED' ? 'OBSERVED' : 'INFERRED',
      confidence: edge.provenance === 'OBSERVED' ? 'VERIFIED' : 'SUPPORTED',
      freshness: 'CURRENT', evidence_refs: [], temporal_ref: { category: 'TOPOLOGY_EDGE', entity_id: edge.id },
    })),
  };
}

function elementClasses(entity: YggdrasilTopologyNode | YggdrasilTopologyEdge, diffOperation?: string): string {
  return [
    entity.resolution_state === 'UNRESOLVED' ? 'unresolved' : '',
    entity.freshness === 'STALE' ? 'stale' : '',
    entity.provenance === 'INFERRED' ? 'inferred' : '',
    diffOperation === 'ADDED' ? 'diff-added' : '',
    diffOperation === 'REMOVED' ? 'diff-removed' : '',
  ].filter(Boolean).join(' ');
}

function YggdrasilView({ platform, topologyProjection, graphState, onGraphStateChange }: {
  platform: OperatorPlatformProjection;
  topologyProjection?: YggdrasilTopologyProjection;
} & GraphStateProps): JSX.Element {
  const query = graphState.yggQuery;
  const selectedNodeClasses = useMemo(() => new Set(graphState.yggSelectedNodeClasses), [graphState.yggSelectedNodeClasses]);
  const selectedEdgeClasses = useMemo(() => new Set(graphState.yggSelectedEdgeClasses), [graphState.yggSelectedEdgeClasses]);
  const selectedProvenance = useMemo(() => new Set(graphState.yggSelectedProvenance), [graphState.yggSelectedProvenance]);
  const selectedConfidence = useMemo(() => new Set(graphState.yggSelectedConfidence), [graphState.yggSelectedConfidence]);
  const selectedRoles = useMemo(() => new Set(graphState.yggSelectedRoles), [graphState.yggSelectedRoles]);
  const selectedId = graphState.yggSelectedId;
  const coreRef = useRef<Core | null>(null);
  const enriched = topologyProjection?.payload ?? null;
  const fallback = useMemo(() => fallbackTopology(platform), [platform]);
  const nodes = enriched?.nodes ?? fallback.nodes;
  const edges = enriched?.edges ?? fallback.edges;
  const temporalMatched = topologyProjection?.temporal_linkage.status === 'MATCHED';
  const temporalEntries = temporalMatched ? (platform.temporal_diff.payload?.entries ?? []) : [];
  const changeByEntity = useMemo(() => new Map(temporalEntries.map((entry) => [entry.entity_id, entry.operation])), [temporalEntries]);

  const visibleNodes = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return nodes.filter(
      (node) =>
        selectedNodeClasses.has(node.node_class) && selectedProvenance.has(node.provenance) &&
        selectedConfidence.has(node.confidence) &&
        (node.node_class !== 'INTERFACE' || node.roles.some((role) => selectedRoles.has(role))) &&
        (normalized.length === 0 ||
          node.label.toLowerCase().includes(normalized) ||
          node.id.toLowerCase().includes(normalized) || node.source_ref.toLowerCase().includes(normalized)),
    );
  }, [nodes, query, selectedConfidence, selectedNodeClasses, selectedProvenance, selectedRoles]);
  const visibleIds = useMemo(() => new Set(visibleNodes.map((node) => node.id)), [visibleNodes]);
  const visibleEdges = useMemo(
    () => edges.filter(
      (edge) => selectedEdgeClasses.has(edge.edge_class) && selectedProvenance.has(edge.provenance) &&
        selectedConfidence.has(edge.confidence) && visibleIds.has(edge.source) && visibleIds.has(edge.target),
    ),
    [edges, selectedConfidence, selectedEdgeClasses, selectedProvenance, visibleIds],
  );
  const removedGhosts = useMemo(() => graphState.yggDiffOverlay ? temporalEntries.filter(
    (entry) => entry.operation === 'REMOVED' && ['TOPOLOGY_NODE', 'TOPOLOGY_EDGE'].includes(entry.category),
  ) : [], [graphState.yggDiffOverlay, temporalEntries]);
  const elements = useMemo<ElementDefinition[]>(
    () => [
      ...visibleNodes.map((node) => ({
        classes: elementClasses(node, graphState.yggDiffOverlay ? changeByEntity.get(node.id) : undefined),
        data: {
          id: node.id,
          label: node.label,
          color: NODE_COLORS[node.node_class],
          tooltip: `${node.node_class} · ${node.provenance} · ${node.confidence}`,
        },
      })),
      ...visibleEdges.map((edge) => ({
        classes: elementClasses(edge, graphState.yggDiffOverlay ? changeByEntity.get(edge.id) : undefined),
        data: { id: edge.id, source: edge.source, target: edge.target, relation: edge.relation },
      })),
      ...removedGhosts.flatMap<ElementDefinition>((entry) => {
        const prior = entry.prior_value;
        if (prior == null || typeof prior !== 'object') return [];
        const value = prior as Record<string, unknown>;
        if (entry.category === 'TOPOLOGY_NODE') return [{ classes: 'diff-removed', data: {
          id: `ghost:${entry.entity_id}`, label: String(value.label ?? entry.entity_id),
          color: '#fb7185', tooltip: 'Removed in current generation',
        } }];
        const source = String(value.source ?? '');
        const target = String(value.target ?? '');
        if (!visibleIds.has(source) || !visibleIds.has(target)) return [];
        return [{ classes: 'diff-removed', data: { id: `ghost:${entry.entity_id}`, source, target } }];
      }),
    ],
    [changeByEntity, graphState.yggDiffOverlay, removedGhosts, visibleEdges, visibleIds, visibleNodes],
  );
  const selected = nodes.find((node) => node.id === selectedId) ?? null;
  const selectedEvidence = enriched?.evidence.filter((record) => selected?.evidence_refs.includes(record.id)) ?? [];
  const captureCore = useCallback((instance: Core) => {
    coreRef.current = instance;
  }, []);

  const toggleValue = <T extends string>(values: T[], value: T, key: keyof OperatorPlatformGraphState): void => {
    const next = new Set(values);
    if (next.has(value)) next.delete(value); else next.add(value);
    onGraphStateChange({ ...graphState, [key]: [...next].sort() });
  };
  const focusDependencies = (): void => {
    const core = coreRef.current;
    if (core == null || selectedId == null) return;
    const selectedNode = core.getElementById(selectedId);
    let neighborhood = selectedNode.closedNeighborhood();
    for (let depth = 1; depth < graphState.yggTraversalDepth; depth += 1) neighborhood = neighborhood.closedNeighborhood();
    core.elements().addClass('dimmed');
    neighborhood.removeClass('dimmed');
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) core.fit(neighborhood, 70);
    else core.animate({ fit: { eles: neighborhood, padding: 70 }, duration: 240 });
  };
  const highlightPath = (): void => {
    const core = coreRef.current;
    if (core == null || selectedId == null || graphState.yggPathTargetId == null) return;
    const path = core.elements().aStar({ root: core.getElementById(selectedId), goal: core.getElementById(graphState.yggPathTargetId), directed: true }).path;
    core.elements().addClass('dimmed').removeClass('path-highlight');
    path.removeClass('dimmed').addClass('path-highlight');
    core.fit(path, 70);
  };
  const highlightRoutes = (): void => {
    const core = coreRef.current;
    if (core == null) return;
    const routes = core.edges().filter((edge) => edge.data('relation') === 'ROUTES_TO' || edge.id().includes('ROUTES_TO'));
    const context = routes.add(routes.connectedNodes());
    core.elements().addClass('dimmed').removeClass('path-highlight');
    context.removeClass('dimmed').addClass('path-highlight');
    core.fit(context, 70);
  };
  const resetGraph = (): void => {
    const core = coreRef.current;
    core?.elements().removeClass('dimmed');
    if (core == null) return;
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) core.fit(core.elements(), 42);
    else core.animate({ fit: { eles: core.elements(), padding: 42 }, duration: 240 });
  };

  return (
    <section className="operator-view" aria-labelledby="yggdrasil-heading">
      <div className="view-heading-row">
        <div>
          <span className="view-kicker">Routing topology</span>
          <h1 id="yggdrasil-heading">YGGDRASIL</h1>
        </div>
        <SourceState state={platform.topology.status} />
      </div>
      <SectionFindings findings={platform.topology.validation_findings} />
      {enriched == null && <div className="section-findings" role="status">Enrichment unavailable. Displaying the validated v0.2 topology fallback.</div>}
      {topologyProjection?.temporal_linkage.status === 'STALE' && <div className="section-findings" role="status">Temporal overlay is stale for this generation and has been suppressed.</div>}
      <div className="topology-toolbar">
        <label className="search-field">
          <span>Search topology</span>
          <input value={query} onChange={(event) => onGraphStateChange({ ...graphState, yggQuery: event.target.value })} />
        </label>
        <div className="entity-filters" aria-label="Node class filters">
          {NODE_CLASSES.map((nodeClass) => (
            <label key={nodeClass} style={{ '--entity-color': NODE_COLORS[nodeClass] } as CSSProperties}>
              <input
                type="checkbox"
                checked={selectedNodeClasses.has(nodeClass)}
                onChange={() => toggleValue(graphState.yggSelectedNodeClasses, nodeClass, 'yggSelectedNodeClasses')}
              />
              {nodeClass}
            </label>
          ))}
        </div>
        <details className="topology-filter-menu"><summary>Edge layers</summary><div>{EDGE_CLASSES.map((edgeClass) => <label key={edgeClass}><input type="checkbox" checked={selectedEdgeClasses.has(edgeClass)} onChange={() => toggleValue(graphState.yggSelectedEdgeClasses, edgeClass, 'yggSelectedEdgeClasses')} />{edgeClass}</label>)}</div></details>
        <details className="topology-filter-menu"><summary>Interface roles</summary><div>{INTERFACE_ROLES.map((role) => <label key={role}><input type="checkbox" checked={selectedRoles.has(role)} onChange={() => toggleValue(graphState.yggSelectedRoles, role, 'yggSelectedRoles')} />{role}</label>)}</div></details>
        <details className="topology-filter-menu"><summary>Evidence overlay</summary><div>{PROVENANCE_LEVELS.map((value) => <label key={value}><input type="checkbox" checked={selectedProvenance.has(value)} onChange={() => toggleValue(graphState.yggSelectedProvenance, value, 'yggSelectedProvenance')} />{value}</label>)}{CONFIDENCE_LEVELS.map((value) => <label key={value}><input type="checkbox" checked={selectedConfidence.has(value)} onChange={() => toggleValue(graphState.yggSelectedConfidence, value, 'yggSelectedConfidence')} />{value}</label>)}</div></details>
      </div>
      <div className="topology-actions">
        <label>Neighborhood <select aria-label="Neighborhood depth" value={graphState.yggTraversalDepth} onChange={(event) => onGraphStateChange({ ...graphState, yggTraversalDepth: Number(event.target.value) as 1 | 2 | 3 })}><option value="1">1 hop</option><option value="2">2 hops</option><option value="3">3 hops</option></select></label>
        <button type="button" onClick={focusDependencies} disabled={selectedId == null}>Focus neighborhood</button>
        <label>Path target <select aria-label="Path target" value={graphState.yggPathTargetId ?? ''} onChange={(event) => onGraphStateChange({ ...graphState, yggPathTargetId: event.target.value || null })}><option value="">Select target</option>{visibleNodes.filter((node) => node.id !== selectedId).map((node) => <option key={node.id} value={node.id}>{node.label}</option>)}</select></label>
        <button type="button" onClick={highlightPath} disabled={selectedId == null || graphState.yggPathTargetId == null}>Show path</button>
        <button type="button" onClick={highlightRoutes}>Highlight routes</button>
        <label><input type="checkbox" checked={graphState.yggDiffOverlay} onChange={(event) => onGraphStateChange({ ...graphState, yggDiffOverlay: event.target.checked })} />Change overlay</label>
        <button type="button" onClick={resetGraph}>Fit graph</button>
      </div>
      <div className="topology-summary" role="status">Showing {visibleNodes.length} of {nodes.length} nodes and {visibleEdges.length} of {edges.length} edges. {enriched == null ? 'v0.2 fallback.' : `${enriched.summary.unresolved_node_count} unresolved; ${enriched.summary.stale_entity_count} stale; ${enriched.summary.inferred_edge_count} inferred edges.`}</div>
      {visibleNodes.length === 0 ? (
        <EmptyState title="No matching topology" detail="Adjust the search or entity filters." />
      ) : (
        <div className="topology-workspace">
          <TopologyCanvas
            elements={elements}
            selectedId={selectedId}
            onSelect={(id) => onGraphStateChange({ ...graphState, yggSelectedId: id })}
            onReady={captureCore}
          />
          <aside className="selection-inspector" aria-live="polite">
            {selected == null ? (
              <EmptyState title="Select a node" detail="Inspect status, provenance, and route context." />
            ) : (
              <>
                <span className="entity-label">{selected.node_class}</span>
                <h2>{selected.label}</h2>
                <dl>
                  <dt>Status</dt><dd>{selected.status}</dd>
                  <dt>Source</dt><dd>{selected.source_ref}</dd>
                  <dt>Provenance</dt><dd>{selected.provenance}</dd>
                  <dt>Confidence</dt><dd>{selected.confidence}</dd>
                  <dt>Resolution</dt><dd>{selected.resolution_state}</dd>
                  <dt>Freshness</dt><dd>{selected.freshness}</dd>
                </dl>
                <h3>Evidence</h3>
                {selectedEvidence.length === 0 ? <p className="inspector-muted">No embedded evidence records.</p> : selectedEvidence.map((record) => <details key={record.id} className="evidence-drilldown"><summary>{record.id}</summary><code>{record.path}</code><span>{record.integrity_state}</span><code>{record.content_sha256 ?? 'NOT_COMPUTABLE'}</code></details>)}
              </>
            )}
          </aside>
        </div>
      )}
      <footer className="view-footer">{visibleNodes.length} nodes · {visibleEdges.length} edges · projection only</footer>
    </section>
  );
}

function contractElements(contract: OperatorPlatformContract | null): ElementDefinition[] {
  if (contract == null) return [];
  const elements: ElementDefinition[] = [
    {
      data: {
        id: contract.id,
        label: contract.id.split('.').slice(-1)[0],
        color: ENTITY_COLORS.CONTRACT,
      },
    },
  ];
  const relations: Array<[string, string[], string]> = [
    ['PRODUCES', contract.producers, ENTITY_COLORS.SYSTEM],
    ['VALIDATES', contract.validators, ENTITY_COLORS.RECEIPT],
    ['CONSUMES', contract.consumers, ENTITY_COLORS.ROUTE],
  ];
  for (const [relation, values, color] of relations) {
    values.forEach((value, index) => {
      const id = `${relation}:${value}`;
      elements.push({ data: { id, label: value, color } });
      elements.push({
        data: {
          id: `${relation}:${index}:${contract.id}`,
          source: relation === 'PRODUCES' ? id : contract.id,
          target: relation === 'PRODUCES' ? contract.id : id,
        },
      });
    });
  }
  return elements;
}

function ContractsView({ platform, graphState, onGraphStateChange }: { platform: OperatorPlatformProjection } & GraphStateProps): JSX.Element {
  const query = graphState.contractQuery;
  const selectedId = graphState.contractSelectedId;
  const graph = platform.contract_graph.payload;
  const contracts = graph?.contracts ?? [];
  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return contracts.filter((contract) =>
      normalized.length === 0 || contract.id.toLowerCase().includes(normalized) ||
      contract.owner.toLowerCase().includes(normalized),
    ).slice(0, 150);
  }, [contracts, query]);
  const selected = contracts.find((contract) => contract.id === selectedId) ?? filtered[0] ?? null;
  return (
    <section className="operator-view" aria-labelledby="contracts-heading">
      <div className="view-heading-row">
        <div><span className="view-kicker">Producer · contract · validator · consumer</span><h1 id="contracts-heading">Contract graph</h1></div>
        <SourceState state={platform.contract_graph.status} />
      </div>
      <SectionFindings findings={platform.contract_graph.validation_findings} />
      <div className="metric-strip">
        <div><strong>{graph?.contract_count ?? 0}</strong><span>Contracts</span></div>
        <div><strong>{graph?.unowned_count ?? 0}</strong><span>Unowned</span></div>
        <div><strong>{graph?.unvalidated_count ?? 0}</strong><span>Unvalidated</span></div>
      </div>
      <label className="search-field contract-search"><span>Search contracts or owners</span><input value={query} onChange={(event) => onGraphStateChange({ ...graphState, contractQuery: event.target.value })} /></label>
      <div className="contract-workspace">
        <div className="contract-table-wrap">
          <table className="contract-table">
            <thead><tr><th>Contract</th><th>Owner</th><th>Validation</th><th>Reachability</th></tr></thead>
            <tbody>{filtered.map((contract) => (
              <tr key={contract.id} onClick={() => onGraphStateChange({ ...graphState, contractSelectedId: contract.id })} className={selected?.id === contract.id ? 'is-selected' : ''}>
                <td><button type="button" onClick={() => onGraphStateChange({ ...graphState, contractSelectedId: contract.id })}>{contract.id}</button></td>
                <td className={!contract.owner_resolved ? 'finding-text' : ''}>{contract.owner}</td>
                <td className={contract.validators.length === 0 ? 'finding-text' : ''}>{contract.validation_mode}</td>
                <td>{contract.production_reachability}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
        <div className="contract-graph-panel">
          {selected == null ? <EmptyState title="No contracts" detail="No contract evidence matched the current search." /> : (
            <>
              <h2>{selected.id.split('.').slice(-1)[0]}</h2>
              <TopologyCanvas elements={contractElements(selected)} selectedId={selected.id} onSelect={() => undefined} layoutName="breadthfirst" />
              <code>{selected.owner}</code>
            </>
          )}
        </div>
      </div>
      <footer className="view-footer">Showing {filtered.length} of {contracts.length} contracts</footer>
    </section>
  );
}

export function OperatorPlatformGraphViewPanel({
  view,
  platform,
  topologyProjection,
  graphState,
  onGraphStateChange,
}: {
  view: 'yggdrasil' | 'contracts';
  platform: OperatorPlatformProjection;
  topologyProjection?: YggdrasilTopologyProjection;
} & GraphStateProps): JSX.Element {
  if (view === 'yggdrasil') return <YggdrasilView platform={platform} topologyProjection={topologyProjection} graphState={graphState} onGraphStateChange={onGraphStateChange} />;
  return <ContractsView platform={platform} graphState={graphState} onGraphStateChange={onGraphStateChange} />;
}
