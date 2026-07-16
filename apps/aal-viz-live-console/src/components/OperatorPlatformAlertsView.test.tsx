import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import bundleJson from '../../public/projection-bundle.json';
import type { LiveConsoleProjectionBundle } from '../types';
import OperatorPlatformAlertsView from './OperatorPlatformAlertsView';

const bundle = bundleJson as unknown as LiveConsoleProjectionBundle;

describe('OperatorPlatformAlertsView', () => {
  it('groups, filters, and inspects the generated suppression corpus', async () => {
    const user = userEvent.setup();
    render(
      <OperatorPlatformAlertsView
        alerts={bundle.route_receipt_advisory_alerts}
        deltaIntelligence={bundle.yggdrasil_topology_delta_intelligence}
        onOpenInYggdrasil={vi.fn()}
      />,
    );
    expect(screen.getByRole('heading', { name: 'Alerts' })).toBeInTheDocument();
    expect(screen.getByText('No matching alerts')).toBeInTheDocument();
    await user.click(screen.getByRole('tab', { name: 'Suppressed' }));
    expect(screen.getAllByText(/BELOW_SCORE_THRESHOLD/).length).toBeGreaterThan(0);
    await user.selectOptions(screen.getByLabelText('Severity'), 'INFO');
    expect(screen.getByText(/Persistent info integrity finding/i)).toBeInTheDocument();
  });

  it('opens embedded alert evidence in YGGDRASIL without acknowledgement writeback', async () => {
    const user = userEvent.setup();
    const onOpen = vi.fn();
    render(
      <OperatorPlatformAlertsView
        alerts={bundle.route_receipt_advisory_alerts}
        deltaIntelligence={bundle.yggdrasil_topology_delta_intelligence}
        onOpenInYggdrasil={onOpen}
      />,
    );
    await user.click(screen.getByRole('tab', { name: 'Suppressed' }));
    const buttons = screen.getAllByRole('button', { name: 'Open in YGGDRASIL' });
    await user.click(buttons[0]);
    expect(onOpen).toHaveBeenCalledWith(expect.stringMatching(/^alert:/), expect.any(String));
    expect(screen.queryByRole('button', { name: /acknowledge/i })).not.toBeInTheDocument();
  });

  it('renders a visible fallback when the optional sidecar is absent', () => {
    render(<OperatorPlatformAlertsView onOpenInYggdrasil={vi.fn()} />);
    expect(screen.getByText('Alert projection unavailable')).toBeInTheDocument();
  });
});
