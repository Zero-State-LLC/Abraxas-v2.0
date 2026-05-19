# P52 PLANNING GATE — EXPORT / PREVIEW ARCHIVE INDEX

## 1. P52 PLANNING SUMMARY
Decision: **P52_PLAN_READY**, **P52_ARCHIVE_INDEX_REQUIRED**, and **P52_AUDIT_REQUIRED**.

Selected lane: **Export / Preview Archive Index**.

The safe P52 lane is a deterministic, passive archive index over the sealed P46/P47/P48/P49 export, preview, and governance receipt surfaces. The index should expose artifact path, hash, role, status, receipt posture, registry classification, and observed blocker metadata only. It must not create a package layer, execution layer, distribution claim, forecast surface, readiness surface, action route, command route, or control surface.

Planning posture: planning-only. No P52 code, generated artifact, queue, routing, canon, runtime, or archive package mutation is included in this planning gate.

## 2. SEALED BASELINE CONFIRMATION
Accepted sealed baseline:
- P42 Operator Narrative Report: COMPLETE_AND_STABLE
- P43 Report Governance Audit: COMPLETE_AND_STABLE
- P44 Report UI Overlay: COMPLETE_AND_STABLE
- P45 UI Overlay Governance Audit: COMPLETE_AND_STABLE
- P45 CI repair: P45_CI_REPAIRED
- P46 Narrative Export Bundle: COMPLETE_AND_STABLE
- P47 Export Bundle Governance Audit: COMPLETE_AND_STABLE
- P48 Static Preview Bundle: COMPLETE_AND_STABLE
- P49 Static Preview Governance Audit: COMPLETE_AND_STABLE
- P50 Static Preview Language Boundary Repair: COMPLETE_AND_STABLE
- P51 Structural Source Continuity Repair: COMPLETE_AND_STABLE

Repo state captured for this planning gate:
- Branch: `work`
- HEAD: `0df9e5c06e7cc6071a4654451dd96ef641a5eb15`
- Working tree before this planning document: clean
- Latest relevant history shows P51 merged at `0df9e5c`, P51 repair at `823ed90`, P50 repair at `d6d87eb`, P49 at `8e7db88`, P48 at `7c5dc2b`, P47 at `4e27957`, and P46 at `7e39dc0`.

Observed sealed-chain state:
- P46 export bundle exists and remains deterministic/passive with eight sealed source references.
- P47 export bundle governance audit exists with `final_status: PASS`, `audit_posture: CLEAN`, and no blocker summary.
- P48 static preview bundle exists and remains deterministic/passive over export plus audit references.
- P49 static preview governance audit exists with `final_status: PASS`, `audit_posture: CLEAN`, no blocker summary, validated preview hash, passive-reference checks, and language-boundary checks.
- P46/P48 still carry non-P51 upstream blockers as observed metadata. P52 must preserve those blockers without suppressing or resolving them.

## 3. CANDIDATE INVENTORY

### Lane 1 — Export / Preview Archive Index
- Existing related files:
  - `core/operator_narrative_export_bundle.py`
  - `core/operator_narrative_export_bundle_governance_audit.py`
  - `core/operator_narrative_static_preview_bundle.py`
  - `core/operator_narrative_static_preview_governance_audit.py`
  - `scripts/run_operator_narrative_export_bundle.py`
  - `scripts/run_operator_narrative_export_bundle_governance_audit.py`
  - `scripts/run_operator_narrative_static_preview_bundle.py`
  - `scripts/run_operator_narrative_static_preview_governance_audit.py`
  - `tests/test_operator_narrative_export_bundle.py`
  - `tests/test_operator_narrative_export_bundle_governance_audit.py`
  - `tests/test_operator_narrative_static_preview_bundle.py`
  - `tests/test_operator_narrative_static_preview_governance_audit.py`
  - `out/exports/operator_narrative_export_bundle_001.latest.{json,md}`
  - `out/audit/operator_narrative_export_bundle_governance_audit_001.latest.{json,md}`
  - `out/previews/operator_narrative_static_preview_001.latest.{json,md}`
  - `out/audit/operator_narrative_static_preview_governance_audit_001.latest.{json,md}`
- Missing surfaces:
  - archive index module, runner, schema, tests, registry coverage, and generated archive index artifacts.
  - archive path support in generated artifact registry scanning if `out/archive/` is used.
- Likely input artifacts:
  - P46 export bundle JSON/MD.
  - P47 export bundle governance audit JSON/MD.
  - P48 static preview JSON/MD.
  - P49 static preview governance audit JSON/MD.
- Likely output artifacts:
  - `out/archive/operator_narrative_export_preview_archive_index_001.latest.json`
  - `out/archive/operator_narrative_export_preview_archive_index_001.latest.md`
