from core.codegen.shadow_replay_harness import ShadowReplayHarness


def test_shadow_replay_harness_replays_fixtures() -> None:
    harness = ShadowReplayHarness(fixtures=[{"fixture_id": "f1"}])
    result = harness.replay()
    assert result["fixture_count"] == 1
    assert result["execution_authority"] is False
