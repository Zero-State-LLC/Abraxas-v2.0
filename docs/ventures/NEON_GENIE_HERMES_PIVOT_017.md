# Neon Genie Hermes Pivot 017

Brier Score: 0.11  
Status: **ACTIVE** · advisory_only · 2026-07-31

## Decision

**Canonical Hermes packaging skill for Neon Genie:**

```text
https://github.com/scrimshawlife-ctrl/Neon-Genie-Hermes
Hub path: skills/neon-genie
Install: hermes skills install scrimshawlife-ctrl/Neon-Genie-Hermes/skills/neon-genie
```

Abraxas-v2.0 **does not** own packaging CLI, Hub mirrors, run-envelope emission, or privacy runtime. Those ship from Neon-Genie-Hermes.

## What stays in Abraxas

| Surface | Path | Role after pivot |
|---------|------|------------------|
| Invention umbrella | `skills/abx-neon-genie` | Classify, overlap-detect, route ownership, venture packet shaping |
| Venture planning docs | `docs/ventures/*` | Docs-only planning (no runtime activation) |
| Forecast / oracle / YGGDRASIL | Abraxas core | Unchanged; never delegated to Neon Genie |
| Evidence forager + ingest | existing skills | Still used when abx-neon-genie needs EvidencePack |

## Operator path

1. **Hermes skill install / packaging / doctor / privacy / dist**  
   → work in **Neon-Genie-Hermes** (or installed `~/.hermes/skills/neon-genie`).
2. **Invention request with AAL ownership routing**  
   → load Abraxas `abx-neon-genie`; when packaging artifacts are required, call or hand off to Neon-Genie-Hermes.
3. **Do not** re-implement `do receipt` / `do envelope` / Hub package generation inside Abraxas.

## Boundaries (unchanged)

- `RUNTIME_MUTATION=false` unless separately gated in Abraxas.
- No canon promotion via this pivot.
- No product launch claim.
- Neon Genie remains `advisory_only` (no spend/execute).
- Privacy: Neon-Genie-Hermes `local_only` default; purpose-bound consent only.

## Provenance

- Parent planning: [`NEON_GENIE_INTEGRATION_007.md`](./NEON_GENIE_INTEGRATION_007.md)
- Neon Genie privacy runtime on Hermes main: PR #17
- Binding note in Hermes: `docs/ABRAXAS_PIVOT.md`, `references/abraxas-binding.md`
- Skill pointer: `skills/abx-neon-genie/SKILL.md` § Canonical packaging home
