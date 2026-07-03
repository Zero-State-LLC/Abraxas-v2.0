import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import App from './App';
import { sampleProjectionBundle } from './data/sampleProjectionBundle';
import { loadProjectionBundle } from './data/loadProjectionBundle';
import { loadOperatorActionPackets } from './data/loadOperatorActionPackets';

vi.mock('./data/loadProjectionBundle', () => ({
  loadProjectionBundle: vi.fn(),
}));
vi.mock('./data/loadOperatorActionPackets', () => ({
  loadOperatorActionPackets: vi.fn(),
}));
vi.mock('./data/liveProjectionFeed', () => ({
  resolveProjectionFeedConfig: vi.fn(() => ({ wsUrl: null, pollMs: 5000 })),
  startProjectionFeed: vi.fn(() => vi.fn()),
}));

describe('App — smoke', () => {
  beforeEach(() => {
    vi.mocked(loadProjectionBundle).mockResolvedValue({
      bundle: sampleProjectionBundle,
      source_mode: 'SAMPLE_FALLBACK',
      fail_closed_reason: null,
    });
    vi.mocked(loadOperatorActionPackets).mockResolvedValue(null);
  });

  it('renders without crashing', () => {
    render(<App />);
    expect(document.body).toBeTruthy();
  });

  it('renders the console title', () => {
    render(<App />);
    expect(screen.getByText(/AAL-VIZ LIVE CONSOLE/i)).toBeInTheDocument();
  });

  it('renders the combined live posture panel', () => {
    render(<App />);
    expect(
      screen.getByTestId('combined-health-migration-artifact-panel'),
    ).toBeInTheDocument();
  });

  it('shows a source-mode indicator', () => {
    render(<App />);
    const indicator = screen.getByTestId('source-mode-indicator');
    expect(indicator).toBeInTheDocument();
    expect(indicator.textContent).toBeTruthy();
  });

  it('shows SAMPLE FALLBACK source mode (initial state)', () => {
    render(<App />);
    const indicator = screen.getByTestId('source-mode-indicator');
    expect(indicator.textContent).toMatch(/SAMPLE FALLBACK/i);
  });

  it('shows feed connection posture', () => {
    render(<App />);
    const indicator = screen.getByTestId('connection-status-indicator');
    expect(indicator.textContent).toMatch(/SAMPLE FALLBACK/i);
  });

  it('shows feed transport diagnostics', () => {
    render(<App />);
    const details = screen.getByTestId('feed-transport-details');
    expect(details.textContent).toMatch(/TRANSPORT SAMPLE/i);
    expect(details.textContent).toMatch(/RETRY DELAY NONE/i);
  });

  it('renders 10 systems in the spine grid from initial state', () => {
    render(<App />);
    const spineItems = document.querySelectorAll('.spine-item__name');
    const spineNames = Array.from(spineItems).map((el) => el.textContent ?? '');
    const expectedNames = [
      'NEON GENIE',
      'PSE',
      'HOLLERSPORTS',
      'LEVEL99',
      'NOCTIS',
      'BEATOVEN',
      'PHONOMICON',
      'PSYFI',
      'PATCHHIVE',
      'GLOBAL SPINE REGISTRY',
    ];
    for (const name of expectedNames) {
      expect(spineNames).toContain(name);
    }
  });

  it('has exactly 10 spine grid items', () => {
    render(<App />);
    const listItems = document.querySelectorAll('.spine-item');
    expect(listItems.length).toBe(10);
  });

  it('renders the AuthorityBoundaryPanel', () => {
    render(<App />);
    expect(screen.getByTestId('authority-boundary-panel')).toBeInTheDocument();
  });

  it('renders the migration runner posture panel', () => {
    render(<App />);
    expect(screen.getByTestId('migration-runner-posture-panel')).toBeInTheDocument();
  });

  it('renders the OperatorActionPacketPanel', () => {
    render(<App />);
    expect(screen.getByTestId('operator-action-packet-panel')).toBeInTheDocument();
  });

  it('has no enabled execute/promote/mutate buttons', () => {
    render(<App />);
    const allButtons = screen.getAllByRole('button');
    const dangerLabels = ['promote', 'execute', 'mutate', 'activate production', 'publish'];
    const enabledDanger = allButtons.filter((btn) => {
      const label = (btn.textContent ?? '').toLowerCase();
      return dangerLabels.some((d) => label.includes(d)) && !btn.hasAttribute('disabled');
    });
    expect(enabledDanger).toHaveLength(0);
  });

  it('resolves effects without errors', async () => {
    await act(async () => {
      render(<App />);
    });
    expect(screen.getByTestId('source-mode-indicator')).toBeInTheDocument();
  });
});
