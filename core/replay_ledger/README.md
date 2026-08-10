# ReplayLedger.v1 + ReplayTemporalDiff.v1 Canonical Layer

Deterministic, immutable replay history and temporal diff contracts for continuity and divergence diagnostics.

This layer is non-executing and non-mutating: no live execution, mutation authorization, routing changes, adapter activation, global runtime activation, or subsystem rewiring.

Future convergence: this canonical replay ledger/diff layer coexists with existing replay history modules until interfaces converge.

Converged: validation findings/reports use the shared `core.contract_validation` shape (`ContractValidationFinding` / `ContractValidationReport`), with receipt hashes unchanged (golden-tested in `tests/test_contract_validation_convergence.py`).
