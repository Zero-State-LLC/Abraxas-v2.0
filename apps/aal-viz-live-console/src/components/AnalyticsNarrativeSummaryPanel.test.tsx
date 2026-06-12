import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { AnalyticsNarrativeSummaryPanel } from './AnalyticsNarrativeSummaryPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';
import type { OperatorActionPacketsBundle } from '../types';

const SAMPLE_PACKETS: OperatorActionPacketsBundle = {
  schema_version: 'AALViz.OperatorActionPackets.v0.1',
  generated_at: '2026-05-30T00:00:00Z',
  authority: {
    execution_allowed: false,
    runtime_mutation_allowed: false,
    promotion_allowed: false,
    production_activation_allowed: false,
    metric_emission_allowed: false,
    forecast_influence_allowed: false,
    p43_lanes_allowed: false,
  },
  source_projection_bundle_hash: null,
  fail_closed_reason: null,
  packets: [],
};

describe('AnalyticsNarrativeSummaryPanel', () => {
  it('renders briefing card, findings, templates, gaps, prompts, and flow', () => {
    render(<AnalyticsNarrativeSummaryPanel bundle={sampleProjectionBundle} packetsBundle={SAMPLE_PACKETS} />);

    expect(screen.getByTestId('analytics-narrative-summary-panel')).toBeInTheDocument();
    expect(screen.getByTestId('narrative-briefing-card')).toHaveTextContent('NARRATIVE_COMPRESSION_ONLY');
    expect(screen.getByTestId('narrative-findings')).toHaveTextContent('PROVENANCE-LABELED FINDINGS');
    expect(screen.getByTestId('narrative-template-rules')).toHaveTextContent('DETERMINISTIC TEMPLATE RULES');
    expect(screen.getByTestId('narrative-gap-list')).toHaveTextContent('Operator Feedback');
    expect(screen.getByTestId('narrative-review-prompts')).toHaveTextContent('REVIEW PROMPTS ONLY');
    expect(screen.getByTestId('narrative-generation-flow')).toHaveTextContent('gap_detection');
    expect(screen.getByTestId('narrative-source-packets')).toHaveTextContent('workflow-analytics-latest');
    expect(screen.getByTestId('narrative-confidence-rules')).toHaveTextContent('CONFIDENCE CAPPEDTRUE');
  });

  it('does not expose action controls or narrative authority paths', () => {
    render(<AnalyticsNarrativeSummaryPanel bundle={sampleProjectionBundle} packetsBundle={SAMPLE_PACKETS} />);

    const panel = screen.getByTestId('analytics-narrative-summary-panel');
    expect(within(panel).queryAllByRole('button')).toHaveLength(0);

    const locks = screen.getByTestId('narrative-summary-locks');
    expect(locks).toHaveTextContent('NOTION WRITEFALSE');
    expect(locks).toHaveTextContent('WEBSOCKETFALSE');
    expect(locks).toHaveTextContent('AUTO EXECUTIONFALSE');
    expect(locks).toHaveTextContent('OUTCOME RESOLVEFALSE');
    expect(locks).toHaveTextContent('FORECAST MUTATIONFALSE');
    expect(locks).toHaveTextContent('SCORE MUTATIONFALSE');
    expect(locks).toHaveTextContent('ROUTING MUTATIONFALSE');
    expect(locks).toHaveTextContent('TRUTH AUTHORITYFALSE');
  });
});
