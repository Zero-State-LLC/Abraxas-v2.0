from __future__ import annotations

import hashlib
import json
import subprocess
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OperatorNarrativeArchiveChainGlobalVerification.v1"
PATCH_ID = "PATCH-P57-OPERATOR-NARRATIVE-ARCHIVE-CHAIN-GLOBAL-VERIFICATION-001"
VERIFICATION_ID = "operator_narrative_archive_chain_global_verification_001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

_P51_REPAIRED_BLOCKERS = {
    "source_missing:p42_report_json",
    "source_missing:p44_ui_overlay_json",
    "overlay report hash lineage mismatch",
}

_COMMANDS = [
    "pytest -q",
    "pyright",
    "ruff check .",
    "python scripts/run_artifact_regeneration.py --full --validation-only",
    "python scripts/run_artifact_regeneration.py --check-drift",
]

_DENY_FALSE = {
    "package_created", "distribution_claims_allowed", "release_readiness_claimed", "command_authority", "ui_command_authority", "action_authority", "recommendation_authority", "inference_authority", "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "mutation_allowed", "authority_granted", "execution_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "adaptive_behavior_allowed", "psychological_claims_allowed", "speculative_causation_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control", "script_allowed", "html_script_allowed", "external_fetch_allowed", "form_allowed", "button_allowed",
}
_GOVERNANCE_FLAGS = {
    "global_verification_only": True,
    "verification_receipt_only": True,
    "advisory_only": True,
    "read_only": True,
    "non_authoritative": True,
    "source_linked": True,
    "deterministic_receipt": True,
    "no_architecture_expansion": True,
    **{k: False for k in _DENY_FALSE},
}


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "CORRUPT"
    return (payload, "PRESENT") if isinstance(payload, dict) else (None, "CORRUPT")


def _snip(text: str, limit: int = 1200) -> str:
    return text[:limit]


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _run_default(command: str, timeout_seconds: int) -> dict[str, Any]:
    started = time.time()
    try:
        proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout_seconds)
        could_run = True
        timed_out = False
        code = int(proc.returncode)
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
    except subprocess.TimeoutExpired as exc:
        could_run = True
        timed_out = True
        code = None
        stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    except OSError as exc:
        could_run = False
        timed_out = False
        code = None
        stdout = ""
        stderr = str(exc)

    duration_ms = int((time.time() - started) * 1000)
    return {
        "command": command,
        "exit_code": code,
        "duration_ms": duration_ms,
        "timed_out": timed_out,
        "could_run": could_run,
        "stdout_digest": _digest(stdout),
        "stderr_digest": _digest(stderr),
        "stdout_snippet": _snip(stdout),
        "stderr_snippet": _snip(stderr),
        "passed": bool(could_run and (not timed_out) and code == 0),
    }


