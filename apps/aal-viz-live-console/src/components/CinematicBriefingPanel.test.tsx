import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { CinematicBriefingPanel } from './CinematicBriefingPanel';
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

describe('CinematicBriefingPanel', () => {
  it('renders story blocks, camera path, coaching, snapshots, and script preview', () => {
    render(<CinematicBriefingPanel bundle={sampleProjectionBundle} packetsBundle={SAMPLE_PACKETS} />);

    expect(screen.getByTestId('cinematic-briefing-panel')).toBeInTheDocument();
    expect(screen.getByTestId('briefing-story-blocks')).toHaveTextContent('ANALYTICS STORY BLOCKS');
    expect(screen.getByTestId('briefing-story-blocks')).toHaveTextContent('SOURCE NARRATIVE analytics-narrative-latest');
    expect(screen.getByTestId('briefing-camera-path')).toHaveTextContent('ESTABLISHING');
    expect(screen.getByTestId('briefing-camera-path')).toHaveTextContent('VISUAL');
    expect(screen.getByTestId('briefing-coaching-suggestions')).toHaveTextContent('review only');
    expect(screen.getByTestId('briefing-export-snapshots')).toHaveTextContent('SCRIPT_TEXT');
    expect(screen.getByTestId('briefing-export-snapshots')).toHaveTextContent('file write FALSE');
    expect(screen.getByTestId('briefing-voiceover-script')).toHaveTextContent('Operator Feedback');
  });

  it('does not expose export, execution, or writeback controls', () => {
    render(<CinematicBriefingPanel bundle={sampleProjectionBundle} packetsBundle={SAMPLE_PACKETS} />);

    const panel = screen.getByTestId('cinematic-briefing-panel');
    expect(within(panel).queryAllByRole('button')).toHaveLength(0);

    const locks = screen.getByTestId('briefing-locks');
    expect(locks).toHaveTextContent('STORY FACTSFALSE');
    expect(locks).toHaveTextContent('CAMERA MUTATIONFALSE');
    expect(locks).toHaveTextContent('SNAPSHOT WRITEFALSE');
    expect(locks).toHaveTextContent('VOICEOVER WRITEFALSE');
    expect(locks).toHaveTextContent('NOTION WRITEFALSE');
    expect(locks).toHaveTextContent('WEBSOCKETFALSE');
    expect(locks).toHaveTextContent('AUTO EXECUTIONFALSE');
    expect(locks).toHaveTextContent('TRUTH AUTHORITYFALSE');
  });
});
