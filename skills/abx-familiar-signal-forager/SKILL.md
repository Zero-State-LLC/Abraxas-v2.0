---
name: abx-familiar-signal-forager
description: "Use when acquiring external or local signal into EvidencePacks for Abraxas/Hermes — web, papers, markets, social, repo. OBSERVED/INFERRED/SPECULATIVE/NOT_COMPUTABLE; SHADOW forage; never fabricates sources."
version: 0.1.0
author: Hermes / Abraxas Governed Operator
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [abraxas, signal, forage, evidence, ingest, provenance, research, shadow]
    related_skills: [abraxas-master-loop-workflow, abx-neon-genie, abx-hermes-skill-evolution, abraxas-repo-intel, arxiv, web-scraping, polymarket]
---

# abx-familiar-signal-forager

**Role:** Hermes-side **signal acquisition syscall** for the Abraxas OS.  
Turns vague research / market / competitive / symbolic curiosity into a **typed EvidencePack** with register tiers. Does **not** forecast, invent ventures, mutate canon, or authorize production.

Ownership matrix row: `abx-familiar` · pipeline `familiar_ingestion` · lane **SHADOW** · contract path previously **MISSING** — this skill closes the *agent-facing* contract; core schema may lag.

## When to Use

- User asks to research, scout, monitor, or "pull signal" on a topic
- Neon Genie / venture work needs market, competitor, adoption, or revenue claims
- Oracle / BeliefGraph / forecasting needs OBSERVED inputs
- Skill evolution / CFAR needs literature or repo evidence before synthesis
- Cron / hyperagent missions: recurring topic forage with compliance filters

**Do not use for:**
- Execution, deploy, CLEAR deletion, or live production activation
- Dream interpretation (Noctis), music (BeatOven), viz rendering (AAL-Viz)
- Replacing `abraxas-ingest` / universal_ingest runners (hand off packs to them)

## Hard rules

1. **No fabricated sources.** Missing data → `NOT_COMPUTABLE`, not invented URLs.
2. **Register every claim:**
   - `OBSERVED` — direct quote/metric from a retrieved primary source (URL + excerpt)
   - `INFERRED` — reasonable join of ≥2 OBSERVED with explicit join logic
   - `SPECULATIVE` — hypothesis labeled as such; never mixed into OBSERVED
   - `NOT_COMPUTABLE` — claim type that cannot be grounded with available tools/time
3. **SHADOW default.** `execution_authority: false`, `promotion_authorized: false`
4. **Evidence before confident language.** If pack lacks OBSERVED density, refuse revenue/market sizing certainty.
5. **Smallest complete packet.** Prefer 5 high-signal sources over 50 SEO pages.
6. **Cite tools honestly.** Web/search failures are OBSERVED failures, not silence.

## Standard forage workflow

### 0. CFAR / construct (optional, 30s)

If the question is ill-posed, define the *construct* first (what would count as evidence?) before retrieval. Aligns with Abraxas CFAR advisory gate.

### 1. Frame the hunt

Write a one-screen brief:

```yaml
topic: ""
intent: research | competitive | market | regulatory | tech | memetic | local_ops
time_horizon: ""
must_answer: []      # concrete questions
hard_exclusions: []  # out of scope / compliance
max_sources: 8
output_path: ""      # default: out/signal_forage/<slug>/evidence_pack.v0.json
```

### 2. Source rotation (diversify; avoid single-domain grip)

Rotate across families until `max_sources` or diminishing returns:

| Family | Hermes means | Notes |
|--------|--------------|-------|
| General web | `web_search` + `web_extract` | Prefer primary docs, filings, official blogs |
| Academic | `arxiv` skill | Papers → OBSERVED abstracts/methods only |
| Markets | `polymarket` | Prices are OBSERVED; causality is INFERRED |
| Social | `x_search` / xurl | Treat as weak OBSERVED; high noise |
| Repo / local | `search_files`, git, OP.SEARCH_SIGNAL | Code and receipts are first-class |
| Prior sessions | `session_search` | Continuity only; re-verify live sources |

**Anti-grip:** no more than ~30% of sources from one domain cluster unless the topic is that domain.

### 3. Normalize each hit

For every source:

```yaml
source_id: S001
url_or_path: ""
retrieved_at_policy: session_wall_clock_ok_for_forage  # packs are not Abraxas canonical_hash artifacts unless written via core writers
title: ""
publisher: ""
source_class: primary | secondary | social | market | code | session
excerpt: ""           # short, faithful
claims: []            # see claim shape
```

