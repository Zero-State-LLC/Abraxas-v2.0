from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

INDEX_FILES = [
    "docs/START_HERE.md",
    "docs/INDEX.md",
    "docs/audits/AUDIT_INDEX.md",
    "docs/audits/REPOSITORY_ORGANIZATION_INVENTORY_001.md",
    "docs/audits/DOCUMENTATION_TOPOLOGY_AUDIT_001.md",
    "docs/audits/REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md",
    "docs/releases/RELEASE_INDEX.md",
    "docs/artifacts/ARTIFACT_INDEX.md",
    "docs/testing/TEST_INDEX.md",
    "operator_input/README.md",
]

LINK_RE = re.compile(r"\]\(([^)#]+)(?:#[^)]*)?\)")


def _resolve_link(source: Path, target: str) -> Path:
    cleaned = target.strip()
    if cleaned.startswith("/"):
        return REPO_ROOT / cleaned.lstrip("/")
    return (source.parent / cleaned).resolve()


def test_repository_organization_index_files_exist() -> None:
    for rel in INDEX_FILES:
        assert (REPO_ROOT / rel).is_file(), rel


def test_repository_organization_index_internal_links_resolve() -> None:
    missing: list[str] = []
    for rel in INDEX_FILES:
        source = REPO_ROOT / rel
        text = source.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = _resolve_link(source, target)
            try:
                resolved.relative_to(REPO_ROOT.resolve())
            except ValueError:
                missing.append(f"{rel}: external-escape {target}")
                continue
            if not resolved.exists():
                missing.append(f"{rel}: {target} -> {resolved}")
    assert not missing, "broken links:\n" + "\n".join(missing)
