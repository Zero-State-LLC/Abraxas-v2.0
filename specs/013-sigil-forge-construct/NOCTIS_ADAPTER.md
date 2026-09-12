# Spec 013A — Noctis SIG adapter (SHADOW specify)

**Date**: 2026-09-11
**Lane**: SHADOW specify. No overlay rewrite. No implement. No merge until a named sentence.
**Notion**: https://app.notion.com/p/3d93e8ba2f5c81f583c2f6b3c351ac88
**Parent**: Spec 013
**Canon (read-only)**: ABX-CAN-037 · `noctis.op.generate_sigil.v1`

## Posture

Continue after PR #1142. Function id stays `noctis.op.generate_sigil.v1`. Rune stays SIG. Geometry engine is `sigil.forge.construct` / Sigil-Forge 0.13.0. Do not import that engine into `core/` or `server/`. Do not edit the CAN-037 page body.

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
Record both. Do not claim they are the same. A `--noctis-seed` bind is a later source-repo sentence.

## Refuse

Authority-seal mint. Empty/all-vowel intent with no recoverable field. Invented geometry. Forecast language on the glyph.

## Seal

CANON-SHADOW · SPECIFY_READY · NO_CANON_MUTATION · NO_OVERLAY_ID_CHANGE · NO_ENGINE_IMPORT
