# Abraxas Documentation Index

Abraxas Codex v2.7 - respecting custom instructions + surfaces + governance loop + Notion mirror

Status: `D1_1_MASTER_INDEX_REFRESH_READY_ADVISORY_ONLY`
Brier Score: 0.10

This master index routes contributors by surface role. It is a navigation/projection surface only and does not create governance, canon, MCP, runtime, sandbox, or writeback authority.

## Primary Hubs

| Need | Route | Why this matters | Next action |
|------|-------|------------------|-------------|
| New contributor path | [`START_HERE.md`](START_HERE.md) | Gives the 5-minute route through the repo. | Start there before editing. |
| Repo identity/status | [`../README.md`](../README.md), [`../STATUS.md`](../STATUS.md) | Establishes current system posture. | Check current state. |
| Architecture | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | Shows subsystem shape and boundaries. | Locate the subsystem. |
| Governance/instructions | [`../GOVERNANCE_V3.md`](../GOVERNANCE_V3.md), [`../AGENTS.md`](../AGENTS.md) | Defines authority locks and operator control. | Read before changing behavior. |
| Continuation plans | [`../PLANS.md`](../PLANS.md) | Lists active lanes and receipts. | Confirm current frontier. |
| Task mirror | [Notion Sprint 001 Hub](https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254) | Living board/source mirror. | Use for alignment; no autonomous writeback. |

## Surface Role Routes

| Surface role | Current route | Why this matters | Next action |
|--------------|---------------|------------------|-------------|
| Identity/status | [`../README.md`](../README.md), [`../STATUS.md`](../STATUS.md) | Defines what the repo is and how healthy it is. | Use for orientation. |
| Governance | [`../GOVERNANCE_V3.md`](../GOVERNANCE_V3.md), [`../AGENTS.md`](../AGENTS.md) | Authority, locks, and operator rules. | Treat as protected. |
| Architecture | [`../ARCHITECTURE.md`](../ARCHITECTURE.md), [`architecture/`](architecture/) | System shape and technical maps. | Follow existing subsystem boundaries. |
| Code/module maps | [`../core/`](../core/), [`../Scripts/`](../Scripts/), [`../scripts/`](../scripts/) | Engineering surfaces and runners. | Prefer no-arg receipt runners for generated artifacts. |
| Generated artifacts | [`artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md), [`../core/generated_artifact_registry.py`](../core/generated_artifact_registry.py) | Artifact lifecycle and regeneration policy. | Verify canonical generator before editing outputs. |
| Audit history | [`audits/AUDIT_INDEX.md`](audits/AUDIT_INDEX.md) | Current and historical evidence. | Classify rather than delete. |
| Releases | [`releases/RELEASE_INDEX.md`](releases/RELEASE_INDEX.md) | Continuation/release baseline. | Start from the active baseline. |
| Runtime docs | [`runtime/`](runtime/) | Planning and readiness surfaces. | Keep execution authority separate. |
| Oracle docs | [`oracle/`](oracle/) | Oracle planning/intake surfaces. | Keep live gates explicit. |
| Visualization docs | [`visualization/`](visualization/) | VIZ and projection surfaces. | Keep UI projection read-only unless gated. |

## Active Receipt Routes

| Receipt | Runner | Status |
|---------|--------|--------|
| [`../out/audit/docs_navigation_refresh_001.latest.json`](../out/audit/docs_navigation_refresh_001.latest.json) | [`../Scripts/run_docs_navigation_refresh_receipt.py`](../Scripts/run_docs_navigation_refresh_receipt.py) | `DOCS_NAVIGATION_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json`](../out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json) | [`../Scripts/run_rune_integrity_scanner_guardrails_receipt.py`](../Scripts/run_rune_integrity_scanner_guardrails_receipt.py) | Advisory scanner/guardrails |
| [`../out/audit/hyperstition_evaluator_deepening_receipt_001.latest.json`](../out/audit/hyperstition_evaluator_deepening_receipt_001.latest.json) | [`../Scripts/run_hyperstition_evaluator_deepening_receipt.py`](../Scripts/run_hyperstition_evaluator_deepening_receipt.py) | Advisory evaluator projection |
| [`../out/audit/viz01_live_feed_enhancement_receipt_001.latest.json`](../out/audit/viz01_live_feed_enhancement_receipt_001.latest.json) | Registered no-arg runner | VIZ-01 read-only projection feed |

## Deep History Routes

Why this matters: historical chains are evidence, not clutter. Keep them discoverable without making new contributors parse every old receipt first.

Next action:
- Audit history: [`audits/AUDIT_INDEX.md`](audits/AUDIT_INDEX.md)
- Release/continuation history: [`releases/RELEASE_INDEX.md`](releases/RELEASE_INDEX.md)
- Generated artifact lifecycle: [`artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md)
- Full artifact registry: [`../core/generated_artifact_registry.py`](../core/generated_artifact_registry.py)

## D1.1 Refresh Status

Why this matters: Slice57 implements the Priority 3 documentation-debt route from the Notion board without opening any execution gate.

Next action:
- Verify `python Scripts/run_docs_navigation_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/docs_navigation_refresh_001.latest.json`
- Keep `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` unissued unless the operator explicitly provides it in a future gate.

Provenance: Notion Sprint 001 Hub + Loop 805 Slice57 + Hash: receipt canonical_hash
