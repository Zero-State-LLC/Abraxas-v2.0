"""Artifact storage port — filesystem adapter for local/sandbox."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import (
    CanonicalWriteError,
    prepare_canonical_artifact,
    write_canonical_artifact,
)


class ArtifactStore(Protocol):
    def write_artifact(
        self,
        relative_path: str,
        payload: dict[str, Any],
        *,
        artifact_class: ArtifactClass | str,
        append_only: bool = False,
    ) -> dict[str, Any]:
        """Write classified artifact; return stamped payload."""

    def read_json(self, relative_path: str) -> dict[str, Any]:
        """Read JSON object by repo-relative path under out/."""

    def exists(self, relative_path: str) -> bool: ...


class FilesystemArtifactStore:
    """Local/sandbox adapter rooted at repo_root with out_dir confinement."""

    def __init__(self, repo_root: Path, out_dir: Path | None = None) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.out_dir = Path(out_dir or (self.repo_root / "out")).resolve()

    def _resolve_out(self, relative_path: str) -> Path:
        ref = relative_path.replace("\\", "/").lstrip("./")
        if ".." in ref.split("/"):
            raise CanonicalWriteError(f"path traversal denied: {relative_path}")
        if not ref.startswith("out/"):
            raise CanonicalWriteError(f"path must be under out/: {relative_path}")
        # Map logical out/... paths into the configured out_dir (may differ from
        # repo_root/out when RuntimeSettings.out_dir is overridden for drills).
        suffix = ref[len("out/") :]
        target = (self.out_dir / suffix).resolve()
        try:
            target.relative_to(self.out_dir)
        except ValueError as exc:
            raise CanonicalWriteError(
                f"path traversal denied: {relative_path}"
            ) from exc
        return target

    def write_artifact(
        self,
        relative_path: str,
        payload: dict[str, Any],
        *,
        artifact_class: ArtifactClass | str,
        append_only: bool = False,
    ) -> dict[str, Any]:
        target = self._resolve_out(relative_path)
        write_canonical_artifact(
            target,
            payload,
            artifact_class=artifact_class,
            out_root=self.out_dir,
            append_only=append_only,
        )
        return prepare_canonical_artifact(payload, artifact_class)

    def read_json(self, relative_path: str) -> dict[str, Any]:
        target = self._resolve_out(relative_path)
        data = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise CanonicalWriteError("stored artifact must be a JSON object")
        return data

    def exists(self, relative_path: str) -> bool:
        try:
            return self._resolve_out(relative_path).is_file()
        except CanonicalWriteError:
            return False
