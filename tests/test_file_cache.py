from __future__ import annotations

import json
from pathlib import Path

from core.file_cache import clear_file_cache, read_json_cached


def test_read_json_cached_invalidates_on_file_change(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    target.write_text('{"value":1}\n', encoding="utf-8")
    clear_file_cache()

    first = read_json_cached(target)

    target.write_text('{"value":2,"items":[1]}\n', encoding="utf-8")
    second = read_json_cached(target)

    assert first == {"value": 1}
    assert second == {"value": 2, "items": [1]}


def test_read_json_cached_returns_detached_copy(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    target.write_text(json.dumps({"nested": {"value": 1}}), encoding="utf-8")
    clear_file_cache()

    payload = read_json_cached(target)
    payload["nested"]["value"] = 99

    assert read_json_cached(target) == {"nested": {"value": 1}}
