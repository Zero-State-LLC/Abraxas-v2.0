# ABRAXAS SKILL ROUTER

## Purpose

`SKILLS.md` is the canonical registry and router for repository skills. It answers: which skill should an agent load for this task, and which skills should it not load?

## Authority

`AGENTS.md` and `GOVERNANCE_V3.md` outrank every skill. A skill may specialize execution, but it may not override `AGENTS.md`, grant itself production/canon/runtime authority, require ceremony for ordinary bounded engineering, or reinterpret historical artifacts as current authority. Producer identity is provenance only.

## Routing rules

Default engineering path:

```text
AGENTS.md -> Governance V3 -> relevant domain docs -> bounded engineering -> validation
```

Load a skill only when it adds task-specific capability. Do not load a skill merely because it exists.

| Task shape | Route |
| --- | --- |
| trivial lookup | direct response / direct tool use |
| bounded repo implementation | no skill by default; optionally `abraxas-repo-intel` for discovery |
| external signal acquisition | `abx-familiar-signal-forager` |
| invention/opportunity shaping | `abx-neon-genie` |
| dream/symbolic NOCTIS work | `abx-noctis-dream-functions` |
| esoteric symbolic analysis | `abx-esoteric-intelligence` |
| skill performance evolution | `abx-hermes-skill-evolution` |
| autonomous multi-cycle campaign | `abraxas-master-loop-workflow` |
| HyperAgent role/fleet work | `hyperagent-orchestrator` |
| Holler sports data/calibration/slang | Holler skills under `skills/holler-sports/` |
| modular synth catalog campaign | `modular-synth-catalog-research` |

## Default engineering behavior

Routine engineering starts at Governance V3 Layer 0. It does not require authorization packets, seal packets, WorkPackets, master-loop loading, Brier scoring, evaluator persona ceremonies, or skill mutation receipts. Use MSW from `AGENTS.md`: keep only changes that are necessary to satisfy and prove the task contract.

## Skill registry

