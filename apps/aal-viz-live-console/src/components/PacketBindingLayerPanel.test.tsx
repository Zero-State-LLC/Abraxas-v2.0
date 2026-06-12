import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { PacketBindingLayerPanel } from './PacketBindingLayerPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

afterEach(cleanup);

describe('PacketBindingLayerPanel', () => {
  it('renders binding summary, records, Notion map, stream, and locks', () => {
    render(<PacketBindingLayerPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('packet-binding-layer-panel')).toBeInTheDocument();
    expect(screen.getByTestId('packet-binding-summary')).toBeInTheDocument();
    expect(screen.getByTestId('packet-binding-records')).toBeInTheDocument();
    expect(screen.getByTestId('packet-binding-notion-map')).toBeInTheDocument();
    expect(screen.getByTestId('packet-binding-stream')).toBeInTheDocument();
    expect(screen.getByTestId('packet-binding-locks')).toBeInTheDocument();
  });

  it('keeps missing Notion deep links not-computable', () => {
    render(<PacketBindingLayerPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('packet-binding-summary').textContent).toContain('NOTION LINKS NOT_COMPUTABLE');
    expect(screen.getByTestId('packet-binding-notion-map').textContent).toContain('NOT_COMPUTABLE');
    expect(screen.queryByRole('link', { name: 'OPEN' })).not.toBeInTheDocument();
  });

  it('does not expose writer, websocket mutation, scoring, validation, or promotion controls', () => {
    render(<PacketBindingLayerPanel bundle={sampleProjectionBundle} />);

    const buttons = screen.queryAllByRole('button');
    expect(buttons).toHaveLength(0);

    const locks = screen.getByTestId('packet-binding-locks');
    expect(locks.textContent).toContain('NOTION WRITER ENABLEDFALSE');
    expect(locks.textContent).toContain('WEBSOCKET BROADCAST ENABLEDFALSE');
    expect(locks.textContent).toContain('WS MUTATES SOURCE FIELDSFALSE');
    expect(locks.textContent).toContain('SELECTION PROMOTESFALSE');
    expect(locks.textContent).toContain('SELECTION VALIDATESFALSE');
    expect(locks.textContent).toContain('SELECTION SCORESFALSE');
  });
});

