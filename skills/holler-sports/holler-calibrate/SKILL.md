---
name: holler-calibrate
description: DESIGN_ONLY calibration specification; no executable calibration helper. Return NOT_COMPUTABLE without measured outcomes; no computed Brier or regime claims.
version: 1.0.0
author: Hermes (Abraxas systems engineer)
license: Proprietary
metadata:
  hermes:
    tags: [holler-sports, calibration, brier, model-evaluation, adversarial, regime-detection, provenance]
    related_skills: [holler-ingest, holler-forecast, holler-market-signal, abraxas-orchestrator, hermes-agent-skill-authoring]
---

Supported mode: **full checkout**. Read repository-root `skills/OPERATING.md`
for Python 3.12 bootstrap, canonical source/version, explicit output paths,
unshipped sibling fallback and fail-closed verification before using this skill.

# Holler Calibration — DESIGN_ONLY

No supported calibration helper or validated regime/robustness detector is
shipped by this skill. Do not execute the former illustrative NumPy skeleton.
It silently truncated pairs and multiplied a score without calibrating forecasts.
Missing algorithm references and claims of production readiness are retired.
Return NOT_COMPUTABLE with the missing inputs/method, not a numeric risk/Brier
value. No recurring or live pipeline is authorized by this document.

## Required implementation contract (not an executable recipe)
- Require nonempty equal-length arrays of finite probabilities in [0,1] and
  binary settled outcomes. Reject booleans as probabilities, NaN, infinity,
  unknown/unsettled outcomes, and mismatched IDs before computation.
- Bind each prediction to pre-outcome timestamp, settlement criteria and source.
- Fit calibration on explicit training data and evaluate on disjoint held-out
  IDs/time windows; prevent leakage and report both sets and sample counts.
- Brier is mean squared probability error on actual settled pairs. Never reduce
  a reported score by a fixed multiplier and call that calibration.
- Regime detection and robustness stay NOT_COMPUTABLE until an actual named
  method, input contract, statistical assumptions, and tests are provided.
- Candidate methods cannot grant betting, deployment, promotion, or cron authority.

## Verification
```bash
python -m pytest -c /dev/null -p no:cacheprovider skills/tests/test_skill_docs.py -q
```
This checks the design-only boundary, not calibration accuracy. No output artifact
or runtime test can be claimed for an algorithm that is not shipped.
