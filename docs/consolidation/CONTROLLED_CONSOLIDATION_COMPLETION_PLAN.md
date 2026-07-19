# Abraxas v2.0 Controlled Consolidation Completion Plan

```yaml
document_type: ENGINEERING_COMPLETION_PLAN
program: ABRAXAS_V2_CONTROLLED_CONSOLIDATION
repository: scrimshawlife-ctrl/Abraxas-v2.0
baseline_branch: main
audited_main_sha: d3c405bc06de5ac141ed9793c49078e9ffcc8acb
program_priority: P0
governance_posture: ADVISORY_ONLY
deployment: HOLD
production_activation: DENY
feature_expansion: FREEZE
target_state: STABILIZATION_BASELINE_PROVEN
```

## 1. Program mandate

Abraxas v2.0 remains a governed stabilization candidate while the repository is reduced to a mechanically proven product boundary. This program does not authorize production activation, deployment, autonomous execution, external calls, secret persistence, canon mutation, runtime promotion, or expansion of the supported contract surface.

The completion target is one canonical baseline, one minimal executable product graph, one authority evaluator, one evidence-publication path, one release identity model, one reproducible validation ladder, and one current documentation surface.

## 2. Governing determination

### OBSERVED

- Governance and readiness machinery are mature.
- Production activation remains denied.
- Deploy readiness remains `NO_GO`.
- Freeze gates report passing.
- Baseline evidence remains partial.
- Recent work focuses on drift, ghost paths, and readiness closure.
- PR #958 remains an unresolved architecture-level stabilization change.

### INFERRED

- The primary engineering problem is consolidation, not capability.
- Complexity is dominated by evidence and control-plane proliferation.
- Further feature expansion would increase ambiguity faster than value.
- Production activation before consolidation is premature.

### SPECULATIVE

- A significant repository surface may be nonessential to the minimum product.
- Multiple readiness abstractions may encode overlapping state.
- A reduced supported runtime can likely be extracted without losing the research corpus.

### SEAL

```yaml
audit_verdict: CONTROLLED_CONSOLIDATION_REQUIRED
release_candidate: CONDITIONAL
deployment: HOLD
production_activation: DENY
feature_expansion: FREEZE
```

## 3. Required end state

```yaml
canonical_baseline:
  count: 1
  source_sha_bound: true
  reproducible: true
product_architecture:
  count: 1
  runtime_graph_complete: true
  unreachable_paths_classified: true
authority_evaluator:
  canonical_implementation_count: 1
  all_sensitive_gates_delegate: true
  fail_closed: true
artifact_publication:
  explicit_command_required: true
  dirty_worktree_rejected: true
  source_sha_embedded: true
  manifest_required: true
release_identity:
  documented: true
  machine_validated: true
release_checks:
  visible_on_main: true
  branch_protected: true
active_documentation:
  current_architecture_count: 1
  current_plan_count: 1
  current_risk_register_count: 1
  current_baseline_receipt_count: 1
  current_interface_registry_count: 1
```

## 4. Program constraints

Only changes that directly support reproducibility, consolidation, authority centralization, artifact isolation, validation, classification, release identity, documentation reduction, or removal/quarantine of obsolete surfaces are permitted.

Prohibited during the program:

- new intelligence domains;
- new campaign classes;
- new autonomous agents;
- new public APIs;
- new canonical artifact families;
- new governance layers;
- new production execution routes;
- new writeback capabilities;
- unrelated refactors.

Every work package must use a dedicated branch, pinned base SHA, bounded scope, explicit validation commands, and a completion receipt.

## 5. Work package sequence

| WP | Priority | Objective | Depends on |
|---|---:|---|---|
| WP0 | P0 | Program controls and freeze boundary | None |
| WP1 | P0 | Sole canonical baseline | WP0 |
| WP2 | P0 | Minimal executable product graph | WP1 |
| WP3 | P0 | Canonical authority evaluator | WP1, WP2 |
| WP4 | P1 | Artifact isolation and publication | WP1 |
| WP5 | P1 | Resolve PR #958 | WP2, WP3 |
| WP6 | P1 | Release identity taxonomy | WP1, WP2 |
| WP7 | P1 | Visible mandatory release checks | WP1, WP3, WP4, WP6 |
| WP8 | P2 | Historical surface reduction | WP1, WP2, WP6 |
| WP9 | P0 | Final conformance and seal | WP1-WP8 |

