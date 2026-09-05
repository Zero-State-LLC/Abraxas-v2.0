---
name: holler-ingest
description: Bounded HTTP JSON ingestion client validating HollerNormalizedEnvelope.v1 with provenance and caching; no domain adapters or HollerSportsBatch validation.
version: 1.0.0
author: Hermes (Abraxas systems engineer)
license: Proprietary
platforms: [macos, linux]
metadata:
  hermes:
    tags: [holler-sports, ingest, data-pipeline, provenance, deterministic, schema-validation, caching]
    related_skills: [holler-calibrate, holler-market-signal, holler-forecast, holler-app-compliance, holler-visualize, abraxas-orchestrator]
---

Supported mode: **full checkout**. Read repository-root `skills/OPERATING.md`
for Python 3.12 bootstrap, canonical source/version, explicit output paths,
unshipped sibling fallback and fail-closed verification before using this skill.

# Holler Ingest — normalized envelope client

Status: bounded client, not production-ready domain ingestion. The library at
`scripts/holler_ingest_client.py` exposes `HollerIngestClient.fetch(provider, url,
params=None)` and `batch_ingest(jobs)`. Import by file path with importlib or add
this skill's scripts directory to sys.path in the calling application.

`HollerNormalizedEnvelope.v1` validates only an object with a `data` array of
nonempty objects and no top-level error/errors/fallback. It does not establish
source truth, sports-domain semantics, provider completeness, or freshness.
Provider adapters and HollerSportsBatch conversion are NOT_COMPUTABLE until
implemented and independently validated. Do not claim that envelope validation
is full domain schema validation. Empty data is a valid empty response, not
proof that the provider was completely enumerated.

Only approved URLs may be fetched; obtain credentials from a secure store, never
put them in artifacts. HTTP/auth/timeout/JSON errors raise `IngestError` with
FETCH_FAILED. Invalid envelopes raise SCHEMA_INVALID. No mock fallback exists.
OBSERVED means bytes returned by the provider, not independently established
facts. Hashes are full SHA-256 of sorted compact UTF-8 JSON. Cache state comes
from response metadata, not directory names; unknown timing stays null. Brier
is null because ingestion is not a settled forecast. Batch results preserve each
job by positional job_id even when providers repeat; any failure aborts the batch.

## Offline verification
```bash
python -m pytest -c /dev/null -p no:cacheprovider skills/tests/test_holler_ingest_safety.py -q
```
The test injects responses and never makes network requests. It verifies schema
rejection, HTTP/JSON errors, exact payload hashes, cache metadata, and duplicate
provider jobs. Do not run this helper as an implicit live endpoint smoke test.
No fixed integration hashes or illustrative non-JSON skeletons are supplied.
