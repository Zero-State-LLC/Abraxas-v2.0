from __future__ import annotations

from pathlib import Path

from scripts._receipt_runner import run_receipt


def run(*, repo_root: str | Path = ".", out_path: str | Path | None = None):
    return run_receipt("core.geometric_binder_orchestrator_integration_harness", repo_root=repo_root, out_path=out_path)


def main(argv: list[str] | None = None) -> None:
    del argv
    run()


if __name__ == "__main__":
    main()
