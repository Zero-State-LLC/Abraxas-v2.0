# ADR-0017 — Bounded Activation Policy

## Status

Accepted (2026-07-26)

## Context

Governance V3 and `docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md` authorize lane-based activation (`LOCAL_DEV`, `SANDBOX`, `INTERNAL_CANARY`, `EXTERNAL_PRODUCTION`) without routine authorization packets for local/sandbox engineering.

`ARCHITECTURE.md` and parts of `README.md` still describe a universal requirement for operator-authorized artifact chains before any computation. That contradiction blocks production convergence and confuses agents/operators.

## Decision

1. `core/governance/activation_policy.py` is the single runtime authority for activation-lane evaluation.
2. Lane matrix matches the Production Convergence program target (no auth packet for LOCAL_DEV/SANDBOX; operator gate for EXTERNAL_PRODUCTION).
3. Hard boundaries remain enforced in code: canon mutation, SHADOW→FORECAST escalation, unbounded credentials, irreversible mutation without rollback, fabricated evidence, public production deploy without operator approval.
4. Historical `production activation = DENIED` receipts remain valid for their evidence package/date; they do not override lane policy for routine engineering.
5. Empty authorization receipts must not be generated to simulate approval.

## Consequences

- Documentation must be reconciled to cite activation lanes rather than blanket artifact-chain blocking.
- `production_activation_authority_gate` remains fail-closed for EXTERNAL_PRODUCTION and is not a local-dev blocker.
- Later phases may wire activation checks into CLI/API startup without reintroducing ceremony packets.
