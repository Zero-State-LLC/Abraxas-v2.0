import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OperatorNarrativeReportPanel } from './OperatorNarrativeReportPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';
import type { LiveConsoleProjectionBundle, OperatorNarrativeReportPacket } from '../types';

const operatorNarrativeReport: OperatorNarrativeReportPacket = {
  packet_type: 'OperatorNarrativeReportUIOverlay.v1',
  final_status: 'BLOCKED',
  overlay_posture: 'BLOCKED',
  report_overlay_summary: {
    report_final_status: 'NOT_COMPUTABLE',
    report_posture: 'NOT_COMPUTABLE',
    blocker_count: 2,
    section_count: 2,
  },
  section_navigation: [
    { section_id: 'weather_routing', title: 'Weather + Routing', status: 'OBSERVED', index: 0 },
    { section_id: 'blockers', title: 'Blockers', status: 'OBSERVED', index: 1 },
  ],
  overlay_cards: [
    {
      card_id: 'card.section.weather_routing',
      title: 'Weather + Routing',
      status: 'OBSERVED',
      observed_fields: { routing_posture: 'BLOCKED' },
    },
    {
      card_id: 'card.report_blockers',
      title: 'Blocker Summary',
      blocker_count: 2,
      blocker_summary: ['blocker-a', 'blocker-b'],
    },
  ],
  governance_flags: {
    advisory_only: true,
    projection_only: true,
  },
};

describe('OperatorNarrativeReportPanel', () => {
  it('renders fallback posture when narrative overlay is absent', () => {
    render(<OperatorNarrativeReportPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('operator-narrative-report-panel')).toBeInTheDocument();
    expect(screen.getByTestId('operator-narrative-empty')).toBeInTheDocument();
    expect(screen.getByTestId('operator-narrative-advisory-notice')).toBeInTheDocument();
    expect(screen.getByText(/fallback absent/i)).toBeInTheDocument();
  });

  it('renders P44 artifact sections and degraded caption when present', () => {
    const bundle: LiveConsoleProjectionBundle = {
      ...sampleProjectionBundle,
      operator_narrative_report: operatorNarrativeReport,
    };
    render(<OperatorNarrativeReportPanel bundle={bundle} />);

    expect(screen.getByText(/p44 artifact/i)).toBeInTheDocument();
    expect(screen.getByText(/2 sections · 2 blockers/i)).toBeInTheDocument();
    expect(screen.getByTestId('operator-narrative-sections')).toBeInTheDocument();
    expect(screen.getAllByText('Weather + Routing').length).toBeGreaterThan(0);
    expect(screen.getByTestId('operator-narrative-blockers')).toBeInTheDocument();
    expect(screen.getByText('blocker-a')).toBeInTheDocument();
  });
});
