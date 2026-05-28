---
name: P104 Seal Finalization Decision
description: Implementation facts for P104 — operator decision record after P103 review; mirrors P96/P100 pattern; requires human artifact to advance beyond PENDING.
---

# P104 Seal Finalization Decision

**Why:** P104 records operator decision posture after P103 REVIEW_READY. Mirrors P96's role after P95. No authority granted — decision record only.

**Source gate:** P103 `finalization_review_status == REVIEW_READY` AND `review_passed: True`. Either absent → BLOCKED.

**Human artifact:** `input/operator_authorization_record_approval_record_seal_finalization_decision.json` — does NOT exist in repo. Must be provided by operator before lane advances beyond PENDING.

**`upstream_review_hash` in human artifact must equal P103 FILE hash (sha256 of bytes)**, not the canonical_hash field. Current P103 file hash: `c84c2acec4c0a2bb152a9bdba350b648d545c4156be97632c69838abf8e8c7b3`. This will change if P103 artifact is regenerated.

**Required acknowledgements (5):** `advisory_only_acknowledged`, `no_execution_authority_granted_acknowledged`, `no_seal_executed_acknowledged`, `finalization_not_executed_acknowledged`, `finalization_decision_record_only_acknowledged`.

**Decision posture audit: 11 checks.** Unknown decision values fail on `decision_in_allowed_list` (not `unrecognised_decision_value`) because the allowed-list audit check fires first.

**Status routing:**
- Source missing → NOT_COMPUTABLE
- Source not REVIEW_READY → BLOCKED_BY_..._FINALIZATION_REVIEW
- Source ready, no human artifact → PENDING (self-route to P104)
- Audit failure → FAILED
- `approve_finalization_review_record` + audit pass → APPROVED_RECORD → P105
- Other ALLOWED_DECISIONS + audit pass → REJECTED_RECORD → P103 or P102

**Tests:** 22 passed after 2 fixes: (1) `_seed_p103` default `status` arg was a broken string expression — hardcoded the constant directly; (2) `test_failed_unknown_decision` expected `unrecognised_decision_value` in blockers but unknown decisions fail the audit at `decision_in_allowed_list` first.

**All authority locks hardcoded false; autonomous_approval hardcoded false.**
