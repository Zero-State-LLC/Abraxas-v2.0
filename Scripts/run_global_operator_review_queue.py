from __future__ import annotations

from core.global_operator_review_queue import write_global_operator_review_queue_artifacts


def main() -> int:
    artifacts = write_global_operator_review_queue_artifacts()
    print(artifacts["queue_run"]["status"])
    print(artifacts["queue_run"]["run_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
