from __future__ import annotations

from pathlib import Path

from run_hybrid_cycle import run

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    run(
        batch_id="AFE-BATCH-001",
        runs=10,
        seed_start=42,
        environment_set="baseline,scarcity,high-noise,authority,meme",
        export_target="notion",
        out_path=ROOT / "out" / "afe_batch_001.latest.json",
    )


if __name__ == "__main__":
    main()
