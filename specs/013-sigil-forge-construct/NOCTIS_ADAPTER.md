# Spec 013A — Noctis SIG adapter (SHADOW specify)

**Date**: 2026-09-11
**Lane**: SHADOW specify. No overlay rewrite. No implement.
**Notion**: https://app.notion.com/p/3d93e8ba2f5c81f583c2f6b3c351ac88
**Parent**: Spec 013
**Canon (read-only)**: ABX-CAN-037 · `noctis.op.generate_sigil.v1`

## Posture

Function id stays `noctis.op.generate_sigil.v1`. Rune stays SIG. Geometry engine is `sigil.forge.construct` / Sigil-Forge 0.13.0. Do not import that engine into `core/` or `server/`. Do not edit the CAN-037 page body.

## Chain (R011D)

```
noctis.op.interpret_dream.v1  →  analysis
noctis.op.generate_sigil.v1   →  sigil.forge.v0 (engine)
noctis.op.log_grimoire.v1     →  overlay log, unchanged
```

## Map

| CAN-037 | Forge / packet | Honesty |
|---|---|---|
| intent | `--intent` | OBSERVED |
| analysis | derive intent from declared `intent` or joined `motif_handles`; else NOT_COMPUTABLE | INFERRED rule |
| seed (int) | packet `noctis_seed` only; 0.13.0 geometry uses `intent_digest` | OBSERVED gap |
| sigil_svg / image_path | `glyph.svg` / `glyph.png` after verify | OBSERVED |
| metadata.provenance | forge-packet + overlay id | OBSERVED |
| efficacy | JSON null | frozen |

## Seed gap

CAN-037 reproducibility = payload + int seed + code version.
Forge 0.13.0 identity = SHA-256(normalized intent).
Record both. Do not claim they are the same.

## Option A locked — 2026-09-11

Seed is metadata. Geometry is `intent_digest`.

| object | type | seat |
|---|---|---|
| CAN-037 generate_sigil.seed | int | packet `noctis_seed` |
| DreamInput / Analysis seed | string 8–128 | packet `dream_seed` |
| Forge geometry | SHA-256(normalized intent) | `compute_forge` only |
| polish gen_seed | int(digest[:8], 16) | presentation only |
| wallpaper seed | int(sha256(digest\|surface\|mode\|theme)[:16], 16) | presentation only |
| commitment nonce | per-run | never geometry |

C4 LOCKED: seed does not enter Spare reduction, kamea path, or `compute_forge`.
Option B (`--noctis-seed` mix-in) stays closed until a sentence names the Sigil-Forge repo.
Do not use polish or wallpaper seeds as the overlay seed.
CAN-037 golden-test sentence for SVG seed behavior remains unsatisfied under A. Recorded, not patched.

## Refuse

Authority-seal mint. Empty/all-vowel intent with no recoverable field. Invented geometry. Forecast language on the glyph.

## Seal

CANON-SHADOW · SPECIFY_READY · NO_CANON_MUTATION · NO_OVERLAY_ID_CHANGE · NO_ENGINE_IMPORT
