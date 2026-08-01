# SHADOW signal forage — cron / operator template

**Lane:** SHADOW · `execution_authority: false`  
**Skill:** `abx-familiar-signal-forager`  
**Runner:** `scripts/research/run_shadow_signal_forage_template.py`  
**OS doc:** `docs/architecture/ABRAXAS_HERMES_OS_UNIFICATION_001.md`

## Intent

Recurring **evidence acquisition** without production activation. Cron may:

1. Emit a stub pack (no network) as a heartbeat placeholder, **or**
2. Remind / dispatch Hermes to run a live forage into `out/signal_forage/`, **or**
3. Validate the latest pack and surface failures only

Never set `signal_forage_execution_authorized: true` historical gates from this template.

## Directory layout

```text
out/signal_forage/<YYYY-MM-DD>_<slug>/
  evidence_pack.v0.json
  evidence_brief.md
```

## Local template commands

```bash
cd /home/scrimshawlife/Abraxas-v2.0

# Stub (no network) — useful for path/CI smoke
env -u PYTHONPATH -u PYTHONHOME python \
  scripts/research/run_shadow_signal_forage_template.py \
  --emit-stub --topic "weekly-agent-os-scan" --intent tech

# Validate a pack
env -u PYTHONPATH -u PYTHONHOME python \
  scripts/research/run_shadow_signal_forage_template.py \
  --validate out/signal_forage/2026-07-27_hermes-agent-skill-os-patterns/evidence_pack.v0.json
```

## Hermes live forage (preferred)

In a Hermes session with Abraxas `skills.external_dirs` mounted:

1. `skill_view(abx-familiar-signal-forager)`
2. Frame `must_answer` for the week's topic
3. Rotate sources (web / arxiv / repo); write EvidencePack.v0
4. Optional Neon Genie:

```python
from skills.abx_neon_genie...  # or direct path load
# request:
{
  "mode": "TREND_LED",
  "seed": "<topic>",
  "evidence_pack_path": "out/signal_forage/<slug>/evidence_pack.v0.json",
  "require_evidence": true
}
```

## Hermes cronjob sketch (operator-created)

Create only with operator approval (`cronjob` tool or `hermes cron`):

| Field | Value |
|-------|--------|
| name | `abx-shadow-signal-forage-weekly` |
| schedule | `0 16 * * 1` (Mondays 09:00 America/Los_Angeles ≈ 16:00 UTC) |
| deliver | `origin` or `local` |
| skills | `["abx-familiar-signal-forager"]` |
| enabled_toolsets | `["web", "terminal", "file"]` |
| workdir | `/home/scrimshawlife/Abraxas-v2.0` |
| no_agent | `false` for live forage; `true` only with `--emit-stub` script |

### Prompt body (self-contained)

```text
SHADOW only. Load abx-familiar-signal-forager.
Topic: weekly scan of Hermes Agent skill/OS public docs + one arxiv agent-skills paper.
must_answer:
  1) Any new official Hermes skills.external_dirs or evolution docs?
  2) One new OBSERVED research claim on agent-skill governance?
Write EvidencePack.v0 under out/signal_forage/<utc_date>_weekly-agent-os-scan/.
Validate with:
  python scripts/research/run_shadow_signal_forage_template.py --validate <pack>
Do not claim market TAM. execution_authority=false. Do not open PRs or push.
Reply with pack path + register_counts only.
```

### Script-only heartbeat (no LLM)

```bash
# no_agent=true pattern
python scripts/research/run_shadow_signal_forage_template.py \
  --emit-stub --topic weekly-agent-os-scan --intent tech
# empty stdout optional; template always prints path — wrap if silence desired
```

## Neon Genie hand-off

After a real pack exists:

```bash
env -u PYTHONPATH -u PYTHONHOME python - <<'PY'
import json, sys
sys.path.insert(0, "skills/abx-neon-genie")
import neon_genie_router as r
receipt = r.run_venture_cycle({
    "mode": "TREND_LED",
    "seed": "governed skill OS",
    "evidence_pack_path": "out/signal_forage/2026-07-27_hermes-agent-skill-os-patterns/evidence_pack.v0.json",
})
print(receipt["evidence_status"], receipt.get("evidence_density"), receipt["commercial_claims_blocked"])
PY
```

## Guardrails

- No EXTERNAL_PRODUCTION
- No CLEAR deletion
- No sealed canary spine regeneration
- Commercial claims stay NOT_COMPUTABLE without OBSERVED density
- Operator approves any cron that posts externally or spends paid API budget beyond normal search
