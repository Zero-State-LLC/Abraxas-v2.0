---
name: abx-campaign-director
description: "Umbrella orchestrator for Abraxas engineering campaigns. Resolves phase, selects bounded work packets, enforces protected state, and routes campaign classes including STABILIZATION_READINESS to abx-stabilization-readiness. Core implementation: core/campaign_director/ and scripts/run_campaign_director*.py."
version: 0.2.0
author: Abraxas Governed Operator
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, campaign-director, orchestration, stabilization]
    related_skills: [abx-stabilization-readiness, abx-hermes-skill-evolution, abraxas-repo-intel]
---

# ABX Campaign Director

## Role

Remain the **single umbrella** above domain campaigns. Do not add another meta-umbrella.

## Campaign classes

| Class | Delegate |
|-------|----------|
| Structural engineering (default) | `core/campaign_director` modes A–F |
| `STABILIZATION_READINESS` | `abx-stabilization-readiness` |

## STABILIZATION_READINESS responsibilities

- Resolve current stabilization phase.
- Select bounded work packets (no unrelated feature expansion).
- Track entry criteria across Python and TypeScript.
- Require clean-state evidence before/after each packet (operator/evidence skills).
- Produce campaign-level readiness via **independent** stabilization gate.
- Stop when terminal stabilization decision is recorded.

## Routing

```python
from core.campaign_director.stabilization_campaign import (
    is_stabilization_campaign,
    stabilization_routing_packet,
    campaign_should_stop_on_terminal,
)
```

When `campaign_class == STABILIZATION_READINESS`, run:

```bash
uv run python skills/abx-stabilization-readiness/run_advisory.py
```

Do not bypass the director with ad-hoc stabilization scripts in production workflows.

## Protected state

Unchanged from Governance V3: no authority expansion, canon mutation, production activation, or promotion without explicit operator paths.

## Scripts

- `scripts/run_campaign_director_plan.py`
- `scripts/run_campaign_director.py`
- `scripts/run_campaign_director_recovery.py`
- `scripts/run_campaign_director_validate.py`

## Stabilization campaign state (reference)

See `skills/abx-stabilization-readiness/fixtures/sample_campaign_state.json`.