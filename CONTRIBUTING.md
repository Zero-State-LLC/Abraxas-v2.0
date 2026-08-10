# CONTRIBUTING TO ABRAXAS v2.0

> **License:** This repository is **proprietary**. Contributions are accepted only under the terms of [`LICENSE`](LICENSE) (assignment / exclusive license to Applied Alchemy Labs). Do not submit third-party open-source code under conflicting terms.


## Before you touch anything

**Required reading (in order):**

1. `README.md` — version posture and canonical state
2. `AGENTS.md` — operator doctrine and governance boundaries
3. `PLANS.md` — current canonical roadmap and P-lane edge
4. `ARCHITECTURE.md` — how the layers fit together
5. `QUICKSTART.md` — safe demo path and first commands
6. `docs/GLOSSARY.md` — translation of project-specific terms

Do not modify code until you have read all five documents above.


## Collaboration (GitHub Project)

Shared work is tracked on the **Abraxas v2.0** project board:

- Board: https://github.com/users/scrimshawlife-ctrl/projects/5
- Repo: https://github.com/scrimshawlife-ctrl/Abraxas-v2.0
- Preferred flow: **issue → branch → PR → board Status** (`Todo` → `In Progress` → `Done`)
- Collaborators need **Write** on the repo (accept invite) and **Writer** on the project

### Labels

| Label | Use |
|-------|-----|
| `collab` | Multi-person / coordination work |
| `track/rdi` | Representation-driven instantiation / Fable |
| `track/ai-os` | AI OS / Hermes SHADOW kernel |
| `track/docs` | Documentation-only |
| `needs-review` | Ready for peer look |
| `good-first-collab` | Safe starter task |

### Rules of engagement

1. Read `AGENTS.md`, `PLANS.md`, and `STATUS.md` before coding.
2. Open a PR against `main` (required status: `validate-commits`, `fast-ci`).
3. Keep SHADOW / advisory boundaries — no EXTERNAL_PRODUCTION without operator grant.
4. Link PRs to issues (`Fixes #NNNN` / `Refs #NNNN`) so they appear on the board.
5. Proprietary license: see `LICENSE` — contributions assign to Applied Alchemy Labs.


---

## Choosing your work type

### Type 1 — Bug fix or test fix

A failing test, a broken runner, a hash mismatch, or a schema violation.

**Safe starting point:**

```bash
env -u PYTHONPATH -u PYTHONHOME python -m pytest tests/test_<affected_module>.py -q
env -u PYTHONPATH -u PYTHONHOME python -m ruff check core/<affected_module>.py
```

Legacy mixed-case `Scripts.*` imports are still accepted for compatibility on
mixed-device workflows, but new code should prefer lowercase `scripts.*`.

**Rules:**
- Fix only the specific failing surface.
- Do not regenerate unrelated `out/` artifacts.
- Do not touch `out/research_canary_*` or `out/research_*/`.
- Re-run the doctrine validator after your fix:
  ```bash
  python scripts/governance/run_doctrine_validator.py
  ```

---

### Type 2 — Documentation-only patch

Updating `README.md`, `PLANS.md`, `AGENTS.md`, `ARCHITECTURE.md`,
`QUICKSTART.md`, `CONTRIBUTING.md`, or `docs/GLOSSARY.md`.

**Rules:**
- No `out/` artifacts regenerated.
- No `core/` or `scripts/` logic changed.
- No authority flags modified.
- Run doctrine validator to confirm nothing broke:
  ```bash
  python scripts/governance/run_doctrine_validator.py
  ```
- Confirm research-canary artifacts untouched:
  ```bash
  git diff HEAD -- out/research_canary*
  ```

---

### Type 3 — New metric operator (artifact-chain continuation)

Adding the next step in the TRANSPORT, GEODESIC, CHAMFER, or WASSERSTEIN
chain — or starting a new operator from scratch.

**Required before starting:**
- Read `out/canon_resume_state/latest.json` for the current resume pointer.
- Read the most recent artifact in the chain you are extending.
- Confirm gate hashes in your new artifact match the prior artifact's
  `canonical_hash`.

**Pattern to follow:**

Every artifact-chain step has the same four files:

```
contracts/canon/<name>.v1.schema.json     ← JSON Schema
core/<name>.py                            ← builder + validator
scripts/run_<name>.py                     ← runner (writes to out/)
tests/test_<name>.py                      ← tests (replay-stable)
```

Plus two config changes:
- `core/config.py` — add `@property` for the new output path
- `.gitignore` — add `!out/metric_operator/<name>.latest.json` exception

**Source hash binding:** Your new artifact must read the prior artifact from
disk and verify its `canonical_hash`. Hard-code the expected hash as a
constant at the top of your `core/<name>.py`. If the hash does not match at
runtime, raise immediately.

**Authority locks:** New steps inherit the locks of the prior step and may
unlock only what the prior gate explicitly authorizes. Do not add new
`true` locks that were not authorized upstream.

