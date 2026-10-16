from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import run_fast_ci


class _Result:
    def __init__(self, code: int = 0) -> None:
        self.returncode = code


def _git(repo: Path, *args: str) -> None:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stderr.decode(errors="replace")


def _initialized_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "--quiet")
    (repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(
        repo,
        "-c",
        "user.name=Fast CI Test",
        "-c",
        "user.email=fast-ci@example.invalid",
        "commit",
        "--quiet",
        "-m",
        "baseline",
    )
    return repo


def _snapshot(
    *entries: tuple[str, run_fast_ci._PathState],
) -> run_fast_ci._WorktreeSnapshot:
    return run_fast_ci._WorktreeSnapshot(root=Path("/repo"), entries=tuple(entries))


def _patch_stable_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    stable = _snapshot()
    snapshots = iter((stable, stable))
    monkeypatch.setattr(
        run_fast_ci, "_capture_worktree_snapshot", lambda: next(snapshots)
    )


def test_pyright_timeout_returns_nonzero(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(run_fast_ci, "_preflight_check", lambda: 0)
    _patch_stable_guard(monkeypatch)
    monkeypatch.setenv("ABRAXAS_PYRIGHT_TIMEOUT_SECONDS", "10")

    def _fake_run(
        command: list[str], check: bool, timeout: int | None = None
    ) -> _Result:
        if command and command[0] == "pyright":
            raise subprocess.TimeoutExpired(cmd=command, timeout=timeout or 0)
        return _Result(0)

    monkeypatch.setattr(run_fast_ci.subprocess, "run", _fake_run)

    status = run_fast_ci.main()
    captured = capsys.readouterr()

    assert status == 124
    assert "Command timed out after 10s:" in captured.err


def test_non_pyright_commands_do_not_receive_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(run_fast_ci, "_preflight_check", lambda: 0)
    _patch_stable_guard(monkeypatch)
    monkeypatch.delenv("ABRAXAS_PYRIGHT_TIMEOUT_SECONDS", raising=False)

    seen: list[tuple[list[str], int | None]] = []

    def _fake_run(
        command: list[str], check: bool, timeout: int | None = None
    ) -> _Result:
        seen.append((command, timeout))
        return _Result(0)

    monkeypatch.setattr(run_fast_ci.subprocess, "run", _fake_run)

    assert run_fast_ci.main() == 0
    *validation, pyright = seen
    assert len(validation) == len(run_fast_ci.COMMANDS)
    assert all(timeout is None for _, timeout in validation)
    assert pyright[0][0] == "pyright"
    assert pyright[1] == run_fast_ci.DEFAULT_PYRIGHT_TIMEOUT_SECONDS
    # Under pytest, advisory gates are skipped so they cannot rewrite tracked reports
    # during the outer fast-CI suite (see _run_advisory_report_only_gates).


def test_advisory_report_only_commands_are_configured() -> None:
    joined = [" ".join(cmd) for cmd in run_fast_ci.ADVISORY_REPORT_ONLY_COMMANDS]
    assert any("run_boundary_advisory_check" in c for c in joined)
    assert any("run_sole_writer_advisory_check" in c for c in joined)
    assert any("run_neon_genie_allowlist_check" in c for c in joined)


def test_advisory_gates_invoke_scripts_when_not_under_pytest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("ABRAXAS_FAST_CI_SKIP_ADVISORY", raising=False)
    seen: list[list[str]] = []

    def _fake_run(
        command: list[str], check: bool, timeout: int | None = None
    ) -> _Result:
        seen.append(command)
        return _Result(0)

    monkeypatch.setattr(run_fast_ci.subprocess, "run", _fake_run)
    run_fast_ci._run_advisory_report_only_gates()
    joined = [" ".join(cmd) for cmd in seen]
    assert any("run_boundary_advisory_check" in c for c in joined)
    assert any("run_sole_writer_advisory_check" in c for c in joined)


def test_default_scope_uses_bounded_pyright_targets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ABRAXAS_FAST_CI_PYRIGHT_SCOPE", raising=False)
    monkeypatch.setattr(run_fast_ci.Path, "exists", lambda self: True)
    command, scope = run_fast_ci._resolve_pyright_command()
    assert scope == "bounded"
    assert command[0] == "pyright"
    assert command[1:] == list(run_fast_ci.DEFAULT_FAST_CI_PYRIGHT_TARGETS)


def test_full_scope_override_uses_full_pyright(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ABRAXAS_FAST_CI_PYRIGHT_SCOPE", "full")
    command, scope = run_fast_ci._resolve_pyright_command()
    assert scope == "full"
    assert command == ["pyright"]


def test_missing_bounded_target_is_skipped_with_note(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = run_fast_ci.DEFAULT_FAST_CI_PYRIGHT_TARGETS[0]

    def _exists(self: run_fast_ci.Path) -> bool:
        return str(self) != missing

    monkeypatch.delenv("ABRAXAS_FAST_CI_PYRIGHT_SCOPE", raising=False)
    monkeypatch.setattr(run_fast_ci.Path, "exists", _exists)

    command, scope = run_fast_ci._resolve_pyright_command()
    captured = capsys.readouterr()

    assert scope == "bounded"
    assert missing not in command
    assert f"skipping missing pyright target: {missing}" in captured.out


def test_generated_drift_is_restored_and_does_not_fail_when_residual_empty(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Fully restored temporary dirt must not force drift exit code 3."""
    generated = run_fast_ci._PathState(" M", b"tracked", "file:changed")
    before = _snapshot()
    after = _snapshot(("out/generated.json", generated))
    # Third snapshot is clean again (matches entry) after restore.
    snapshots = iter((before, after, before))
    restored: list[str] = []

    monkeypatch.setattr(run_fast_ci, "_preflight_check", lambda: 0)
    monkeypatch.setattr(run_fast_ci, "_run_validation_commands", lambda: 0)
    monkeypatch.setattr(
        run_fast_ci, "_capture_worktree_snapshot", lambda: next(snapshots)
    )

    def _restore(
        initial: run_fast_ci._WorktreeSnapshot,
        final: run_fast_ci._WorktreeSnapshot,
        changed: list[str],
    ) -> list[str]:
        assert initial == before
        assert final == after
        restored.extend(changed)
        return changed

    monkeypatch.setattr(run_fast_ci, "_restore_clean_entry_paths", _restore)

    assert run_fast_ci.main() == 0
    assert restored == ["out/generated.json"]
    captured = capsys.readouterr()
    assert '"out/generated.json"' in captured.err
    assert "temporary validation dirt restored" in captured.out


def test_validation_failure_status_wins_when_drift_is_also_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generated = run_fast_ci._PathState("??", b"", "file:new")
    before = _snapshot()
    after = _snapshot(("generated.txt", generated))
    snapshots = iter((before, after, before))

    monkeypatch.setattr(run_fast_ci, "_preflight_check", lambda: 0)
    monkeypatch.setattr(run_fast_ci, "_run_validation_commands", lambda: 17)
    monkeypatch.setattr(
        run_fast_ci, "_capture_worktree_snapshot", lambda: next(snapshots)
    )
    monkeypatch.setattr(
        run_fast_ci,
        "_restore_clean_entry_paths",
        lambda initial, final, changed: changed,
    )

    assert run_fast_ci.main() == 17


def test_changed_dirty_entry_path_is_reported_without_restore(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    original = run_fast_ci._PathState(" M", b"tracked", "file:original")
    changed = run_fast_ci._PathState(" M", b"tracked", "file:changed")
    before = _snapshot(("source.py", original))
    after = _snapshot(("source.py", changed))
    snapshots = iter((before, after, after))

    monkeypatch.setattr(run_fast_ci, "_preflight_check", lambda: 0)
    monkeypatch.setattr(run_fast_ci, "_run_validation_commands", lambda: 0)
    monkeypatch.setattr(
        run_fast_ci, "_capture_worktree_snapshot", lambda: next(snapshots)
    )
    monkeypatch.setattr(
        run_fast_ci,
        "_restore_clean_entry_paths",
        lambda initial, final, paths: [],
    )

    assert run_fast_ci.main() == run_fast_ci.FAST_CI_DRIFT_EXIT_CODE
    captured = capsys.readouterr()
    assert "preserved paths that were dirty at entry" in captured.err
    assert "residual worktree changes after cleanup" in captured.err


def test_snapshot_failure_stops_before_validation(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    validation_ran = False

    def _validation() -> int:
        nonlocal validation_ran
        validation_ran = True
        return 0

    monkeypatch.setattr(run_fast_ci, "_preflight_check", lambda: 0)
    monkeypatch.setattr(
        run_fast_ci,
        "_capture_worktree_snapshot",
        lambda: (_ for _ in ()).throw(RuntimeError("not a git checkout")),
    )
    monkeypatch.setattr(run_fast_ci, "_run_validation_commands", _validation)

    assert run_fast_ci.main() == run_fast_ci.FAST_CI_DRIFT_EXIT_CODE
    assert validation_ran is False
    assert "unable to capture entry worktree state" in capsys.readouterr().err


def test_real_git_cleanup_restores_tracked_and_removes_untracked(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _initialized_repo(tmp_path)
    monkeypatch.chdir(repo)
    before = run_fast_ci._capture_worktree_snapshot()

    (repo / "tracked.txt").write_text("generated\n", encoding="utf-8")
    (repo / "generated.txt").write_text("generated\n", encoding="utf-8")
    after = run_fast_ci._capture_worktree_snapshot()
    changed = run_fast_ci._changed_paths(before, after)

    assert changed == ["generated.txt", "tracked.txt"]
    assert run_fast_ci._restore_clean_entry_paths(before, after, changed) == changed
    assert (repo / "tracked.txt").read_text(encoding="utf-8") == "baseline\n"
    assert not (repo / "generated.txt").exists()
    assert run_fast_ci._capture_worktree_snapshot() == before


def test_unchanged_dirty_baseline_does_not_count_as_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _initialized_repo(tmp_path)
    monkeypatch.chdir(repo)
    (repo / "tracked.txt").write_text("user change\n", encoding="utf-8")
    (repo / "notes.txt").write_text("user notes\n", encoding="utf-8")

    before = run_fast_ci._capture_worktree_snapshot()
    after = run_fast_ci._capture_worktree_snapshot()

    assert run_fast_ci._changed_paths(before, after) == []


def test_dirty_path_content_change_is_detected_but_not_restored(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _initialized_repo(tmp_path)
    monkeypatch.chdir(repo)
    tracked = repo / "tracked.txt"
    tracked.write_text("user change\n", encoding="utf-8")
    before = run_fast_ci._capture_worktree_snapshot()

    tracked.write_text("validation changed it\n", encoding="utf-8")
    after = run_fast_ci._capture_worktree_snapshot()
    changed = run_fast_ci._changed_paths(before, after)

    assert changed == ["tracked.txt"]
    assert run_fast_ci._restore_clean_entry_paths(before, after, changed) == []
    assert tracked.read_text(encoding="utf-8") == "validation changed it\n"
