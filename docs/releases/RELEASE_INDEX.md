# Release Index

Index of [`docs/releases/`](.) continuation and release documents.

## Authoritative current baseline

| Document | Status | Purpose |
|----------|--------|---------|
| [`POST_2_5_0_CONTINUATION_AUDIT.md`](POST_2_5_0_CONTINUATION_AUDIT.md) | **ACTIVE** | Primary continuation baseline after Product 2.5.0 |
| [`POST_MERGE_748_SPEC_STACK_NOTION_SYNC_CLOSURE_CONTINUATION_PLAN.md`](POST_MERGE_748_SPEC_STACK_NOTION_SYNC_CLOSURE_CONTINUATION_PLAN.md) | **ACTIVE** | Post-#748 closure; Notion sync 1a/1b complete |
| [`POST_MERGE_747_SPEC_STACK_ROUTING_CLOSURE_CONTINUATION_PLAN.md`](POST_MERGE_747_SPEC_STACK_ROUTING_CLOSURE_CONTINUATION_PLAN.md) | Reference closure | Post-#747 routing confirmation |
| [`POST_MERGE_746_SPEC_STACK_SCHEMA_AUDIT_NOTION_HANDOFF_CONTINUATION_PLAN.md`](POST_MERGE_746_SPEC_STACK_SCHEMA_AUDIT_NOTION_HANDOFF_CONTINUATION_PLAN.md) | Reference routing body | Dual Notion sync workstreams + harness auth deferred |
| [`POST_MERGE_744_SPEC_STACK_SCHEMA_AUDIT_CONTINUATION_PLAN.md`](POST_MERGE_744_SPEC_STACK_SCHEMA_AUDIT_CONTINUATION_PLAN.md) | Reference | Post-#744 routing |
| [`POST_MERGE_742_REPOSITORY_ORGANIZATION_CONTINUATION_PLAN.md`](POST_MERGE_742_REPOSITORY_ORGANIZATION_CONTINUATION_PLAN.md) | Reference | Post-#742 routing |
| [`POST_MERGE_739_INTAKE_CLEARED_CONTINUATION_PLAN.md`](POST_MERGE_739_INTAKE_CLEARED_CONTINUATION_PLAN.md) | Reference | Post-#739/#741 codegen chain |
| [`PRODUCT_2_5_0_RELEASE_READY.md`](PRODUCT_2_5_0_RELEASE_READY.md) | Reference | 2.5.0 release closure |
| [`VERSION_STRATEGY.md`](VERSION_STRATEGY.md) | Reference | Versioning policy |

## Continuation plan chain (newest wins)

```text
PRODUCT_2_5_0_RELEASE_READY
  └─ POST_2_5_0_CONTINUATION_AUDIT (authoritative)
       ├─ POST_MERGE_724_EXTENSIVE_CONTINUATION_PLAN
       ├─ POST_MERGE_735_CONTINUATION_PLAN (#735 Notion 6/6)
       ├─ POST_MERGE_738_CODEGEN_ATTESTATION_CONTINUATION_PLAN (#738)
       ├─ POST_MERGE_739_INTAKE_CLEARED_CONTINUATION_PLAN (#739/#741)
       ├─ POST_MERGE_742_REPOSITORY_ORGANIZATION_CONTINUATION_PLAN (#742)
       ├─ POST_MERGE_744_SPEC_STACK_SCHEMA_AUDIT_CONTINUATION_PLAN (#744/#745)
       ├─ POST_MERGE_746_SPEC_STACK_SCHEMA_AUDIT_NOTION_HANDOFF_CONTINUATION_PLAN (#746) ← reference routing body
       ├─ POST_MERGE_747_SPEC_STACK_ROUTING_CLOSURE_CONTINUATION_PLAN (#747) ← reference closure
       └─ POST_MERGE_748_SPEC_STACK_NOTION_SYNC_CLOSURE_CONTINUATION_PLAN (#748) ← current closure
```

## All release documents

| Document | PR era | Status | Superseded by |
|----------|--------|--------|---------------|
| `PRODUCT_2_5_0_RELEASE_READY.md` | #714 | Reference | POST_2_5_0 audit |
| `POST_2_5_0_CONTINUATION_AUDIT.md` | #714–#748 | **Active baseline** | — |
| `POST_P132_RESEARCH_CANARY_CONTINUATION_PLAN.md` | #727–#733 | Reference (6/6 complete) | POST_2_5_0 audit |
| `POST_MERGE_720_722_CONTINUATION_PLAN.md` | #720–#722 | Historical | POST_MERGE_723+ |
| `POST_MERGE_723_CONTINUATION_PLAN.md` | #723 | Historical | POST_MERGE_724+ |
| `POST_MERGE_724_EXTENSIVE_CONTINUATION_PLAN.md` | #724 | Historical | POST_MERGE_735+ |
| `POST_MERGE_735_CONTINUATION_PLAN.md` | #735 | Reference | POST_MERGE_738+ |
| `POST_MERGE_738_CODEGEN_ATTESTATION_CONTINUATION_PLAN.md` | #738 | Reference (Phase 1 → #739) | POST_MERGE_739 |
| `POST_MERGE_739_INTAKE_CLEARED_CONTINUATION_PLAN.md` | #739/#741 | Reference | POST_MERGE_742 |
| `POST_MERGE_742_REPOSITORY_ORGANIZATION_CONTINUATION_PLAN.md` | #742 | Reference | POST_MERGE_744 |
| `POST_MERGE_744_SPEC_STACK_SCHEMA_AUDIT_CONTINUATION_PLAN.md` | #744/#745 | Reference | POST_MERGE_746 |
| `POST_MERGE_746_SPEC_STACK_SCHEMA_AUDIT_NOTION_HANDOFF_CONTINUATION_PLAN.md` | #746 | Reference routing body | POST_MERGE_747 |
| `POST_MERGE_747_SPEC_STACK_ROUTING_CLOSURE_CONTINUATION_PLAN.md` | #747 | Reference closure | POST_MERGE_748 |
| `POST_MERGE_748_SPEC_STACK_NOTION_SYNC_CLOSURE_CONTINUATION_PLAN.md` | #748 | **Active closure** | — |
| `POST_CLEARANCE_OPTIONAL_FORKS.md` | — | Reference | — |
| `HELD_WORK_OPERATOR_FOLLOWUP.md` | — | Reference (operator manual) | — |
| `FULL_FEATURES_RELEASE_ROADMAP_COMPLETION.md` | #710 | Reference | Governance V3 |
| `VERSION_STRATEGY.md` | — | Reference | — |

## Obsolete / do not treat as current edge

- `POST_MERGE_720_722_*` — superseded by extensive continuation and 2.5.0 audit
- Any doc referencing "intake gate BLOCKED" or "#741 pending" without sweep update — use POST_2_5_0 after sweep

## Next distinct lane (not a release doc)

Harness implementation authorization requires separate operator payload (`authorize_harness_implementation: true`). Intake clearance alone is insufficient.
