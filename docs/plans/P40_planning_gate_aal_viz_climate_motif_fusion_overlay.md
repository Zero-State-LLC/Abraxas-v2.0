# P40 PLANNING GATE — AAL-VIZ CLIMATE + MOTIF FUSION OVERLAY

## 1. P40 PLANNING SUMMARY
Decision: **P40_PLAN_READY**.

Recommended lane: **AAL-Viz Climate + Motif Fusion Overlay**.

Rationale: P35/P37/P39 and P38 already provide the exact projection-grade primitives needed for a deterministic, advisory-only fusion packet. This yields immediate consumer leverage without crossing SHADOW/FORECAST boundaries.

## 2. SEALED BASELINE CONFIRMATION
Baseline state is treated as sealed and unchanged:
P27–P39 COMPLETE_AND_STABLE, replay consensus drift closed, full suite green, artifact drift clean, governance boundaries preserved.

## 3. CANDIDATE INVENTORY
### Lane 1: AAL-Viz Climate + Motif Fusion Overlay
- Existing related surfaces:
  - Climate overlay packet and writer
  - Motif overlay packet and writer
  - Seasonality surface packet and writer
  - Motif governance audit receipt
- Missing surfaces:
  - Fusion packet module/runner/schema/tests/registry entries
- Likely input artifacts:
  - `out/projections/aal_viz_operator_climate_overlay_001.latest.json`
  - `out/projections/aal_viz_pressure_motif_overlay_001.latest.json`
  - `out/projections/operator_load_seasonality_001.latest.json`
  - `out/audit/motif_governance_audit_001.latest.json` (lineage optional)
- Likely output artifact:
  - `out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json`
  - markdown sibling
- Governance risk: low (projection-only)
- Projection coupling risk: moderate but bounded and deterministic
- Implementation cost: low-medium
- Downstream leverage: high
- Immediate operator value: high

### Lane 2: Motif Governance Drift Receipt
- Existing related surfaces: P36/P37/P38
- Missing surfaces: cross-version comparator requires multiple motif generations
- Inputs: multiple versioned motif registry/overlay + historical audits
- Output: drift receipt
- Governance risk: low
- Coupling risk: low
- Cost: medium
- Leverage: medium (later)
- Immediate value: low now

### Lane 3: Operator Narrative Report
- Existing surfaces: all current packets support narrative synthesis
- Missing surfaces: narrative-only reporting module
- Inputs: existing projections/audits
- Output: narrative markdown/json
- Governance risk: low
- Coupling risk: low
- Cost: low
- Leverage: low-medium
- Immediate value: medium

### Lane 4: Forecast Readiness Boundary Packet
- Existing surfaces: many prerequisites partial
- Missing surfaces: strict boundary design for forecast claims
- Inputs: broad runtime + governance chain
- Output: readiness boundary packet
- Governance risk: high (SHADOW/FORECAST boundary)
- Coupling risk: high
- Cost: high
- Leverage: potentially high but premature
- Immediate value: low (risk-adjusted)

### Lane 5: Operator Load Seasonality Audit Receipt
- Existing surfaces: P39 exists
- Missing surfaces: downstream consumer evidence to audit seasonality uptake
- Inputs: P39 + consumer outputs over time
- Output: seasonality audit receipt
- Governance risk: low
- Coupling risk: low-medium
- Cost: low-medium
- Leverage: medium later
- Immediate value: low-medium now

## 4. SCORE TABLE (1–5)
| Lane | Readiness | Immediate Value | Dependency Stability | Governance Safety | Implementation Cost | Projection Determinism Safety | Downstream Leverage | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. Climate+Motif Fusion Overlay | 5 | 5 | 5 | 5 | 4 | 5 | 5 | **34** |
| 2. Motif Governance Drift Receipt | 2 | 2 | 2 | 5 | 3 | 5 | 3 | **22** |
| 3. Operator Narrative Report | 4 | 3 | 5 | 5 | 5 | 5 | 2 | **29** |
| 4. Forecast Readiness Boundary Packet | 1 | 2 | 2 | 1 | 1 | 2 | 4 | **13** |
| 5. Seasonality Audit Receipt | 3 | 3 | 4 | 5 | 4 | 5 | 3 | **27** |

## 5. SELECTED P40 LANE
**Selected:** Lane 1 — AAL-Viz Climate + Motif Fusion Overlay.

Why it wins:
- Highest deterministic readiness with sealed upstream dependencies (P35/P37/P39 + optional P38 lineage).
- Max immediate reuse for render consumers through one unified packet.
- Preserves advisory-only posture and avoids authority escalation.

