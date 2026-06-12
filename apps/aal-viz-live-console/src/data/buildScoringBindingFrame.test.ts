import { describe, expect, it } from 'vitest';
import { buildScoringBindingFrame } from './buildScoringBindingFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { LiveConsoleProjectionBundle } from '../types';

describe('buildScoringBindingFrame', () => {
  it('builds deterministic scoring-ledger projection frames', () => {
    const first = buildScoringBindingFrame(sampleProjectionBundle);
    const second = buildScoringBindingFrame(sampleProjectionBundle);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizScoringBindingFrame.v1');
    expect(first.authority).toBe('SCORING_LEDGER_AND_PROJECTION_ONLY');
    expect(first.promotion_policy).toBe('NO_AUTOMATIC_PROMOTION_FROM_SCORE_ONLY');
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('keeps ordinary projection packets not-computable for Brier scoring', () => {
    const frame = buildScoringBindingFrame(sampleProjectionBundle);

    expect(frame.scoring_records.every((record) => record.scoring_status === 'NOT_COMPUTABLE')).toBe(true);
    expect(frame.scoring_records.every((record) => record.brier_score === null)).toBe(true);
    expect(frame.calibration_summary.scoring_status).toBe('NOT_COMPUTABLE');
    expect(frame.calibration_summary.sample_size).toBe(0);
  });

  it('computes descriptive Brier score only when forecast probability and outcome are both present', () => {
    const bundle: LiveConsoleProjectionBundle = {
      ...sampleProjectionBundle,
      systems: [
        {
          ...sampleProjectionBundle.systems[0],
          projection_packets: [
            {
              packet_id: 'forecast-outcome-pkt-001',
              packet_type: 'FORECAST_OUTCOME_RESOLUTION',
              status: 'RESOLVED',
              display_value: '1',
              authority_source: 'SHADOW_LANE',
              projection_only: true,
            },
          ],
        },
      ],
    };
    const frame = buildScoringBindingFrame(bundle);

    expect(frame.scoring_records[0].join_state).toBe('JOINED');
    expect(frame.scoring_records[0].scoring_status).toBe('SCORED');
    expect(frame.scoring_records[0].brier_score).toBe(0);
    expect(frame.calibration_summary.sample_size).toBe(1);
  });

  it('locks scoring output out of promotion, execution, truth, and weight mutation authority', () => {
    const frame = buildScoringBindingFrame(sampleProjectionBundle);

    expect(frame.scoring_locks.brier_descriptive_only).toBe(true);
    expect(frame.scoring_locks.automatic_promotion_allowed).toBe(false);
    expect(frame.scoring_locks.execution_authority).toBe(false);
    expect(frame.scoring_locks.truth_authority).toBe(false);
    expect(frame.scoring_locks.model_weight_mutation_allowed).toBe(false);
    expect(frame.scoring_locks.notion_score_write_enabled).toBe(false);
    expect(frame.scoring_locks.websocket_score_broadcast_enabled).toBe(false);
  });
});
