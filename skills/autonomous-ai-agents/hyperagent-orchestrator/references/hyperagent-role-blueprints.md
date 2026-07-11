# HyperAgent Role Blueprints

## Planner
Purpose: break a goal into ordered work packets.
Inputs: goal, constraints, budget, deadline, policy.
Outputs: task graph, acceptance criteria, risk list.
Tools: web/search, notes, lightweight analysis.

## Navigator
Purpose: gather sources and locate the next dependency.
Inputs: target domain, evidence requirements.
Outputs: source bundle, citations, open questions.
Tools: web, browser, search, document readers.

## Analyst
Purpose: compress sources into claims.
Inputs: evidence bundle.
Outputs: observed / inferred / speculative summary, provenance, confidence, gaps.
Tools: analysis, code, calculator, tables.

## Editor
Purpose: turn analysis into a user-facing deliverable.
Inputs: structured claims, style constraints.
Outputs: draft, concise summary, final artifact.
Tools: writing, formatting, export.

## Executor
Purpose: perform bounded actions.
Inputs: explicit task, policy guardrails, allowed tools.
Outputs: action log, result payload, failure details.
Tools: shell, browser, integrations, code exec.

## Reviewer
Purpose: check completion and policy.
Inputs: draft artifact, expected contract.
Outputs: pass/fail, issues, remediation list.
Tools: diff, schema validation, basic checks.

## Fleet Monitor
Purpose: long-running oversight.
Inputs: schedule, thresholds, alert policy.
Outputs: status snapshots, escalations, summaries.
Tools: cron, logs, dashboards, integrations.
