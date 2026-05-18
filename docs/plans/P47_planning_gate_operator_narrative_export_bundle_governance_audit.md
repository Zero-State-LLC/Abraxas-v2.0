# P47 PLANNING GATE — OPERATOR NARRATIVE EXPORT BUNDLE GOVERNANCE AUDIT

## 1. P47 PLANNING SUMMARY
Decision: **P47_PLAN_READY** and **P47_AUDIT_REQUIRED**.

Selected lane: **Operator Narrative Export Bundle Governance Audit**.

This lane is audit-only, deterministic, and bounded to validating sealed P46 export outputs plus registry/governance semantics. It adds no capability surface and preserves passive/export-only posture.

## 2. SEALED BASELINE CONFIRMATION
Accepted baseline for this planning gate:
- P42: COMPLETE_AND_STABLE
- P43: COMPLETE_AND_STABLE
- P44: COMPLETE_AND_STABLE
- P45: COMPLETE_AND_STABLE
- P45_CI_REPAIRED
- P46: COMPLETE_AND_STABLE

Repo snapshot captured during planning:
- Branch: `work`
- HEAD: `1dc088186c923679738106f4fdc966ad87d0a286`
- Working tree: clean (`git status --short --branch`)

## 3. CANDIDATE INVENTORY

### Lane 1 — Operator Narrative Export Bundle Governance Audit
- Existing related files:
  - `core/operator_narrative_export_bundle.py`
  - `scripts/run_operator_narrative_export_bundle.py`
  - `tests/test_operator_narrative_export_bundle.py`
  - `out/exports/operator_narrative_export_bundle_001.latest.json`
  - `out/exports/operator_narrative_export_bundle_001.latest.md`
  - `core/generated_artifact_registry.py`
  - Audit precedents: P43/P45 governance audit modules.
- Missing surfaces:
  - P47 audit module/runner/schema/tests + audit artifacts.
- Likely inputs:
  - P46 export json/md.
  - Registry snapshot and CI drift classification view.
- Likely outputs:
  - `out/audit/operator_narrative_export_bundle_governance_audit_001.latest.json`
  - `out/audit/operator_narrative_export_bundle_governance_audit_001.latest.md`
- Governance risk: low.
- Determinism risk: low.
- Passive-reference leakage risk: low.
- Implementation cost: low-medium.
- Downstream leverage: high.
- Immediate operator value: high.

### Lane 2 — Operator Narrative Static Preview Bundle
- Existing related files:
  - P44 UI overlay + P46 export bundle.
- Missing surfaces:
  - preview contract + rendering/preview language boundary audit.
- Inputs:
  - P44/P46 artifacts.
- Outputs:
  - static preview bundle packet(s).
- Governance risk: medium.
- Determinism risk: medium.
- Passive-reference leakage risk: medium.
- Implementation cost: medium.
- Downstream leverage: medium.
- Immediate value: medium.

### Lane 3 — Export Bundle Archive Index
- Existing related files:
  - registry and bundle patterns.
- Missing surfaces:
  - archive index schema, chronology/stability rules.
- Inputs:
  - multiple export bundle generations.
- Outputs:
  - archive index artifact(s).
- Governance risk: low-medium.
- Determinism risk: medium (ordering over time).
- Passive-reference leakage risk: low.
- Implementation cost: medium.
- Downstream leverage: medium-high.
- Immediate value: medium-low.

### Lane 4 — Motif Governance Drift Receipt
- Existing related files:
  - motif governance surfaces.
- Missing surfaces:
  - replay-window substrate and stable cross-version selector.
- Inputs:
  - multiple motif generations.
- Outputs:
  - drift receipt artifact(s).
- Governance risk: medium.
- Determinism risk: medium-high.
- Passive-reference leakage risk: low.
- Implementation cost: medium-high.
- Downstream leverage: medium.
- Immediate value: low-medium.

### Lane 5 — Forecast Readiness Boundary Packet
- Existing related files:
  - partial governance scaffolds only.
- Missing surfaces:
  - strict SHADOW/FORECAST boundary packet chain.
- Inputs:
  - forecast/readiness related surfaces.
- Outputs:
  - readiness boundary packet.
- Governance risk: high.
- Determinism risk: medium.
- Passive-reference leakage risk: high.
- Implementation cost: high.
- Downstream leverage: deferred.
- Immediate value: low.

## 4. SCORE TABLE (1–5)
| Lane | Readiness | Immediate Value | Dependency Stability | Governance Safety | Implementation Cost (lower cost = higher score) | Audit Determinism Safety | Downstream Leverage | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. Export Bundle Governance Audit | 5 | 5 | 5 | 5 | 4 | 5 | 5 | **34** |
| 2. Static Preview Bundle | 3 | 3 | 3 | 3 | 3 | 3 | 3 | **21** |
| 3. Export Bundle Archive Index | 2 | 2 | 2 | 4 | 3 | 3 | 4 | **20** |
| 4. Motif Governance Drift Receipt | 2 | 2 | 2 | 3 | 2 | 2 | 3 | **16** |
| 5. Forecast Readiness Boundary Packet | 1 | 1 | 1 | 1 | 1 | 1 | 2 | **8** |

## 5. SELECTED P47 LANE
Selected lane: **Operator Narrative Export Bundle Governance Audit**.

Why it wins:
- Depends only on already-sealed P46 outputs and existing audit patterns.
- Hardens governance envelope and passive semantics before any externalized preview/index lanes.
- Maximizes safety and determinism with minimal capability expansion.