Why others wait:
- Lane 2 needs multi-version motif history.
- Lane 3 is useful but lower infrastructure leverage than fusion substrate.
- Lane 4 is boundary-risky and premature.
- Lane 5 should follow at least one downstream seasonality consumer.

Exact scope boundary:
- Read-only aggregation and deterministic projection of existing overlay/seasonality primitives.
- No new inference, recommendation, routing, or forecast logic.

Forbidden scope:
- No queue or routing mutation.
- No forecast/readiness claims.
- No command channel/UI authority.
- No canon/runtime mutation.

## 6. EXPECTED FILES / ARTIFACTS
Expected implementation surfaces:
- `core/aal_viz_climate_motif_fusion_overlay.py`
- `scripts/viz/run_aal_viz_climate_motif_fusion_overlay.py`
- `tests/test_aal_viz_climate_motif_fusion_overlay.py`
- `contracts/operator_attention/aal_viz_climate_motif_fusion_overlay.v1.schema.json`
- `core/generated_artifact_registry.py` (new entries)
- `core/config.py` (new output path helper)

Expected artifacts:
- `out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json`
- `out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.md`

## 7. FUSION SEMANTICS
Required semantics:
- projection-only, render-consumer-ready, deterministic, non-authoritative.
- advisory-only governance flags hard-true.
- no inference authority, no mutation authority, no routing authority, no forecast authority, no readiness claims, no UI command authority.

Fusion content contract:
- Pass through climate primitives from P35: layers/cards/nodes/badges/edges.
- Pass through motif primitives from P37: layers/cards/nodes/badges/edges.
- Include P39 recurrence summary and seasonality posture/status.
- Include motif governance audit status from P38 when present via lineage.
- Include source artifact paths + source hash lineage.
- Optionally emit unified deterministic render layers/cards/edges when merge rules are total-order deterministic.

Deterministic merge guardrails:
- Stable sort keys for all merged arrays.
- Duplicate identity folding by deterministic composite key.
- Deterministic hash over canonicalized fusion payload.
- Fail-closed to NOT_COMPUTABLE on missing/corrupt mandatory source artifacts.

## 8. GOVERNANCE BOUNDARIES
Invariant set (must hold):
- advisory_only=true
- projection_only=true
- non_authoritative=true
- authority_granted=false
- execution_authority=false
- mutation_allowed=false
- queue_mutation_allowed=false
- routing_change_allowed=false
- forecast_authority=false
- readiness_claims_allowed=false
- command_channel=false
- auto_execute=false
- auto_approve=false

SHADOW/FORECAST separation remains strict.

## 9. RISKS / DRIFT FLAGS
- Upstream schema drift in P35/P37/P39 field names.
- Inconsistent primitive identity keys causing non-deterministic ordering.
- Optional P38 lineage missing; should degrade gracefully without authority expansion.
- Artifact lineage mismatch between declared source hashes and loaded payload hashes.

Mitigations:
- Schema validation tests + deterministic snapshot tests.
- Explicit stable sort and composite IDs.
- Source presence map + blocker_summary propagation.
- Hash lineage consistency checks in packet build.

## 10. NEXT CODEX IMPLEMENTATION PROMPT
Implement **P40 AAL-Viz Climate + Motif Fusion Overlay** as projection-only deterministic fusion over P35/P37/P39 with optional P38 lineage.

Requirements:
1. Add `core/aal_viz_climate_motif_fusion_overlay.py` with:
   - `build_aal_viz_climate_motif_fusion_overlay_packet(...)`
   - markdown builder
   - packet writer
   - strict governance flags (advisory/projection/non-authoritative)
   - fail-closed NOT_COMPUTABLE behavior for missing/corrupt required sources
2. Add runner script `scripts/viz/run_aal_viz_climate_motif_fusion_overlay.py`.
3. Add schema contract `contracts/operator_attention/aal_viz_climate_motif_fusion_overlay.v1.schema.json`.
4. Register outputs in `core/generated_artifact_registry.py`.
5. Add config path in `core/config.py`.
6. Add tests `tests/test_aal_viz_climate_motif_fusion_overlay.py` for:
   - deterministic build
   - missing/corrupt source fail-closed
   - governance invariants
   - schema validation
   - registry coverage
7. Emit artifacts:
   - `out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json`
   - `out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.md`

Hard boundaries:
- No inference/routing/forecast/readiness/UI command authority.
- No queue/canon/runtime mutation.
- Preserve sealed states P27–P39.