**Forbidden tokens:** The following substrings must not appear in any string
value in the artifact (enforced by `_check_no_forbidden`):
`executable`, `callable`, `runtime`, `scheduler`, `cache`, `forecast`,
`scoring`, `metric-computation`, `metric-value`, `geodesic-distance`,
`numpy`, `scipy`, `gpu-kernel`, `dijkstra-execution`,
`shortest-path-computation`, `fixture-file`, `manifest-file`, `schema-file`.

Note: `generated_by` values use underscores, never hyphens (e.g.
`TRANSPORT_FIXTURE_CORPUS_CREATION_PLAN_BUILDER`, not
`TRANSPORT-FIXTURE-CORPUS-CREATION-PLAN-BUILDER`).

---

### Type 4 — Schema or contract change

Modifying a `contracts/canon/*.v1.schema.json` or adding a new schema.

**Rules:**
- Schema changes are breaking changes. If the schema changes, every artifact
  produced under the old schema must be re-validated or re-emitted.
- Create a new schema version (`*.v2.schema.json`) rather than mutating an
  existing sealed schema.
- Run the full test suite after any schema change:
  ```bash
  python -m pytest tests/ -q
  ```

---

## Hard stops — do not start without operator instruction

These actions require an explicit operator decision artifact before proceeding:
- **Spine refresh** (`run_temporal_continuity_spine_precheck.py` or anything
  downstream in that chain) — must not be triggered autonomously.
- **Research-canary artifacts** — `out/research_canary_*` and
  `out/research_*/` are a sealed boundary. Any modification requires a
  separate operator-authorized governance design.
- **FORECAST lane activation** — blocked. No artifact currently authorizes it.
- **Production activation** — blocked. `production_activation: false` on every
  artifact.
- **Canon promotion** — blocked. `canon_promotion: false` on every artifact.
- **P43 surface lanes** — blocked. `p43_surface_lanes_authorized: false`.
- **Any `run_research_canary_*.py` script** — do not run without explicit
  instruction. These scripts touch the research-canary guardrail boundary.

---

## Validation checklist before opening a PR

```bash
# 1. Run targeted tests for your touched surface
python -m pytest tests/test_<your_module>.py -q

# 2. Lint check
python -m ruff check core/<your_module>.py scripts/run_<your_module>.py tests/test_<your_module>.py

# 3. Doctrine validator
python scripts/governance/run_doctrine_validator.py

# 4. Confirm research-canary untouched
git diff HEAD -- out/research_canary*

# 5. Confirm no unintended out/ changes
git diff HEAD -- out/
```

All five must pass cleanly before a PR is opened.

---

## PR conventions

- **Branch name**: `<artifact-id>-<sequence>` (e.g.
  `transport-fixture-corpus-creation-plan-001`)
- **PR title**: `<ARTIFACT_ID_UPPERCASE>` (e.g.
  `TRANSPORT_FIXTURE_CORPUS_CREATION_PLAN_001`)
- **Squash merge** only — no merge commits.
- **Commit message** must include `canonical_hash=<64-char-hex>` for any
  artifact emitted.

---

## Commit Message Standards (Conventional Commits)

Abraxas uses **Conventional Commits** to enable clear history, reliable automation, and alignment with Semantic Versioning.

All commit messages **must** follow this format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Allowed Types

| Type     | Meaning                                      | Version Impact          |
|----------|----------------------------------------------|-------------------------|
| `feat`   | New feature or additive capability           | Minor (usually)         |
| `fix`    | Bug fix                                      | Patch                   |
| `docs`   | Documentation only                           | Patch                   |
| `refactor` | Code change that neither fixes a bug nor adds a feature | Patch / Minor     |
| `perf`   | Performance improvement                      | Patch / Minor           |
| `test`   | Adding or correcting tests                   | Patch                   |
| `chore`  | Maintenance, tooling, config                 | Patch                   |
| `ci`     | CI configuration changes                     | Patch                   |
| `revert` | Revert a previous commit                     | Varies                  |

**Breaking changes** must include `BREAKING CHANGE:` in the footer (or `!` after the type, e.g. `feat!: ...`).

### Examples

```bash
feat(cli): add new evidence packet operator for optimization surfaces

fix(governance): correct stabilization window calculation in P102G handoff

chore: update version badge and COMPATIBILITY.md

feat(optimization)!: change Optuna backend public interface

BREAKING CHANGE: The optimization module now requires explicit provenance tagging on all runs.
```

### Enforcement

- All PRs are validated by the `Conventional Commits` GitHub Action.
- Non-conforming commits will block the PR.
- See `.commitlintrc.json` for the exact rules.

### Related Documents

- `COMPATIBILITY.md` — defines what constitutes a breaking change to the public surface
- `CHANGELOG.md` — structured release history (follows Keep a Changelog + SemVer)
- `README.md` — current version and high-level policy

