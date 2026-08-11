from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_release_config_does_not_push_back_to_protected_main() -> None:
    config = (REPO / "release.config.js").read_text(encoding="utf-8")

    assert "'@semantic-release/github'" in config
    assert "'@semantic-release/git'" not in config
    assert "'@semantic-release/changelog'" not in config
    assert "CHANGELOG.md" not in config
    assert "HEAD:main" not in config


def test_root_release_dependencies_match_config() -> None:
    package = json.loads((REPO / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((REPO / "package-lock.json").read_text(encoding="utf-8"))
    deps = package["devDependencies"]
    lock_root_deps = lock["packages"][""]["devDependencies"]

    assert "@semantic-release/git" not in deps
    assert "@semantic-release/changelog" not in deps
    assert "@semantic-release/git" not in lock_root_deps
    assert "@semantic-release/changelog" not in lock_root_deps
    assert "node_modules/@semantic-release/git" not in lock["packages"]
    assert "node_modules/@semantic-release/changelog" not in lock["packages"]
    assert deps == lock_root_deps


def test_release_workflow_is_pinned_and_engine_aligned() -> None:
    workflow = (REPO / ".github/workflows/release.yml").read_text(encoding="utf-8")

    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in workflow
    assert "actions/setup-node@820762786026740c76f36085b0efc47a31fe5020" in workflow
    assert "node-version: 22.22.2" in workflow
    assert "cache-dependency-path: package-lock.json" in workflow
    assert "contents: write" in workflow


def test_dependency_ci_hygiene_status_doc_records_dependabot_and_release_fix() -> None:
    doc = (REPO / "docs/status/DEPENDENCY_CI_WORKFLOW_HYGIENE_1121.md").read_text(
        encoding="utf-8"
    )

    assert "Issue: `#1121`" in doc
    assert "no open Dependabot PRs" in doc
    assert "@semantic-release/git" in doc
    assert "protected `main`" in doc
    assert "does not bypass branch protection" in doc