- Governance risk: low if path/hash/status only.
- Archive determinism risk: low because the lane indexes one sealed generation and can use fixed role order.
- Passive-index leakage risk: low if blocker text is metadata only and forbidden command/action/forecast/readiness language is excluded from generated prose.
- Implementation cost: low-medium because it follows P46/P48 bundle patterns and P47/P49 audit constraints, with one registry scope addition.
- Downstream leverage: high because it creates a stable substrate for P53 archive-index governance audit and later archive package assessment.
- Immediate operator value: high because it gives passive visibility across export, preview, and governance receipts without distributing or executing them.

### Lane 2 — Archive Index Governance Audit
- Existing related files:
  - P47/P49 governance audit patterns.
- Missing surfaces:
  - archive index artifact must exist first.
- Likely input artifacts:
  - P52 archive index JSON/MD after implementation.
- Likely output artifacts:
  - archive index governance audit JSON/MD.
- Governance risk: low.
- Archive determinism risk: low.
- Passive-index leakage risk: low.
- Implementation cost: medium.
- Downstream leverage: high.
- Immediate operator value: medium-high, but dependency-blocked until P52 index exists.

### Lane 3 — Static Preview Archive Package
- Existing related files:
  - export and preview artifacts; no package-specific archive surface.
- Missing surfaces:
  - audited archive index and package boundary doctrine.
- Likely input artifacts:
  - export, preview, archive index, and archive index audit artifacts.
- Likely output artifacts:
  - package manifest or package artifact, deferred.
- Governance risk: medium-high because package/distribution semantics can imply readiness or use.
- Archive determinism risk: medium.
- Passive-index leakage risk: medium-high.
- Implementation cost: medium-high.
- Downstream leverage: medium-high.
- Immediate operator value: medium, but premature without index and audit.

### Lane 4 — Motif Governance Drift Receipt
- Existing related files:
  - motif governance audit and motif overlay surfaces.
- Missing surfaces:
  - stable multi-generation replay-window substrate and cross-generation selector.
- Likely input artifacts:
  - motif audit generations and replay-window records.
- Likely output artifacts:
  - motif governance drift receipt JSON/MD.
- Governance risk: medium.
- Archive determinism risk: medium-high.
- Passive-index leakage risk: low.
- Implementation cost: medium-high.
- Downstream leverage: medium.
- Immediate operator value: low-medium for this lane because export/preview continuity is the active open threshold.

### Lane 5 — Forecast Readiness Boundary Packet
- Existing related files:
  - governance flags deny forecast/readiness authority across the narrative chain.
- Missing surfaces:
  - strict SHADOW/FORECAST boundary packet doctrine and source substrate.
- Likely input artifacts:
  - forecast/readiness-facing governance receipts, not yet mature.
- Likely output artifacts:
  - boundary packet JSON/MD.
- Governance risk: high.
- Archive determinism risk: medium.
- Passive-index leakage risk: high.
- Implementation cost: high.
- Downstream leverage: deferred.
- Immediate operator value: low for P52 because this would reopen SHADOW/FORECAST tension before the archive substrate is sealed.

## 4. SCORE TABLE
Scoring scale: 1–5. Higher is safer/better. Implementation cost is inverted, where lower cost receives a higher score.

| Lane | Readiness | Immediate Value | Dependency Stability | Governance Safety | Implementation Cost | Archive Determinism Safety | Downstream Leverage | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. Export / Preview Archive Index | 5 | 5 | 5 | 5 | 4 | 5 | 5 | **34** |
| 2. Archive Index Governance Audit | 2 | 4 | 2 | 5 | 3 | 5 | 5 | **26** |
| 3. Static Preview Archive Package | 1 | 3 | 1 | 2 | 2 | 3 | 4 | **16** |
| 4. Motif Governance Drift Receipt | 2 | 2 | 2 | 3 | 2 | 2 | 3 | **16** |
| 5. Forecast Readiness Boundary Packet | 1 | 1 | 1 | 1 | 1 | 2 | 2 | **9** |

## 5. SELECTED P52 LANE
Selected lane: **Export / Preview Archive Index**.

Why it wins:
- It has the highest deterministic score because P46/P47/P48/P49 artifacts now exist and can be consumed in a fixed role order.
- It adds immediate passive visibility over the sealed export/preview chain without creating package, distribution, execution, forecast, or readiness semantics.
- It gives the next audit lane a concrete artifact to verify instead of auditing an absent surface.
- It preserves existing blockers as observed status metadata instead of resolving, hiding, or reclassifying them.

Why the others wait:
- Archive Index Governance Audit must wait for a concrete P52 index artifact.
- Static Preview Archive Package must wait for both an index and an audit because package language carries distribution semantics risk.
- Motif Governance Drift Receipt should wait for a multi-generation/replay-window substrate.
- Forecast Readiness Boundary Packet should wait because it carries SHADOW/FORECAST and readiness-language risk.

