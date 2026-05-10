from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from .models import CanonSyncPacket


def canonical_doctrine_hash(packet: CanonSyncPacket) -> str:
    data = asdict(packet)
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
