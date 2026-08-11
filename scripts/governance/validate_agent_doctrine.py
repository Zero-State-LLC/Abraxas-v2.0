"""Validate Abraxas agent doctrine and skill routing surfaces.

Lightweight deterministic checks only. This is not a governance engine.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "SKILLS.md"
AGENTS = ROOT / "AGENTS.md"
MASTER = ROOT / "skills" / "abraxas-master-loop-workflow" / "SKILL.md"

VALID_STATUSES = {
    "ACTIVE",
    "SPECIALIZED",
    "SUPERSEDED",
    "LEGACY",
    "CANDIDATE_FOR_MERGE",
}
REQUIRED_AGENTS_REFS = [
    "GOVERNANCE_V3.md",
    "SKILLS.md",
    "ARCHITECTURE.md",
    "docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md",
    "core/operator_loop.py",
    "contracts/engineering/work_packet.v1.schema.json",
    "contracts/engineering/handoff_envelope.v1.schema.json",
]
REQUIRED_SKILLS_AUTHORITY = [
    "A skill may specialize execution",
    "may not override `AGENTS.md`",
    "grant itself production/canon/runtime authority",
]
PROHIBITED_CURRENT_TERMS = [
    r"Governance V2",
    r"Never just respond",
    r"all non-trivial Abraxas work",
    r"any non-trivial Abraxas work",
    r"Brier ≥",
]
AUTHORITY_CONFLICT_PATTERNS = [
    r"may override AGENTS\.md",
    r"can override AGENTS\.md",
    r"grants? (production|canon|runtime|execution) authority",
    r"producer identity grants authority",
]
LINK_TARGET_FILES = [
    AGENTS,
    SKILLS,
    MASTER,
    ROOT / "skills" / "abraxas-jamon-agentic-workflow" / "SKILL.md",
    ROOT / "docs" / "CODEX_CUSTOM_INSTRUCTIONS.md",
    ROOT / ".cursor" / "rules" / "operator-loop-ownership.mdc",
    ROOT / "docs" / "architecture" / "ABRAXAS_HERMES_OS_UNIFICATION_001.md",
    ROOT / "docs" / "status" / "HISTORICAL_GOVERNANCE_AGENT_NOTES.md",
    ROOT / "docs" / "adr" / "ADR-0019-AGENT-DOCTRINE-SKILL-ROUTING.md",
]


@dataclass(frozen=True)
class SkillRow:
    name: str
    path: str
    status: str
    default: str
    trigger: str
    purpose: str


def _strip_code(value: str) -> str:
    return value.strip().strip("`").strip()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_skill_registry(text: str) -> list[SkillRow]:
    rows: list[SkillRow] = []
    in_registry = False
    for line in text.splitlines():
        if line.strip() == "## Skill registry":
            in_registry = True
            continue
        if in_registry and line.startswith("## "):
            break
        if not in_registry or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 11 or cells[0] in {"Name", "---"} or set(cells[0]) == {"-"}:
            continue
        rows.append(
            SkillRow(
                name=_strip_code(cells[0]),
                path=_strip_code(cells[1]),
                status=_strip_code(cells[2]),
                default=_strip_code(cells[3]).lower(),
                trigger=cells[4],
                purpose=cells[5],
            )
        )
    return rows


def check_registry() -> list[str]:
    errors: list[str] = []
    text = _read(SKILLS)
    rows = parse_skill_registry(text)
    if not rows:
        return ["SKILLS.md registry parsed zero skill rows"]

    names = [row.name for row in rows]
    if len(names) != len(set(names)):
        errors.append("SKILLS.md contains duplicate skill names")

    default_true = [row.name for row in rows if row.default == "true"]
    if default_true:
        errors.append(
            f"No skill may be universal default; found default=true: {default_true}"
        )

    for row in rows:
        if row.status not in VALID_STATUSES:
            errors.append(f"{row.name} has invalid status {row.status!r}")
        target = ROOT / row.path
        if (
            row.status in {"ACTIVE", "SPECIALIZED", "CANDIDATE_FOR_MERGE"}
            and not target.is_file()
        ):
            errors.append(
                f"{row.name} points to missing active/specialized skill path {row.path}"
            )
        if row.path.endswith("SKILL.md") and not target.is_file():
            errors.append(f"{row.name} references missing SKILL.md path {row.path}")
    return errors


def check_required_references() -> list[str]:
    errors: list[str] = []
    agents = _read(AGENTS)
    skills = _read(SKILLS)
    for ref in REQUIRED_AGENTS_REFS:
        if ref not in agents:
            errors.append(f"AGENTS.md missing required reference {ref}")
    for phrase in REQUIRED_SKILLS_AUTHORITY:
        if phrase not in skills:
            errors.append(f"SKILLS.md missing authority statement phrase: {phrase}")
    if "MSW execution kernel" not in agents:
        errors.append("AGENTS.md missing MSW execution kernel")
    if "MASTER_LOOP" not in agents:
        errors.append("AGENTS.md missing MASTER_LOOP routing row")
    return errors


def _skill_files() -> Iterable[Path]:
    yield from sorted((ROOT / "skills").glob("*/SKILL.md"))
    yield from sorted((ROOT / "skills").glob("*/*/SKILL.md"))


def check_authority_conflicts() -> list[str]:
    errors: list[str] = []
    current_files = [
        AGENTS,
        SKILLS,
        MASTER,
        ROOT / "skills" / "abraxas-jamon-agentic-workflow" / "SKILL.md",
    ]
    for path in current_files:
        text = _read(path)
        for pattern in PROHIBITED_CURRENT_TERMS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                errors.append(
                    f"{path.relative_to(ROOT)} contains prohibited current doctrine term: {pattern}"
                )

    for path in _skill_files():
        text = _read(path)
        for pattern in AUTHORITY_CONFLICT_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                errors.append(
                    f"{path.relative_to(ROOT)} contains authority conflict pattern: {pattern}"
                )

    master = _read(MASTER)
    if "Not the default for bounded engineering" not in master:
        errors.append(
            "master-loop skill must state it is not default for bounded engineering"
        )
    if "SPECIALIZED" not in master or "default: false" not in master:
        errors.append("master-loop skill must carry SPECIALIZED/default:false metadata")
    return errors


def _markdown_links(text: str) -> Iterable[str]:
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for match in pattern.finditer(text):
        target = match.group(1).strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        yield target


def check_markdown_links() -> list[str]:
    errors: list[str] = []
    for path in LINK_TARGET_FILES:
        if not path.exists():
            errors.append(f"link-check file missing: {path.relative_to(ROOT)}")
            continue
        text = _read(path)
        for raw in _markdown_links(text):
            target = raw.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)} link escapes repo: {raw}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)} broken link: {raw}")
    return errors


def validate() -> dict[str, object]:
    errors = []
    errors.extend(check_registry())
    errors.extend(check_required_references())
    errors.extend(check_authority_conflicts())
    errors.extend(check_markdown_links())
    return {
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
        "skill_count": len(parse_skill_registry(_read(SKILLS)))
        if SKILLS.exists()
        else 0,
    }


def main() -> int:
    result = validate()
    if not result["ok"]:
        for error in result["errors"]:  # type: ignore[index]
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
