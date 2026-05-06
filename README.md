# ABRAXAS v2.0.1

Deterministic governed symbolic execution substrate.

Core principles:
- governance first
- replayability
- deterministic execution
- fail-closed authority
- projection-only visualization
- shadow-only execution

Current milestone:
v2.0.1-rune-layer

## v2.0.4 Governed State Engine

- Governed state engine overview with deterministic, authority-locked state snapshots.
- Deterministic state reduction via ordered transition hashing.
- Stabilization windows driven by replay match/failure counts.
- State lineage semantics with cycle detection and fail-closed behavior.
- Replay-safe state evolution through replay packet validation and rollback gating.
- Rollback doctrine encoded as deterministic rollback packets.
- Operator-reviewed state transitions with explicit pending actions and rollback visibility.
