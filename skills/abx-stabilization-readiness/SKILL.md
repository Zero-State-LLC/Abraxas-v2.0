---
name: abx-stabilization-readiness
description: "Controlled execution layer for Abraxas stabilization: director, contract inventory, reproducibility audit, conformance harness, and independent entry gate. Advisory and read-only until operator authorization. Routed under ABX Campaign Director as CAMPAIGN_CLASS.STABILIZATION_READINESS."
version: 0.1.0
author: Abraxas Governed Operator
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, stabilization, contract-inventory, reproducibility, conformance, campaign-director]
    related_skills: [abx-campaign-director, abraxas-repo-intel, abx-hermes-skill-evolution]
---

# ABX Stabilization Readiness

## Work order

`WO-ABX-STABILIZATION-SKILL-FOUNDATION-001` — advisory skill package, schemas, fixtures, tests, campaign-director routing, **no production activation**.

## Boundary

`ADVISORY_ONLY | READ_ONLY | NO_PRODUCTION_ACTIVATION`

The director selects work; the **stabilization gate** certifies entry. Those roles must not collapse.

## Hierarchy

```text
ABX Campaign Director
    └── ABX Stabilization Director (this package)
            ├── Repo Intel (abraxas-repo-intel)
            ├── Contract Inventory
            ├── Reproducibility Auditor
            ├── Conformance Harness
            ├── Regression Observer (abx_skill_extended_canary_observer)
            └── Stabilization Gate
                    └── Operator Decision Stack
```

## Modules

| Module | Role |
|--------|------|
| `director.py` | `RUNE.STABILIZATION_DIRECT` — phase + bounded packets |
| `contract_inventory.py` | Classify surfaces; no freeze without operator |
| `reproducibility_auditor.py` | Lock/toolchain advisory audit |
| `conformance_harness.py` | Load/validate behavioral corpus fixtures |
| `stabilization_gate.py` | Terminal entry decision from evidence only |
| `contracts.py` / `models.py` | Shared enums and deterministic models |

## Phases

```text
PHASE.0_BASELINE_DISCOVERY
PHASE.1_REPRODUCIBILITY
PHASE.2_CONTRACT_FREEZE
PHASE.3_CONFORMANCE
PHASE.4_STRESS_AND_REPLAY
PHASE.5_ENTRY_DECISION
```

## Campaign state (v1)

```json
{
  "campaign_id": "ABRAXAS_STABILIZATION_READINESS_CAMPAIGN_001",
  "campaign_class": "STABILIZATION_READINESS",
  "phase": "PHASE.0_BASELINE_DISCOVERY",
  "feature_expansion_allowed": false
}
```

## Terminal decisions

- `STABILIZATION_ENTRY_READY`
- `STABILIZATION_ENTRY_READY_WITH_BOUNDED_EXCEPTIONS`
- `STABILIZATION_ENTRY_HELD`

## Run (advisory)

```bash
cd "$(git rev-parse --show-toplevel)"
uv run python skills/abx-stabilization-readiness/run_advisory.py
```

Artifacts: `out/stabilization_readiness/*.latest.json`

## Selection priority

```text
repository corruption risk
> nondeterminism
> validation unreliability
> public contract ambiguity
> cross-language mismatch
> test coverage gaps
> performance optimization
> feature expansion (ineligible during campaign)
```

## Skill evolution

`abx-hermes-skill-evolution` improves stabilization modules; it does **not** own the campaign. Stabilization-specific failure classes, replay families, and promotion rules are documented in that skill's stabilization appendix.

## Operator decisions (stabilization)

- `AUTHORIZE_STABILIZATION_READINESS_CAMPAIGN`
- `APPROVE_CONTRACT_FREEZE`
- `APPROVE_BOUNDED_STABILIZATION_EXCEPTIONS`
- `AUTHORIZE_STABILIZATION_ENTRY`
- `HOLD_STABILIZATION_ENTRY`
- `REOPEN_FROZEN_CONTRACT`

Frozen contracts require `REOPEN_FROZEN_CONTRACT` before mutation.