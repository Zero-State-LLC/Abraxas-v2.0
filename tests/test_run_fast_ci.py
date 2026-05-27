from __future__ import annotations

import subprocess

import pytest

from scripts import run_fast_ci


class _Result:
    def __init__(self, code: int = 0) -> None:
        self.returncode = code


def test_pyright_timeout_returns_nonzero(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(run_fast_ci, "_preflight_check", lambda: 0)
    monkeypatch.setenv("ABRAXAS_PYRIGHT_TIMEOUT_SECONDS", "10")

    def _fake_run(command: list[str], check: bool, timeout: int | None = None) -> _Result:
        if command and command[0] == "pyright":
            raise subprocess.TimeoutExpired(cmd=command, timeout=timeout or 0)
        return _Result(0)

    monkeypatch.setattr(run_fast_ci.subprocess, "run", _fake_run)

    status = run_fast_ci.main()
    captured = capsys.readouterr()

    assert status == 124
    assert "Command timed out after 10s:" in captured.err


def test_non_pyright_commands_do_not_receive_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run_fast_ci, "_preflight_check", lambda: 0)
    monkeypatch.delenv("ABRAXAS_PYRIGHT_TIMEOUT_SECONDS", raising=False)

    seen: list[tuple[list[str], int | None]] = []

    def _fake_run(command: list[str], check: bool, timeout: int | None = None) -> _Result:
        seen.append((command, timeout))
        return _Result(0)

    monkeypatch.setattr(run_fast_ci.subprocess, "run", _fake_run)

    assert run_fast_ci.main() == 0
    assert seen[0][1] is None
    assert seen[1][1] is None
    assert seen[2][1] is None
    assert seen[3][0][0] == "pyright"
    assert seen[3][1] == run_fast_ci.DEFAULT_PYRIGHT_TIMEOUT_SECONDS


def test_default_scope_uses_bounded_pyright_targets(monkeypatch: pytest.MonkeyPatch) -> None:
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


def test_missing_bounded_target_is_skipped_with_note(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
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
