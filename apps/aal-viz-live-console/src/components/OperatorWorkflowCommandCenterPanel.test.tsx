import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { OperatorWorkflowCommandCenterPanel } from './OperatorWorkflowCommandCenterPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';
import { buildOperatorWorkflowCommandCenterFrame } from '../data/buildOperatorWorkflowCommandCenterFrame';
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

describe('OperatorWorkflowCommandCenterPanel', () => {
  it('renders workflow zones, audit preview, timeline, and context panels', () => {
    const frame = buildOperatorWorkflowCommandCenterFrame(sampleProjectionBundle, SAMPLE_PACKETS);
    render(<OperatorWorkflowCommandCenterPanel bundle={sampleProjectionBundle} packetsBundle={SAMPLE_PACKETS} />);

    expect(screen.getByTestId('operator-workflow-command-center-panel')).toBeInTheDocument();
    expect(screen.getByTestId('workflow-command-summary')).toHaveTextContent(`${frame.workflows.length} WORKFLOWS`);
    expect(screen.getByTestId('workflow-inbox-list')).toHaveTextContent('LEFT RAIL');
    expect(screen.getByTestId('workflow-detail-panel')).toHaveTextContent('CENTER');
    expect(screen.getByTestId('workflow-evidence-checklist')).toHaveTextContent('TRUTH VALIDATION FALSE');
    expect(screen.getByTestId('workflow-provider-side-panel')).toHaveTextContent('PROVIDER AUTHORITY');
    expect(screen.getByTestId('workflow-decision-composer')).toHaveTextContent('commit authority FALSE');
    expect(screen.getByTestId('workflow-correction-composer')).toHaveTextContent('score mutation FALSE');
    expect(screen.getByTestId('workflow-audit-preview')).toHaveTextContent('AUDIT PREVIEW BEFORE COMMIT');
    expect(screen.getByTestId('workflow-timeline')).toHaveTextContent('ACTION LOG');
    expect(screen.getByTestId('workflow-command-bar')).toHaveTextContent('static accessibility mode');
    expect(screen.getByTestId('workflow-notion-context-panel')).toHaveTextContent('notion write FALSE');
  });

  it('does not expose interactive command buttons or authority mutation locks', () => {
    render(<OperatorWorkflowCommandCenterPanel bundle={sampleProjectionBundle} packetsBundle={SAMPLE_PACKETS} />);

    const panel = screen.getByTestId('operator-workflow-command-center-panel');
    expect(within(panel).queryAllByRole('button')).toHaveLength(0);

    const locks = screen.getByTestId('workflow-command-locks');
    expect(locks).toHaveTextContent('NOTION WRITEFALSE');
    expect(locks).toHaveTextContent('WEBSOCKETFALSE');
    expect(locks).toHaveTextContent('AUTO EXECUTIONFALSE');
    expect(locks).toHaveTextContent('OUTCOME MUTATIONFALSE');
    expect(locks).toHaveTextContent('CORRECTION APPLYFALSE');
    expect(locks).toHaveTextContent('SCORE MUTATIONFALSE');
    expect(locks).toHaveTextContent('ROUTING MUTATIONFALSE');
    expect(locks).toHaveTextContent('TRUTH AUTHORITYFALSE');
  });
});
