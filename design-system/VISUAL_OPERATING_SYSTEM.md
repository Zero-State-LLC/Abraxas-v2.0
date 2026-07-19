# Abraxas Visual Operating System

**Mandate:** Complete visual OS for a deterministic symbolic-intelligence platform.  
**Aesthetic:** 2035 engineering OS — Apple HI clarity × Palantir density × Omniverse precision × game HUD readability — without copying any of them.  
**Forbidden:** mystical, fantasy, occult, decorative-only chrome, fake AI clichés.

---

## 1. Architecture of the language

```text
Semantic layer (meaning)          Presentation layer (style)
─────────────────────────         ──────────────────────────
registers, authority,             color, type, stroke,
evidence_state, domain,           radius, elevation, motion
rune function, surface tier   →   tokens + components + glyphs
```

New product states extend **semantic tokens** first; visuals follow.

---

## 2. Color language

| Role | Token family | Use |
|------|--------------|-----|
| Primary accent | `--abx-accent-primary` | Runtime, focus, canonical |
| Secondary | `--abx-accent-secondary` | Oracle / deep structure |
| Tertiary | `--abx-accent-tertiary` | Operator emphasis, tier-2 |
| Success / Error / Warning | `--abx-status-*` | Validation, alerts |
| Observation / Inference / Speculation | `--abx-sem-*` | Output registers |
| Advisory / Shadow / Denied | `--abx-auth-*` | Authority posture |

Dark theme is default. Light theme is full parity under `[data-theme="light"]`.

Accessibility: focus rings use `--abx-border-focus`; text contrast targets WCAG AA on base surfaces.

---

## 3. Typography

| Role | Spec |
|------|------|
| UI / body | IBM Plex Sans |
| Code / HUD / numbers / tables | IBM Plex Mono |
| Labels | 11px uppercase tracking |
| HUD | 10px mono uppercase |

See `tokens/typography.tokens.json`.

---

## 4. Iconography

Family: **stroke 1.5**, round caps, 24×24 grid, works at 16/24/48.

Seed set: `icons/system/*.svg` (44 icons). Expand to 100–300 without changing stroke grammar.

---

## 5. Rune language

Engineering glyphs — **not** occult. Frame + cyan stroke.  
Seed: `runes/glyphs/*.svg` (24). Map to `contracts/runes/catalog.v1.json` via `runes/glyph_map.v1.json`.

---

## 6. Components

`components/primitives.css`: buttons, chips (evidence/authority), panels, HUD, tabs, terminal, callouts.

---

## 7. Data visualization

| Chart type | Encoding |
|------------|----------|
| Knowledge / dependency graphs | Tier borders; node = entity; edge = relation |
| Forecast | Speculative/forecast domain color; dashed |
| Confidence | Opacity + width; never hue-only |
| Uncertainty | Muted + hatch / gap, not red |
| Lineage | Directed edges, receipt chips at sinks |
| Telemetry | Domain color series; tabular mono numbers |

---

## 8. Logo

`brand/logo-mark.svg` — lattice + core node: **order emerging from complexity**.  
Variants: horizontal, mono, favicon.

---

## 9. Motion

Informational only. See `motion/principles.md` + `tokens/motion.tokens.json`.

---

## 10. Documentation visuals

Use chips + callouts from primitives. Architecture diagrams follow illustration rules and existing `docs/media/*`.

---

## 11. System mapping

| Abraxas concept | Visual binding |
|-----------------|----------------|
| OBSERVED / INFERRED / SPECULATIVE | `--abx-sem-*` chips |
| SUPPORTED / ADVISORY | canonical vs advisory chips |
| Activation DENIED | `--abx-auth-denied` |
| deploy_held / NO_GO | `--abx-auth-held` |
| Evidence Partial/Verified | `--abx-ev-*` |
| RUNE.* contracts | Engineering glyphs |
| Operator console | tokens wired into aal-viz CSS |
| Production readiness package | Partial/Verified badges |

Full machine map: `ASSET_REGISTRY.v1.json`.
