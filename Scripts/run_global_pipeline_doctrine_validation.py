from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.global_pipeline_doctrine_validation import (  # noqa: E402
    write_global_pipeline_doctrine_validation_artifacts,
)


def main() -> None:
    write_global_pipeline_doctrine_validation_artifacts()


if __name__ == "__main__":
    main()
