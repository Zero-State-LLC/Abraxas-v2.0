"""Script: build and write the governed global pipeline registry surfaces.

Usage:
    python scripts/run_global_pipeline_registry.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_registry import main


if __name__ == "__main__":
    main()
