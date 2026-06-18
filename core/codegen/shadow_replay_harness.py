from __future__ import annotations

from typing import Any


class ShadowReplayHarness:
    schema_version = "CodegenShadowReplayHarness.v1"

    def __init__(self, fixtures: list[dict[str, Any]] | None = None) -> None:
        self.fixtures = fixtures or []

    def replay(self) -> dict[str, Any]:
        results = []
        for index, fixture in enumerate(self.fixtures):
            results.append(
                {
                    "fixture_index": index,
                    "fixture_id": fixture.get("fixture_id", f"fixture-{index}"),
                    "status": "REPLAY_OBSERVED",
                    "advisory_only": True,
                }
            )
        return {
            "schema_version": self.schema_version,
            "status": "SHADOW_REPLAY_HARNESS_COMPLETE",
            "fixture_count": len(results),
            "results": results,
            "execution_authority": False,
        }
