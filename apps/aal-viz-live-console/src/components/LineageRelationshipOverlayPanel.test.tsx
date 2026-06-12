import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { LineageRelationshipOverlayPanel } from './LineageRelationshipOverlayPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

afterEach(cleanup);

describe('LineageRelationshipOverlayPanel', () => {
  it('renders declared nodes, arrows, legend, focus, and authority locks', () => {
    render(<LineageRelationshipOverlayPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('lineage-relationship-overlay-panel')).toBeInTheDocument();
    expect(screen.getByTestId('lineage-node-field')).toBeInTheDocument();
    expect(screen.getByTestId('lineage-edge-list')).toBeInTheDocument();
    expect(screen.getByTestId('lineage-selected-focus')).toBeInTheDocument();
    expect(screen.getByTestId('lineage-link-legend')).toBeInTheDocument();
    expect(screen.getByTestId('lineage-authority-locks')).toBeInTheDocument();
  });

  it('renders all sample systems as selectable display-only nodes', () => {
    render(<LineageRelationshipOverlayPanel bundle={sampleProjectionBundle} />);

    for (const system of sampleProjectionBundle.systems) {
      expect(screen.getByTestId(`lineage-node-${system.system_id}`)).toBeInTheDocument();
    }
  });

  it('updates selection focus without rendering mutation controls', () => {
    render(<LineageRelationshipOverlayPanel bundle={sampleProjectionBundle} />);

    fireEvent.click(screen.getByTestId('lineage-node-noctis'));

    expect(screen.getByTestId('lineage-selected-focus').textContent).toContain('noctis');
    const selectableButtons = screen.queryAllByRole('button');
    expect(
      selectableButtons.some((button) => /mutate|promote/i.test(button.textContent ?? '')),
    ).toBe(false);
  });

  it('shows not-computable link styling for missing relationship source state', () => {
    render(<LineageRelationshipOverlayPanel bundle={sampleProjectionBundle} />);

    const edgeList = screen.getByTestId('lineage-edge-list');
    expect(edgeList.textContent).toContain('NOT_COMPUTABLE_LINK');
  });

  it('shows authority locks as false for scoring, forecasting, validation, promotion, and truth', () => {
    render(<LineageRelationshipOverlayPanel bundle={sampleProjectionBundle} />);
    const locks = screen.getByTestId('lineage-authority-locks');

    expect(locks.textContent).toContain('SCORING AUTHORITYFALSE');
    expect(locks.textContent).toContain('FORECASTING AUTHORITYFALSE');
    expect(locks.textContent).toContain('VALIDATION AUTHORITYFALSE');
    expect(locks.textContent).toContain('PROMOTION AUTHORITYFALSE');
    expect(locks.textContent).toContain('TRUTH AUTHORITYFALSE');
    expect(locks.textContent).toContain('MISSING SOURCE DIMMEDTRUE');
  });
});
