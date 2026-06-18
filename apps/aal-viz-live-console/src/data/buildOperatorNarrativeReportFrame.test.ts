import { describe, expect, it } from 'vitest';
import { buildOperatorNarrativeReportFrame } from './buildOperatorNarrativeReportFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { LiveConsoleProjectionBundle, OperatorNarrativeReportPacket } from '../types';

const operatorNarrativeReport: OperatorNarrativeReportPacket = {
  packet_type: 'OperatorNarrativeReportUIOverlay.v1',
  final_status: 'BLOCKED',
  overlay_posture: 'BLOCKED',
  report_overlay_summary: {
    report_final_status: 'NOT_COMPUTABLE',
    report_posture: 'NOT_COMPUTABLE',
    audit_final_status: 'PASS',
    audit_posture: 'CLEAN',
    blocker_count: 3,
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
      blocker_count: 3,
      blocker_summary: ['blocker-a', 'blocker-b', 'blocker-c'],
    },
  ],
  governance_flags: {
    advisory_only: true,
    projection_only: true,
  },
};

describe('buildOperatorNarrativeReportFrame', () => {
  it('returns fallback frame when operator narrative is absent', () => {
    const frame = buildOperatorNarrativeReportFrame(sampleProjectionBundle);

    expect(frame.source_mode).toBe('FALLBACK_ABSENT');
    expect(frame.section_count).toBe(0);
    expect(frame.sections).toEqual([]);
  });

  it('derives sections and capped blockers from bundle packet', () => {
    const bundle: LiveConsoleProjectionBundle = {
      ...sampleProjectionBundle,
      operator_narrative_report: operatorNarrativeReport,
    };
    const frame = buildOperatorNarrativeReportFrame(bundle);

    expect(frame.source_mode).toBe('P44_ARTIFACT');
    expect(frame.final_status).toBe('BLOCKED');
    expect(frame.section_count).toBe(2);
    expect(frame.sections[0]?.title).toBe('Weather + Routing');
    expect(frame.cards).toHaveLength(1);
    expect(frame.blocker_total).toBe(3);
    expect(frame.blocker_preview).toEqual(['blocker-a', 'blocker-b', 'blocker-c']);
  });
});
