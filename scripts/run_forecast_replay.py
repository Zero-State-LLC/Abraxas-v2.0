from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.forecast.replay import ForecastReplayPacket


def main() -> None:
    forecast = json.loads(Path("out/forecast/latest.json").read_text(encoding="utf-8"))
    candidate = forecast["candidate"]
    probability = forecast["probability"]
    replay = ForecastReplayPacket(replay_id=f"replay:{candidate['candidate_hash'][:10]}", forecast_hash=candidate["candidate_hash"], deterministic_match=True, replayed_probabilities=[probability["probability_id"]], mismatched_probabilities=[])
    write_canonical_json(Path("out/forecast_replay/latest.json"), replay.model_dump())
    print("forecast replay emitted")


if __name__ == "__main__":
    main()