---

## Script Organization & Tooling

Runner scripts (`run_*.py`) live under **domain packages**. Organization is **complete**
(`python scripts/organize_scripts.py status` → `complete: true`). Full map: [`scripts/README.md`](scripts/README.md).

| Directory       | Purpose                                      | Example Scripts                     |
|-----------------|----------------------------------------------|-------------------------------------|
| `temporal/`     | Temporal continuity, lineage, state, spine   | `run_temporal_*.py`                 |
| `governance/`   | Promotion, receipts, authorization, policy   | `run_governance_*.py`, `run_review_*` |
| `research/`     | Research canaries, shadow work, diagnostics  | `run_research_*.py`, `run_research_canary_*.py` |
| `artifact/`     | Artifact regeneration, inventory, lineage    | `run_artifact_*.py`                 |
| `ingest/`       | Oracle intake, global ingest, handoff        | `run_ingest_*.py`, `run_oracle_*.py`|
| `metric/`       | Metric operators, ranking, registry          | `run_metric_*.py`, `run_rank*.py`   |
| `operator/`     | Operator consoles, review queue, narrative   | `run_operator_*.py` (no `__init__.py`) |
| `viz/`          | AAL-Viz, overlays, projection builders       | `run_aal_viz_*.py`, `build_aal_viz_*.py` |
| `transport/`    | Transport, Wasserstein                       | `run_transport_*.py`, `run_wasserstein_*.py` |
| `hygiene/`      | v2 hygiene gates                             | `run_v2_hygiene_*.py`               |

Cross-platform note: some hygiene validators pin raw-byte `file_hash` values on sealed source records. On Windows CRLF checkouts, use the documented LF-normalization acceptance path rather than regenerating `out/operator_review/*`. See [`docs/workflows/source-hash-line-ending-portability.md`](docs/workflows/source-hash-line-ending-portability.md).
| `codegen/`      | ABX codegen / grok / hermes spine            | `run_abx_*.py`                      |
| `geometry/`     | Chamfer / geodesic / heavy-tail              | `run_chamfer_*.py`                  |
| `readiness/`    | Production readiness / sole-writer           | `run_sole_*.py`, `run_production_*` |
| `runtime/`      | Runtime inventory / state                    | `run_runtime_*.py`                  |
| `notion/`       | Notion sync                                  | `run_notion_*.py`                   |
| `belief/`       | Belief graph / Brier                         | `run_belief_*.py`, `run_brier_*`    |
| `campaign/`     | Campaign / external action                   | `run_campaign_*.py`                 |
| `preflight/`    | Operator preflight payloads                  | `preflight_*.py`                    |
| `tools/`        | Optional non-runner tooling                  | `demo_safe_status.py`               |
| `common/`       | Shared utilities                             | (existing)                          |

**Root keepers:** only `scripts/run_fast_ci.py` among `run_*`. Do not add new `scripts/run_*.py` at root—place under a domain (and extend `PREFIX_MAP` in `organize_scripts.py` if needed).

### Using the Organizer Tool

```bash
# Layout status (expect complete: true)
python scripts/organize_scripts.py status

# Preview what would be moved (always safe)
python scripts/organize_scripts.py dry-run

# Actually perform the moves (feature branch only)
python scripts/organize_scripts.py execute

# With structured logging to a file (ELK / Filebeat ready)
python scripts/organize_scripts.py execute --log-file logs/organization.jsonl
```

The tool outputs structured JSON (both logs and final summary) and supports `--log-file` for JSON Lines output, making it easy to ship to ELK stacks via Filebeat/Logstash.

### Recommended Git Workflow

**Never reorganize directly on `main`.** Always use a dedicated branch:

```bash
git checkout -b chore/script-organization

git organize          # Dry-run (recommended first)
git organize-run      # Execute moves

git add -A
git commit -m "chore(scripts): reorganize runner scripts into logical subdirectories"
git push origin chore/script-organization
# Open PR for review
```

**Git aliases** (add to your `~/.gitconfig` or repo config):

```ini
[alias]
    organize = "!python scripts/organize_scripts.py --dry-run"
    organize-run = "!python scripts/organize_scripts.py --execute"
```

This makes the tool feel native:

```bash
git organize
git organize-run
```

### Commit Message Convention for Reorganization

Use Conventional Commits with clear scope:

```bash
chore(scripts): reorganize runner scripts into logical subdirectories

- Moved 312 scripts across 9 domain directories
- Added organize_scripts.py automation tool
- Added structured JSON logging + ELK integration
- Updated CONTRIBUTING.md
```

---

## Asking for help

If the current state is ambiguous, run the safe status demo first:

```bash
python scripts/tools/demo_safe_status.py
```

Then read `out/canon_resume_state/latest.json` for the current resume pointer.
Both are read-only and will not modify any artifacts.
