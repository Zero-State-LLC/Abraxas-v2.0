"""Validate the v2.0 doctrine-revision version policy.

Policy (docs/releases/VERSION_STRATEGY.md): v2.0 publishes doctrine revisions,
not product versions. semantic-release creates the ``v1.N.M`` tags; VERSION and
the top CHANGELOG.md entry are synced to the latest tag by an ordinary PR after
each release, because the release bot cannot push to protected ``main``.

Release-timing rules:
- VERSION must name a ``v*`` tag that is an ancestor of HEAD (fail otherwise).
- The top CHANGELOG.md entry must equal VERSION (fail otherwise).
- pyproject's version must be the reference label, never a product version.
- A newer reachable tag than VERSION means the sync PR has not landed yet: a
  warning on ordinary commits, a failure with ``--strict`` (sync PR / release lane).
- Without tags in the checkout (shallow CI clone) the tag rules are
  NOT_COMPUTABLE: reported, and a failure only with ``--strict``.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

REFERENCE_PACKAGE_VERSION = "0.0.0+reference"
_CHANGELOG_HEAD = re.compile(r"^#{1,2} \[?(\d+\.\d+\.\d+)\]?", re.MULTILINE)
_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def reachable_release_tags(repo: Path) -> list[str]:
    """Return ``v1.N.M``-style versions of tags reachable from HEAD, newest first."""
    out = _git(repo, "tag", "--merged", "HEAD", "--list", "v*")
    versions = [t[1:] for t in out.splitlines() if _SEMVER.match(t[1:] if t else "")]
    return sorted(versions, key=_version_key, reverse=True)


def evaluate(repo: Path, *, strict: bool = False) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    version = (repo / "VERSION").read_text(encoding="utf-8").strip()
    if not _SEMVER.match(version):
        errors.append(f"VERSION_NOT_SEMVER:{version}")

    match = _CHANGELOG_HEAD.search((repo / "CHANGELOG.md").read_text(encoding="utf-8"))
    changelog_top = match.group(1) if match else None
    if changelog_top != version:
        errors.append(f"CHANGELOG_TOP_MISMATCH:{changelog_top}!={version}")

    pyproject = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))
    package_version = pyproject.get("project", {}).get("version")
    if package_version != REFERENCE_PACKAGE_VERSION:
        errors.append(f"PYPROJECT_NOT_REFERENCE:{package_version}")

    tags = reachable_release_tags(repo)
    tag_status = "NOT_COMPUTABLE" if not tags else "OK"
    if not tags:
        (errors if strict else warnings).append("NO_RELEASE_TAGS_IN_CHECKOUT")
    elif version not in tags:
        errors.append(f"VERSION_HAS_NO_REACHABLE_TAG:v{version}")
    elif tags[0] != version:
        tag_status = "LAGGING"
        message = f"VERSION_LAGS_LATEST_TAG:v{version}<v{tags[0]}"
        (errors if strict else warnings).append(message)

    return {
        "status": "FAIL" if errors else "PASS",
        "version": version,
        "changelog_top": changelog_top,
        "latest_reachable_tag": f"v{tags[0]}" if tags else None,
        "tag_status": tag_status,
        "strict": strict,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument(
        "--strict",
        action="store_true",
        help="release lane / sync PR: tags required and VERSION must equal the latest tag",
    )
    args = parser.parse_args(argv)
    result = evaluate(args.repo.resolve(), strict=args.strict)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
