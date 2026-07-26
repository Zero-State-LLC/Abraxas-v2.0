# CLEAR Dual-Control Operator Checklist 001

**Status:** Operator procedure (no execution authority granted by this document)  
**Date:** 2026-07-26  
**Purpose:** Complete dual-control review of the CLEAR disposition draft before any mass deletion.

## Binding facts (repo evidence)

| Fact | Value | Source |
| --- | --- | --- |
| Engineering disposition | `DRAFT_ISSUED` | `out/production_convergence/clear_disposition_draft.v1.json` |
| Operator disposition | `PENDING_OPERATOR` | same |
| Dual-control | `PENDING` · A/B attestations null | same |
| Mass deletion authorized | **false** | same + analysis packets |
| Deletions proposed / executed | **0** | draft summary |
| Entry count | 24 | draft summary |
| Engineering counts | KEEP 7 · MERGE_CANDIDATE 12 · DEFER_CLEAR 4 · DEPRECATE_DOCUMENT_ONLY 1 | draft summary |

Related packets:

- `out/production_convergence/clear_reference_analysis.v1.json`
- `out/production_convergence/clear_operator_review.v1.json`
- `out/production_convergence/phase14_clear_disposition_and_canary_writer.v1.json`
- Spec map: `docs/architecture/PRODUCTION_CONVERGENCE_AUDIT_001.md` (CLEAR section)

## Hard rules

1. **No mass deletion** until dual-control is complete and an explicit deletion mandate exists.
2. Engineering draft classes are **recommendations only** — operator may KEEP any path.
3. Completing this checklist does **not** authorize EXTERNAL_PRODUCTION, sandbox probe, or deploy unhold.
4. Do not fabricate attestations. Record real operator A and operator B identities only when both have reviewed.

## Operator steps

### 1. Context load

- [ ] Read `PLANS.md` active objective and blocked list
- [ ] Read `STATUS.md` CLEAR rows
- [ ] Open `clear_disposition_draft.v1.json` and verify `canonical_hash` matches your local file
- [ ] Optional: regenerate operator-loop glance (projection only):

```bash
python3 scripts/viz/gather_operator_loop_github_ci_evidence.py
python3 scripts/viz/build_aal_viz_operator_loop_projection.py
```

### 2. Review classes (per entry or by disposition bucket)

For each engineering disposition, decide:

| Engineering class | Operator options |
| --- | --- |
| `KEEP` | Confirm KEEP |
| `MERGE_CANDIDATE` | KEEP / MERGE_LATER / need more evidence |
| `DEFER_CLEAR` | KEEP / DEFER / schedule follow-up (still no delete) |
| `DEPRECATE_DOCUMENT_ONLY` | KEEP / document deprecation only (no delete) |

- [ ] Review KEEP bucket (7)
- [ ] Review MERGE_CANDIDATE bucket (12)
- [ ] Review DEFER_CLEAR bucket (4)
- [ ] Review DEPRECATE_DOCUMENT_ONLY bucket (1)

**Default safe disposition:** KEEP or DEFER — never DELETE without a separate dual-control deletion mandate.

### 3. Dual-control attestations

Both controls must attest **after** independent review of the draft.

| Control | Role | Attestation recorded |
| --- | --- | --- |
| Control A | First operator | [ ] identity / date / decision summary |
| Control B | Second operator (distinct person) | [ ] identity / date / decision summary |

Required attestation fields (minimum):

- `attestor_id` or name
- `attested_at` (UTC ISO-8601)
- `disposition_summary` (e.g. “no deletions; keep all 24 as non-delete”)
- `mass_deletion_authorized: false` unless a **separate** deletion mandate is issued
- `draft_canonical_hash` (must match draft file)

### 4. Recording outcomes (engineering follow-up)

After A and B attest:

1. Engineering records attestations into a new advisory receipt (do not silently edit sealed hashes without a governed writer).
2. Update `operator_disposition_status` only via a proper PR that preserves `mass_deletion_authorized: false` unless deletion is explicitly mandated.
3. Update Notion hub (CONTINUATION P0.1) with the dual-control outcome.
4. If any DELETE class is ever authorized: require a **new** dual-control deletion mandate listing exact paths — this checklist alone is insufficient.

### 5. Explicit non-outcomes

This checklist completion **does not**:

- flip `mass_deletion_authorized` to true by itself
- authorize EXTERNAL_PRODUCTION
- authorize sandbox probe (`ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` remains unissued)
- unhold deploy (`NO_GO` remains until H.1/H.2 process)

## Suggested operator decision language (copy-paste)

```text
CLEAR dual-control review of clear_disposition_draft.v1 (hash <paste>).
Control A: <name> <UTC>
Control B: <name> <UTC>
Outcome: no mass deletion; mass_deletion_authorized remains false.
Per-bucket notes: <optional>
Next: eng records dual-control receipt; Notion hub note; continue KEEP/DEFER posture.
```

## References

- `docs/architecture/PRODUCTION_CONVERGENCE_AUDIT_001.md`
- `PLANS.md` — post–Phase 14 active workstreams
- `STATUS.md` — CLEAR disposition rows
- Multi-agent loop (projection only): `docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md`
