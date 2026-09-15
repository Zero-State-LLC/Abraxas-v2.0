---
name: abx-neon-genie
description: "Umbrella router and venture-cycle coordinator for Abraxas invention and opportunity synthesis. Classifies input modes, acquires evidence via existing skills, orchestrates bounded ideation stages, enforces subsystem ownership, performs overlap/duplicate detection, shapes venture packets, routes specialized work to owning subsystems, and emits operator-review + provenance receipts. Does not absorb forecasting, governance, execution, content virality, competitive intelligence, visualization rendering, or minting authority."
version: 0.1.0
author: Abraxas Governed Operator
license: Proprietary
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, neon-genie, venture, ideation, invention, concept, recombination, scoring, shadow-product, validation-routing]
    related_skills: [abraxas-repo-intel, abraxas-validation-routing, abraxas-automated-production-governance, abx-runes-yggdrasil-manager, abx-familiar-signal-forager, abx-noctis-dream-functions, abraxas-ingest]
    authority: INVENTION_ROUTING_AND_SHAPING_ONLY
    runtime_authority: false
    canon_authority: false
    promotion_authority: false
    forecast_authority: false
---

Supported mode: **full checkout**. Read repository-root `skills/OPERATING.md`
for Python 3.12 bootstrap, canonical source/version, explicit output paths,
unshipped sibling fallback and fail-closed verification before using this skill.

# ABX-NEON-GENIE (Umbrella)

## Purpose

Coordinate invention, recombination, differentiation, venture shaping, scoring, packaging, and catalog routing while preserving strict subsystem ownership.

Neon Genie **invents and structures**. It routes specialized work elsewhere.

## Invocation Conditions

Use for:
- Prompt-led, market-led, capability-led, constraint-led, trend-led, painpoint-led, symbolic-led, or monetization-led invention requests.
- Venture/testbed concept generation.
- Duplicate prevention against current repo subsystems and catalogs.
- Routing invention outputs to owning subsystems.

Do **not** use for direct forecasting, dream interpretation, content virality testing, competitive intelligence collection, visualization rendering, or execution.

## Input Modes (v0.4 canonical)

PROMPT_LED | MARKET_LED | CAPABILITY_LED | CONSTRAINT_LED | TREND_LED | PAINPOINT_LED | SYMBOLIC_LED | MONETIZATION_LED

## Output Classes

BUSINESS | SOFTWARE | SERVICE | CONTENT_ENGINE | INTERNAL_MODULE | WRAPPER | DATA_PRODUCT | HYBRID

## Core Responsibilities (Umbrella Only)

- Classify request and required evidence.
- Acquire evidence via Signal Forager + Ingest when needed.
- Invoke bounded Neon Genie stages (intake → discover → recombine → differentiate → score → shape → package).
- Run overlap/duplicate detection against subsystem inventory, app catalog, prior concepts.
- Classify: NOVEL | ADJACENT | WRAPPER_CANDIDATE | CHILD_SUBSYSTEM | DUPLICATE | NOT_COMPUTABLE.
- Emit typed venture packet + IdeationOperatorPacket.v0 + route decision.
- Route specialized work (Noctis for symbolic seeds, Level 99 for public memetic, LeakForge for competitive pressure, AAL-Viz for projection, etc.).
- Emit operator-review receipt and operation trace for skill evolution.

## Ownership Routing (Hard Boundaries)

| Overlap                          | Route To                  |
|----------------------------------|---------------------------|
| Forecasting / prediction         | Abraxas                   |
| Dream / symbolic interpretation  | Noctis (seeds only)       |
| Music / psychosonics             | BeatOven                  |
| Emotional introspection          | PsyFi                     |
| Provenance / minting             | Phonomicon                |
| Visualization                    | AAL-Viz (projection-only) |
| Virality / public content        | Level 99                  |
| Agentic execution / research     | ABX-Familiar              |
| Competitive intelligence         | SignalOps / LeakForge     |
| New bounded subsystem            | INTERNAL_MODULE candidate |

Never present a renamed existing AAL subsystem as net-new.

## Evidence Rule

Evidence-backed market, revenue, competitor, or adoption claims require an EvidencePack (via Signal Forager + Ingest). Otherwise: NOT_COMPUTABLE.

### EvidencePack.v0 hand-off (wired)

Pass forager output into the router:

```python
import importlib.util
from pathlib import Path
path = Path("skills/abx-neon-genie/neon_genie_router.py")
spec = importlib.util.spec_from_file_location("neon_router", path)
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)
router.run_venture_cycle({
    "mode": "TREND_LED",  # or MARKET_LED / MONETIZATION_LED / …
    "seed": "…",
    "evidence_pack_path": "out/signal_forage/<slug>/evidence_pack.v0.json",
    "require_evidence": True,
})
```

Implementation:

