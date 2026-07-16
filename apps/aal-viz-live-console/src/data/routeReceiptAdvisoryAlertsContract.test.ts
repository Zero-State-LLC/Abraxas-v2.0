import { describe, expect, it } from 'vitest';
import bundleJson from '../../public/projection-bundle.json';
import type { LiveConsoleProjectionBundle } from '../types';
import { validateRouteReceiptAdvisoryAlertsProjection } from './routeReceiptAdvisoryAlertsContract';

const bundle = bundleJson as unknown as LiveConsoleProjectionBundle;

function fixture() {
  const value = bundle.route_receipt_advisory_alerts;
  if (value == null) throw new Error('generated advisory alerts fixture is missing');
  return structuredClone(value);
}

describe('ROUTE_RECEIPT advisory alerts runtime contract', () => {
  it('accepts the generated v1.140.0 suppression projection', () => {
    const alerts = fixture();
    expect(validateRouteReceiptAdvisoryAlertsProjection(
      alerts,
      bundle.yggdrasil_topology_delta_intelligence,
      bundle.yggdrasil_topology,
    )).toBeNull();
    expect(alerts.summary.active_count).toBe(0);
    expect(alerts.summary.suppressed_count).toBe(162);
    expect(alerts.summary.published_receipt_count).toBe(0);
  });

  it('rejects authority, binding, path, and policy tampering', () => {
    const authority = fixture();
    authority.authority.notification_delivery_allowed = true as false;
    expect(validateRouteReceiptAdvisoryAlertsProjection(authority)).toMatch(/projection locks/);

    const stale = fixture();
    stale.generation.delta_generation_id = 'f'.repeat(64);
    expect(validateRouteReceiptAdvisoryAlertsProjection(
      stale, bundle.yggdrasil_topology_delta_intelligence,
    )).toMatch(/delta generation is stale/);

    const path = fixture();
    path.source_artifacts[0].path = '../alerts.json';
    expect(validateRouteReceiptAdvisoryAlertsProjection(path)).toMatch(/source/);

    const policy = fixture();
    policy.policy.cooldown_seconds = 1 as 86400;
    expect(validateRouteReceiptAdvisoryAlertsProjection(policy)).toMatch(/policy/);
  });

  it('rejects score-tier, suppression, resolution, and acknowledgement tampering', () => {
    const score = fixture();
    const candidate = score.sections.suppressed_candidates.entries?.[0];
    if (candidate == null) throw new Error('suppressed fixture is missing');
    candidate.score_tier = 'CRITICAL';
    expect(validateRouteReceiptAdvisoryAlertsProjection(score)).toMatch(/malformed/);

    const suppression = fixture();
    const suppressed = suppression.sections.suppressed_candidates.entries?.[0];
    if (suppressed == null) throw new Error('suppressed fixture is missing');
    suppressed.suppression_reasons = [];
    expect(validateRouteReceiptAdvisoryAlertsProjection(suppression)).toMatch(/suppression semantics/);

    const resolution = fixture();
    const record = structuredClone(resolution.sections.suppressed_candidates.entries?.[0]);
    if (record == null) throw new Error('suppressed fixture is missing');
    record.lifecycle = 'RESOLVED';
    record.event_type = 'RESOLVED';
    record.receipt_disposition = 'PUBLISH';
    record.suppression_reasons = [];
    resolution.sections.suppressed_candidates.entries = [];
    resolution.sections.resolved_alerts.entries = [record];
    expect(validateRouteReceiptAdvisoryAlertsProjection(resolution)).toMatch(/false resolution/);

    const acknowledgement = fixture();
    const acknowledged = acknowledgement.sections.suppressed_candidates.entries?.[0];
    if (acknowledged == null) throw new Error('suppressed fixture is missing');
    acknowledged.acknowledged = true;
    acknowledged.acknowledgement_ref = `ack:${'1'.repeat(64)}`;
    acknowledgement.generation.acknowledgement_generation_id = '2'.repeat(64);
    expect(validateRouteReceiptAdvisoryAlertsProjection(acknowledgement)).toBeNull();
    expect(acknowledged.receipt_disposition).toBe('SUPPRESS');
  });
});
