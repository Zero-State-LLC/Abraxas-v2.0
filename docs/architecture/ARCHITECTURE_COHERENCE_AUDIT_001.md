# Architecture Coherence Audit 001

- **Date:** 2026-10-10 · **Base:** `main` at `2861822b` (#1153)
- **Scope:** whole repository. Execution paths were traced from code. Documents were checked against code.
- **Layer:** Governance V3 Layer 0, engineering only. This audit changes no gates, no locks, and no canon.
- **Method:** a graft context graph (31.5k symbols, 81k call edges); a static import graph over all 3,983 Python modules; reachability from the product entry points; targeted pytest runs; a full-suite run; read-only `gh`.
- **Revision 2 (2026-10-10, same day):** the operator decided repository ownership, version authority, `/analyze` and canary evidence, CI and Sigil-Forge. §8 records the decisions, §15 the new findings, and §9–§14 the work done under them.
- **Labels:** findings carry `OBSERVED` / `INFERRED` / `SPECULATIVE` / `NOT_COMPUTABLE` labels, as defined in AGENTS.md §5.

## 1. Assessment

The governing intent is coherent and well stated. AGENTS.md, Governance V3 and the RDI and Three-Settlement doctrines agree with each other.

The code around that intent is not coherent:

- **The product is small.** It is a deterministic advisory spine behind `python -m abraxas` and `apps.api.create_app`. That spine reaches about 110 of the 1,561 `core/` modules (7%). `OBSERVED`
- **Most of `core/` is receipt-generation lanes.** About 1,190 modules are reached only from runner scripts. They are plan, gate, review and receipt generators for historical lanes, and each one carries its own copy of the shared primitives. `OBSERVED`
- **The safety net has holes.** Hosted CI has been switched off since 2026-09-17, fast CI is red on `main`, and fast CI does not select governance tests at all. `OBSERVED`
- **The front-door documents are stale.** STATUS, PLANS and ARCHITECTURE describe a state that is 60 days old, and some of their architectural claims are false (§5, D-series). `OBSERVED`

Overall health: **sound doctrine, fragile engineering substrate.** The highest-value work is not restructuring. It is three things:

1. Restore a trustworthy automated gate.
2. Make the shared primitives (canonical hashing, authority locks, settings) single-owner.
3. Declare which code is product, which is governed-lane, and which is history.

## 2. Authority and precedence (as observed)

`AGENTS.md` §2 is the operative authority order: user task → AGENTS → GOVERNANCE_V3 → SKILLS → skills → domain docs/contracts/tests → implementation.

There is no `CONTEXT.md` and no file named "constitution". AGENTS.md calls itself the "constitutional router". `OBSERVED`

Conflicts the operator has not resolved:

| Topic | Claim A | Claim B | Status |
| --- | --- | --- | --- |
| Planning truth | GOVERNANCE_V3: Notion owns planning/status | PLANS.md: "CURRENT CANONICAL ROADMAP" | Unresolved. This audit treats PLANS as the repo-side roadmap and Notion as the operator view. |
| What this repo is | README/`docs/SIBLING_REPOS.md` (#1135): doctrine + candidate architecture; runtime lives in `Zero-State-LLC/Abraxas` | STATUS: product CLI, `create_app`, supported interfaces live here | Unresolved (see Decision 2) |
| Version | `VERSION`/`pyproject`/`core/settings.py`: 2.5.0 | tags/semantic-release: v1.180.0; CHANGELOG stops at 1.178.0 | Unresolved (see Decision 3) |
| Second front door | `docs/START_HERE.md`/`docs/INDEX.md` reading order | AGENTS.md §3 mandatory startup | AGENTS.md wins by precedence |

## 3. Architecture as it runs today

```text
python -m abraxas analyze ─► abraxas.cli._cmd_analyze ─► AbraxasClient.analyze
POST /analyze ─► apps.api.boundaries (auth/rate seams off by default) ─► routers.analyze
        └──────────────► core.application.advisory_spine.run_advisory_spine   (pure, deterministic)
              ├ core.governance.activation_policy.evaluate_activation(lane)  → DENIED | OPERATOR_GATE
              ├ core.services.validation_service.validate(schema_ref)         → INVALID_INPUT
              ├ core.alembic.oracle_bridge.task_envelope_from_oracle_candidate
              ├ core.alembic.pipeline.execute_advisory
              └ core.canonical.json.canonical_hash(result)                    → OK
   CLI: optional write_canonical_artifact(--out)        API: returns JSON, never persists
replay   ─► AbraxasClient.replay ─► analyze(alembic task only)   (re-execution, not verification)
forage / os forensics ─► EvidencePack path ─► spine_bridge / familiar bridges
   ─► propagation / disposition / MemeticOpsGate (always DENIED) ─► writes under REPO_ROOT/out
scripts/<domain>/run_*.py (736) ─► core builders ─► out/**  (governed receipt lanes)
scripts/artifact/run_artifact_regeneration.py ─► core.generated_artifact_registry (71 generators) ─► drift check
```

The documented spine is `InputEnvelope → Ingest → Evidence → BeliefGraph → [Alembic] → Oracle → AdvisoryResult → ArtifactRepository → CLI/API`. It is a target, not an executable path:

- `InputEnvelope` and `ArtifactRepository` exist only as strings in `core/production_convergence/golden_path.py`. `NOT_COMPUTABLE`
- No `core.belief_graph` module is reachable from the CLI or the API. `OBSERVED`
- Oracle feeds Alembic as an input candidate; it is not a stage after Alembic. `OBSERVED`

### Reachability of `core/` (1,561 modules)

| Reached from | Modules | Share |
| --- | --- | --- |
| Product entry points (`abraxas.cli`, `abraxas.client`, `apps.api.main`) | 110 | 7% |
| CI-run scripts (5 workflow scripts + 71 regeneration generators) | 155 | 10% |
| Other runner scripts | 964 | 62% |
| Tests only | 306 | 20% |
| Path strings, config or docs only | 9 | <1% |
| Nothing at all | 17 | 1% |

Tests, including the scripts they load by path, reach 1,526 of the 1,561 modules. "Scripts only" means off the product path; it does not mean untested.

### Ownership of shared state

- **Canonical serialization and hashing:** `core/canonical/json.py`, imported by 1,383 modules. This is the intended single owner, but it is reimplemented elsewhere (A1).
- **Authority locks:** split across four mechanisms (A2).
- **Paths and settings:** split between `core/config.py` `RuntimePaths` and `core/settings.py` `RuntimeSettings`, plus about 615 literal `"out/"` paths (A4).
- **Activation decision:** `core/governance/activation_policy.py`. Its only runtime caller is the advisory spine (A3).

## 4. Target architecture (smallest coherent change)

The target keeps every capability and adds no subsystem. It declares four tiers and gives each shared primitive a single owner.

| Tier | What belongs there | Rule |
| --- | --- | --- |
| **T1 Product spine** | `abraxas/`, `apps/api/`, `core/application/`, `core/services/`, `core/governance/`, `core/canonical/`, `core/settings.py`, `core/ports/`, `core/alembic/`, the forensics/forage/instantiation surfaces the CLI reaches | Must be covered by fast CI. No wall-clock or uuid in results. Errors map to typed statuses. |
| **T2 Governed lanes** | Receipt, gate and plan builders under `core/` that `scripts/<domain>/run_*.py` reaches, plus `core/generated_artifact_registry.py` | Use T1 primitives only (no private hash helpers). Write through the canonical writers. |
| **T3 Research and experiments** | Metric families (`wasserstein_*`, `chamfer_*`, `geodesic_*`, `transport_*`, `metric_*`, `norm_*`), `abx-afe/`, `specs/` bind packs | Advisory. May not be imported by T1. |
| **T4 Historical** | P70–P130 chains, `out/operator_review/**`, superseded skills | Read-only provenance. Removal only under CLEAR dual control. |

Single owners:

- **Hashing:** `core.canonical.json`. Every other `_canonical_json`/`stable_hash` helper delegates to it or is removed. Removal is tested by comparing old and new hashes.
- **Authority lock vocabulary:** one registry in `core/governance/authority.py`, which `write_canonical_artifact` checks for every artifact class.
- **Settings:** `RuntimeSettings`. `RuntimePaths` is derived from it, and a single set of environment variable names is used (`ABRAXAS_*`).
- **The `analyze` application service:** `run_advisory_spine`. It takes the runtime context (repo root, clock) from its caller. Both CLI and API stay as thin adapters, which is already the shape.

## 5. Findings register

Severity: H = correctness, safety or trust in gates; M = maintenance cost or latent defect; L = hygiene.

### Gates and verification

| ID | Label | Finding | Evidence | Consequence | Sev | Disposition | Verify by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G1 | OBSERVED | Hosted CI has not run on `main` since 2026-09-17 | `gh variable list` → `HOSTED_ACTIONS_AVAILABLE=false`; `gh run list --branch main` all `skipped`; #1134–#1153 merged without green hosted CI | No automated gate is enforcing anything | H | **Operator decision** (billing) | `gh run list` shows a green `ci` |
| G2 | OBSERVED | Fast CI is red on `main` | `tests/test_abx_skill_evolution_decision_ledger.py::test_full_cycle_rc0_no_mutation`. Root cause: `scripts/codegen/run_abx_hermes_skill_evolution_cycle.py:97` adds the fail-closed decision validator's exit code to `rc`. The validator exits 1 whenever no validated human decision exists, which is the normal state (since `1e2a5b01`, 2026-09-15). | Every fast-CI run fails, and ruff and pyright never run | H | **Fixed in this PR** (operator-approved 2026-10-10): the runner records BLOCKED as status and still fails on a crash; the validator is unchanged | `test_full_cycle_rc0_no_mutation` passes |
| G3 | OBSERVED | Tests write fixture artifacts and a fake operator decision into the working tree | `tests/conftest.py:14-22` autouse session fixture seeds about 20 files into `out/audit`. `tests/test_abx_skill_evolution_decision_ledger.py:38` writes `APPROVE_EXTENDED_OBSERVATION` with `operator_id: "test"` into `out/operator_input/`. `tests/test_abx_skill_evolution_formal_operator_decision_builder.py:32` unlinks the real decision path. | Test runs can overwrite or delete a real operator decision and leave a fabricated one behind. A full-suite run also rewrites 34 tracked `out/` files and replaces `apps/aal-viz-live-console/public/projection-bundle.json` (a −175k-line diff). This contradicts ARCHITECTURE ("tests never write to out/"). | H | **Operator-input part fixed in this PR:** the ledger/reconciliation tests run in `tmp_path`, and the builder tests restore the real decision files after each test. The session seeding and tracked-file churn remain (P0). | `out/operator_input/` holds no decision after the skill-evolution tests; `git status` clean after a full run (P0) |
| G4 | OBSERVED | Fast CI selects tests by path keyword | `tests/conftest.py:24-58` marks any path containing governance/audit/registry/artifact/temporal/… as `slow`. That deselects 3,353 of 13,859 tests, including all 37 governance-named files and `test_artifact_classification.py`. | Governance invariants are untested on every PR | H | Refactor: mark by explicit marker, not by path substring | Count of deselected governance tests = 0 |
| G5 | OBSERVED | CI path filters skipped the product | `.github/workflows/ci.yml` did not list `abraxas/**`, `apps/api/**`, `contracts/**`, `skills/**` | Product-only PRs ran no tests | H | **Fixed in this PR** | Workflow diff |
| G6 | OBSERVED | Type checking is disabled | `pyrightconfig.json` `typeCheckingMode: "off"` overrides pyproject's strict setting; ruff checks 3 files | The "pyright passes" claim carries no information | M | Clarify, then turn on `basic` for T1 paths | pyright on T1 with `basic` |
| G7 | OBSERVED | Fast CI dirties tracked files | Four advisory scripts write `out/production_readiness/ws1,ws5/*.json` after the drift guard | Every local CI run leaves churn to revert | M | Refactor: write to a temp dir or run before the guard | `git status` clean after fast CI |
| G8 | OBSERVED | 20 test files are outside every CI run | `abx-afe/tests` (11) and `skills/tests` (9) are outside `testpaths`; `skills/tests/test_holler_ingest_safety.py` needs `requests_cache`, which is not a declared dependency (the other 85 `skills/tests` pass) | Skill safety tests never run in CI | M | Add to fast CI; declare or skip the optional dependency | CI log |
| G9 | OBSERVED | Doc-text tests pin prose | `tests/test_readme_status_alignment.py`; `tests/test_temporal_continuity_repair_execution_plan_router.py:396-402` expects a script name that is absent from README and AGENTS (static evidence; I did not run that test in isolation) | Doc rewrites break tests, and docs-only PRs auto-merge without CI | M | Convert to invariant checks or delete | — |
| G11 | OBSERVED | Safety hardening left contradicting tests behind | `1e2a5b01` made slang-emergence, HyperAgent deploy and Holler ingest fail closed and added safety tests in `skills/tests` (never run by CI); five tests in `tests/` still asserted the invented 0.89 Brier score, live deploy, and fallback data | Fast CI went red, and the stale tests pinned the unsafe behaviour | H | **Fixed in this PR:** the five tests now assert the fail-closed contract (Jev `align_five`, 0.89) | 12 tests pass |
| G12 | OBSERVED | Two Sigil-Forge tests depend on a sibling checkout | `tests/test_sigil_forge_mount.py:119,182` need `~/Sigil-Forge`; without it the bridge falls back to `local_spare_reduction` | Fast CI is red on any machine without that checkout | M | **Owner decision:** skip when the sibling is absent, or vendor a fixture | Fast CI green on a clean machine |
| G10 | OBSERVED | About 75 tests skip when an artifact is absent, and `pytest.ini` sets `--maxfail=1` | 79 `pytest.skip` plus 71 `importorskip` | A clean checkout passes vacuously, and full-suite red size is hidden | M | Refactor: seed into `tmp_path`, drop maxfail from the full suite | — |

### Shared primitives and authority

| ID | Label | Finding | Evidence | Consequence | Sev | Disposition | Verify by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | OBSERVED | Canonical hashing is reimplemented about 140 times with different semantics | 83 `_canonical_json`, 8 `_canonical_hash`, 6 `stable_hash`, 41 inline `sha256(json.dumps(...))`; for example `core/abraxas_oracle_change_ledger.py:15` (`default=str`, 16-hex truncation) and `core/aal_viz_yggdrasil_topology_delta_intelligence.py:60` (`ensure_ascii=True`) | The same payload gets different "canonical" hashes in different modules | H | Consolidate onto `core.canonical.json`, one family per PR, gated by drift check | Property test comparing each helper with `canonical_hash` |
| A2 | OBSERVED | `canonical_dumps` accepted NaN/Infinity and did not round floats inside tuples | `core/canonical/json.py` | Invalid JSON could be written, and tuple vs list inputs hashed differently | M | **Fixed in this PR** | `tests/test_canonical_json.py` |
| A3 | OBSERVED | The advisory spine asserts its own activation evidence | `core/application/advisory_spine.py:51-73` `_lane_request` hard-codes every control as present (for example `operator_review_present=True` for INTERNAL_CANARY). The API caller chooses the lane. | `INTERNAL_CANARY` gets CONDITIONAL_ALLOW for any anonymous caller. Effects stay advisory-only. | H | Refactor: controls come from settings or receipts. **Needs a decision on the evidence source** (§8, Decision 4). | `test_activation_policy` lane matrix through the spine |
| A4 | OBSERVED | Lock enforcement is fragmented | Pydantic `Authority` (6 flags); `_FORBIDDEN_AUTHORITY_TRUE_FLAGS` (7, checked only for `GOVERNANCE_DECISION`, a class used 0 times); 163 per-module `_authority_locks()` vocabularies; 576 bare `write_canonical_json` writers bypass classification | A true lock is caught only if its key is in a 7-name set | H | Consolidate the vocabulary; validate in `write_canonical_artifact` for every class | Test feeding every `_authority_locks()` key set |
| A5 | OBSERVED | Paths and settings have two owners | `RuntimePaths.from_env` reads `OUT_DIR`/`CONTRACTS_DIR` relative to cwd (217 users). `RuntimeSettings` reads `ABRAXAS_*` relative to repo root (11 users). `RuntimeSettings.runtime_paths()` has 0 callers. cli.py hard-codes `REPO_ROOT/"out"`. | The same deployment can resolve two different `out/` roots | M | Consolidate on `RuntimeSettings`; derive `RuntimePaths` | Settings tests |
| A6 | OBSERVED | `analyze --schema-ref` resolved against the process cwd | `run_advisory_spine` called `validation_validate` without `repo_root`, while `AbraxasClient.validate` passed it | `analyze` and `validate` disagreed on the same schema outside the repo dir | H | **Fixed in this PR** | `tests/test_advisory_spine_repo_root.py` (fails before, passes after) |
| A7 | OBSERVED | A network call in core bypasses the provider port | `core/codegen/oracle_signal/oracle_full_live_runtime_execution.py:225-231` calls `urlopen` on an env-supplied URL with no scheme allowlist. The gates are a source-literal phrase and `execute_requested`. `gated_invoke` has 0 non-test callers. | Latent: the default is off. If enabled, `file://` would be accepted. | M | Route through `ProviderPort` + `gated_invoke`; allow http(s) only | Callers of `urlopen` |
| A8 | OBSERVED | Layering inversions | core→scripts: `core/abx_research_canary_artifact_registry_coverage_audit.py:14` and six `core/sync/v2_hygiene_phase1_*_gate.py:12` files. core→abraxas: `core/hyperstition_*` → `abraxas.v2`; `core/production_convergence/recovery_drill.py:9` → `AbraxasClient`. Cycle: `contracts/codegen/validators.py:9` → `core.canonical.json`. | Import-order fragility; core cannot be used without scripts | M | Move the shared constants and `abraxas/v2` models into core | Import graph shows 0 such edges |
| A9 | OBSERVED | Wall-clock in deterministic builders | 45 core files call `datetime.now`; 5 dataclasses have `default_factory=datetime.now`; `uuid4` fallbacks in `core/services/validation_service.py:83`. The `Clock` port is used by 4 files. | Rebuilds are not byte-stable | M | Refactor builders to take `Clock` | Double build with a frozen clock |
| A10 | OBSERVED | API exposure is inverted | Read-only GETs are denied by default, but `POST /analyze` is on and anonymous. The size check runs after parsing. Unvalidated `X-Request-ID` was echoed back. | Compute is open while reads are closed | M | Request-ID validation **fixed in this PR**. Default posture held for operator (§8, Decision 4). | `tests/test_api_service_hardening.py` |
| A11 | OBSERVED | Bad input gives a 500 or a traceback | `AnalyzeRequest.alembic_mode` is a plain `str`, so `"bogus"` → HTTP 500; the CLI prints a raw pydantic traceback | Clients cannot tell misuse from failure | M | Map to 4xx and a typed CLI error | API test with an invalid mode |
| A12 | OBSERVED | `replay` re-executes; it does not replay | `abraxas/client.py:105-133` drops input_payload, schema_ref, oracle_candidate and lane, and rewrites run_id | `replay` cannot verify a prior result | M | Clarify the name, or store and replay the full request | Replay hash equals the original |

### Structure and dead code

| ID | Label | Finding | Evidence | Consequence | Sev | Disposition | Verify by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | OBSERVED | `core/` is 92% off the product path | Reachability table (§3) | Shared-primitive changes ripple through about 1,400 lane modules | M | Clarify with tiers (§4); defer removal to CLEAR | — |
| S2 | INFERRED | 21 scaffold packages share one 6-file template | overlay_*×8, human_decision_*×2, manual_*×3, proposal_*×3, review_*×2, and others: 248 files, all from the 2026-05-06 version-sweep commits; lineage/replay siblings are 0.86–0.94 similar | Every fix is replicated 21 times | M | Consolidate later into generic Lineage/Replay packets. Blocked by hash-pinned `schema_version` names in `out/`. | Drift check unchanged |
| S3 | OBSERVED | `core/sync/` is misnamed | 137 files, 59.8k lines, 109 of them `v2_hygiene_phase*` gate generators; 0 product consumers | The name hides what it is | L | Rename into a receipts namespace. Blocked by the `tests/script_runner_loader.py` `core.sync.X` rule. | — |
| S4 | OBSERVED | Metric families are mostly lifecycle ceremony | 115 modules, 42.9k lines; about 6 compute anything; no consumers outside the families | Experiments never connected to the spine | M | Keep the kernels; archive the ceremony after CLEAR | — |
| S5 | OBSERVED | Empty files satisfy milestone evidence | `core/spine/milestone_registry.py:106` checks `exists()`; the v2.0.1 rune-layer milestone cites four 0-byte files and two missing tests | Milestone "complete" status is not evidence | H | Refactor: require a non-empty, importable file with the expected symbols. **Next phase**, because it changes milestone receipts. | Registry test |
| S6 | OBSERVED | The top-level `api/` is a second, unguarded API | `api/{hybrid,sse,websocket}_server.py` bind `0.0.0.0` with an unauthenticated `POST /process`; no importers, tests or CI; CLEAR entry DEFER | A footgun if anyone runs it | H | Deprecate now; remove under CLEAR | — |
| S7 | OBSERVED | Dead and broken root files | `aal_ongoing_evolution.py` (syntax error), `abraxas_v2.0_summary.md` (12 bytes), empty `abraxas_v2/__init__.py`, and three core modules containing only placeholder text | Noise; one is not valid Python | L | **Removed in this PR** (no references found) | Full-suite run |
| S8 | OBSERVED | `core/hygiene/` and `core/conflict_scan.py` are documented as merged but have no callers or tests | Named only in ARCHITECTURE/STATUS/docs | Overstated readiness | M | Clarify as "not wired" | — |
| S9 | OBSERVED | `dashboard/app.py` cannot run | It needs `streamlit`, which is not a dependency; it is the sole importer of `workflows/la_ca_adaptive_pipeline.py` | Dead path | L | Move to `examples/` or remove | — |
| S10 | INFERRED | About 60% of the 795 scripts are one-shot receipt generators | 509 receipt/gate/plan names; 237 have no CI, test or doc reference | Navigation cost | L | Defer to CLEAR (it lists "712 runners" as MERGE_CANDIDATE) | — |

### Documentation and roadmap

| ID | Label | Finding | Evidence | Disposition |
| --- | --- | --- | --- | --- |
| D1 | OBSERVED | STATUS and PLANS are dated 2026-08-11 / tip #1133 | 30 commits landed since then. They include the Sigil-Forge and Neon Genie SHADOW mounts (#1148), spec packs 009–013A (#1142–#1144), Familiar scanner SHADOW evidence (22 direct-to-main commits) and persistence observability (#1152–#1153). Four open PRs (#1149, #1151, #1154, #1155) against "0 open". | STATUS current-state block **refreshed in this PR** |
| D2 | OBSERVED | ARCHITECTURE makes claims the code disproves | "Core modules never write to disk" (472 core files write); "RuntimePaths: all output paths in one place" (about 615 literal paths); "Tests never write to out/" (G3); `artifacts/shadow/` does not exist; "Grok and Codex are peer collaborators" is stale | **Corrected in this PR** |
| D3 | OBSERVED | PLANS.md is about 80% closed-history log | Lines 322–995 are the LOOP-805 slice log and the P70–P130 archive | Clarify: a short roadmap at the top (this PR adds the phase table); archive the log later |
| D4 | OBSERVED | `MEMORIES.md` had unresolved merge-conflict markers | Lines 7–13; both sides cited PRs #1015/#1016/#1018, all merged 2026-07-26 | **Resolved in this PR** |
| D5 | OBSERVED | Four version numbers | See §2 | Operator decision (Decision 3) |
| D6 | OBSERVED | Only one spec carries the full chain from journey to task | `docs/integrations/ABX_SHADOW_PERSISTENCE_OBSERVABILITY_001.md` (#1152) has a traceability table; nothing else does | Use it as the template; §7 applies it to `analyze` |

## 6. Changes in this PR

| Change | Behavioural implication | Equivalence or proof |
| --- | --- | --- |
| `run_advisory_spine(..., repo_root=)`, passed by `AbraxasClient` and `routers.analyze` (A6) | `analyze --schema-ref` resolves against the configured repo root, not the cwd. The API uses `settings.repo_root`, which defaults to the cwd, so it is unchanged unless `ABRAXAS_REPO_ROOT` is set. | New test fails on the old code and passes on the new; existing CLI/API/validation tests pass |
| `canonical_dumps`: `allow_nan=False`, tuples normalized like lists (A2) | NaN/Infinity now raise `ValueError` instead of writing invalid JSON. Tuple floats round to 6 places, so hashes change only for in-memory tuples containing floats. | New serializer tests. Full suite and drift check: see §9. |
| `X-Request-ID` echoed only if it matches `[A-Za-z0-9._:-]{1,128}`; otherwise a fresh ID (A10) | Unsafe or oversized client IDs are replaced | New parametrized hardening test |
| CI path filters add `abraxas/**`, `apps/api/**`, `contracts/**`, `skills/**` (G5) | More PRs trigger CI once hosted CI is back on | Workflow diff |
| Removed six dead or placeholder files (S7) | None. They had no references; one was a syntax error. | Reference search plus full suite |
| Evolution-cycle runner records the decision validator's BLOCKED status instead of failing (G2) | The cycle exits 0 while awaiting an operator decision and writes `operator_decision_validation_status`. A validator crash, or a missing BLOCKED receipt, still fails the cycle. The validator is unchanged and still fail-closed. | `test_full_cycle_rc0_no_mutation` passes; 83 skill-evolution and stabilization tests pass |
| Five tests aligned with the 2026-09-15 fail-closed skill contracts (G11) | Tests only: they now assert NOT_COMPUTABLE with no invented slang or Brier score, refusal of live deploy, and `IngestError` without leaking the raw error | 12 tests pass |
| Skill-evolution tests stop writing into the real `out/operator_input/` (G3) | Tests only. Two tests that relied on the planted fake decision now build their own fixture in `tmp_path`; the reconciliation test also accepts the documented `CURRENT_DECISION_MISSING` state. | `out/operator_input/` holds no decision after the run |
| `MEMORIES.md` conflict resolved; STATUS, ARCHITECTURE and PLANS reconciled (D1, D2, D4) | Docs only | Doctrine validator and doc tests |

Judgment calls were run through Jev (TypeSafe System One):

| Call | Jev answer | Confidence | Note |
| --- | --- | --- | --- |
| Runner fix for G2 | record BLOCKED as status | 1.0 | First blocked by the permission classifier as weakening a security check; applied after explicit operator approval on 2026-10-10 |
| CI path filters | add | 0.94 | — |
| Review recorded as one audit doc plus corrections | yes | 0.96 | — |
| Serializer fix now | yes | **0.58 (low)** | Applied, conditional on the drift check staying clean |
| Remove dead files now | yes | **0.46 (low)** | Limited to six files with no references; nothing under CLEAR's scope |
| Pre-existing fast-CI failures | align the five stale skill tests; leave Sigil-Forge to its owner | 0.89 | — |

## 7. Specification chain: `analyze`

This applies the template from `docs/integrations/ABX_SHADOW_PERSISTENCE_OBSERVABILITY_001.md`.

| Step | Content |
| --- | --- |
| **Journey** | An operator or service submits a payload (with an optional schema, Oracle candidate or Alembic task) and receives a deterministic advisory result that grants no authority. |
| **Workflow** | Adapter (CLI `analyze` or `POST /analyze`) → lane check → schema validation → Oracle-to-task bridge → Alembic advisory execution → `canonical_hash` → return. The CLI may also write the result via `write_canonical_artifact`. |
| **State transitions** | `REQUEST` → `DENIED` (lane not permitted, or a FORECAST-lane task) · `OPERATOR_GATE` (EXTERNAL_PRODUCTION) · `INVALID_INPUT` (schema failure) · `OK` (advisory result + hash). There is no other terminal state, and no state grants authority (`_AUTHORITY_LOCKS` are all false). |
| **Contracts** | `AdvisorySpineRequest` (pydantic, `extra=forbid`); `contracts/services/validation_service.{request,response}.v1.schema.json`; `contracts/api/openapi_supported_surface.v1.json`; `ActivationLane`/`ActivationRequest` (`core/governance/activation_policy.py`) |
| **Acceptance tests** | AT-AN-1, EXTERNAL_PRODUCTION → OPERATOR_GATE (`tests/test_api_analyze.py`, `tests/test_abraxas_cli.py`). AT-AN-2, the same input gives the same `canonical_hash` (CLI tests). AT-AN-3, `schema_ref` resolution does not depend on the cwd (`tests/test_advisory_spine_repo_root.py`, new). AT-AN-4, an invalid `alembic_mode` gives 4xx, not 500 (**missing**, A11). AT-AN-5, lane evidence is not self-asserted (**missing**, A3). |
| **Implementation tasks** | Phase 1 (below): A11 → AT-AN-4; A3 → AT-AN-5; A12 decides what `replay` means. |

## 8. Decisions

Operator decisions on 2026-10-10. Each one is applied in this PR (§6 and §15).

| # | Question | Decision |
| --- | --- | --- |
| 1 | Evolution-cycle fail-closed status (G2/G3) | Fix approved; applied |
| 2 | Repository identity | v2.0 is the **doctrine and reference** repo; its code is reference, not a supported product. `Zero-State-LLC/Abraxas` `main` is canonical execution. Executable work moves by reviewed, tested port (`docs/SIBLING_REPOS.md`). |
| 3 | Version authority | v2.0 claims no product version. The `v1.N.M` tags are doctrine revisions, mirrored in `VERSION` and checked by a timing-aware validator (`docs/releases/VERSION_STRATEGY.md`). |
| 4 | `/analyze` and canary evidence | Authenticated by default. Anonymous access only behind an explicit local-dev flag that cannot apply in a deployed profile. Bounded rate, size and time. Canary activation only on signed evidence from outside the candidate. |
| 5 | CI | No private Actions billing. Prepare publication; if it stays private or blocked, use the committed local-CI record. |
| 6 | Sigil-Forge | Pinned fixture for contract tests; live tests behind a registered marker; a required lane fails without the checkout. |

**Still open (operator judgment):**

1. **Publication blockers** (§13). The roughly 2,400 pre-relicense commits are Apache-2.0. Commit metadata contains personal emails and machine hostnames. A scraped ModularGrid catalog is in the tree. Publishing needs either a fresh-history public mirror or an authorized history rewrite.
2. **Deletion queue** (§12). Each entry needs two named, distinct operators.
3. **Port PRs to `Zero-State-LLC/Abraxas`** (§11). They are opened for review only; merging is the canonical repo owners' call.
4. **graft `.gitignore` line.** It is kept local (Jev 0.26, low confidence). Commit it only if the team adopts graft.

## 9. Verification (this PR)

- Targeted: `tests/test_advisory_spine_repo_root.py`, `test_api_analyze.py`, `test_abraxas_cli.py`, `test_validation_service.py` → 18 passed. `tests/test_canonical_json.py` → 19 passed. `tests/test_api_service_hardening.py` → 8 passed.
- Full suite, every marker, no maxfail (`pytest -o addopts="" --maxfail=100000 tests`). On `main` at `2861822b`: 13,793 passed, 59 failed, 7 skipped. On this branch before the G2/G3 fix: 13,802 passed, 59 failed, 7 skipped. The failure sets were **identical**, so the other changes introduce no regression. The 59 pre-existing failures fall into these groups: temporal-continuity doc and registry pins (20), AAL-Viz projection (14), research-canary registry audits (7), codegen spine plans (4), slang-emergence (3), governance runtime scaffold (2), Sigil-Forge mount (2), skill evolution (2, fixed here), and 5 singles. They are recorded for P0; none was introduced here.
- Skill-evolution set after the G2/G3 fix: 83 passed. `skills/tests`: 85 passed (excluding the file that needs `requests_cache`).
- Fast CI selection (`-m "not slow and not integration and not canon and not artifact"`, no maxfail): on `main`, 8 failures (7 listed in G11/G12 plus `test_full_cycle_rc0_no_mutation`). On this branch, 2 failures, both G12 (`test_sigil_forge_mount.py`, which needs `~/Sigil-Forge`). The drift check passes. Fast CI's ruff step passes, and pyright exits 0 on its 100 bounded targets. Ruff findings on every changed file are at or below their count on `main`.

### Revision 2 verification (LOCAL_VERIFICATION, not GitHub Actions)

The record is `docs/status/local-ci/005417806567500e21909dd974be373412b7d668.json`. It was run with `python -m scripts.governance.local_ci_record run` in a fresh worktree at `00541780`: a true clean checkout, with no ignored leftovers.

- **Full suite:** 13,908 passed, **1 failed**, 10 skipped. `main` had 59 failures (53 on a clean checkout).
  - The single failure is the P84 bridge route-refresh test, which is tracked-artifact drift (G13). It is now a strict xfail in `tests/known_failures.json` (P3).
- **Fast CI:** exited 1 on that same test. Its selection now includes every governance test.
- **Record status:** **FAIL.**
  - Partly that test.
  - Partly that fast CI's report-only advisory gates still rewrite four tracked `out/production_readiness/*` files after the drift guard (G7, open).
  - The record tool's path parser dropped the first character of the first changed path. Fixed in the next commit.
- **Validity:** commits after `00541780` changed code (the registry entry, the parser fix), so `local_ci_record check` reports this sign-off as superseded. **A fresh record is the next step.**

### Revision 2b verification (2026-10-13, LOCAL_VERIFICATION, not GitHub Actions)

The record is `docs/status/local-ci/ed7fe4409636fd437275a3c4006bf68b707913a2.json`, taken in a fresh worktree at `ed7fe440`, after the G7 fix (advisory gates run with `--no-write`).

- **Status: PASS.**
- **Fast CI:** exit 0, with every governance test selected.
- **Full suite:** 13,908 passed, 1 xfailed (the registered P84 drift, strict), 10 skipped.
- **Tree:** tracked files unchanged by the run.
- **Validity:** this sign-off stays valid until a non-documentation change lands (`python -m scripts.governance.local_ci_record check`).

## 10. Phase status (revision 2)

| Phase | Status | Done (evidence) | Remaining | Depends on |
| --- | --- | --- | --- | --- |
| **P0 Trustworthy gate** | **Done, except G10** (G7 fixed 2026-10-13; local CI record PASS at `ed7fe440`) | G2, G3, G4 and G15: explicit markers, governance tests selected, strict-xfail registry. G14: 34 tracked-file writers isolated, plus a session guard. G16: three real bugs fixed. G11, G12, G13, A11. Pre-existing failures fixed rather than skipped (§9). | G7: the fast-CI advisory gates still write tracked `out/production_readiness/*` after the drift guard. G10: the session seed fixture still writes ignored `out/audit` files, and some tests still read them. | — |
| **P1 Spine hardening** | **Mostly done** | A3 (signed independent canary evidence), A10 (auth by default), A11 (4xx), A6, the version endpoint | A5 settings consolidation; A12 `replay` semantics; ports §11 | Port PR review upstream |
| **P2 Single-owner primitives** | Not started | — | A1, A4, A8, A9 | P0 |
| **P3 Truthful evidence** | Partly done | D1–D5 and D7 docs/version reconciled; G13 registry truthfulness | S5 milestone evidence, S8, G6 pyright, G9 doc pins elsewhere, D3 PLANS log archive | P0 |
| **P4 Reduction under CLEAR** | Queued | §12 deletion queue with evidence | Two-operator sign-off per entry | CLEAR mandate |

## 10a. Phases as first planned (superseded by the table above)


| Phase | Outcome | Items | Depends on | Acceptance | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| **P0 Trustworthy gate** | Fast CI green and meaningful | G2+G3 (Decision 1), G4, G7, G8, G10 | Decision 1, Decision 5 | Fast CI exits 0 on a clean checkout and leaves `git status` clean; governance tests selected; `skills/tests` run | CI log; `git status` |
| **P1 Spine hardening** | T1 contracts explicit and tested | A3, A10 default, A11, A12, A5 | P0, Decisions 2 and 4 | AT-AN-4 and AT-AN-5 pass; one settings owner | Tests |
| **P2 Single-owner primitives** | One hash, one lock vocabulary | A1 (per family), A4, A9, A8 | P0 | 0 private hash helpers in T1/T2; locks validated on every write; frozen-clock double build is byte-identical | AST scan; drift check |
| **P3 Truthful evidence** | Milestones and docs cannot overstate | S5, S8, G9, D3, D5, G6 | P0 | Milestones require importable code; pyright `basic` on T1 | Registry test; pyright log |
| **P4 Reduction under CLEAR** | Smaller tree | S2, S3, S4, S6, S9, S10 | CLEAR dual-control mandate | Exact-path mandate; drift check unchanged | Mandate + PR |

## 11. Port queue to `Zero-State-LLC/Abraxas`

The ranking and its evidence come from a read-only survey of upstream `main` at `94021671`. Upstream has no `/analyze` equivalent and no single auth scheme. Its closest compute route, `POST /api/oracle/run`, has no authentication, rate limit or body limit. Its HMAC receipts (`shared/signing.py`) silently fall back to unsigned. Its lifecycle lanes (`abx/lifecycle_policy.py`) accept self-reported evidence booleans. pawl reports are unsigned and not bound to a commit.

| # | Port | Status | Evidence |
| --- | --- | --- | --- |
| 1 | `canonical_json` rejects NaN/Infinity | **Prepared**: commit `bd741113` on local branch `port/canonical-json-reject-nan`, patch in the backups folder | Upstream full suite in an isolated env: 3956 passed / 30 failed. The 30 are the same as the unmodified baseline; the new test passes. Rounding is deliberately **not** ported, because it would change upstream hashes. |
| 2 | Access policy for `/api/oracle/run` (X-ABX-Token, loopback-only anonymous, rate/body/time bounds) | Designed (`apps/api/boundaries.py`) | Needs upstream design review: upstream mixes FastAPI and Express |
| 3 | Signed independent canary evidence mapped onto SHADOW→CANARY→ACTIVE | Designed (`core/governance/activation_evidence.py`) | Upstream receipts must stop falling back to unsigned |
| 4 | Validation service | Queued | — |
| 5 | Advisory spine | Last, if ever | It drags in `core/alembic` (29 files) |

## 12. Deletion queue (awaiting two-operator sign-off)

Nothing below is deleted. CLEAR (`docs/status/CLEAR_DUAL_CONTROL_OPERATOR_CHECKLIST_001.md`) requires two **distinct named operators** per mandate, listing exact paths. Repeated runs by one agent do not count as two operators. Evidence was gathered on 2026-10-10 by reference search over every `.py/.json/.yml/.toml/.md/.js/.ts` outside `out/`, plus dynamic-loader rules.

| Path(s) | Evidence | Why remove | Blocker | Operator A | Operator B |
| --- | --- | --- | --- | --- | --- |
| `api/hybrid_server.py`, `api/sse_server.py`, `api/websocket_server.py` | Only named in `core/production_convergence/{inventory,duplication,deprecation_ledger}.py` data, as deprecation candidates. No importers, tests or CI. | They bind `0.0.0.0` with an unauthenticated `POST /process`, outside every access control (S6) | CLEAR entry DEFER | | |
| `dashboard/app.py`, `workflows/la_ca_adaptive_pipeline.py` | `dashboard` needs `streamlit`, which is not a dependency, so it cannot run. `workflows/` is imported only by `dashboard` and named in `docs/intelligence_quickstart.md`. | Dead path (S9) | — | | |
| `core/execution/__init__.py`, `core/execution/context.py`, `core/execution/replay_runner.py`, `core/runes/rollback.py` | 0 bytes; no references | Empty modules | S5: sibling empty files are cited as milestone evidence; fix S5 first | | |
| `core/evaluation/evaluator.py`, `core/temporal/temporal_slicing.py`, `core/rune_bind_merge_candidate_generator_stub.py`, `core/shadow_map_generator_stub.py`, `core/temporal_formula_export_helper_stub.py` | No static, dynamic, string, CI or doc references | Unconnected stubs | — | | |

These are **not queued**; they need owner judgment:
- `.codebase-memory/graph.db.zst` (22.7 MB in HEAD). It is referenced by `.gitattributes`, `.gitignore` and a phase-13 receipt.
- Root `scripts.py`, a shadowed shim. Its reference search is ambiguous.
- The scraped ModularGrid catalog under `skills/modular-synth-catalog-research/references/` (publication blocker, §13).

## 13. Publication readiness (`Zero-State-LLC/Abraxas-v2.0`)

Reviewed 2026-10-10. The review was read-only; visibility, settings and history were not changed. **Verdict: not ready to publish as-is. Owner authorization is needed.**

- **Secrets: none found.** Gitleaks 8.30.1 (`--redact`) scanned the full history of a fresh mirror (4,518 commits, including the 1,107 `refs/pull/*` that become public), the working tree, all 1,156 issue/PR bodies and all 1,309 comments. It produced 18 findings, all the `generic-api-key` rule matching 64-hex SHA-256 digests. A pattern sweep of every added line for AWS, GitHub, OpenAI/Anthropic, Slack, Google, Stripe and HF keys, JWTs, PEM blocks, password assignments and credentialed URLs found 0. No `.env`, key, keystore or dump file was ever committed. **Nothing needs rotation.** Scanner output is evidence, not proof.
- **Blockers that need owner authorization:**
  1. **Licence history.** About 2,400 of `main`'s 2,608 commits predate the relicense (`d1821fa7`, 2026-07-29) and are **Apache-2.0**. Publishing would release those snapshots permanently. Rewriting history cannot clear GitHub's retained `refs/pull/*`, so a **fresh-history public mirror** is the cleaner route.
  2. **Personal data in commit metadata.** Two personal gmail addresses, an openclaw.ai address, and the hostnames `lunas-MacBook-Air.local` and `AAL-mainnet.localdomain` as author emails. The commits in this PR use the same local identity. 64 home-directory paths in the tree.
  3. **Third-party content.** A scraped ModularGrid catalog (it says so in its own header) and an arXiv abstract.
- **Owner judgment:** 152 private Notion page links in the tree (522 in history); all issues and PRs becoming public; the 22.7 MB database file in HEAD.
- **Settings to fix before any publication:** enable secret scanning and push protection; add a `main` ruleset with required checks (`main` is unprotected today); require approval for outside contributors' workflows; then set `HOSTED_ACTIONS_AVAILABLE=true`. Workflows are already safe for public forks: no `pull_request_target` or `workflow_run`, and only `GITHUB_TOKEN`. `LICENSE` is now off the docs auto-merge list (this PR).
- **Runner eligibility:** GitHub-hosted standard runners are free for public repositories (GitHub billing docs; INFERRED, not re-fetched). This org is on the Team plan, and its Actions settings returned 403 to this account.
- **Stopgap in force:** `python -m scripts.governance.local_ci_record run|check` (§9). Local records are LOCAL_VERIFICATION, never GitHub Actions results.

## 14. Challenge review (revision 2)

| Question | Answer |
| --- | --- |
| Did complexity disappear or move? | Path-word markers, self-asserted canary controls, placeholder auth and four version numbers were removed outright. New surfaces: one evidence verifier, one access-policy module, one version validator, one local-CI tool and one mirror helper. Each replaces implicit behaviour with an explicit, tested contract. `run_doctrine_validator` still hard-codes 30+ cwd-relative paths; tests work around it with a mirror rather than fix it (P2). |
| One owner per responsibility? | Repository ownership: `SIBLING_REPOS.md`. Version: `VERSION_STRATEGY.md` plus the validator. Canary authority: the trust store (deployment), never the candidate. Settings are still split (A5, P1). |
| Doctrine vs reference vs supported execution? | Distinguished in README, ARCHITECTURE, STATUS, `/version` (`role: doctrine-reference`, `product_version: null`) and pyproject (`0.0.0+reference`). |
| Can a new engineer trace the workflows? | `analyze`: §3 map plus §7 chain. Canary: `activation_evidence` docstring → `evaluate_activation` → spine. |
| Necessary distinctions lost? | No. DERIVED_OPTIONAL vs BUILD_CANONICAL was **restored** for P79–P84. Evidence statuses keep nine distinct failure reasons. |
| Auth and canary safe by default? | Yes. With no token configured the endpoint returns 503. The anonymous flag is refused outside `local` and from non-loopback clients. Canary evidence that is absent or unverifiable denies the lane. Limitation: the rate limiter is per process, and a timed-out worker thread is not killed (reference only). |
| Evidence independently verifiable? | Yes: Ed25519 with a deployment-owned trust store. The candidate cannot sign; self-issued evidence is SELF_ASSERTED. No real issuer exists yet: pawl and CI produce no signed, SHA-bound evidence (§11). |
| Fixtures keep contract coverage? | The Sigil-Forge pin asserts the same frozen identity; the replay raises on any unrecorded intent; a live drift test compares live output with the pin. |
| Skips and local CI honest? | Missing-checkout tests are SKIPPED, or an error in required lanes. Known failures are strict xfails listed in `tests/known_failures.json`. Local records say LOCAL_VERIFICATION. |
| Implementation, docs, bindings, version policy and kanban agree? | Checked by the doc tests, the doctrine validator and the version validator (§9). The GitHub Project board was not updated; it is the owner's board. |

## 15. Revision-2 findings and dispositions

| ID | Label | Finding | Disposition |
| --- | --- | --- | --- |
| G13 | OBSERVED | Four P79–P84 plans were drift-checked as BUILD_CANONICAL although they derive from a git-ignored input. The two test sets contradicted each other. | **Fixed:** DERIVED_OPTIONAL (Jev 0.91) |
| G14 | OBSERVED | 34 test modules wrote tracked files. One rebuilt `projection-bundle.json` (−181k lines) and the topology artifact from a degraded corpus, which broke later tests. | **Fixed:** tmp roots, a repo mirror, or injected output (one new `--output-root` flag); plus a session guard |
| G15 | OBSERVED | `pytest.ini` set `norecursedirs = temporal viz` ("skip broken suites"); markers were inferred from path words. | **Fixed:** explicit markers, `--strict-markers`, `xfail_strict = true` |
| G16 | OBSERVED | Three real bugs hid in deselected tests: `review_queue` KeyError on the gate-status contract; generator paths stale after the `scripts/<domain>` move; `AuthorityScope.NOT_COMPUTABLE` removed but still used. | **Fixed**, each failing closed |
| G17 | OBSERVED | Content-count and doc pins had drifted with legitimate additions or moved text. | **Fixed** with cited commits; assertions unchanged |
| D7 | OBSERVED | Version authority: 2.5.0 was a "product version"; the tags are snapshots; CHANGELOG commit-back was removed in #1121. | **Fixed** (§8 decision 3) |
| D8 | OBSERVED | Bindings pointed at archived `scrimshawlife-ctrl/Sigil-Forge` and `Hyperlex` copies. | **Fixed** |
| S11 | OBSERVED | Sigil-Forge bridge caches the first imported `forge_core` regardless of the matched root, so the discovery label can name the wrong engine. | Defer (P1); the tests work around it |
| P1-pub | OBSERVED | Publication blockers (§13) | Operator |
