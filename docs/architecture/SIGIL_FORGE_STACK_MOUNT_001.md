# Sigil-Forge Stack Mount 001

**Status:** ACTIVE SHADOW · advisory implementation spine  
**Date:** 2026-09-16  
**Authority:** LOCAL_DEV / SHADOW only · no EXTERNAL_PRODUCTION grant  
**Runtime:** **agent-agnostic** standalone CLI + `forge_core`. Hermes is last-compat only — not the end-product runtime, Notion reader, or installer.  
**Notion:** Master Index model-stack owners stamp 2026-09-15. Navigation child: [Sigil-Forge — Abraxas SHADOW mount](https://app.notion.com/p/Sigil-Forge-Abraxas-SHADOW-mount-navigation-3de3e8ba2f5c81c68ef5c27909a935b0) (does not replace the unshared owner page).  
**Companions:** `contracts/specialist_models/stack.v1.json` · `contracts/sigil_forge/` · Hyperlex `compat/abraxas/` · `skills/abx-esoteric-intelligence/`

---

## 1. What this mount is

Sigil-Forge is a **standalone construction engine** (`Zero-State-LLC/Sigil-Forge`, Zero State Proprietary License 1.0): Python CLI + pure `forge_core`. Abraxas mounts it the same way Hyperlex is mounted: typed packets across the boundary, **no smash-merge**, no live rune-catalog write.

Any agent (Grok, Codex, Claude, a raw shell) invokes:

```bash
python3 scripts/sigil_forge.py construct --intent "…" --out DIR
# or
export SIGIL_FORGE_HOME=/path/to/Sigil-Forge
```

`SKILL.md` is an **optional agent contract** (intake/wizard/safety). It is not the product identity. Hermes may copy the tree into `~/.hermes/skills/`; that path is last-compat only.

| Surface | Owner | Must not |
|---------|-------|----------|
| Construction engine + wallpaper product + PoI | Sigil-Forge CLI / `forge_core` | Live inside `core/` · require Hermes |
| Genotype + ingest envelope | `abx-esoteric-intelligence` adapter | Invent Spare primitives |
| Visual OS runes / AAL-Viz mark | design-system | Display occult craft as chrome |
| Specialist model stack | Notion ownership + this contract | Collapse five owners into one model |

Three names stay distinct: **AAL-Viz mark** ≠ **ABX-Rune glyph** ≠ **Sigil-Forge product**.

Discovery order for the Abraxas bridge:

1. `SIGIL_FORGE_HOME` / `SIGIL_FORGE_ROOT` / `SIGIL_FORGE_DIR` / `SIGIL_FORGE_SKILL_DIR`
2. `~/Sigil-Forge`, `~/.sigil-forge`, sibling checkouts
3. `HERMES_SKILL_DIR` / `~/.hermes/skills/sigil-forge` (**compat only**)

Tests: contract tests in `tests/test_sigil_forge_mount.py` always run against a pinned replay of `forge_core` outputs (`tests/fixtures/sigil_forge_pinned/`, provenance in its `PROVENANCE.md`). Tests marked `sigil_forge_live` need a real checkout: they are skipped when it is missing, and fail instead when `ABRAXAS_REQUIRE_SIGIL_FORGE=1`.

State default: `$SIGIL_FORGE_STATE_DIR` or `~/.sigil-forge/state` (legacy Hermes state used only if that tree already exists).

---

## 2. Kernel path (v1, now)

```text
Operator intent
  → any agent / CLI  (construct | wizard --next | forge_core | abraxas forage forge-ingest)
  → forge_core (pure) + optional wallpaper (product)
  → ABX.SigilGenotype.v1          # digest + Spare primitives; no plaintext
  → ForgeIngestEnvelope.v1        # EvidencePack.v0 seed, SHADOW
  → FamiliarIngestionReceipt.v0   # INGESTED_SHADOW
  → spine touchpoint + oracle/belief seeds  # no queue write, no truth assignment
  → AAL-Viz inspect chips         # registers / proof status; no restyle
```

Lane: **SHADOW**. `forecast_authority=false`, `canon_authority=false`, `execution_authority=false`.

Claim classes: **COMPUTED** for digest/geometry; **NOT_COMPUTABLE** for all-vowel / refused / missing craft; never **OBSERVED** efficacy.

---

## 3. Specialist model pipeline (how this evolves)

Notion (2026-09-15) lists model-stack owners: **Athanor · Semion · Trutina · Sigil-Forge · Hyperlex**. Owner pages were **OBSERVED** on 2026-09-17 via `ntn` saved credentials (Daniel’s Space). Hermes bot is not the product reader.

Specialists are **models + CLIs**, not agent skills and not a Hermes product. Intake still enters FAMILIAR. They do not open a second forage door.

```text
v1  TOOLS          Hyperlex receipts + Sigil-Forge genotype/ingest
                   deterministic, labeled, SHADOW, agent-agnostic CLI

v2  MODELS         Specialists train on packet features
                   (digest, channel bitmap, lineage, Brier series)
                   not on plaintext intent by default
                   Alembic hybrid plans fuse ArchitectureContribution
                   Athanor refines · Semion interprets

v3  CALIBRATION    Trutina weighs specialist outputs
                   operator disposes conflicts
                   geometry / lexical signal never auto-FORECAST
```

| Specialist | OBSERVED job (owner page) | Packet | Abraxas mount |
|------------|---------------------------|--------|---------------|
| **Hyperlex** | Form / lexical / slang | receipts, `RUNE.HLX.*` | compat layer exists |
| **Sigil-Forge** | Construct / verify / wallpaper (`sigil.forge.construct`) | `sigil.forge.v0` + genotype/ingest | SHADOW mounted |
| **Athanor** | Tradition retrieve (`athanor.structure`) | `athanor.packet.v0` | none — SLOT_RESERVED |
| **Semion** | Sign triad (`semion.triad`) | `semion.frame.v0` | none — SLOT_RESERVED |
| **Trutina** | Settled Brier (`trutina.score`) | `brier.score.v0` | none — SLOT_RESERVED |

Route: cultural atoms → Hyperlex. Tradition → Athanor. Sign-class → Semion. Settled scores → Trutina. Construct → Sigil-Forge. Forecast asks stay NOT_COMPUTABLE until Trutina has a settled pair.

Do **not** add these as ENABLED rows in `contracts/alembic/architecture_registry.json` until a real adapter exists. Stub ENABLED is a lie.

Feature contract for v2 training (Sigil-Forge → other specialists):

- Public: `intent_digest`, `sigil_root`, channel applied/skipped bitmap, construction family, square name, engine id  
- Private (passphrase vault / capsule): plaintext intent, commitment nonce  
- Never: efficacy labels, Visual OS tokens, Goetic/Enochian seals, Hermes session ids as identity

Hyperlex already has `compat/abraxas/` with no `import abraxas`. Sigil-Forge follows that pattern from the Abraxas side (`sigil_forge_bridge.py` optional-loads `forge_core`).

---

## 4. Runes (advisory)

Proposed only — `contracts/sigil_forge/rune_proposals.v1.json`:

- `RUNE.SIGIL.CLASSIFY`
- `RUNE.SIGIL.GENOTYPE`
- `RUNE.SIGIL.FORGE`

Register via `abx-runes-yggdrasil-manager` before any live catalog use. Unbound runes fail closed.

---

## 5. Proof of Intent / ZK (Phase-0 landed)

`ForgeIngestEnvelope.v1` now carries a public PoI surface when the engine is mounted:

- `intent_commitment` — public value only (nonce never serialized)
- `sigil_root` — Merkle over **genotype leaves** (`intent_digest` + commitment + construction); scope `public_genotype_leaves`
- `zk_provenance` — `ABX_ZK_PROVENANCE_V1` with `status: commitment` or honest `skipped`; `proof: null`

This is **not** the full forge-run root (no glyph/manifest/ciphertext leaves). Geometry identity remains `intent_digest` (deterministic). Commitment is per-run salt.

Alembic: `contracts/sigil_forge/architecture_descriptor.v1.json` is `SHADOW_ONLY`.  
`SigilForgeShadowAdapter` lives in `skills/abx-esoteric-intelligence/alembic_sigil_forge.py` and is **not** in `DEFAULT_ADAPTERS` or `architecture_registry.json`. Invoke is explicit/opt-in.

Inspect: `forge_ingest.inspect_projection` → `ForgeInspectProjection.v1` chips. AAL-Viz sample system `sigil_forge` + `buildForgeInspectSystem` project those chips (engine / construction / proof / SHADOW). Projection only.

Public inputs: `intent_commitment` + `sigil_root` + `intent_digest`.  
Witness stays in the capsule/vault. Provenance of construction ≠ proof the sigil “works”.

---

## 6. Evidence

- `python -m pytest tests/test_sigil_forge_mount.py tests/test_alife_adapter.py`
- `python3 -m abraxas forage forge-ingest --intent "I maintain calm focus while shipping Sigil-Forge" --print-only`
- `python3 $SIGIL_FORGE_HOME/scripts/sigil_forge.py check` (or a clone)
- Golden: `I maintain calm focus while shipping Sigil-Forge` → primitives `mntclfswhpgr`

**FINAL_STATUS:** `SIGIL_FORGE_KERNEL_C_D_SHADOW`
