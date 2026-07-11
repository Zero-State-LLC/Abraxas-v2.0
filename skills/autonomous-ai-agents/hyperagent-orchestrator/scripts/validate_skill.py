#!/usr/bin/env python3
"""Lightweight validator for a skill directory.

Checks:
- SKILL.md exists
- frontmatter starts at byte 0
- description/name present
- support file pointers exist when declared in the body
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

def _parse_frontmatter(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    current_key: str | None = None
    current_list: list[str] | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith(" ") and current_key and current_list is not None:
            item = line.strip()
            if item.startswith("-"):
                current_list.append(item[1:].strip())
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            current_list = []
            data[key] = ""
            continue
        current_list = None
        data[key] = value.strip('"\'')
    return data


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill = skill_dir / "SKILL.md"
    if not skill.exists():
        return [f"missing {skill}"]
    content = skill.read_text(encoding="utf-8")
    if not content.startswith("---"):
        errors.append("frontmatter must start at byte 0")
        return errors
    match = re.search(r"\n---\s*\n", content[3:])
    if not match:
        errors.append("missing frontmatter terminator")
        return errors
    fm_text = content[3 : 3 + match.start()]
    fm = _parse_frontmatter(fm_text)
    for key in ("name", "description"):
        if not fm.get(key):
            errors.append(f"missing frontmatter key: {key}")
    if len(fm.get("description", "")) > 1024:
        errors.append("description exceeds 1024 chars")
    if len(content) > 100_000:
        errors.append("skill exceeds 100000 chars")
    required = [
        "references/hyperagent-platform-facts.md",
        "references/hyperagent-abraxas-bridge.md",
        "references/hyperagent-role-blueprints.md",
        "templates/hyperagent-agent-config.json",
        "templates/hyperagent-skill.json",
        "assets/hyperagent-agent-config.schema.json",
        "assets/abraxas-hyperagent-mapping.yaml",
        "scripts/hyperagent_auth_helper.py",
        "scripts/hyperagent_deploy_role.py",
        "scripts/hyperagent_export_import_bridge.py",
        "scripts/validate_skill.py",
    ]
    for rel in required:
        if not (skill_dir / rel).exists():
            errors.append(f"missing support file: {rel}")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_skill.py /path/to/skill-dir", file=sys.stderr)
        return 2
    skill_dir = Path(sys.argv[1]).expanduser().resolve()
    errors = validate(skill_dir)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"OK: {skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
