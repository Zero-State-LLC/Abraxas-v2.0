# Abraxas authored skills — supported installation and verification

## Canonical source and scope
These are repository-local skills from scrimshawlife-ctrl/Abraxas-v2.0, not
standalone installed packages. Use a full checkout pinned to a reviewed commit;
record `git rev-parse HEAD` in every handoff. The Python wheel excludes skills
and repository runners. Copying a single skill directory is unsupported for
checkout-dependent routes. Personal, organizational and legacy NeonGenie/Jamon
copies are not interchangeable. Select one canonical source per trigger. Compare
commits and preserve operator files before any separately approved migration;
never silently install or overwrite a different Hermes profile.

## Bootstrap (operator-selected checkout, not an install into Hermes)
Set ABRAXAS_ROOT to the absolute reviewed full checkout and ABRAXAS_OUTPUT to a
new caller-owned output directory outside installed skills. Then in Bash:
```bash
set -euo pipefail
: "${ABRAXAS_ROOT:?Set the reviewed checkout path}"
: "${ABRAXAS_OUTPUT:?Set a new caller-owned output directory}"
cd "$ABRAXAS_ROOT"
test -f pyproject.toml && test -d core && test -d contracts && test -d skills
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev,holler]'
mkdir -p "$ABRAXAS_OUTPUT"
git rev-parse HEAD
```
Python 3.12+ is required. Holler extras are requests + requests-cache; jsonschema
is a core dependency. No rtk or NumPy is needed for these repaired recipes.
Package installation may require network/package authorization; runtime smoke
tests below are offline. Resolve skill paths from this checkout, not an assumed
HERMES_SKILL_DIR shell export. Never run an installer as part of validation.

## Optional/unshipped sibling skills
abx-runes-yggdrasil-manager, abraxas-validation-routing, abraxas-ingest and
abraxas-automated-production-governance are not shipped here and have no verified
installation source in this checkout. Names in related_skills are recommendations,
not evidence of availability. Do not invent a skill or its installation URL.
For missing rune/registry/governance operations: STOP with BLOCKED_DEPENDENCY and
request the operator's approved source/version. Local pure advisory functions
and synthetic fixture tests need no registration and may run without those
siblings. Use local contracts and targeted pytest directly for validation;
manual source acquisition may produce an unpromoted EvidencePack. Never treat
these fallbacks as equivalent to missing external ingestion or governance.
This dependency rule applies to conditional sibling calls in every entrypoint.

## Evidence and verification
Run exact targeted tests without shell pipelines that hide exit codes:
```bash
python -m pytest -c /dev/null -p no:cacheprovider skills/tests -q
```
This isolated authored-skill suite is the scope-specific equivalent for these
repairs, not certification of repository CI or production. Report current
collection failures, not a historical blocker count. No empty glob, JSON parse,
old receipt, process launch, or syntax check establishes behavioral success.
For emitted packets, use exact expected paths in the fresh output directory:
```bash
python skills/verify_artifact.py --schema contracts/noctis/dream_operator_packet.v0.schema.json --member operator_packet "$ABRAXAS_OUTPUT/noctis.json"
```
The validator rejects missing files, invalid schema and non-false authority
locks. It does not attest source truth, model quality, completeness, freshness or
human identity. Check packet-specific privacy, lineage, hashes and semantics with
the associated tests too. For multiple outputs, enumerate every required file
and compare actual counts programmatically. Never claim OBSERVED from a fixture;
label fixture packets SYNTHETIC and keep them separate from live receipts.
No live service, deployment, cron, wagering, promotion or external writes are
part of the supported verification procedure.
