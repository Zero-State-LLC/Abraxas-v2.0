import { describe, expect, it } from 'vitest';
import { buildOperatorWorkflowCommandCenterFrame } from './buildOperatorWorkflowCommandCenterFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
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

describe('buildOperatorWorkflowCommandCenterFrame', () => {
  it('builds a deterministic v7.7 workflow command center frame', () => {
    const frame = buildOperatorWorkflowCommandCenterFrame(sampleProjectionBundle, SAMPLE_PACKETS);
    const repeat = buildOperatorWorkflowCommandCenterFrame(sampleProjectionBundle, SAMPLE_PACKETS);

    expect(frame).toEqual(repeat);
    expect(frame.packet_type).toBe('AALVizOperatorWorkflowCommandCenterFrame.v1');
    expect(frame.drop_name).toBe('AAL-Viz v7.7 — Operator Workflow UI Code Drop');
    expect(frame.authority).toBe('WORKFLOW_GUIDANCE_REVIEW_STATE_AND_PROJECTION_ONLY');
    expect(frame.mutation_policy).toBe('NO_EXECUTION_OUTCOME_FORECAST_SCORE_PROVIDER_AUTHORITY_OR_ROUTING_MUTATION');
    expect(frame.folded_versions).toContain('v7.6');
    expect(frame.features).toContain('workflow_inbox');
    expect(frame.features).toContain('audit_preview');
    expect(frame.provenance_hash).toMatch(/^[0-9a-f]{8}$/);
  });

  it('derives workflow states and append-only action packets from review suggestions', () => {
    const frame = buildOperatorWorkflowCommandCenterFrame(sampleProjectionBundle, SAMPLE_PACKETS);

    expect(frame.workflows.length).toBeGreaterThan(0);
    expect(frame.actions).toHaveLength(frame.workflows.length);
    expect(frame.workflows.some((workflow) => workflow.status === 'EVIDENCE_REQUESTED')).toBe(true);
    expect(frame.workflows.some((workflow) => workflow.active_step === 'EVIDENCE')).toBe(true);

    for (const workflow of frame.workflows) {
      expect(workflow.projection_only).toBe(true);
      expect(workflow.review_state_management_only).toBe(true);
      expect(workflow.commit_authority).toBe(false);
      expect(workflow.outcome_mutation_allowed).toBe(false);
      expect(workflow.forecast_mutation_allowed).toBe(false);
      expect(workflow.score_mutation_allowed).toBe(false);
      expect(workflow.routing_mutation_allowed).toBe(false);
      expect(workflow.required_evidence.length).toBeGreaterThan(0);
    }

    for (const action of frame.actions) {
      expect(action.authority).toBe('OPERATOR_WORKFLOW_LOG_ONLY');
      expect(action.append_only).toBe(true);
      expect(action.external_execution_allowed).toBe(false);
      expect(action.notion_write_allowed).toBe(false);
      expect(action.payload_hash).toMatch(/^[0-9a-f]{8}$/);
    }
  });

  it('keeps state machine and workflow locks advisory-only', () => {
    const frame = buildOperatorWorkflowCommandCenterFrame(sampleProjectionBundle, SAMPLE_PACKETS);

    expect(frame.status_transitions.NEW).toEqual(['TRIAGED', 'DISMISSED', 'BLOCKED']);
    expect(frame.status_transitions.COMMITTED).toEqual(['ARCHIVED']);
    expect(frame.status_transitions.ARCHIVED).toEqual([]);
    expect(frame.status_transitions.NOT_COMPUTABLE).toEqual([]);

    expect(frame.workflow_locks.display_only).toBe(true);
    expect(frame.workflow_locks.audit_preview_required_before_commit).toBe(true);
    expect(frame.workflow_locks.evidence_completion_is_not_truth_validation).toBe(true);
    expect(frame.workflow_locks.notion_deep_links_context_only).toBe(true);
    expect(frame.workflow_locks.accessibility_static_review_mode).toBe(true);
    expect(frame.workflow_locks.notion_write_adapter_enabled).toBe(false);
    expect(frame.workflow_locks.websocket_live_updates_enabled).toBe(false);
    expect(frame.workflow_locks.autonomous_execution_allowed).toBe(false);
    expect(frame.workflow_locks.external_action_execution_allowed).toBe(false);
    expect(frame.workflow_locks.outcome_mutation_allowed).toBe(false);
    expect(frame.workflow_locks.correction_application_allowed).toBe(false);
    expect(frame.workflow_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.workflow_locks.score_mutation_allowed).toBe(false);
    expect(frame.workflow_locks.provider_authority_mutation_allowed).toBe(false);
    expect(frame.workflow_locks.strategy_routing_mutation_allowed).toBe(false);
    expect(frame.workflow_locks.truth_authority).toBe(false);
  });
});