## 6. WP0 — Program control and freeze boundary

### Deliverables

```text
docs/consolidation/PROGRAM_CHARTER.md
docs/consolidation/SCOPE_BOUNDARY.yaml
docs/consolidation/WORK_PACKAGE_REGISTRY.yaml
docs/consolidation/DECISION_LOG.md
out/consolidation/program_entry_receipt.v1.json
```

### Actions

1. Confirm whether `origin/main` still resolves to the audited SHA.
2. If `main` advanced, inspect and classify intervening commits and select a new entry SHA through an explicit decision receipt.
3. Record the feature-freeze rules and allowed change classes.
4. Define the completion-receipt schema for every work package.
5. Define stop conditions.

### Stop conditions

Stop and require operator review if production activation is enabled, deployment is unheld, a new authority path bypasses governance, main contains unresolved drift, the repository cannot reproduce fast validation, secrets are found, or baseline generation requires mutation of tracked source paths.

### Acceptance

```yaml
program_entry_sha: PINNED
feature_freeze: ACTIVE
work_packages: REGISTERED
stop_conditions: ENFORCED
production_activation: DENIED
deployment: HELD
```

## 7. WP1 — Establish one canonical baseline

### Objective

Produce one reproducible baseline receipt bound to one exact source commit and make it the sole active baseline.

### Required procedure

Use a clean checkout or isolated worktree. Capture `HEAD`, tree SHA, `origin/main`, and pre-run worktree state. Run the validation ladder from a scrubbed environment preserving only explicitly required variables and setting deterministic controls such as `TZ=UTC`, `PYTHONHASHSEED=0`, and `SOURCE_DATE_EPOCH`.

Select one canonical dependency representation in this order: existing committed lockfile, generated `uv.lock`, fully pinned requirements export, or environment freeze as temporary evidence only.

### Validation ladder

```yaml
validation_stages:
  - repository_preflight
  - syntax_validation
  - fast_ci
  - full_pytest
  - strict_type_check
  - lint
  - schema_validation
  - authority_invariant_tests
  - dependency_audit
  - secret_scan
  - artifact_drift_check
  - documentation_crosslink_check
```

Do not claim a full-suite pass if only selected tests ran.

### Required measurements

Capture:

- source commit, tree SHA, branch, dirty-before, dirty-after;
- operating system, architecture, Python executable and version;
- pip, uv, pytest, Ruff, and Pyright versions;
- dependency lock path, SHA-256, generation command, and dependency count;
- tests collected, passed, failed, skipped, xfailed, xpassed, errors, deselected, and duration;
- total warnings, warning categories, new warnings, allowed warnings, and disallowed warnings;
- lint, type, dependency-audit, schema, secret-scan, and drift exit codes;
- tracked mutations, untracked output, restored paths, and residual dirty paths;
- artifact root, manifest path, manifest hash, file count, and total bytes.

### Canonical receipt

```text
out/production_readiness/baseline/current_baseline_receipt.v1.json
out/production_readiness/baseline/current_baseline_receipt.v1.md
out/production_readiness/baseline/current_artifact_manifest.v1.json
out/production_readiness/baseline/current_warning_inventory.v1.json
```

All prior baselines must be marked `SUPERSEDED` or moved to `archive/production_readiness/baselines/`. Exactly one receipt may contain `active: true`.

Add a validator that fails if more than one active baseline exists, none exists, the source SHA is inconsistent, or referenced artifacts are missing.

### Acceptance

```yaml
exact_sha_pinned: PASS
scrubbed_environment_used: PASS
full_suite_executed: PASS
dependency_lock_hashed: PASS
test_counts_and_duration_captured: PASS
warnings_captured: PASS
drift_result_clean: PASS
artifact_manifest_complete: PASS
sole_active_baseline: PASS
```

