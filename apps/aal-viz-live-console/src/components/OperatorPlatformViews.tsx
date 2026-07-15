import { useCallback, useEffect, useMemo, useRef, type CSSProperties, type KeyboardEvent } from 'react';
import cytoscape, { type Core, type ElementDefinition } from 'cytoscape';
import type {
  OperatorPlatformContract,
  OperatorPlatformEntityType,
  OperatorPlatformProjection,
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
    <div
      aria-label={`Interactive projection graph with ${elements.filter((element) => element.data.source == null).length} nodes. Use arrow keys to select nodes and Escape to clear selection.`}
      className="topology-canvas"
      data-testid="topology-canvas"
      onKeyDown={onKeyDown}
      ref={hostRef}
      role="application"
      tabIndex={0}
    />
  );
}

export interface OperatorPlatformGraphState {
  yggQuery: string;
  yggSelectedTypes: OperatorPlatformEntityType[];
  yggSelectedId: string | null;
  contractQuery: string;
  contractSelectedId: string | null;
}

interface GraphStateProps {
  graphState: OperatorPlatformGraphState;
  onGraphStateChange: (state: OperatorPlatformGraphState) => void;
}

function YggdrasilView({ platform, graphState, onGraphStateChange }: { platform: OperatorPlatformProjection } & GraphStateProps): JSX.Element {
  const query = graphState.yggQuery;
  const selectedTypes = useMemo(() => new Set(graphState.yggSelectedTypes), [graphState.yggSelectedTypes]);
  const selectedId = graphState.yggSelectedId;
  const coreRef = useRef<Core | null>(null);
  const topology = platform.topology.payload;
  const nodes = topology?.nodes ?? [];

  const visibleNodes = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return nodes.filter(
      (node) =>
        selectedTypes.has(node.entity_type) &&
        (normalized.length === 0 ||
          node.label.toLowerCase().includes(normalized) ||
          node.source_ref.toLowerCase().includes(normalized)),
    );
  }, [nodes, query, selectedTypes]);
  const visibleIds = useMemo(() => new Set(visibleNodes.map((node) => node.id)), [visibleNodes]);
  const visibleEdges = useMemo(
    () => (topology?.edges ?? []).filter(
      (edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target),
    ),
    [topology?.edges, visibleIds],
  );
  const elements = useMemo<ElementDefinition[]>(
    () => [
      ...visibleNodes.map((node) => ({
        data: {
          id: node.id,
          label: node.label,
          color: ENTITY_COLORS[node.entity_type],
        },
      })),
      ...visibleEdges.map((edge) => ({
        data: { id: edge.id, source: edge.source, target: edge.target, relation: edge.relation },
      })),
    ],
    [visibleEdges, visibleNodes],
  );
  const selected = nodes.find((node) => node.id === selectedId) ?? null;
  const captureCore = useCallback((instance: Core) => {
    coreRef.current = instance;
  }, []);

  const toggleType = (entityType: OperatorPlatformEntityType): void => {
    const next = new Set(selectedTypes);
    if (next.has(entityType)) next.delete(entityType);
    else next.add(entityType);
    onGraphStateChange({ ...graphState, yggSelectedTypes: [...next].sort() });
  };
  const focusDependencies = (): void => {
    const core = coreRef.current;
    if (core == null || selectedId == null) return;
    const selectedNode = core.getElementById(selectedId);
    const neighborhood = selectedNode.closedNeighborhood();
    core.elements().addClass('dimmed');
    neighborhood.removeClass('dimmed');
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) core.fit(neighborhood, 70);
    else core.animate({ fit: { eles: neighborhood, padding: 70 }, duration: 240 });
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
      <div className="topology-toolbar">
        <label className="search-field">
          <span>Search topology</span>
          <input value={query} onChange={(event) => onGraphStateChange({ ...graphState, yggQuery: event.target.value })} />
        </label>
        <div className="entity-filters" aria-label="Entity type filters">
          {(Object.keys(ENTITY_COLORS) as OperatorPlatformEntityType[]).map((entityType) => (
            <label key={entityType} style={{ '--entity-color': ENTITY_COLORS[entityType] } as CSSProperties}>
              <input
                type="checkbox"
                checked={selectedTypes.has(entityType)}
                onChange={() => toggleType(entityType)}
              />
              {entityType}
            </label>
          ))}
        </div>
        <button type="button" onClick={focusDependencies} disabled={selectedId == null}>
          Focus dependencies
        </button>
        <button type="button" onClick={resetGraph}>Fit graph</button>
      </div>
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
                <span className="entity-label">{selected.entity_type}</span>
                <h2>{selected.label}</h2>
                <dl>
                  <dt>Status</dt><dd>{selected.status}</dd>
                  <dt>Source</dt><dd>{selected.source_ref}</dd>
                  <dt>Provenance</dt><dd>{selected.provenance}</dd>
                </dl>
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
  graphState,
  onGraphStateChange,
}: {
  view: 'yggdrasil' | 'contracts';
  platform: OperatorPlatformProjection;
} & GraphStateProps): JSX.Element {
  if (view === 'yggdrasil') return <YggdrasilView platform={platform} graphState={graphState} onGraphStateChange={onGraphStateChange} />;
  return <ContractsView platform={platform} graphState={graphState} onGraphStateChange={onGraphStateChange} />;
}