Why others wait:
- Static preview should follow governance proof to avoid language/control drift.
- Archive index is more valuable after P47 stabilizes per-bundle validation rules.
- Motif drift receipt remains substrate-constrained.
- Forecast readiness packet remains boundary-sensitive and premature.

Exact scope boundary:
- Validate P46 export bundle json/md and derived audit json/md only.
- Validate deterministic packet structure and governance boundary compliance.

Forbidden scope:
- No P46 packet mutation logic changes.
- No new UI/runtime commands or routing/queue/canon/runtime mutation.
- No forecast/readiness/recommendation/action semantics.
- No authority escalation.

Expected files (implementation lane, not this plan):
- `core/operator_narrative_export_bundle_governance_audit.py`
- `scripts/run_operator_narrative_export_bundle_governance_audit.py`
- `contracts/operator_attention/operator_narrative_export_bundle_governance_audit.v1.schema.json`
- `tests/test_operator_narrative_export_bundle_governance_audit.py`
- `core/config.py` (audit latest path)
- `core/generated_artifact_registry.py` (P47 audit artifacts)

Expected tests:
- schema/contract validation
- deterministic audit hash stability
- source missing/corrupt fail-closed tests
- fixed manifest role-order verification
- hash inventory equivalence verification
- bundle_hash recomputation verification (canonical packet-minus-bundle_hash)
- governance/language boundary forbidden token assertions
- registry classification assertions for P46 + P47 outputs

Expected artifacts:
- `out/audit/operator_narrative_export_bundle_governance_audit_001.latest.json`
- `out/audit/operator_narrative_export_bundle_governance_audit_001.latest.md`

## 6. EXPECTED FILES / ARTIFACTS
Expected P47 audit payload sections:
- `schema_version`, `patch_id`, `audit_id`, `final_status`, `audit_posture`
- `checked_artifacts` (P46 json/md paths)
- `manifest_integrity_summary`
- `hash_integrity_summary`
- `source_lineage_integrity_summary`
- `governance_envelope_integrity_summary`
- `registry_classification_summary`
- `language_boundary_summary`
- `findings`, `finding_counts`, `blocker_summary`
- `source_hashes`, `audit_hash`, `governance_flags`, `provenance`

## 7. AUDIT SEMANTICS
P47 audit must verify:
1. P46 export bundle JSON exists/readable.
2. P46 export bundle Markdown exists/readable.
3. `artifact_manifest` uses fixed role order:
   - report_json, report_markdown,
   - report_governance_audit_json, report_governance_audit_markdown,
   - ui_overlay_json, ui_overlay_markdown,
   - ui_overlay_governance_audit_json, ui_overlay_governance_audit_markdown.
4. All required P42/P43/P44/P45 artifact roles are present exactly once.
5. Manifest path refs are passive only.
6. Every manifest entry has `exists/readable/sha256/classification/passive_reference_only`.
7. `hash_inventory` equals manifest-derived hashes by artifact_id.
8. `source_lineage_map` is present and key-sorted/stable.
9. `governance_envelope` preserves export-only/passive-bundle-only/read-only/non-authoritative boundaries.
10. `bundle_hash` recomputes using canonical packet-minus-bundle_hash convention.
11. Markdown contains no command/action/recommendation/forecast/readiness/mutation language.
12. Registry classifies P46 export artifacts as `DERIVED_OPTIONAL` and not CI-drift-enforced.
13. Audit output contains no executable URLs, command fields, action fields, approval fields, routing fields, or mutation fields.

## 8. GOVERNANCE BOUNDARIES
- Audit-only lane; no capability additions.
- Deterministic and fail-closed.
- Non-authoritative, advisory-only, read-only.
- No queue/routing/canon/runtime mutation.
- Preserve SHADOW/FORECAST separation.
- Preserve sealed status of P42/P43/P44/P45/P46 and P45_CI_REPAIRED marker.

## 9. RISKS / DRIFT FLAGS
- Current checked-in P46 export artifact is `BLOCKED` and includes inherited blocker_summary terms containing forbidden words; P47 audit must distinguish inherited source strings from control semantics in audit-generated markdown.
- Registry statuses include `managed` and `orphaned` for md/json variants; audit policy should enforce determinism class and non-CI-drift enforcement, not require homogeneous final_status labels.
- If manifest contract evolves without synchronized tests, false FAIL/WARN drift is likely.

## 10. NEXT CODEX IMPLEMENTATION PROMPT
Implement **P47 Operator Narrative Export Bundle Governance Audit** with strict audit-only scope.

Required outputs:
- `core/operator_narrative_export_bundle_governance_audit.py`
- `scripts/run_operator_narrative_export_bundle_governance_audit.py`
- `contracts/operator_attention/operator_narrative_export_bundle_governance_audit.v1.schema.json`
- `tests/test_operator_narrative_export_bundle_governance_audit.py`
- registry/config wiring for audit latest path + artifact registration
- `out/audit/operator_narrative_export_bundle_governance_audit_001.latest.json`
- `out/audit/operator_narrative_export_bundle_governance_audit_001.latest.md`

Constraints:
- no queue/routing/canon/runtime mutation
- no recommendation/action/forecast/readiness semantics
- no authority escalation
- deterministic canonical hashing and sorted findings
- fail-closed on missing/corrupt sources
- preserve SHADOW/FORECAST boundary and all sealed states