def build_operator_narrative_archive_chain_global_verification_packet(
    *,
    p56_receipt_json_path: str | Path = "out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.json",
    command_runner: Callable[[str, int], dict[str, Any]] | None = None,
    timeout_seconds: int = 1800,
) -> dict[str, Any]:
    p56_path = Path(p56_receipt_json_path)
    p56, p56_status = _read_json(p56_path)
    blockers: list[str] = []

    command_results = []
    runner = command_runner or _run_default
    if p56_status == "PRESENT":
        for cmd in _COMMANDS:
            result = runner(cmd, timeout_seconds)
            command_results.append(result)
            if not result.get("could_run", False):
                blockers.append(f"command not runnable: {cmd}")
            elif result.get("timed_out", False):
                blockers.append(f"command timed out: {cmd}")
            elif int(result.get("exit_code", 1)) != 0:
                blockers.append(f"command failed: {cmd}")
    else:
        blockers.append(f"required source not readable: p56_stability_receipt_json ({p56_status})")

    p56_summary: dict[str, Any] = {}
    repaired_reintroduced: list[str] = []
    if p56:
        fs = str(p56.get("final_status", NOT_COMPUTABLE))
        sp = str(p56.get("stability_posture", NOT_COMPUTABLE))
        rc = int(p56.get("replay_count", -1)) if isinstance(p56.get("replay_count"), int) else -1
        p56_summary = {"final_status": fs, "stability_posture": sp, "replay_count": rc}
        if fs != "STABILITY_RECEIPT_DEGRADED":
            blockers.append("p56 final_status invalid for sealed degraded continuity")
        if sp != "STABLE_WITH_OBSERVED_BLOCKERS":
            blockers.append("p56 stability_posture invalid for observed-blocker continuity")
        if rc != 3:
            blockers.append("p56 replay_count must equal 3")
        repaired_reintroduced = sorted(_P51_REPAIRED_BLOCKERS & set((p56.get("repaired_blocker_guard_summary", {}).get("p51_repaired_blockers_reintroduced", []))))
        if repaired_reintroduced:
            blockers.append("p51 repaired blockers reintroduced")

    drift_result = next((r for r in command_results if r["command"].endswith("--check-drift")), None)
    regen_result = next((r for r in command_results if r["command"].endswith("--validation-only")), None)

    if p56_status != "PRESENT" or any((not r.get("could_run", True)) for r in command_results):
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif blockers:
        final_status, posture = "GLOBAL_VERIFICATION_FAIL", "FAILED"
    else:
        final_status, posture = "GLOBAL_VERIFICATION_PASS", "VERIFIED"

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "verification_id": VERIFICATION_ID,
        "final_status": final_status,
        "verification_posture": posture,
        "command_results": command_results,
        "source_artifact_summary": {
            "p56_receipt_json_path": p56_path.as_posix(),
            "p56_receipt_json_presence": p56_status,
        },
        "p56_continuity_summary": p56_summary,
        "blocker_guard_summary": {
            "p51_repaired_blockers_reintroduced": repaired_reintroduced,
            "p56_blocker_summary_count": len((p56 or {}).get("blocker_summary", []) if isinstance((p56 or {}).get("blocker_summary"), list) else []),
        },
        "governance_boundary_summary": {
            "forbidden_authority_flags_false": sorted(_DENY_FALSE),
            "verification_only": True,
            "no_architecture_expansion": True,
        },
        "artifact_drift_summary": {
            "validation_only_passed": bool(regen_result and regen_result.get("passed")),
            "check_drift_passed": bool(drift_result and drift_result.get("passed")),
        },
        "source_hashes": {
            "p56_stability_receipt_json": canonical_hash(p56) if p56 else NOT_COMPUTABLE,
        },
        "blocker_summary": sorted(set(blockers)),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "deterministic": True,
            "read_only": True,
            "non_authoritative": True,
            "source_linked": True,
            "fail_closed": True,
        },
    }
    packet["verification_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_archive_chain_global_verification_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P57 Operator Narrative Archive Chain Global Verification Sweep",
        "",
        f"- verification_id: `{packet.get('verification_id','')}`",
        f"- final_status: `{packet.get('final_status','')}`",
        f"- verification_posture: `{packet.get('verification_posture','')}`",
        f"- verification_hash: `{packet.get('verification_hash','')}`",
        "",
        "## Command Results",
    ]
    for item in packet.get("command_results", []):
        lines.append(
            f"- `{item.get('command')}` exit=`{item.get('exit_code')}` passed=`{item.get('passed')}` timed_out=`{item.get('timed_out')}` duration_ms=`{item.get('duration_ms')}`"
        )
    lines.extend(["", "## Blockers"])
    blockers = packet.get("blocker_summary", [])
    lines.extend([f"- `{b}`" for b in blockers] if blockers else ["- none"])
    lines.extend(["", "## Governance Boundary"])
    for k, v in (packet.get("governance_flags") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_archive_chain_global_verification(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(
        build_operator_narrative_archive_chain_global_verification_markdown(packet),
        encoding="utf-8",
    )
