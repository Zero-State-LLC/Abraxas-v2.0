import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { WorkflowOperatorAnalyticsPanel } from './WorkflowOperatorAnalyticsPanel';
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

describe('WorkflowOperatorAnalyticsPanel', () => {
  it('renders analytics, performance, visual mapping, and lock sections', () => {
    render(<WorkflowOperatorAnalyticsPanel bundle={sampleProjectionBundle} packetsBundle={SAMPLE_PACKETS} />);

    expect(screen.getByTestId('workflow-operator-analytics-panel')).toBeInTheDocument();
    expect(screen.getByTestId('workflow-analytics-summary')).toHaveTextContent('DESCRIPTIVE ANALYTICS');
    expect(screen.getByTestId('workflow-bottleneck-panel')).toHaveTextContent('BOTTLENECK STEP');
    expect(screen.getByTestId('review-aging-panel')).toHaveTextContent('STALE REVIEW RATE');
    expect(screen.getByTestId('suggestion-effectiveness-panel')).toHaveTextContent('ACCEPTANCE RATE');
    expect(screen.getByTestId('operator-performance-dashboard')).toHaveTextContent('OPERATOR PERFORMANCE FEEDBACK');
    expect(screen.getByTestId('operator-calibration-panel')).toHaveTextContent('RANK AUTHORITYFALSE');
    expect(screen.getByTestId('override-outcome-panel')).toHaveTextContent('PENDING');
    expect(screen.getByTestId('correction-quality-panel')).toHaveTextContent('HASH PRESERVATIONTRUE');
    expect(screen.getByTestId('operator-feedback-visual-mapping')).toHaveTextContent('workflow_bottleneck');
  });

  it('does not expose controls or analytics authority paths', () => {
    render(<WorkflowOperatorAnalyticsPanel bundle={sampleProjectionBundle} packetsBundle={SAMPLE_PACKETS} />);

    const panel = screen.getByTestId('workflow-operator-analytics-panel');
    expect(within(panel).queryAllByRole('button')).toHaveLength(0);

    const locks = screen.getByTestId('workflow-analytics-locks');
    expect(locks).toHaveTextContent('NOTION WRITEFALSE');
    expect(locks).toHaveTextContent('WEBSOCKETFALSE');
    expect(locks).toHaveTextContent('AUTO EXECUTIONFALSE');
    expect(locks).toHaveTextContent('PROMOTIONFALSE');
    expect(locks).toHaveTextContent('FORECAST MUTATIONFALSE');
    expect(locks).toHaveTextContent('PROVIDER AUTHORITYFALSE');
    expect(locks).toHaveTextContent('ROUTING MUTATIONFALSE');
    expect(locks).toHaveTextContent('TRUTH AUTHORITYFALSE');
  });
});
