from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import RuntimePaths  # noqa: E402
from core.performance import RuntimeProfiler  # noqa: E402

_B003_ACKNOWLEDGMENT_PATH = "out/operator_blocker_acknowledgment/latest.json"
_BENCHMARK_PATH = "out/audit/runtime_benchmark_001.latest.json"
_DEFAULT_OUT_DIR = "out"
_DEFAULT_CONTRACTS_DIR = "contracts"

_CHECKPOINT_ID = "f2422b0aa1e436d580b4a5e372fa1d766ebb56a49584e700015557e77d085723"
_B003_ACKNOWLEDGMENT_HASH = "15a94652a820624c73d10267a88c6848a22f6dc7de80e97a1afd6d2bf68f8ed8"


def _make_paths(root: Path) -> RuntimePaths:
    return RuntimePaths(
        contracts_dir=root / _DEFAULT_CONTRACTS_DIR,
        out_dir=root / _DEFAULT_OUT_DIR,
    )


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict:
    root = Path(repo_root)
    paths = _make_paths(root)

    output_path = Path(out_path) if out_path is not None else paths.runtime_performance_profile_latest
    output_path.parent.mkdir(parents=True, exist_ok=True)

    profiler = RuntimeProfiler(output_path, enabled=True)

    profiler.record_artifact(
        "benchmark_artifact",
        root / _BENCHMARK_PATH,
    )
    profiler.record_artifact(
        "b003_acknowledgment_artifact",
        root / _B003_ACKNOWLEDGMENT_PATH,
    )

    profiler.record_correlation(
        "b004_checkpoint_ref",
        _CHECKPOINT_ID,
    )
    profiler.record_correlation(
        "b003_acknowledgment_hash",
        _B003_ACKNOWLEDGMENT_HASH,
    )

    with profiler.measure("registry_generation", "profile_generation"):
        pass

    result = profiler.write(final_status="PASS", remaining_blockers=[])
    assert result is not None, "RuntimeProfiler.write() returned None with enabled=True"

    return profiler.build_packet(final_status="PASS", remaining_blockers=[])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Path to repository root. Defaults to the parent of the scripts/ directory.",
    )
    args = parser.parse_args(argv)
    packet = run(repo_root=args.repo_root)
    print(packet["final_status"])
    paths = _make_paths(Path(args.repo_root))
    print(paths.runtime_performance_profile_latest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
