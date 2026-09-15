---
name: slang-emergence
description: DESIGN_ONLY slang and memetic analysis specification with a NOT_COMPUTABLE receipt helper; no observed evidence, computed Brier, or implemented forecasting.
version: 1.0.0
author: Hermes (Abraxas systems engineer)
license: Proprietary
metadata:
  hermes:
    tags: [holler-sports, slang-emergence, memetic-engineering, hyperstition, symbolic-forecasting, provenance, brier]
    related_skills: [holler-market-signal, holler-forecast, holler-calibrate, holler-ingest, abraxas-orchestrator, x-twitter-scraper, firecrawl]
---

Supported mode: **full checkout**. Read repository-root `skills/OPERATING.md`
for Python 3.12 bootstrap, canonical source/version, explicit output paths,
unshipped sibling fallback and fail-closed verification before using this skill.

# Slang Emergence — design stub

Status: NOT_COMPUTABLE. No X retrieval adapter, validated organic/coordinated
classifier, virality model, or live cron pipeline is shipped. The previous canned
observations and fixed Brier score were removed, not treated as measurements.
Do not infer live execution from archived receipts.

The pure function `detect_memetic_patterns(query)` in
`scripts/slang_emergence_engine.py` returns empty evidence registers, an explicit
reason, and null Brier. It performs no retrieval or automatic file write.
A future detector needs retrieved source IDs/URLs/timestamps and an independently
validated method. Score forecasts only after valid settlement, never for prose
quality or presumed virality. Synthetic examples must be opt-in and labeled
SYNTHETIC; none are substituted on failure.

## Offline invocation and verification
```bash
python skills/holler-sports/slang-emergence/scripts/slang_emergence_engine.py --query "unretrieved query" --output "$ABRAXAS_OUTPUT/slang.json"
python -m pytest -c /dev/null -p no:cacheprovider skills/tests/test_slang_safety.py -q
```
stdout is one complete JSON object. Explicit output paths are optional; no
private author-specific location is written. A NOT_COMPUTABLE receipt verifies
honest failure behavior, not functioning emergence detection.
