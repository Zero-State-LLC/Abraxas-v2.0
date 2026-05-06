"""Doctrine constants and helpers for ABRAXAS v2.0."""

from __future__ import annotations

SCHEMA_VERSION_PIPELINE = "AbraxasPipelineAutomationContract.v1.1"
SCHEMA_VERSION_REGISTRY = "GlobalPipelineRegistry.v1"
SCHEMA_VERSION_RUNE = "RuneContract.v1"
SCHEMA_VERSION_YGGDRASIL = "YggdrasilRouteGraph.v1"
SCHEMA_VERSION_RECEIPT = "RepoExecutionReceipt.v1"
SCHEMA_VERSION_REVIEW_QUEUE = "OperatorReviewQueueRun.v1"
SCHEMA_VERSION_AAL_VIZ = "GlobalPipelineAALVizProjectionPacket.v1"

DOCTRINE_RULES = [
    "governance before intelligence",
    "deterministic outputs",
    "typed IR everywhere",
    "explicit authority boundaries",
    "SHADOW / FORECAST separation",
    "ABX-Runes as typed operation layer",
    "YGGDRASIL as route/dependency topology",
    "AAL-Viz is projection-only",
    "receipts + proofs are mandatory",
    "fail closed on missing provenance",
    "no implementation claim without execution receipt",
]
