# Sigil-Forge pinned fixture

Lets the Sigil-Forge contract tests in `tests/test_sigil_forge_mount.py` run on any
machine, with no Sigil-Forge checkout.

| field | value |
|---|---|
| source repo | https://github.com/Zero-State-LLC/Sigil-Forge |
| source commit | `aeb328950c1aee21e035d1e48a076bd333490955` (2026-10-09, "fix: drop unused xml.etree import (#13)") |
| source version | 0.13.1 (`VERSION`) |
| source file exercised | `scripts/forge_core.py` (`compute_forge`, `ForgeConfig(mode="creative", spare_mode="letter_monogram")`) |
| recorded on | 2026-10-10 |
| fixture version | `SigilForgePinnedOutputs.v1` |
| license of source | Zero State Proprietary License 1.0 (`LicenseRef-Zero-State-Proprietary-1.0`) |

## What is here

- `forge_core_outputs.v1.json`: the outputs the real `compute_forge` returned at the
  pinned commit for each fixture intent (digest, Spare letters, square name and order).
- `scripts/forge_core.py`: an Abraxas-authored replay with the same call surface the
  bridge uses. It returns only recorded outputs and raises `LookupError` for any other
  intent or config, so a test cannot pass on invented primitives.
- `regenerate.py`: rebuilds the JSON from a checkout.

No Sigil-Forge source code is copied. The ZSPL-1.0 licence forbids copying the
software without Zero State's written permission, so the fixture holds outputs only.

## What it does not cover

The replay has no `commitment` or `artifact_root`, so Proof-of-Intent stays
`skipped` under it. `sigil_root` uses a per-run nonce and is never stable, so it is
not recorded. Both are covered by the live tests.

## Test lanes

- Contract (always runs): `pytest tests/test_sigil_forge_mount.py -m "not sigil_forge_live"`
- Live (real checkout): `SIGIL_FORGE_HOME=/path/to/Sigil-Forge pytest -m sigil_forge_live tests/test_sigil_forge_mount.py`.
  With no checkout these tests are SKIPPED.
- Required lane (release or integration): add `ABRAXAS_REQUIRE_SIGIL_FORGE=1`.
  A missing checkout is then an error, not a skip.

`test_live_forge_matches_pinned_outputs` fails when the live engine drifts from this pin.

## Updating the pin

```sh
git -C "$SIGIL_FORGE_HOME" fetch && git -C "$SIGIL_FORGE_HOME" checkout <new-sha>
python tests/fixtures/sigil_forge_pinned/regenerate.py "$SIGIL_FORGE_HOME"
SIGIL_FORGE_HOME="$SIGIL_FORGE_HOME" ABRAXAS_REQUIRE_SIGIL_FORGE=1 \
  python -m pytest -o addopts="" tests/test_sigil_forge_mount.py
```

Then update the commit, version and date in the table above. The script refuses a
checkout whose `scripts/` has local changes. Commit the JSON and this file together.
If the digest or `primitives_len` changes, the frozen identity in
`skills/abx-esoteric-intelligence/fixtures/specialist_features.calm_focus.v1.jsonl`
has changed too. That needs an owner decision, not just a re-pin.
