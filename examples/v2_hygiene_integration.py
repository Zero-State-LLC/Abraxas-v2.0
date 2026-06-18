#!/usr/bin/env python3
"""Minimal v2 hygiene integration example."""

from abraxas.v2.governance.mode import HygieneMode
from abraxas.v2.hygiene import HygienePipeline, V2Output


def main() -> None:
    output = V2Output(observed={"signal": "example"}, inferred={}, speculative={})
    pipeline = HygienePipeline(mode=HygieneMode.ADVISORY)
    result = pipeline.process(output, {"source": "examples/v2_hygiene_integration.py"})
    print(result.model_dump(mode="json"))


if __name__ == "__main__":
    main()
