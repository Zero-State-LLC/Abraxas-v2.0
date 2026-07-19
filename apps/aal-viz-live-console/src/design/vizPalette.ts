/**
 * Console bridge to Abraxas Visual OS topology palette.
 * Keep hex values aligned with design-system/viz/topology_palette.v1.json.
 */

export const VIZ_CANVAS = {
  background: '#0b1417',
  nodeLabel: '#e7f0f2',
  nodeBorder: '#071013',
  edgeDefault: '#46606a',
  selection: '#f2c14e',
  dimmedOpacity: 0.12,
  white: '#ffffff',
  unresolved: '#f2c14e',
  stale: '#fb7185',
  inferredBorder: '#7dd3fc',
  diffAdded: '#86efac',
  alertUnderlay: '#f59e0b',
} as const;

/** Topology node class → fill (Yggdrasil + operator entities). */
export const NODE_CLASS_COLORS = {
  SYSTEM: '#2dd4bf',
  RUNE: '#f2c14e',
  CONTRACT: '#7dd3fc',
  PACKET: '#c4b5fd',
  RECEIPT: '#86efac',
  ROUTE: '#fb7185',
  INTERFACE: '#f8fafc',
} as const;

export const INTEGRITY_COLORS = {
  HIGH: '#ef4444',
  MEDIUM: '#f2c14e',
  LOW: '#7dd3fc',
  INFO: '#38bdf8',
  NOT_COMPUTABLE: '#a78bfa',
} as const;

export const CONFIDENCE_COLORS = {
  VERIFIED: '#10b981',
  SUPPORTED: '#00d4f5',
  INFERRED: '#a78bfa',
  NOT_COMPUTABLE: '#94a3b8',
} as const;

export const REGISTER_LINK_COLORS = {
  OBSERVED_LINK: '#065f46',
  INFERRED_LINK: '#0891b2',
  SPECULATIVE_LINK: '#b45309',
} as const;

export const TELEMETRY_SERIES = [
  '#00d4f5',
  '#2dd4bf',
  '#f2c14e',
  '#c084fc',
  '#fb7185',
] as const;

/** Build Cytoscape stylesheet fragments using Visual OS palette. */
export function buildTopologyCytoscapeStyle(): Array<{ selector: string; style: Record<string, string | number> }> {
  const c = VIZ_CANVAS;
  const i = INTEGRITY_COLORS;
  return [
    {
      selector: 'node',
      style: {
        'background-color': 'data(color)',
        'border-color': c.nodeBorder,
        'border-width': 2,
        color: c.nodeLabel,
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
        'line-color': c.edgeDefault,
        'target-arrow-color': c.edgeDefault,
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        opacity: 0.72,
      },
    },
    {
      selector: ':selected',
      style: {
        'border-color': c.white,
        'border-width': 4,
        'line-color': c.selection,
        'target-arrow-color': c.selection,
        opacity: 1,
      },
    },
    { selector: '.dimmed', style: { opacity: c.dimmedOpacity } },
    { selector: '.unresolved', style: { 'border-color': c.unresolved, 'border-style': 'dashed' } },
    { selector: '.stale', style: { 'border-color': c.stale, 'line-style': 'dashed' } },
    { selector: '.inferred', style: { 'border-color': c.inferredBorder, 'line-style': 'dotted' } },
    { selector: '.diff-added', style: { 'border-color': c.diffAdded, 'border-width': 4 } },
    {
      selector: '.diff-removed',
      style: {
        opacity: 0.48,
        'border-color': c.stale,
        'border-style': 'dashed',
        'line-style': 'dashed',
      },
    },
    {
      selector: '.integrity-high',
      style: {
        'border-color': i.HIGH,
        'border-width': 5,
        'line-color': i.HIGH,
        'target-arrow-color': i.HIGH,
      },
    },
    {
      selector: '.integrity-medium',
      style: {
        'border-color': i.MEDIUM,
        'border-width': 4,
        'line-color': i.MEDIUM,
        'target-arrow-color': i.MEDIUM,
      },
    },
    { selector: '.integrity-low', style: { 'border-color': i.LOW, 'border-width': 3 } },
    {
      selector: '.integrity-not-computable',
      style: {
        'border-color': i.NOT_COMPUTABLE,
        'border-style': 'dashed',
        'line-style': 'dashed',
      },
    },
    {
      selector: '.delta-score-high',
      style: {
        'background-color': i.HIGH,
        'border-color': c.white,
        'border-width': 5,
        'line-color': i.HIGH,
        'target-arrow-color': i.HIGH,
        opacity: 1,
      },
    },
    {
      selector: '.delta-score-medium',
      style: {
        'background-color': i.MEDIUM,
        'border-color': c.white,
        'border-width': 4,
        'line-color': i.MEDIUM,
        'target-arrow-color': i.MEDIUM,
        opacity: 1,
      },
    },
    { selector: '.delta-score-low', style: { 'border-color': i.LOW, 'border-width': 3 } },
    {
      selector: '.alert-active',
      style: {
        'underlay-color': c.alertUnderlay,
        'underlay-opacity': 0.22,
        'underlay-padding': 7,
      },
    },
    {
      selector: '.alert-selected',
      style: {
        'border-color': c.white,
        'border-width': 6,
        'line-color': c.alertUnderlay,
        'target-arrow-color': c.alertUnderlay,
        opacity: 1,
      },
    },
    {
      selector: '.path-highlight',
      style: {
        opacity: 1,
        'line-color': c.selection,
        'target-arrow-color': c.selection,
        'border-color': c.selection,
      },
    },
  ];
}
