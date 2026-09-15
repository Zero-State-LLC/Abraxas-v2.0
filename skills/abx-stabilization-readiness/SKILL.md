---
name: abx-stabilization-readiness
description: "Builds deterministic advisory evidence for stabilization readiness without freezing contracts, activating production, promoting runtime state, mutating canon, or writing externally."
version: 0.1.0
author: Abraxas Governed Operator
license: Proprietary
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, stabilization, reproducibility, conformance, advisory]
    related_skills: [abx-hermes-skill-evolution]
---

Supported mode: **full checkout**. Read repository-root `skills/OPERATING.md`
for Python 3.12 bootstrap, canonical source/version, explicit output paths,
unshipped sibling fallback and fail-closed verification before using this skill.

# ABX Stabilization Readiness

## Boundary

This skill is `ADVISORY_ONLY` and `READ_ONLY_BY_DEFAULT`. It cannot freeze a
contract, activate production, mutate canon, promote runtime state, perform
external writeback, or start a stabilization campaign autonomously.

## Flow

1. Build a deterministic baseline state for an explicitly supplied commit.
2. Classify observed contract surfaces without inferring frozen status.
3. Record unavailable reproducibility evidence as `NOT_COMPUTABLE`.
4. Run deterministic conformance fixtures for observed Python behavior only.
5. Evaluate the independent fail-closed entry gate.
6. Publish advisory artifacts through `core.canonical.json.write_canonical_json`.

## Operator Boundary

Even a ready gate result is a recommendation. Operator action remains required,
and no approval or authority is issued by this package.


## Runnable foundation lane
Implementation: `skills/abx-stabilization-readiness/director.py` exposes
`build_stabilization_state` and `emit_foundation_artifacts(output_root,
baseline_commit=...)`. It calls `run_conformance_cases` and
`evaluate_stabilization_entry`; missing reproducibility evidence fails closed.
```bash
BASELINE_COMMIT=$(git rev-parse HEAD)
python scripts/readiness/run_stabilization_readiness_advisory.py --baseline-commit "$BASELINE_COMMIT" --output-root "$ABRAXAS_OUTPUT/stabilization"
python skills/verify_artifact.py --schema contracts/stabilization_readiness/stabilization_entry_gate.v1.schema.json "$ABRAXAS_OUTPUT/stabilization/stabilization_entry_gate.latest.json"
python -m pytest -c /dev/null -p no:cacheprovider tests/test_abx_stabilization_readiness.py -q
```
The foundation runner emits exactly five named files listed in director.ARTIFACT_NAMES:
contract inventory, reproducibility baseline, conformance manifest, entry gate,
and foundation receipt. Verify all five exist in the fresh output directory,
receipt artifact hashes match actual payloads, conformance cases pass, and
baseline_commit matches the explicit checkout. The default incomplete evidence
must not authorize entry. A BLOCKED/NOT_COMPUTABLE advisory gate can be the correct
verified outcome; never call that production readiness. No operator approval is
supplied or inferred by this command.