Exact scope boundary:
- Build one deterministic archive index over the current sealed generation of P46/P47/P48/P49 JSON and Markdown artifacts.
- Include path, role, artifact family, artifact status/posture, SHA-256/canonical hash, source hash, receipt hash, registry classification summary, fixed role ordering, and observed blocker metadata.
- Write JSON and Markdown index artifacts only.
- Add schema, runner, generated artifact registry coverage, and tests required to make the index deterministic and governance-safe.

Forbidden scope:
- No executable package, archive package, compressed bundle, distribution claim, publication claim, use claim, readiness claim, forecast claim, recommendation claim, action route, command URL, external fetch, script, form, button, UI command authority, runtime mutation, canon mutation, queue mutation, routing mutation, adaptive behavior, inference authority, blocker suppression, audit weakening, deny-list weakening, fake hash, or missing-artifact-as-present behavior.

## 6. EXPECTED FILES / ARTIFACTS
Expected implementation files:
- `core/operator_narrative_export_preview_archive_index.py`
- `scripts/run_operator_narrative_export_preview_archive_index.py`
- `contracts/operator_attention/operator_narrative_export_preview_archive_index.v1.schema.json`
- `tests/test_operator_narrative_export_preview_archive_index.py`
- `core/generated_artifact_registry.py`

Expected output artifacts:
- `out/archive/operator_narrative_export_preview_archive_index_001.latest.json`
- `out/archive/operator_narrative_export_preview_archive_index_001.latest.md`

Path convention decision:
- Choose singular `out/archive/` for P52.
- Inspection found existing `out/audit/`, `out/exports/`, and `out/previews/`, but no existing `out/archive/` or `out/archives/` directory.
- The user-provided primary expected path is singular `out/archive/`; with no conflicting repo convention, singular should be used.
- P52 implementation must extend generated artifact registry scope matching so `out/archive/` artifacts are discoverable and classified.

Expected tests:
- deterministic index hash is stable across repeated generation.
- fixed archive role ordering over P46 JSON/MD, P47 JSON/MD, P48 JSON/MD, and P49 JSON/MD.
- missing/corrupt source artifacts produce `NOT_COMPUTABLE` and do not fake hashes.
- path/hash/status-only semantics hold for indexed entries.
- governance flags deny command, action, forecast, readiness, recommendation, execution, mutation, queue, routing, canon, runtime, adaptive, and UI command authority.
- passive references reject command/action URLs, external URLs, scripts, forms, buttons, and active fields.
- blocker summary is copied only as observed metadata and does not suppress non-P51 blockers.
- registry classification summary shows archive artifacts as non-authoritative, derived optional, and not CI drift enforced unless a later policy explicitly changes that.
- Markdown output has stable section ordering and newline normalization.
- schema constants match `OperatorNarrativeExportPreviewArchiveIndex.v1`, `PATCH-P52-OPERATOR-NARRATIVE-EXPORT-PREVIEW-ARCHIVE-INDEX-001`, and `operator_narrative_export_preview_archive_index_001`.

## 7. ARCHIVE INDEX SEMANTICS
The archive index should be:
- deterministic.
- passive.
- read-only.
- non-authoritative.
- advisory-only.
- path/hash/status only.
- source-linked.
- single-generation for P52.
- fixed-order by artifact role.
- receipt-aware but not receipt-overriding.
- blocker-aware as observed metadata only.

The archive index should include:
- `schema_version`
- `patch_id`
- `archive_index_id`
- `final_status`
- `archive_posture`
- `artifact_role_order`
- `artifact_index`
- `hash_inventory`
- `source_hashes`
- `receipt_hashes`
- `governance_receipt_summary`
- `registry_classification_summary`
- `blocker_summary`
- `governance_flags`
- `provenance`
- `archive_index_hash`

Recommended fixed artifact role order:
1. `p46_export_bundle_json`
2. `p46_export_bundle_markdown`
3. `p47_export_bundle_governance_audit_json`
4. `p47_export_bundle_governance_audit_markdown`
5. `p48_static_preview_json`
6. `p48_static_preview_markdown`
7. `p49_static_preview_governance_audit_json`
8. `p49_static_preview_governance_audit_markdown`

Required per-entry metadata:
- `artifact_id`
- `role`
- `path`
- `exists`
- `readable`
- `sha256`
- `status_observed`
- `posture_observed`
- `hash_field_observed`
- `hash_value_observed`
- `classification`
- `passive_reference_only`