## 8. WP2 — Define the minimal executable Abraxas product

### Canonical files

```text
docs/architecture/ABRAXAS_MINIMAL_PRODUCT.v1.yaml
docs/architecture/ABRAXAS_MINIMAL_PRODUCT.v1.md
```

The YAML file is authoritative. The Markdown file must be generated from or mechanically checked against it.

### Required schema

```yaml
entrypoints: []
runtime_services: []
operator_interfaces: []
canonical_state: []
authority_evaluator: []
artifact_store: []
external_adapters: []
supported_contracts: []
non_product_experimental_modules: []
classifications:
  engineering_tooling: []
  advisory_analysis: []
  experiment: []
  fixture: []
  legacy: []
  archive: []
  unclassified: []
```

Each entity must record its path, symbol, kind, status, owner, inputs, outputs, calls, callers, authority requirements, writes, external effects, supported contracts, and evidence.

Starting from declared product entrypoints, resolve imports, service calls, CLI dispatch, router registration, configuration-bound dispatch, plugin discovery, state reads and writes, artifact publication, authority checks, and external adapters. Dynamic paths that cannot be proven must be labeled `NOT_COMPUTABLE`.

Anything not reachable from the product graph must be assigned exactly one category: engineering tooling, advisory analysis, experiment, fixture, legacy, or archive.

Add `scripts/run_minimal_product_architecture_check.py`. It must fail for missing supported entrypoints, ownerless services, unclassified external adapters, ungoverned canonical-state writers, untested supported contracts, unclassified modules, or product dependencies on archived modules.

### Acceptance

```yaml
canonical_architecture_file: PRESENT
all_required_sections_complete: PASS
unclassified_paths: 0
product_to_archive_dependencies: 0
architecture_validation: PASS
```

## 9. WP3 — Consolidate authority

### Objective

Create or confirm one canonical `evaluate_authority()` implementation and require every sensitive gate to delegate to it.

Recommended location:

```text
core/governance/authority.py
```

Required interface:

```python
def evaluate_authority(request: AuthorityRequest) -> AuthorityDecision:
    ...
```

The request must include action, actor, environment, source SHA, requested capability, resource, evidence state, governance protocol version, operator grant, expiry, revocation state, dry-run state, and context.

The decision must include `ALLOW`, `DENY`, `HOLD`, or `NOT_COMPUTABLE`; reason codes; effective and denied capabilities; evidence state; grant ID; evaluator version; input digest; and decision digest.

The evaluator must be deterministic, fail-closed, side-effect-free, canonically serialized, independently testable, and explicit about missing evidence and expired or absent grants.

All activation, deployment, deploy-unhold, writeback, sandbox, external-call, secret-access, MCP, canon-mutation, runtime-promotion, contract-promotion, and artifact-publication gates must delegate to it.

Add `scripts/run_authority_bypass_inventory.py` to detect direct activation checks, operator phrase comparisons, local grant parsing, local allow/deny decisions, sensitive side effects without authority decisions, and duplicate authority constants.

Required invariant tests include no-grant denial, expired and revoked grant denial, malformed grant denial, production activation denied by default, deployment held by default, advisory results unable to self-promote, dry-run unable to grant live authority, candidate approval not granting activation, source-SHA mismatch denial, and deterministic decision digests.

### Acceptance

```yaml
canonical_evaluator_count: 1
sensitive_gate_delegation: 100_PERCENT
authority_bypass_count: 0
default_activation: DENY
default_deployment: HOLD
determinism_tests: PASS
authority_invariant_tests: PASS
```

## 10. WP4 — Isolate generated artifacts

### Output model

```yaml
output_roots:
  ephemeral: .tmp/abraxas-build/<run_id>
  local_persistent: out/local/<run_id>
  publish_staging: out/publish-staging/<run_id>
  committed_evidence: out/production_readiness
  archive: archive
```

All runners must accept or inherit `ABX_BUILD_ROOT`. Default behavior must write to an untracked root. Ordinary tests and validation runners may not directly update committed evidence.

Create:

