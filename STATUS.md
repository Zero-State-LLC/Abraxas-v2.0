# ABRAXAS Repository Status

> **Last Updated:** 2026-06-11

This document provides a high-level operational status of the Abraxas v2.0 repository. It is intended to be human- and agent-readable.

## Current Overall State

| Area                    | Status          | Last Major Change                              | Notes |
|-------------------------|-----------------|------------------------------------------------|-------|
| CI/CD Stability         | Excellent       | Reusable workflows + cleanup of all temp flags | Very clean and efficient |
| Governance              | Strong          | PR/Issue templates + CODEOWNERS                | Good foundation in place |
| Automation & Tooling    | Excellent       | organize_scripts.py + completions + benchmarks | Strong tooling + performance testing |
| Security Posture        | Strong          | CodeQL + Dependency Review blocking            | Proper gates |
| Documentation           | Excellent       | Post-P95 sync/hold status alignment            | Advisory-only status is explicit |
| Release Process         | Excellent       | Full semantic-release with release.config.js   | Fully automated |

## Current Governance Boundary

The current repo-visible continuation state is advisory-only. Repo/Notion sync artifacts have been refreshed, but they do not authorize live Notion writeback, GitHub writeback automation, auto-continuation, runtime mutation, scheduler mutation, canon mutation, activation, or execution.

`Global Ingest Adapter Spine` has advanced to additive Oracle Signal shadow intake evidence and a review-only operator decision record. Oracle Signal implementation, ingest runner mutation, queue mutation, route/runtime integration, and execution authority remain blocked until a separate future governed lane explicitly authorizes more.

Current Oracle Signal shadow review evidence:
- `out/oracle/oracle_signal_intake_receipt.latest.json` is advisory-only and not valid for execution.
- `out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json` requested governed review of the shadow receipt.
- `out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json` approves review-only completion and keeps downstream `NOT_COMPUTABLE`.

The operator authorization record chain is present through the P95 seal review. `out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json` is held for operator review and keeps approval, authorization, token minting, record creation, and execution authority false.

Artifact-lineage direct repair has operator approval to author a separate governed execution specification at `out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json`. Direct registry repair, output-pairing repair, docs-reference repair, runner casing policy override, Notion mapping completeness, and execution authority remain blocked.

## Known Temporary Measures

All major temporary `continue-on-error` flags have been removed.

## Recent Major Improvements (June 2026)

- Refreshed repo/Notion advisory sync artifacts after the P95 authorization seal review merge
- Added/merged P81-P95 operator authorization record planning and seal-review surfaces, all advisory-only and held for operator
- Added release.config.js for semantic-release customization
- Integrated semantic-release for fully automated releases
- Reusable workflows and organize_scripts.py enhancements
- All temporary stabilization flags cleaned up
- CI and documentation improvements

## Current CI Health Summary

All major workflows are clean, efficient, and properly gated.

## Governance & Process

- Strong tooling ecosystem
- Fully automated semantic release process
- Excellent documentation navigation

## How Releases Work Now

Pushes to `main` following Conventional Commits will automatically:
- Analyze commits and determine next version
- Update CHANGELOG.md
- Commit the changelog back to the repository
- Create Git tag and GitHub Release

## How to Update This File

Update when major changes occur.
