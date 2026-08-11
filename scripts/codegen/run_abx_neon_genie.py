#!/usr/bin/env python3
"""
Direct runner for abx-neon-genie umbrella (SHADOW_PRODUCT / advisory).

Thin coordinator entry point. Loads modules directly to avoid hyphen package issues.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Neon Genie venture cycle")
    parser.add_argument("--input", type=Path, help="JSON request file")
    parser.add_argument("--mode", default="PROMPT_LED")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("out/neon_genie/neon_genie_ideation_receipt_001.latest.json"),
    )
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[2] / "skills" / "abx-neon-genie"

    # Load modules directly
    router_mod = _load_module_from_path("neon_genie_router", skill_dir / "neon_genie_router.py")
    run_venture_cycle = router_mod.run_venture_cycle

    if args.input and args.input.exists():
        request = json.loads(args.input.read_text())
    else:
        request = {
            "mode": args.mode,
            "seed": "I dreamed of a forest where every tree was a different venture model that grew only when fed user pain.",
            "tags": ["symbolic", "venture", "forest"],
            "require_evidence": False,
        }

    receipt = run_venture_cycle(request)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True))
    print(f"Neon Genie receipt written to {args.output}")
    print(json.dumps(receipt, indent=2)[:1000] + "...")
    return 0


if __name__ == "__main__":
    sys.exit(main())