```text
python scripts/publish_evidence.py
```

The publisher must confirm source SHA equals `HEAD`, reject dirty worktrees, validate freshness and hashes, verify schemas, delegate publication authority to the canonical evaluator, canonicalize JSON, create a deterministic manifest, use atomic writes, prevent path traversal, record toolchain identity, record superseded artifacts, and produce a publication receipt.

An artifact is stale when its source SHA, dependency lock, toolchain identity, referenced files, schema version, or source-tree cleanliness do not match the publication context.

### Acceptance

```yaml
default_validation_root_untracked: PASS
tracked_evidence_direct_write: PROHIBITED
publication_command: PRESENT
dirty_worktree_rejection: PASS
freshness_validation: PASS
canonical_json: PASS
manifest_generation: PASS
normal_validation_residual_drift: 0
```

## 11. WP5 — Resolve PR #958

Inspect its base and head SHAs, mergeability, conflicts, changed files, overlap with landed stabilization work, duplicate authority logic, duplicate readiness abstractions, contract changes, stale fixtures, and current-main test validity.

Choose exactly one disposition:

- `RECONSTRUCT`: retain useful logic in smaller current branches;
- `REBASE`: only when conflicts are mechanical and architecture still matches the minimal product;
- `CLOSE_SUPERSEDED`: when behavior already landed or the PR adds redundant control machinery.

Required receipt:

```text
out/consolidation/pr958_disposition_receipt.v1.json
```

PR #958 must not remain open after this work package.

## 12. WP6 — Establish release identity

Create:

```text
RELEASE_IDENTITY.yaml
```

It must distinguish:

- product version (`2.5.0`);
- repository release sequence (`1.144.6`);
- Python package version;
- governance protocol version;
- independent schema versions;
- independent artifact format versions;
- baseline receipt version and source SHA;
- release-candidate identity and status.

Add `scripts/run_release_identity_check.py` to compare `VERSION`, `pyproject.toml`, `CHANGELOG.md`, the active baseline, release decisions, governance constants, schema registry, and artifact registry. Unexplained mismatches must fail validation.

### Acceptance

```yaml
release_identity_file: PRESENT
all_version_domains_defined: PASS
unexplained_version_mismatches: 0
release_identity_check: PASS
```

## 13. WP7 — Add visible release checks

Require visible checks for:

```yaml
required_checks:
  - fast_ci
  - full_deterministic_suite
  - strict_type_check
  - lint
  - dependency_audit
  - secret_scan
  - artifact_drift_check
  - schema_compatibility
  - authority_invariant_tests
```

Recommended workflow split:

```text
.github/workflows/fast-ci.yml
.github/workflows/full-suite.yml
.github/workflows/security.yml
.github/workflows/contracts.yml
.github/workflows/release-readiness.yml
```

Protect `main` with pull requests, required checks, review, conversation resolution, no force pushes, no deletion, and current-branch requirements. Add CODEOWNERS protection for governance, canonical serialization, evidence publication, architecture, release identity, schemas, and workflows.

### Acceptance

```yaml
checks_visible_on_prs: PASS
checks_visible_on_main: PASS
required_status_checks: CONFIGURED
branch_protection: ACTIVE
authority_paths_codeowned: PASS
```

## 14. WP8 — Reduce historical surface

Only the following should be presented as current:

```text
docs/architecture/ABRAXAS_MINIMAL_PRODUCT.v1.yaml
docs/consolidation/CONTINUATION_PLAN.current.md
docs/consolidation/RISK_REGISTER.current.yaml
out/production_readiness/baseline/current_baseline_receipt.v1.json
out/production_readiness/ws1/interface_registry_snapshot.current.json
RELEASE_IDENTITY.yaml
```

Move superseded material beneath an indexed archive:

```text
archive/plans/
archive/baselines/
archive/receipts/
archive/schemas/
archive/workstreams/
archive/debug_plans/
archive/release_decisions/
archive/inventories/
archive/INDEX.yaml
```

Do not rewrite historical evidence when doing so would invalidate its original hash. Use sidecar archive metadata where required.

