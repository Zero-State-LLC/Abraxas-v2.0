"""P64 manifest source-hash pre-merge gate.

Read-only validator (NW-011). Verifies that every entry in the committed P64
static-archive package manifest has a `sha256` (and, for `.json` sources, a
`canonical_hash`) that matches the checked-out source bytes at its `source_path`.
Also verifies P64 self-consistency (`package_hash` recompute + role order) so a
manually edited manifest cannot pass while the package itself is stale.

This mirrors the manifest-source-hash subset of the P65 governance audit
(`core/operator_narrative_static_archive_package_governance_audit.py`) so the
inconsistency that broke `canon-validation` on main is caught at PR time instead
of only after merge.

No artifact is regenerated, mutated, or written. Exit 0 when every manifest
entry is consistent; exit 1 on any missing/unreadable source or hash mismatch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canonical.json import canonical_hash  # noqa: E402
from core.operator_narrative_static_archive_package import ROLE_ORDER  # noqa: E402

DEFAULT_PACKAGE_JSON_PATH = (
    "out/package/operator_narrative_static_archive_package_001.latest.json"
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify P64 manifest source hashes against the checked-out source bytes."
        )
    )
    parser.add_argument(
        "--package-json-path",
        default=DEFAULT_PACKAGE_JSON_PATH,
        help="Path to the committed P64 package manifest JSON.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used to resolve manifest source paths.",
    )
    return parser.parse_args(argv)


def run_gate(*, package_json_path: str | Path, repo_root: str | Path) -> int:
    root = Path(repo_root)
    pkg_path = root / Path(package_json_path)

    if not pkg_path.exists():
        print(f"FAIL package manifest missing: {pkg_path.as_posix()}", flush=True)
        return 1
    try:
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report and fail, do not raise
        print(
            f"FAIL package manifest unreadable: {pkg_path.as_posix()} ({exc})",
            flush=True,
        )
        return 1

    manifest = pkg.get("package_manifest")
    if not isinstance(manifest, list) or not manifest:
        print("FAIL package_manifest missing or empty", flush=True)
        return 1

    structural: list[str] = []

    recomputed = deepcopy(pkg)
    observed_hash = recomputed.pop("package_hash", None)
    if observed_hash != canonical_hash(recomputed):
        structural.append("package_hash mismatch (P64 not self-consistent)")
    if pkg.get("artifact_role_order") != ROLE_ORDER:
        structural.append("artifact_role_order mismatch")
    if [e.get("role") for e in manifest] != ROLE_ORDER:
        structural.append("package_manifest role order mismatch")

    for problem in structural:
        print(f"STRUCT   {problem}", flush=True)

    mismatches: list[str] = []
    checked = 0

    for i, entry in enumerate(manifest):
        role = entry.get("role", f"idx:{i}")
        source_path = str(entry.get("source_path", ""))
        src = root / source_path
        checked += 1

        if not source_path:
            mismatches.append(f"{role}: empty source_path")
            print(f"MISSING  {role}: empty source_path", flush=True)
            continue
        if not src.exists():
            mismatches.append(f"{role}: source missing ({source_path})")
            print(f"MISSING  {role} -> {source_path}", flush=True)
            continue

        try:
            raw = src.read_bytes()
        except Exception as exc:  # noqa: BLE001
            mismatches.append(f"{role}: source unreadable ({source_path}: {exc})")
            print(f"MISSING  {role} -> {source_path} (unreadable: {exc})", flush=True)
            continue

        entry_problems: list[str] = []

        sha = hashlib.sha256(raw).hexdigest()
        if entry.get("sha256") != sha:
            entry_problems.append("sha256 mismatch")

        if source_path.endswith(".json"):
            try:
                src_obj = json.loads(raw.decode())
                if entry.get("canonical_hash") != canonical_hash(src_obj):
                    entry_problems.append("canonical_hash mismatch")
            except Exception:  # noqa: BLE001
                entry_problems.append("canonical json unreadable")

        if entry_problems:
            detail = ", ".join(entry_problems)
            mismatches.append(f"{role}: {detail} ({source_path})")
            print(f"MISMATCH {role} -> {source_path}: {detail}", flush=True)
        else:
            print(f"OK       {role} -> {source_path}", flush=True)

    consistent = checked - len(mismatches)
    print(f"\nP64 manifest source-hash gate: {consistent}/{checked} consistent", flush=True)
    if structural:
        print(f"P64 self-consistency: {len(structural)} structural problem(s)", flush=True)

    if mismatches or structural:
        print(
            "FAIL: P64 manifest is inconsistent with checked-out source bytes "
            "and/or not self-consistent. Re-seal the package chain against this "
            "ref's committed sources before merge.",
            flush=True,
        )
        return 1

    print(
        "PASS: P64 manifest is self-consistent and matches checked-out source bytes.",
        flush=True,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    return run_gate(
        package_json_path=args.package_json_path,
        repo_root=args.repo_root,
    )


if __name__ == "__main__":
    raise SystemExit(main())
