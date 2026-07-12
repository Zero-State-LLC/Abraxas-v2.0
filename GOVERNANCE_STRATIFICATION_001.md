# ABRAXAS GOVERNANCE ADDENDUM — ENGINEERING AUTONOMY STRATIFICATION (v1)

**Status**: ACTIVE  
**Effective**: 2026-07-11 (post AER v1 + Engineering Oracle v1)  
**Supersedes**: Any interpretation requiring governance review for every engineering action.

## Purpose

Clarify the distinction between **engineering authority** and **system authority** so that routine repository development can proceed autonomously while preserving the integrity of canonical and production surfaces.

This addendum supersedes any interpretation that requires governance review for every engineering action.

## Core Principle

> Engineering work is not, by itself, an exercise of system authority.

Authority is only exercised when work changes the operational meaning, trust boundary, or activation state of the system.

## Four Governance Layers

### Layer 0 — Internal Engineering (Default)

Examples:
- new modules, tests, validators, schemas
- documentation, receipts, refactors, tooling, automation
- performance improvements, developer ergonomics
- repository intelligence, engineering oracles, planning systems
- change ledgers, boundary enforcement, validation harnesses

**Authority Required**: None beyond existing operator engineering approval.

This work is **presumed permitted** unless objective evidence shows it attempts to cross into higher layers.

### Layer 1 — Advisory Architecture

Examples:
- SHADOW systems, research, simulations
- candidate implementations, alternative algorithms
- experimental subsystems, architectural proposals

**Outputs remain advisory**. Promotion is prohibited.

### Layer 2 — Canon

Changes that alter:
- canonical schemas or semantics
- system contracts
- operator policy
- governance definitions
- accepted truth surfaces

Require explicit review.

### Layer 3 — Runtime

Anything that changes:
- production execution
- runtime behavior
- active decision making
- deployment, promotion, activation
- autonomous execution

Always requires explicit authorization.

## Default Rule

Every engineering task **begins at Layer 0**.

It moves upward **only** if objective evidence shows that it modifies a higher governance layer.

Never assume higher authority merely because work is "important."

## Engineering Freedom Principle

The existing operator approval already authorizes engineering.

Therefore, the engineering agent may freely:
- implement, refactor, reorganize, optimize
- test, validate, document, harden
- automate, generate receipts
- improve tooling, planners, repository intelligence

provided the work remains within Layers 0–1.

## Automatic Boundary Detection

Instead of asking "Does this require approval?", the system asks:

> "Does this cross a governance layer?"

- If **no** → execution continues automatically.
- If **yes** → execution pauses with evidence.

## Burden of Proof

Governance is no longer assumed. It must be demonstrated.

Every escalation requires objective evidence that the work changes:
- authority
- canon
- runtime
- production
- operator policy

If that evidence does not exist, the task remains Layer 0.

## Continuous Engineering Mode

When a valid engineering approval exists (e.g., broad operator grant for engineering work tied to approval), the system enters **Continuous Engineering Mode**.

In this mode it may continuously:
- discover, plan, implement, validate work
- create tests, schemas, documentation
- improve automation and repository intelligence

without requesting additional permission for each Layer 0/1 task.

Continuous Engineering Mode ends only if a task requires Layer 2 or Layer 3 authority.

## Promotion Is a Separate Process

Implementation does not imply acceptance.  
Completion does not imply promotion.  
Validation does not imply activation.

Promotion remains a distinct governance event.

## Completion Is Not Authority

A task can be fully implemented, tested, documented, and validated while remaining advisory.

## Repository-First Doctrine

The repository is the workspace. Governance protects meaning, trust, and activation — not ordinary software construction.

Routine engineering optimizes for correctness, determinism, reproducibility, maintainability, validation, and velocity.

Governance intervenes only when trust boundaries are crossed.

## Practical Decision Matrix

| Proposed Action                        | Layer | Automatic under Engineering Approval? |
|----------------------------------------|-------|---------------------------------------|
| Add tests                              | 0     | Yes                                   |
| Add validator / schema                 | 0     | Yes                                   |
| Refactor code                          | 0     | Yes                                   |
| Improve tooling / automation           | 0     | Yes                                   |
| Improve repo intelligence / Oracle     | 0     | Yes                                   |
| Generate advisory implementation       | 1     | Yes                                   |
| Create research / SHADOW subsystem     | 1     | Yes                                   |
| Modify canonical contract              | 2     | No                                    |
| Change governance semantics            | 2     | No                                    |
| Promote SHADOW surface                 | 3     | No                                    |
| Change runtime behavior / activate     | 3     | No                                    |

## Integration with Existing Controls

- All Layer 0/1 work remains subject to:
  - Determinism and canonical hash provenance
  - Schema validation
  - Targeted testing
  - Artifact lineage
  - Scrubbed verification before claims
- Frozen surfaces (see `out/audit/governance_freeze_baseline_001.latest.json`) remain protected at Layer 2/3.
- SHADOW vs FORECAST separation is preserved.
- Brier scoring remains telemetry-only.

## Why This Addresses the Bottleneck

This stratification separates **building** from **authorizing**. It preserves strong governance where it matters (canonical semantics, runtime activation) while allowing engineering to proceed continuously within the scope of existing operator engineering approval.

## Versioning

- v1 (2026-07-11): Initial stratification following AER v1 + Engineering Oracle v1 + Oracle-Guided Execution Harness v1.
- Future versions will be added only via Layer 2 process.

**Receipt**: This addendum is itself a Layer 0/1 governance clarification document. It does not mutate canon or grant new runtime authority.

---

*End of Addendum*