- `evidence_pack.py` — load/normalize EvidencePack.v0, density, commercial gate
- `neon_genie_router.py` — resolves `evidence_pack_path` | `evidence_pack`
- `neon_genie_score.py` — uses `evidence_density`; lowers monetization when blocked
- `neon_genie_package.py` — sets `seed_evidence` + redacts `market_model` to NOT_COMPUTABLE when gated; attaches `operator_packet` (`NeonGenieIdeationOperatorPacket.v0` via `core.neon_genie.ideation_operator_packet`)
- `neon_genie_router.py` — promotes `operator_packet` to run-receipt root (SHADOW operator review only)

Modes that **require** evidence: `MARKET_LED`, `TREND_LED`, `PAINPOINT_LED`, `MONETIZATION_LED`, or `require_evidence: true`.

## Rune / YGGDRASIL Integration

Before registering or changing runes/routes, resolve the unshipped manager per skills/OPERATING.md or STOP with BLOCKED_DEPENDENCY. Pure advisory fixtures do not register routes.

Conceptual runes (to be validated/registered via the manager):
- RUNE.NG.INTAKE
- RUNE.NG.DISCOVER
- RUNE.NG.RECOMBINE
- RUNE.NG.DIFFERENTIATE
- RUNE.NG.SCORE
- RUNE.NG.SHAPE
- RUNE.NG.SIMULATE
- RUNE.NG.PITCH
- RUNE.NG.CATALOG

## Pipeline Contract Status

`neon_genie_ideation` (core/pipelines/registry.py) is Tier 3 SHADOW_PRODUCT, **CONTRACT_V0**:

| Surface | Path |
|---------|------|
| Schema | `contracts/neon_genie/ideation_operator_packet.v0.schema.json` |
| Core builder | `core/neon_genie/ideation_operator_packet.py` |
| Package stage wire | `skills/abx-neon-genie/neon_genie_package.py` → nested `operator_packet` |
| Router receipt | `skills/abx-neon-genie/neon_genie_router.py` → receipt `operator_packet` |

**Next (not this skill's authority):** Hermes Hub packaging remains external (Neon-Genie-Hermes). No packaging runtime, promotion, or forecast influence in Abraxas core.

## Validation Routing

Primary classes: CLASS.REGISTRY_OR_MANIFEST, CLASS.RUNNER_OR_CLI, CLASS.ADVISORY_JSON_GENERATOR, CLASS.JSON_SCHEMA.

Targeted only:
- py_compile
- direct runner execution (synthetic fixtures)
- JSON/schema validation
- overlap/duplicate tests
- authority and boundary scans
- deterministic replay

Full-suite: not implied by targeted checks. Report current failures and scope, never assume a historical blocker.

## Prohibited

- Absorbing other subsystems' intelligence or execution.
- Making evidence-backed commercial claims without EvidencePack.
- Registering duplicate runes or routes.
- Claiming novelty for renamed existing AAL capabilities.
- Direct runtime activation, canon promotion, or forecast influence.

## References

- `references/ABX_NEON_GENIE_NOTION_KNOWLEDGE_TRANSFER_001.md` (canonical Notion architecture)
- `references/input_modes.md`
- `references/output_classes.md`
- `references/ownership_routing_matrix.md`
- `references/venture_packet_v0.4.md`
- `references/duplicate_prevention.md`
- `references/cross_skill_bindings.md`
- `references/NeonGenieSurfaceAudit.v0.1.md`
- `abx-runes-yggdrasil-manager` (for NG runes)
- `abx-familiar-signal-forager` + `abraxas-ingest` (evidence)
- `abx-noctis-dream-functions` (symbolic seeds)
- `abraxas-validation-routing` (targeted validation)

---

**Integration note for larger flows:**

After repo-intel (resolve manager only for actual registration work):
1. Classify request mode.
2. Acquire evidence if required (Forager + Ingest).
3. Run Neon Genie stages.
4. Detect overlaps (high-risk gate).
5. Route to owners.
6. Emit venture packet + receipt + trace.

Build the umbrella first. Extract stable specialist stages (overlap detector, scorer, packager) into sibling skills only after operational traces exist.

## Concrete local invocation
Use an explicit caller-created request JSON (for smoke testing, a labeled
synthetic symbolic seed, not a market observation):
```bash
python skills/abx-neon-genie/neon_genie_router.py --input skills/abx-neon-genie/fixtures/synthetic-request.json > "$ABRAXAS_OUTPUT/neon.json"
python skills/verify_artifact.py --schema contracts/neon_genie/ideation_operator_packet.v0.schema.json --member operator_packet "$ABRAXAS_OUTPUT/neon.json"
python -m pytest -c /dev/null -p no:cacheprovider skills/tests/test_domain_routes.py -q
```
Require a complete operator_packet, commercial_claims_blocked when evidence is
absent, and all execution/promotion/canon authority false. stdout is full JSON,
not a truncated preview. The request is a fixture, not evidence of a live venture.