Archive index must not:
- create executable packages.
- create archive packages.
- create distribution claims.
- claim readiness.
- recommend use.
- add action routes.
- add command URLs.
- add scripts, forms, buttons, or external fetch surfaces.
- mutate archive state outside its own artifacts.
- suppress blockers.
- treat missing artifacts as present.
- weaken governance receipts.
- reclassify upstream status.
- override P47/P49 audit posture.

Markdown sections should be fixed and passive:
1. `Archive Index Summary`
2. `Artifact Role Order`
3. `Artifact Index`
4. `Governance Receipt Summary`
5. `Registry Classification Summary`
6. `Observed Blocker Metadata`
7. `Governance Boundary`

## 8. GOVERNANCE BOUNDARIES
P52 must preserve:
- P42-P51 sealed states and P45_CI_REPAIRED state.
- P49 PASS/CLEAN status.
- P50 language-boundary normalization.
- P45 lineage comparison fail-closed behavior.
- non-P51 blockers as visible observed metadata.
- generated artifact policy rule to never fabricate artifacts.
- SHADOW/FORECAST separation.
- no authority escalation.

P52 governance flags should affirm:
- `archive_index_only: true`
- `passive_index_only: true`
- `read_only: true`
- `advisory_only: true`
- `non_authoritative: true`
- `source_linked: true`
- `deterministic_index: true`

P52 governance flags should deny:
- `command_authority`
- `ui_command_authority`
- `action_authority`
- `recommendation_authority`
- `inference_authority`
- `prediction_allowed`
- `forecast_authority`
- `trend_prediction_allowed`
- `readiness_claims_allowed`
- `mutation_allowed`
- `authority_granted`
- `execution_authority`
- `routing_change_allowed`
- `queue_mutation_allowed`
- `canon_mutation_allowed`
- `runtime_mutation_allowed`
- `adaptive_behavior_allowed`
- `psychological_claims_allowed`
- `speculative_causation_allowed`
- `auto_execute`
- `auto_approve`
- `command_channel`
- `bidirectional_control`
- `script_allowed`
- `html_script_allowed`
- `external_fetch_allowed`
- `form_allowed`
- `button_allowed`

## 9. RISKS / DRIFT FLAGS
- `out/archive/` is not currently part of generated artifact registry scope matching; P52 must add this scope intentionally and test it.
- P46 and P48 currently carry non-P51 blockers. The archive index must preserve them as observed metadata without converting them into P52 failures unless a required P52 source is missing/corrupt.
- P47 and P49 governance audits are PASS/CLEAN; P52 must not override or reinterpret their audit posture.
- Archive/package language is charged. P52 must use index language only and defer package semantics.
- Markdown language scanning should avoid command/action/forecast/readiness terms in generated prose while allowing governance-boundary keys to exist as data.
- If future multi-generation indexing is desired, it should be a later patch with explicit chronology policy. P52 should stay single-generation.

## 10. NEXT CODEX IMPLEMENTATION PROMPT
Implement P52 only: **Export / Preview Archive Index**.

Constraints:
- Do not implement P53.
- Do not implement archive index governance audit yet.
- Do not implement static preview archive package.
- Do not create executable package, distribution, readiness, forecast, action, command, routing, queue, runtime, canon, adaptive, or UI command surfaces.
- Do not weaken P47/P49/P50/P51 governance checks.
- Do not suppress existing blockers.
- Do not fabricate hashes or treat missing artifacts as present.

Expected implementation:
1. Add `core/operator_narrative_export_preview_archive_index.py`.
2. Add `scripts/run_operator_narrative_export_preview_archive_index.py`.
3. Add `contracts/operator_attention/operator_narrative_export_preview_archive_index.v1.schema.json`.
4. Add `tests/test_operator_narrative_export_preview_archive_index.py`.
5. Update `core/generated_artifact_registry.py` so `out/archive/` artifacts are scanned and the two P52 artifacts are classified as `DERIVED_OPTIONAL`, non-authoritative, and not CI drift enforced.
6. Generate:
   - `out/archive/operator_narrative_export_preview_archive_index_001.latest.json`
   - `out/archive/operator_narrative_export_preview_archive_index_001.latest.md`
7. Run targeted tests, full suite, Ruff, Pyright, artifact regeneration/check-drift, and inspect generated artifacts for drift.

Acceptance checks:
- P52 index is deterministic and hash-stable.
- P52 index is passive, read-only, non-authoritative, advisory-only, path/hash/status only.
- P52 index includes P46/P47/P48/P49 paths and hashes in fixed role order.
- P52 index includes source hashes and receipt hashes.
- P52 index includes governance receipt status/posture without changing upstream receipts.
- P52 index includes registry classification summary.
- P52 index includes observed blocker metadata only.
- P52 index contains no executable package, distribution claim, readiness claim, forecast claim, command URL, action URL, script, form, button, or external fetch surface.
- P42-P51 sealed states remain preserved.