| Name | Path | Status | Default | Trigger | Purpose | Inputs | Outputs | May compose with | Must not override | Supersedes / Superseded by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `abraxas-repo-intel` | `skills/abraxas-repo-intel/SKILL.md` | ACTIVE | false | repo mapping, ownership, path/call discovery | produce smallest repo evidence packet before coding | repo files, status docs, search queries | observed paths, architecture notes, gap map | bounded engineering, familiar forager | AGENTS/Governance V3, tests as evidence | none |
| `abx-familiar-signal-forager` | `skills/abx-familiar-signal-forager/SKILL.md` | ACTIVE | false | external/local signal acquisition | EvidencePack-style forage with provenance tiers | web/papers/social/markets/repo signal | OBSERVED/INFERRED/SPECULATIVE/NOT_COMPUTABLE evidence pack | repo-intel, neon-genie, forecast workflows | AGENTS/Governance V3, no fabricated sources | none |
| `abx-neon-genie` | `skills/abx-neon-genie/SKILL.md` | ACTIVE | false | invention, venture, concept recombination | route opportunity ideation without absorbing owner subsystems | prompt, evidence packs, venture request | operator-review venture packet, overlap findings | familiar forager, repo-intel, stabilization | forecasting, governance, execution, minting authority | none |
| `abx-hermes-skill-evolution` | `skills/abx-hermes-skill-evolution/SKILL.md` | ACTIVE | false | skill-performance evidence and candidate patches | generate review-only skill evolution candidates | operation traces, review receipts | SkillEvolutionCandidate, SkillPatchCandidate | stabilization, familiar forager | active skill mutation or promotion | none |
| `abx-stabilization-readiness` | `skills/abx-stabilization-readiness/SKILL.md` | ACTIVE | false | stabilization readiness evidence | deterministic advisory stabilization evidence | receipts, schemas, conformance evidence | readiness packet, residual risks | skill evolution | production activation or contract freeze | none |
| `abraxas-master-loop-workflow` | `skills/abraxas-master-loop-workflow/SKILL.md` | SPECIALIZED | false | autonomous campaigns, recursive improvement, scheduled multi-cycle loops | run durable loop state with MSW claims and stop conditions | contract, state, validation commands, loop memory | cycle receipt, verification, next state | repo-intel, familiar forager, operator loop | default routing for ordinary engineering | supersedes `abraxas-jamon-agentic-workflow` for autonomous loop work |
| `abx-noctis-dream-functions` | `skills/abx-noctis-dream-functions/SKILL.md` | SPECIALIZED | false | NOCTIS dream-symbolic SHADOW lane | route dream material through governed symbolic surfaces | dream narrative, consent/privacy context | symbolic packet, memory candidate, NOT_COMPUTABLE blockers | esoteric intelligence, repo-intel | medical/forecast/canon/direct memory authority | none |
| `abx-esoteric-intelligence` | `skills/abx-esoteric-intelligence/SKILL.md` | SPECIALIZED | false | occult/esoteric/symbolic correspondence analysis | governed symbolic adapter, not ontology authority | explicit symbolic question, source corpus | symbolic analysis with provenance tiers | noctis, neon, familiar forager | forecast, canon, runtime, divination-by-default authority | none |
| `hyperagent-orchestrator` | `skills/autonomous-ai-agents/hyperagent-orchestrator/SKILL.md` | SPECIALIZED | false | HyperAgent auth, role, fleet, bridge work | deterministic external agent role configs and Abraxas bridge | HyperAgent role specs, credentials status, exports | dry-run role configs, bridge payloads | operator loop, familiar forager | credential leakage or external production authority | none |
| `modular-synth-catalog-research` | `skills/modular-synth-catalog-research/SKILL.md` | SPECIALIZED | false | exhaustive modular synth catalog research | long-running provenance-tagged catalog campaign | manufacturer, retail, forum, video sources | Markdown/JSON catalog, source ledger | familiar forager, master loop when campaign-level | Brier on non-forecast facts, default Abraxas routing | none |
| `holler-ingest` | `skills/holler-sports/holler-ingest/SKILL.md` | CANDIDATE_FOR_MERGE | false | Holler sports ingestion | sports data ingestion with provenance | API/CSV/JSON sports data | validated Holler batch | holler-calibrate, slang-emergence | production betting/external action authority | candidate merge into Holler umbrella |
| `holler-calibrate` | `skills/holler-sports/holler-calibrate/SKILL.md` | CANDIDATE_FOR_MERGE | false | sports forecast calibration | Brier/model evaluation where outcomes exist | forecasts, outcomes, adversarial sets | calibration report, regime flags | holler-ingest, FORECAST workflow | Brier for deterministic code/docs | candidate merge into Holler umbrella |
| `slang-emergence` | `skills/holler-sports/slang-emergence/SKILL.md` | CANDIDATE_FOR_MERGE | false | sports slang/memetic signal | cultural/memetic pattern detection and symbolic forecasts | social/culture evidence | provenance-tagged slang signal report | familiar forager, holler-calibrate | unverified virality claims or betting action | candidate merge into Holler umbrella |
| `abraxas-jamon-agentic-workflow` | `skills/abraxas-jamon-agentic-workflow/SKILL.md` | SUPERSEDED | false | historical Jamon workflow reference | preserve predecessor workflow provenance | historical references | reference patterns only | master-loop when needed | current default routing | superseded by `abraxas-master-loop-workflow` and `AGENTS.md` MSW router |

## Composition rules

- Compose skills only when their scopes are both necessary to prove the contract.
- Use `abx-familiar-signal-forager` before claim-heavy external research.
- Use `abraxas-repo-intel` for mapping before broad repository edits.
- Use `abraxas-master-loop-workflow` only when repeated autonomous cycles are required.
- Use `WorkPacket.v1` / `HandoffEnvelope.v1` only for real delegated or peer multi-agent work.

## Supersession rules

Superseded skills remain preserved for provenance. They are not default routes. If a superseded skill contains useful detail, treat it as historical reference and apply current `AGENTS.md`, `GOVERNANCE_V3.md`, and this router first.

## Skill authoring and evolution rules

- New skills must declare a narrow trigger and authority boundary.
- New skills must not duplicate the root router or Governance V3.
- Brier is required only for genuine probabilistic forecasts with settlement semantics.
- Generator/evaluator separation is optional unless risk, ambiguity, research interpretation, or autonomous looping justifies independent evaluation.
- Skill mutation must flow through review-only candidates and operator disposition; no active skill self-mutation.

## Validation

Run doctrine validation after changing this file or any skill:

```bash
python -m scripts.governance.validate_agent_doctrine
python -m pytest tests/test_agent_doctrine_validation.py -q
```

The validator checks registry paths, missing active skills, duplicate universal defaults, authority conflicts, required root references, master-loop non-default status, and touched-file Markdown links.
