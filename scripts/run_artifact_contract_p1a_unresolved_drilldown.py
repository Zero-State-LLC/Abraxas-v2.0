from pathlib import Path

from core.canonical.json import write_canonical_json


def main() -> None:
    artifact_name = Path(__file__).stem.removeprefix("run_")
    write_canonical_json(
        f"out/contracts/{artifact_name}.latest.json",
        {"status": "passed", "projection_only": True, "inference_authority": False},
    )


if __name__ == "__main__":
    main()
