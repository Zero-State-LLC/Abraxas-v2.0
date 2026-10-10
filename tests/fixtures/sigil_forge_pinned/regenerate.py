"""Regenerate forge_core_outputs.v1.json from a Sigil-Forge checkout.

Usage (from the Abraxas repo root):

    git -C "$SIGIL_FORGE_HOME" checkout <sha>
    python tests/fixtures/sigil_forge_pinned/regenerate.py "$SIGIL_FORGE_HOME"

Records what the real forge_core.compute_forge returns for each fixture
intent (letter_monogram, creative mode, as sigil_forge_bridge calls it).
Copies outputs only, never engine code.
"""

from __future__ import annotations

import datetime as _dt
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "forge_core_outputs.v1.json"
SOURCE_REPO = "Zero-State-LLC/Sigil-Forge"
DEFAULT_INTENTS = (
    "i maintain calm focus while shipping sigil-forge",
    "aeiou y",
)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    home = Path(sys.argv[1]).expanduser().resolve()
    scripts = home / "scripts"
    if not (scripts / "forge_core.py").is_file():
        print(f"no scripts/forge_core.py under {home}", file=sys.stderr)
        return 1
    sha = subprocess.check_output(
        ["git", "-C", str(home), "rev-parse", "HEAD"], text=True
    ).strip()
    dirty = subprocess.check_output(
        ["git", "-C", str(home), "status", "--porcelain", "--", "scripts"], text=True
    ).strip()
    if dirty:
        print("scripts/ has local changes; pin a clean commit", file=sys.stderr)
        return 1
    version = (home / "VERSION").read_text(encoding="utf-8").strip()
    sys.path.insert(0, str(scripts))
    import forge_core  # type: ignore

    previous = json.loads(OUT.read_text(encoding="utf-8")) if OUT.is_file() else {}
    intents = [e["normalized"] for e in previous.get("outputs", [])] or list(
        DEFAULT_INTENTS
    )
    cfg = forge_core.ForgeConfig(mode="creative", spare_mode="letter_monogram")
    outputs = []
    for normalized in intents:
        r = forge_core.compute_forge(normalized, cfg)
        outputs.append(
            {
                "normalized": normalized,
                "intent_digest": r.intent_digest,
                "spare_letters": r.spare_letters,
                "square_name": r.square_name,
                "square_order": r.square_order,
            }
        )
    doc = {
        "schema_version": "SigilForgePinnedOutputs.v1",
        "source_repo": SOURCE_REPO,
        "source_commit": sha,
        "source_version": version,
        "source_files": ["scripts/forge_core.py"],
        "license": "LicenseRef-Zero-State-Proprietary-1.0 (outputs only; no engine code copied)",
        "recorded_on": _dt.datetime.now(_dt.UTC).date().isoformat(),
        "config": {"mode": "creative", "spare_mode": "letter_monogram"},
        "outputs": outputs,
    }
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} from {SOURCE_REPO}@{sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