Add `scripts/run_active_document_surface_check.py` to fail when multiple current plans or baselines exist, root documents prioritize superseded material, archived artifacts claim active authority, archive records lack provenance, or current documents reference missing history.

### Acceptance

```yaml
current_architecture_count: 1
current_continuation_plan_count: 1
current_risk_register_count: 1
current_baseline_count: 1
current_interface_registry_count: 1
archive_index_complete: PASS
archived_active_authority_claims: 0
```

## 15. WP9 — Final conformance and seal

Run from a fresh checkout of the proposed completion SHA:

1. verify clean checkout;
2. verify release identity;
3. verify minimal product architecture;
4. verify authority bypass inventory;
5. run fast CI;
6. run the full deterministic suite;
7. run strict type check and lint;
8. run dependency audit and secret scan;
9. run schema compatibility and authority invariants;
10. run artifact-drift validation;
11. generate baseline in an ephemeral root;
12. publish only through the evidence publisher;
13. verify manifest and sole active baseline;
14. verify active-document surface;
15. verify clean post-publication state.

Required completion receipt:

```text
out/production_readiness/consolidation_completion_receipt.v1.json
```

Successful completion changes the state only to:

```yaml
repository_state: STABILIZATION_BASELINE_PROVEN
release_candidate: CONSOLIDATED_CONDITIONAL
deployment: HOLD
production_activation: DENY
feature_expansion: OPERATOR_DECISION_REQUIRED
```

It does not authorize production readiness or activation.

## 16. Recommended pull-request sequence

1. Program controls.
2. Canonical baseline harness.
3. Minimal product architecture.
4. Authority consolidation foundation.
5. Authority caller migration.
6. Artifact isolation.
7. Evidence publication.
8. PR #958 disposition.
9. Release identity.
10. Release checks and protection.
11. Historical surface reduction.
12. Final conformance.

Every PR must remain bounded to one work package or an explicitly declared subset.

## 17. Definition of done

```yaml
baseline:
  exact_sha: true
  scrubbed_full_suite: true
  dependency_lock_hash: true
  counts_and_duration: true
  warnings_inventory: true
  drift_clean: true
  manifest_complete: true
  sole_active: true
architecture:
  one_file: true
  all_paths_classified: true
  zero_unclassified: true
authority:
  one_evaluator: true
  all_sensitive_paths_delegate: true
  bypass_count_zero: true
  fail_closed: true
artifacts:
  isolated_by_default: true
  explicit_publication_only: true
  dirty_tree_rejected: true
  freshness_validated: true
pr958:
  resolved: true
release_identity:
  taxonomy_documented: true
  validator_passes: true
release_checks:
  all_required_checks_visible: true
  branch_protection_active: true
history:
  one_current_document_set: true
  archive_index_complete: true
final:
  completion_receipt: true
  deployment: HOLD
  production_activation: DENY
```

## 18. Final seal

```yaml
OPEN:
  repository: scrimshawlife-ctrl/Abraxas-v2.0
  program: ABRAXAS_V2_CONTROLLED_CONSOLIDATION
  audited_entry_sha: d3c405bc06de5ac141ed9793c49078e9ffcc8acb
ALIGN:
  objective: REDUCE_AMBIGUITY
  primary_output:
    - one_runtime_graph
    - one_authority_evaluator
    - one_active_baseline
    - one_release_identity
    - one_validation_ladder
ASCEND:
  target_state: STABILIZATION_BASELINE_PROVEN
  capability_expansion: PROHIBITED_DURING_PROGRAM
CLEAR:
  unclassified_paths_target: 0
  authority_bypass_target: 0
  active_baseline_count: 1
  current_plan_count: 1
SEAL:
  audit_verdict: CONTROLLED_CONSOLIDATION_REQUIRED
  release_candidate: CONDITIONAL
  deployment: HOLD
  production_activation: DENY
  feature_expansion: FREEZE
```

The next Abraxas milestone is not a larger symbolic-intelligence surface. It is a smaller, mechanically demonstrable system whose runtime, authority, evidence, version identity, and validation state can each be traced to one canonical source.
