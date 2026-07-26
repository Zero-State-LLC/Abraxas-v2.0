# Contributor Path

1. Follow `CONTRIBUTING.md`.
2. Run `python scripts/run_fast_ci.py` before opening a PR.
3. Keep changes advisory-safe and fail-closed.

## Cross-platform hygiene hashes

On Windows, hygiene tests that pin `source_records[].file_hash` can fail if newlines become CRLF. Prefer the validator CRLF→LF acceptance path over regenerating sealed `out/operator_review/*` artifacts.

- Runbook: [`../workflows/source-hash-line-ending-portability.md`](../workflows/source-hash-line-ending-portability.md)
- Targeted tests: `tests/test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt.py`
