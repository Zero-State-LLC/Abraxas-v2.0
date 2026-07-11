# NOCTIS Dream Implementation / Run Receipt (excerpt)

Use full template from abraxas-validation-routing appendix + the exact receipt format in the directive.

Key fields for this surface:
- DREAM_SURFACES_FOUND (PRESENT_AND_CURRENT | MISSING | ...)
- PIPELINE_CONTRACT_STATUS
- RUNE_REGISTRY_STATUS (via runes-yggdrasil-manager)
- AUTHORITY_SCAN_RESULT
- PRIVACY_BOUNDARY_RESULT
- MEMORY_BOUNDARY_RESULT
- FORECAST_BOUNDARY_RESULT
- DIRECT_DREAM_RUN_RESULT (on synthetic)
- DETERMINISM_RESULT

Always report:
COMPLETION_STATUS: PASS_WITH_FULL_SUITE_BASELINE_BLOCKER | INCOMPLETE_VALIDATION | NOT_COMPUTABLE
```