# signal_forage 2026-09-23 — FAMILIAR Scanner (SHADOW)

Lane: SHADOW / advisory. Not FamiliarIngestionReceipt.v0. Not Seed Corpus APPLY.

## Files
- `evidence_pack_ep_20260923_familiar_scanner.json` — EvidencePack.v0
- `seed_windows_2026-09-23.jsonl` — SeedContractWindow.v0 (3 keys)
- `watcher_noise_log_2026-09-23.jsonl` — defer rows; FP still NOT_COMPUTABLE
- `familiar_ingestion_receipt_SANDBOX_REPLICA_20260923.json` — semantic replica only; status SANDBOX_REPLICA_NOT_REPO_CLI

## Notion
03 receipt: https://app.notion.com/p/3e43e8ba2f5c81d8a0d6e711e091df5f
Watcher ledger: https://app.notion.com/p/3dc3e8ba2f5c814780e9eaf58c5242f6

## Official ingest (operator machine with repo checkout)
```
python scripts/ingest/run_familiar_ingestion_from_pack.py \
  --pack out/signal_forage/2026-09-23/evidence_pack_ep_20260923_familiar_scanner.json
```
Until that returns `INGESTED_SHADOW`, ingest is not claimed.

Window counts (budget_truncated, 3 pages x 10): aura_farming 24, HYPER.STITIO 10, AI_SLOP 26. Velocity NOT_COMPUTABLE.