### 4. Claim shape

```yaml
claim_id: C001
text: ""
register: OBSERVED | INFERRED | SPECULATIVE | NOT_COMPUTABLE
supports_questions: []   # indices into must_answer
source_ids: []
join_logic: null | "..."  # required if INFERRED
confidence_note: ""       # qualitative; not a fake Brier resolution
```

### 5. Emit EvidencePack.v0

Write JSON matching `references/evidence_pack.v0.schema.json`.  
Also emit a short markdown brief for humans (`evidence_brief.md`) with:

- Answers to `must_answer` (or explicit NOT_COMPUTABLE)
- Top OBSERVED bullets with links
- Open questions / next forage hooks
- Explicit **non-claims** (what you did not establish)

### 6. Hand-off

| Downstream | How |
|------------|-----|
| Neon Genie | Attach pack path; market fields stay NOT_COMPUTABLE without OBSERVED density |
| Ingest / Oracle | Point operator or runner at pack; do not self-promote to canon |
| Skill evolution | Optional `OperationTrace` via hermes-surface emitter (`task_class: signal_forage`) |
| Operator | Ask before external posts, paid APIs beyond normal search, or irreversible scrapes |

## Hermes invocation checklist

```text
[ ] skill_view(abx-familiar-signal-forager)
[ ] Frame brief (topic, must_answer, exclusions)
[ ] Multi-family search (rotate sources)
[ ] Extract with web_extract / arxiv / etc. — no summary-only ghosts
[ ] Tag every claim with register
[ ] Write EvidencePack JSON + brief
[ ] Refuse confident market language if OBSERVED density low
[ ] Offer trace emission + next hooks
```

## Output locations

Prefer repo-relative when cwd is Abraxas:

- `out/signal_forage/<utc_date>_<slug>/evidence_pack.v0.json`
- `out/signal_forage/<utc_date>_<slug>/evidence_brief.md`
- `out/signal_forage/<utc_date>_<slug>/sources/` (optional raw extracts)

Outside repo: `~/artifacts/signal_forage/...` or session-local path user names.

**Note:** These forage packs are **session/operator evidence**, not automatic canonical domain artifacts. Promotion into Abraxas `out/` canon requires existing writers + governance lanes.

## Brier / telemetry posture

Core module `core/governance/signal_forager_brier_hook.py` emits **telemetry-only** hooks with `resolution_allowed: false`.  
Do **not** resolve Brier outcomes from forage. Optional: attach `claim_id`s that *could* become forecast claims later under Oracle lanes.

## Compliance & safety

- Respect robots/ToS; prefer official APIs and public pages
- No credential stuffing, no bypass of paywalls via shady means
- PII minimization; Daniel privacy defaults
- Competitive intel: public sources only unless operator provides private corpus

## Verification

- Pack validates against `references/evidence_pack.v0.schema.json` (JSON Schema draft-07 subset)
- Every OBSERVED claim has ≥1 `source_id` with URL/path + excerpt
- Every INFERRED claim has `join_logic` and ≥2 sources
- Brief lists unanswered `must_answer` items explicitly
- No `execution_authority: true` anywhere in pack

## Common pitfalls

- Treating LLM prior knowledge as OBSERVED
- Single-SERP monoculture (modular grip / vendor grip)
- Collapsing SPECULATIVE into recommendations without labels
- Writing into sealed `out/research_canary_*` or continuity spines
- Running forage "live runtime authorized" gates — those are historical advisory contracts; this skill stays SHADOW
- Skipping hand-off path so packs die in chat

## References

- **Canonical schema:** `contracts/signal/evidence_pack.v0.schema.json`
- **Canonical validator:** `core/signal/evidence_pack.py` (`python scripts/research/run_evidence_pack_validate.py PATH`)
- `references/evidence_pack.v0.schema.json` — skill mirror (must stay byte-equal to contracts)
- `references/forage-playbook.md` — worked examples + quality bar
- `references/source-rotation.md` — anti-grip rotation
- `docs/architecture/ABRAXAS_HERMES_OS_UNIFICATION_001.md` — OS mount + signal as syscall
- `docs/architecture/ABRAXAS_AI_OS_REALIZATION_BACKLOG_001.md` — realization WPs
- `core/governance/signal_forager_brier_hook.py` — telemetry-only companion
