# SHADOW Substrate — Canon Lock 001

**Status:** ACTIVE_SHADOW · advisory_only · authority bits false  
**Date:** 2026-09-24  
**Notion:** SHADOW Substrate — Canon Lock v0.1 (FAMILIAR spine child)  
**Does not:** flip FORECAST, p89 bind, EXTERNAL_PRODUCTION, Seed Corpus insert, SUAS

## Kernel already landed

EvidencePack.v0 → FamiliarIngestionReceipt.v0 → spine touch → operator review.
CLI: `python -m abraxas forage validate|ingest|spine-touch`.

## What this lock adds

1. Name SHADOW as the realized advisory OS (`ACTIVE_SHADOW`), not a disclaimer.
2. Separate Herald DEST writes from Weaver ingest.
3. Keep `INGESTED_SHADOW_EXTRACTED` off the receipt enum; park it on `ABX.SchedulerSync.v0.ingest_class`.
4. Treat `commercial_claims_blocked` as density-only.
5. Declare `spirits_live = forager, weaver, keeper`.
6. Add SeedContractWindow.v0 runner. Velocity stays NOT_COMPUTABLE.

## Companion clock rule

Daily Forage and Hyperstition Scanner must:

- attach an EvidencePack path and run `scripts/ingest/run_familiar_ingestion_from_pack.py`, or
- stamp `ingest.status = NOT_COMPUTABLE` with a reason.

A 03 URL is never a receipt_id.

## Contracts

- `contracts/companion/scheduler_sync.v0.schema.json`
- `contracts/seed/seed_contract_window.v0.schema.json`
- `scripts/seed/run_seed_contract_window.py`
