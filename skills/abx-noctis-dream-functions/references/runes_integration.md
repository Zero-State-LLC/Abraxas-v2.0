# Rune / YGGDRASIL Integration

This skill **must** coordinate with `abx-runes-yggdrasil-manager` (sibling).

Before using or declaring dream runes:
1. Invoke the runes manager.
2. Discover current coverage.
3. Extend existing runes where possible (prefer over new duplicates).
4. Register only bounded, schema-bound, authority-validated runes.
5. Validate any YGGDRASIL route that includes NOCTIS nodes.

Conceptual runes (subject to manager validation and current repo conventions):
- RUNE.NOCTIS.DREAM.NORMALIZE
- RUNE.NOCTIS.MOTIF.EXTRACT
- RUNE.NOCTIS.CONTINUITY.LINK
- RUNE.NOCTIS.ARTIFACT_INTENT
- RUNE.NOCTIS.YGGDRASIL.BRIDGE (memory candidate only)
- RUNE.NOCTIS.PROJECTION (PROJECTION_ONLY)

YGGDRASIL route example (high-level):
Dream input → policy gate → normalize → motif extract → continuity → intent/projection bridge → receipt.

The runes manager emits the registry/route audits and receipts. This skill consumes the contracts.

## Pipeline Contract Note
`noctis_dream` in core/pipelines/registry.py is Tier 3 SHADOW_SYMBOLIC with `next_action: "convert dream analysis to receipt plus IR plus review pipeline"`.

This skill + runes manager + validation receipts begin to satisfy that next action without fabricating unobserved core logic.