import { describe, expect, it } from 'vitest';
import {
  NODE_CLASS_COLORS,
  buildTopologyCytoscapeStyle,
  CONFIDENCE_COLORS,
  INTEGRITY_COLORS,
} from './vizPalette';

describe('vizPalette Visual OS bridge', () => {
  it('defines colors for all Yggdrasil node classes', () => {
    for (const key of ['SYSTEM', 'RUNE', 'CONTRACT', 'PACKET', 'RECEIPT', 'ROUTE', 'INTERFACE'] as const) {
      expect(NODE_CLASS_COLORS[key]).toMatch(/^#[0-9a-fA-F]{6}$/);
    }
  });

  it('builds cytoscape style with node/edge/selection selectors', () => {
    const style = buildTopologyCytoscapeStyle();
    const selectors = style.map((s) => s.selector);
    expect(selectors).toContain('node');
    expect(selectors).toContain('edge');
    expect(selectors).toContain(':selected');
    expect(selectors).toContain('.integrity-high');
    expect(selectors).toContain('.path-highlight');
  });

  it('maps confidence and integrity to distinct hues', () => {
    expect(new Set(Object.values(CONFIDENCE_COLORS)).size).toBe(4);
    expect(INTEGRITY_COLORS.HIGH).not.toBe(INTEGRITY_COLORS.MEDIUM);
  });
});
