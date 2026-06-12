import { describe, expect, it } from 'vitest';
import { buildMetricDashboardFrame } from './buildMetricDashboardFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';

describe('buildMetricDashboardFrame', () => {
  it('builds deterministic visual annotation frames', () => {
    const first = buildMetricDashboardFrame(sampleProjectionBundle);
    const second = buildMetricDashboardFrame(sampleProjectionBundle);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('ABXMetricDashboardFrame.v1');
    expect(first.authority).toBe('SHADOW_ONLY_TRACE');
    expect(first.output_effect).toBe('VISUAL_ANNOTATION_ONLY');
    expect(first.non_filtering_compliance).toBe(true);
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('keeps all dashboard panels visible', () => {
    const frame = buildMetricDashboardFrame(sampleProjectionBundle);

    expect(frame.panels).toHaveLength(9);
    expect(frame.panels).toContain('Core ABX Metric Strip');
    expect(frame.panels).toContain('Non-Filtering Compliance Monitor');
    expect(frame.rendering_locks.no_panel_hiding).toBe(true);
    expect(frame.rendering_locks.raw_layer_always_visible).toBe(true);
  });

  it('guards candidate metrics from canon promotion', () => {
    const frame = buildMetricDashboardFrame(sampleProjectionBundle);

    expect(frame.candidate_metrics).toHaveLength(5);
    expect(frame.candidate_metrics.map((metric) => metric.metric)).toEqual([
      'HCI',
      'ATI',
      'MRI',
      'IPI',
      'SFI',
    ]);
    expect(frame.candidate_metrics.every((metric) => metric.stabilization_window_required)).toBe(true);
    expect(frame.candidate_metrics.every((metric) => metric.canon_promotion_allowed === false)).toBe(true);
  });

  it('locks non-filtering compliance and forecast weight mutation', () => {
    const frame = buildMetricDashboardFrame(sampleProjectionBundle);

    expect(frame.non_filtering_compliance_monitor.output_preserved).toBe(true);
    expect(frame.non_filtering_compliance_monitor.filter_calls_detected).toBe(false);
    expect(frame.non_filtering_compliance_monitor.suppression_calls_detected).toBe(false);
    expect(frame.non_filtering_compliance_monitor.rewrite_calls_detected).toBe(false);
    expect(frame.rendering_locks.no_output_filtering).toBe(true);
    expect(frame.rendering_locks.no_forecast_weight_mutation).toBe(true);
    expect(frame.rendering_locks.max_overlay_opacity).toBe(0.6);
  });
});
