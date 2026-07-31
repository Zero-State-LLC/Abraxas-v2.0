# Signal contracts

| Schema | Role |
|--------|------|
| `evidence_pack.v0.schema.json` | EvidencePack.v0 — OS signal syscall output from `abx-familiar-signal-forager` |
| `familiar_spine_touchpoint.v0.schema.json` | FamiliarSpineTouchpoint.v0 — advisory seeds for spine (no Oracle execution) |
| `familiar_oracle_belief_bridge.v0.schema.json` | FamiliarOracleBeliefBridge.v0 — SHADOW oracle intake + belief candidate seeds (no runtime/mutation) |

Canonical validation: `core.signal.evidence_pack`, `core.signal.spine_bridge`, `core.signal.familiar_oracle_belief_bridge`.  
Skill-tree copy under `skills/abx-familiar-signal-forager/references/` must stay byte-compatible with the EvidencePack schema.
