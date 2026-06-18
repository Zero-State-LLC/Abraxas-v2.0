import os

from abraxas.v2.governance.mode import HygieneMode, resolve_hygiene_mode


def test_hygiene_mode_defaults_to_advisory() -> None:
    assert resolve_hygiene_mode({}) == HygieneMode.ADVISORY


def test_hygiene_mode_from_env(monkeypatch: os._Environ[str]) -> None:
    monkeypatch.setenv("ABX_V2_HYGIENE_MODE", "STRICT")
    assert resolve_hygiene_mode(os.environ) == HygieneMode.STRICT
