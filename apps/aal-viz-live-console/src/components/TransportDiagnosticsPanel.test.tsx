import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TransportDiagnosticsPanel } from './TransportDiagnosticsPanel';

describe('TransportDiagnosticsPanel', () => {
  it('renders display-only live transport diagnostics', () => {
    render(
      <TransportDiagnosticsPanel
        status="POLLING_FALLBACK"
        transportMode="POLLING"
        reconnectAttempts={2}
        retryDelayMs={4000}
        lastErrorReason="SOCKET_CLOSED"
        fallbackReason="SOCKET_CLOSED"
        lastUpdated="2026-07-06T00:00:00.000Z"
      />,
    );

    expect(screen.getByTestId('transport-diagnostics-panel')).toBeInTheDocument();
    expect(screen.getByText('POLLING FALLBACK')).toBeInTheDocument();
    expect(screen.getByText('MODE POLLING')).toBeInTheDocument();
    expect(screen.getByText('RETRIES 2')).toBeInTheDocument();
    expect(screen.getByText('RETRY DELAY 4000MS')).toBeInTheDocument();
    expect(screen.getAllByText('SOCKET_CLOSED')).toHaveLength(2);
    expect(screen.getByText(/Display-only transport posture/i)).toBeInTheDocument();
  });

  it('fails closed when optional diagnostics are absent', () => {
    render(
      <TransportDiagnosticsPanel
        status="SAMPLE_FALLBACK"
        transportMode="SAMPLE"
        reconnectAttempts={0}
        retryDelayMs={null}
        lastErrorReason={null}
        fallbackReason={null}
        lastUpdated={null}
      />,
    );

    expect(screen.getByText('SAMPLE FALLBACK')).toBeInTheDocument();
    expect(screen.getByText('MODE SAMPLE')).toBeInTheDocument();
    expect(screen.getByText('RETRY DELAY NONE')).toBeInTheDocument();
    expect(screen.getByText('NOT_COMPUTABLE')).toBeInTheDocument();
    expect(screen.getAllByText('NONE').length).toBeGreaterThanOrEqual(2);
  });

  it('does not render action controls', () => {
    render(
      <TransportDiagnosticsPanel
        status="LIVE_STREAM"
        transportMode="WEBSOCKET"
        reconnectAttempts={0}
        retryDelayMs={null}
        lastErrorReason={null}
        fallbackReason={null}
        lastUpdated="2026-07-06T00:00:00.000Z"
      />,
    );

    expect(screen.queryAllByRole('button')).toHaveLength(0);
  });
});
