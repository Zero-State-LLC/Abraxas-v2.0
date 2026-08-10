# ReplayExecutionEnvelope.v1 Canonical Layer

Deterministic, immutable replay/simulation envelope contract for sandboxed execution intent checks.

This layer does not execute live changes, mutate, route, activate adapters, globally activate runtime, or rewire subsystems.

Future convergence: this canonical replay layer coexists with existing replay/execution modules until interfaces converge.

Converged: validation findings/reports use the shared `core.contract_validation` shape (`ContractValidationFinding` / `ContractValidationReport`), with receipt hashes unchanged (golden-tested in `tests/test_contract_validation_convergence.py`).
