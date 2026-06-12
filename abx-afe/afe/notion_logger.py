from __future__ import annotations

from typing import Any

from afe.trace import AUTHORITY


def build_notion_payload_row(
    *,
    batch_id: str,
    run_index: int,
    seed: int,
    trace_packet: dict[str, Any],
    episode_length: int,
) -> dict[str, Any]:
    metrics = trace_packet.get("metrics", {})
    status = str(trace_packet.get("status", "NOT_COMPUTABLE"))
    diagnostics = tuple(str(item) for item in trace_packet.get("shadow_diagnostic_candidates", ()))
    return {
        "Run Name": f"{batch_id} Run {run_index:03d}",
        "Run ID": f"{batch_id}-RUN-{run_index:03d}",
        "Agent Count": 1,
        "Environment": str(trace_packet.get("environment_id", "NOT_COMPUTABLE")),
        "Seed": seed,
        "Episode Length": episode_length,
        "ACS": float(metrics.get("ACS", 0.0)),
        "MDI": float(metrics.get("MDI", 0.0)),
        "SES": float(metrics.get("SES", 0.0)),
        "SLI": float(metrics.get("SLI", 0.0)),
        "ECI": float(metrics.get("ECI", 0.0)),
        "Status": status,
        "Drift Flag": "__YES__" if "MANIPULATION_DRIFT_OBSERVED" in diagnostics else "__NO__",
        "Notes": _notes(status=status, diagnostics=diagnostics),
        "Authority": AUTHORITY,
        "Live Writeback": "__NO__",
    }


def _notes(*, status: str, diagnostics: tuple[str, ...]) -> str:
    if status == "NOT_COMPUTABLE":
        return "Trace packet is NOT_COMPUTABLE; payload row is local-only."
    if diagnostics:
        return "SHADOW diagnostics observed: " + ", ".join(diagnostics)
    return "SHADOW trace completed without elevated diagnostic candidates."
