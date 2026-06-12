import { useMemo } from 'react';
import { buildOperatorWorkflowCommandCenterFrame } from '../data/buildOperatorWorkflowCommandCenterFrame';
import type { LiveConsoleProjectionBundle, OperatorActionPacketsBundle, OperatorWorkflowStatePacket } from '../types';

interface OperatorWorkflowCommandCenterPanelProps {
  bundle: LiveConsoleProjectionBundle;
  packetsBundle: OperatorActionPacketsBundle | null;
}

function evidenceProgress(workflow: OperatorWorkflowStatePacket): string {
  return `${workflow.completed_evidence.length}/${workflow.required_evidence.length}`;
}

function selectedWorkflow(workflows: OperatorWorkflowStatePacket[]): OperatorWorkflowStatePacket | null {
  return workflows[0] ?? null;
}

export function OperatorWorkflowCommandCenterPanel({
  bundle,
  packetsBundle,
}: OperatorWorkflowCommandCenterPanelProps): JSX.Element {
  const frame = useMemo(() => buildOperatorWorkflowCommandCenterFrame(bundle, packetsBundle), [bundle, packetsBundle]);
  const selected = selectedWorkflow(frame.workflows);
  const pendingCount = frame.workflows.filter((workflow) => workflow.status !== 'ARCHIVED' && workflow.status !== 'COMMITTED').length;
  const evidenceRequested = frame.workflows.filter((workflow) => workflow.status === 'EVIDENCE_REQUESTED').length;
  const blockedCount = frame.workflows.filter((workflow) => workflow.status === 'BLOCKED' || workflow.status === 'NOT_COMPUTABLE').length;
  const timeline = frame.actions.slice(0, 6);

  return (
    <section
      className="workflow-command-panel"
      data-testid="operator-workflow-command-center-panel"
      aria-label="AAL-Viz Operator Workflow Command Center"
    >
      <div className="workflow-command-panel__header">
        <span className="workflow-command-panel__title">OPERATOR WORKFLOW COMMAND CENTER</span>
        <span className="workflow-command-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="workflow-command-grid">
        <div className="workflow-command-section workflow-command-section--wide" data-testid="workflow-command-summary">
          <div className="workflow-command-section__label">WORKFLOW INBOX</div>
          <div className="workflow-command-summary-row">
            <span>{frame.workflows.length} WORKFLOWS</span>
            <span>{pendingCount} PENDING</span>
            <span>{evidenceRequested} EVIDENCE REQUESTED</span>
            <span>{blockedCount} BLOCKED/NC</span>
          </div>
          <div className="workflow-command-section__meta">
            Workflow guidance is static review-state projection; commit previews do not write packets or mutate truth.
          </div>
        </div>

        <div className="workflow-command-section" data-testid="workflow-inbox-list">
          <div className="workflow-command-section__label">LEFT RAIL · QUEUE</div>
          {frame.workflows.slice(0, 6).map((workflow) => (
            <div className={`workflow-command-row workflow-command-row--${workflow.urgency_band}`} key={workflow.workflow_id}>
              <span>{workflow.target_id}</span>
              <span>{workflow.status}</span>
              <strong>{workflow.urgency_band}</strong>
            </div>
          ))}
        </div>

        <div className="workflow-command-section" data-testid="workflow-detail-panel">
          <div className="workflow-command-section__label">CENTER · REVIEW DETAIL</div>
          {selected == null ? (
            <div className="workflow-command-empty">NO ACTIVE WORKFLOW</div>
          ) : (
            <div className="workflow-command-detail">
              <strong>{selected.workflow_id}</strong>
              <span>{selected.target_type} · {selected.target_id}</span>
              <span>{selected.active_step} · priority {selected.priority_score.toFixed(4)}</span>
              <span>provenance {selected.provenance}</span>
            </div>
          )}
        </div>

        <div className="workflow-command-section" data-testid="workflow-evidence-checklist">
          <div className="workflow-command-section__label">EVIDENCE CHECKLIST</div>
          {selected == null ? (
            <div className="workflow-command-empty">NO EVIDENCE</div>
          ) : (
            <>
              <div className="workflow-command-progress">
                <span>COMPLETED</span><strong>{evidenceProgress(selected)}</strong><span>TRUTH VALIDATION FALSE</span>
              </div>
              <ul className="workflow-command-list">
                {selected.required_evidence.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </>
          )}
        </div>

        <div className="workflow-command-section" data-testid="workflow-provider-side-panel">
          <div className="workflow-command-section__label">RIGHT · PROVIDER CONTEXT</div>
          <div className="workflow-command-effect-grid">
            <span>PROVIDER AUTHORITY</span>
            <strong>{String(frame.workflow_locks.provider_authority_mutation_allowed).toUpperCase()}</strong>
            <span>NOTION CONTEXT</span>
            <strong>{String(frame.workflow_locks.notion_deep_links_context_only).toUpperCase()}</strong>
            <span>LINEAGE CONTEXT</span>
            <strong>PROJECTION_ONLY</strong>
          </div>
        </div>

        <div className="workflow-command-section" data-testid="workflow-decision-composer">
          <div className="workflow-command-section__label">DECISION COMPOSER PREVIEW</div>
          <div className="workflow-command-composer">
            <span>draft target {selected?.target_id ?? 'NOT_COMPUTABLE'}</span>
            <span>commit authority {String(selected?.commit_authority ?? false).toUpperCase()}</span>
            <span>outcome mutation {String(selected?.outcome_mutation_allowed ?? false).toUpperCase()}</span>
          </div>
        </div>

        <div className="workflow-command-section" data-testid="workflow-correction-composer">
          <div className="workflow-command-section__label">CORRECTION COMPOSER PREVIEW</div>
          <div className="workflow-command-composer">
            <span>correction application {String(frame.workflow_locks.correction_application_allowed).toUpperCase()}</span>
            <span>score mutation {String(frame.workflow_locks.score_mutation_allowed).toUpperCase()}</span>
            <span>forecast mutation {String(frame.workflow_locks.forecast_probability_mutation_allowed).toUpperCase()}</span>
          </div>
        </div>

        <div className="workflow-command-section" data-testid="workflow-audit-preview">
          <div className="workflow-command-section__label">AUDIT PREVIEW BEFORE COMMIT</div>
          <div className="workflow-command-effect-grid">
            <span>REQUIRED</span><strong>{String(frame.workflow_locks.audit_preview_required_before_commit).toUpperCase()}</strong>
            <span>APPEND ONLY</span><strong>{String(frame.workflow_locks.append_only_actions).toUpperCase()}</strong>
            <span>EXTERNAL EXECUTION</span>
            <strong>{String(frame.workflow_locks.external_action_execution_allowed).toUpperCase()}</strong>
          </div>
        </div>

        <div className="workflow-command-section workflow-command-section--wide" data-testid="workflow-timeline">
          <div className="workflow-command-section__label">BOTTOM TIMELINE · ACTION LOG</div>
          <div className="workflow-command-timeline">
            {timeline.map((action) => (
              <span key={action.action_id}>{action.action_type} · {action.payload_hash}</span>
            ))}
          </div>
        </div>

        <div className="workflow-command-section" data-testid="workflow-command-bar">
          <div className="workflow-command-section__label">KEYBOARD COMMAND BAR</div>
          <div className="workflow-command-composer">
            <span>OPEN · TRIAGE · REQUEST_EVIDENCE · ANNOTATE</span>
            <span>buttons 0 · static accessibility mode</span>
          </div>
        </div>

        <div className="workflow-command-section" data-testid="workflow-notion-context-panel">
          <div className="workflow-command-section__label">NOTION CONTEXT PANEL</div>
          <div className="workflow-command-composer">
            <span>deep link surface context only</span>
            <span>notion write {String(frame.workflow_locks.notion_write_adapter_enabled).toUpperCase()}</span>
          </div>
        </div>

        <div className="workflow-command-section workflow-command-section--wide" data-testid="workflow-command-locks">
          <div className="workflow-command-section__label">WORKFLOW LOCKS</div>
          <div className="workflow-command-lock-grid">
            <span>NOTION WRITE</span><strong>{String(frame.workflow_locks.notion_write_adapter_enabled).toUpperCase()}</strong>
            <span>WEBSOCKET</span><strong>{String(frame.workflow_locks.websocket_live_updates_enabled).toUpperCase()}</strong>
            <span>AUTO EXECUTION</span><strong>{String(frame.workflow_locks.autonomous_execution_allowed).toUpperCase()}</strong>
            <span>OUTCOME MUTATION</span><strong>{String(frame.workflow_locks.outcome_mutation_allowed).toUpperCase()}</strong>
            <span>CORRECTION APPLY</span><strong>{String(frame.workflow_locks.correction_application_allowed).toUpperCase()}</strong>
            <span>SCORE MUTATION</span><strong>{String(frame.workflow_locks.score_mutation_allowed).toUpperCase()}</strong>
            <span>ROUTING MUTATION</span><strong>{String(frame.workflow_locks.strategy_routing_mutation_allowed).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(frame.workflow_locks.truth_authority).toUpperCase()}</strong>
          </div>
          <div className="workflow-command-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
