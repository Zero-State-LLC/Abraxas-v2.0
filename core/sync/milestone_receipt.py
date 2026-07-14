from __future__ import annotations

import hashlib
from pathlib import Path




def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact_hashes(*, repo_root: str | Path = ".", artifact_paths: list[str]) -> tuple[dict[str, str], list[str]]:
    root = Path(repo_root)
    hashes: dict[str, str] = {}
    missing: list[str] = []
    for rel in sorted(set(artifact_paths)):
        target = root / rel
        if not target.exists():
            missing.append(rel)
            continue
        hashes[rel] = _sha256_file(target)
    return hashes, sorted(missing)
