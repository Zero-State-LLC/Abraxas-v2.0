from __future__ import annotations

import os
import hashlib
import json
import stat
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPT_DIR_KEY = _SCRIPT_DIR.casefold()
sys.path = [
    path
    for path in sys.path
    if os.path.abspath(path or os.curdir).casefold() != _SCRIPT_DIR_KEY
]

import subprocess  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402

DEFAULT_PYRIGHT_TIMEOUT_SECONDS = 120
ABRAXAS_FAST_CI_PYRIGHT_SCOPE_FULL = "full"
FAST_CI_DRIFT_EXIT_CODE = 3

DEFAULT_FAST_CI_PYRIGHT_TARGETS: tuple[str, ...] = (
    "core/geometric_research_item.py",
    "core/geometric_signal_packet.py",
    "core/metric_operator_registry.py",
    "core/geometric_projection_spec.py",
    "core/yggdrasil_geometric_route_metadata.py",
    "core/oracle_geometric_signal_attachment.py",
    "core/oracle_geometric_attachment_replay_receipt.py",
    "core/oracle_geometric_attachment_stabilization_window.py",
    "core/heavy_tail_signal_calibrator.py",
    "core/counterfactual_geometry_engine.py",
    "core/reservoir_geometry_diagnostic.py",
    "core/metric_operator_baseline_test_vector_pack.py",
    "core/chamfer_baseline_implementation_plan.py",
    "core/chamfer_test_vector_schema_plan.py",
    "core/chamfer_valid_fixture_implementation_plan.py",
    "core/chamfer_invalid_fixture_implementation_plan.py",
    "core/chamfer_not_computable_fixture_implementation_plan.py",
    "core/chamfer_fixture_plan_consolidation_receipt.py",
    "core/chamfer_fixture_implementation_readiness_review.py",
    "core/chamfer_expected_distance_policy_plan.py",
    "core/chamfer_fixture_creation_authorization_review.py",
    "core/chamfer_fixture_creation_pr_plan.py",
    "core/chamfer_fixture_creation_actual_pr_gate.py",
    "core/chamfer_expected_distance_values_actual_pr_gate.py",
    "scripts/run_fast_ci.py",
    "tests/test_geometric_research_item.py",
    "tests/test_geometric_signal_packet.py",
    "tests/test_metric_operator_registry.py",
    "tests/test_geometric_projection_spec.py",
    "tests/test_yggdrasil_geometric_route_metadata.py",
    "tests/test_oracle_geometric_signal_attachment.py",
    "tests/test_oracle_geometric_attachment_replay_receipt.py",
    "tests/test_oracle_geometric_attachment_stabilization_window.py",
    "tests/test_heavy_tail_signal_calibrator.py",
    "tests/test_counterfactual_geometry_engine.py",
    "tests/test_reservoir_geometry_diagnostic.py",
    "tests/test_metric_operator_baseline_test_vector_pack.py",
    "tests/test_chamfer_baseline_implementation_plan.py",
    "tests/test_chamfer_test_vector_schema_plan.py",
    "tests/test_chamfer_valid_fixture_implementation_plan.py",
    "tests/test_chamfer_invalid_fixture_implementation_plan.py",
    "tests/test_chamfer_not_computable_fixture_implementation_plan.py",
    "tests/test_chamfer_fixture_plan_consolidation_receipt.py",
    "tests/test_chamfer_fixture_implementation_readiness_review.py",
    "tests/test_chamfer_expected_distance_policy_plan.py",
    "tests/test_chamfer_fixture_creation_authorization_review.py",
    "tests/test_chamfer_fixture_creation_pr_plan.py",
    "tests/test_chamfer_fixture_creation_actual_pr_gate.py",
    "tests/test_chamfer_expected_distance_values_actual_pr_gate.py",
    "tests/test_chamfer_expected_distance_values.py",
    "core/chamfer_expected_distance_value_plan.py",
    "tests/test_chamfer_fixture_files.py",
    "tests/test_chamfer_expected_distance_value_plan.py",
    "tests/test_run_fast_ci.py",
    "core/operator_narrative_report.py",
    "core/operator_narrative_report_governance_audit.py",
    "core/operator_narrative_report_ui_overlay.py",
    "core/operator_narrative_report_ui_overlay_governance_audit.py",
    "core/operator_narrative_export_bundle.py",
    "core/operator_narrative_export_bundle_governance_audit.py",
    "core/operator_narrative_static_preview_bundle.py",
    "core/operator_narrative_static_preview_governance_audit.py",
    "core/operator_narrative_export_preview_archive_index.py",
    "core/operator_narrative_export_preview_archive_index_governance_audit.py",
    "core/operator_narrative_archive_chain_closure_receipt.py",
    "core/operator_narrative_archive_chain_stability_receipt.py",
    "core/operator_narrative_archive_chain_global_verification.py",
    "core/operator_narrative_static_archive_package.py",
    "core/operator_narrative_static_archive_package_governance_audit.py",
    "core/operator_narrative_static_archive_package_language_boundary_audit.py",
    "core/operator_narrative_static_archive_package_preflight_receipt.py",
    "core/operator_narrative_static_archive_package_boundary_receipt.py",
    "core/operator_narrative_static_archive_package_index_pointer_receipt.py",
    "core/operator_narrative_static_archive_package_final_index_receipt.py",
    "core/operator_narrative_static_archive_package_stability_receipt.py",
    "core/operator_narrative_static_archive_package_chain_closure_receipt.py",
    "core/operator_narrative_static_archive_package_completion_seal_receipt.py",
    "tests/test_operator_narrative_report.py",
    "tests/test_operator_narrative_report_governance_audit.py",
    "tests/test_operator_narrative_report_ui_overlay.py",
    "tests/test_operator_narrative_report_ui_overlay_governance_audit.py",
    "tests/test_operator_narrative_export_bundle.py",
    "tests/test_operator_narrative_export_bundle_governance_audit.py",
    "tests/test_operator_narrative_static_preview_bundle.py",
    "tests/test_operator_narrative_static_preview_governance_audit.py",
    "tests/test_operator_narrative_export_preview_archive_index.py",
    "tests/test_operator_narrative_export_preview_archive_index_governance_audit.py",
    "tests/test_operator_narrative_archive_chain_closure_receipt.py",
    "tests/test_operator_narrative_archive_chain_stability_receipt.py",
    "tests/test_operator_narrative_archive_chain_global_verification.py",
    "tests/test_operator_narrative_static_archive_package.py",
    "tests/test_operator_narrative_static_archive_package_governance_audit.py",
    "tests/test_operator_narrative_static_archive_package_language_boundary_audit.py",
    "tests/test_operator_narrative_static_archive_package_preflight_receipt.py",
    "tests/test_operator_narrative_static_archive_package_boundary_receipt.py",
    "tests/test_operator_narrative_static_archive_package_index_pointer_receipt.py",
    "tests/test_operator_narrative_static_archive_package_final_index_receipt.py",
    "tests/test_operator_narrative_static_archive_package_stability_receipt.py",
    "tests/test_operator_narrative_static_archive_package_chain_closure_receipt.py",
    "tests/test_operator_narrative_static_archive_package_completion_seal_receipt.py",
)


COMMANDS: list[list[str]] = [
    ["python", "-m", "scripts.run_artifact_regeneration", "--check-drift"],
    [
        "python",
        "-m",
        "pytest",
        "-q",
        "-m",
        "not slow and not integration and not canon and not artifact",
    ],
    ["python", "-m", "ruff", "check", "."],
]

# Report-only production-readiness gates (WS1.5). Always fail-open: non-zero
# exit codes are logged and ignored. Run *after* validation status is decided
# so report file writes under out/ do not trip the drift exit path.
ADVISORY_REPORT_ONLY_COMMANDS: list[list[str]] = [
    ["python", "scripts/run_boundary_advisory_check.py"],
    ["python", "scripts/run_sole_writer_advisory_check.py"],
]


@dataclass(frozen=True)
class _PathState:
    status: str
    index_entry: bytes
    worktree_fingerprint: str


@dataclass(frozen=True)
class _WorktreeSnapshot:
    root: Path
    entries: tuple[tuple[str, _PathState], ...]


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode(errors="replace").strip()
        command = " ".join(("git", *args))
        raise RuntimeError(f"{command} failed: {detail or 'unknown git error'}")
    return completed


def _repo_path(root: Path, rel_path: str) -> Path:
    candidate = Path(os.path.abspath(root / rel_path))
    if os.path.commonpath((str(root), str(candidate))) != str(root):
        raise RuntimeError(f"git reported a path outside the repository: {rel_path!r}")
    return candidate


def _worktree_fingerprint(path: Path) -> str:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return "missing"

    mode = stat.S_IFMT(metadata.st_mode)
    digest = hashlib.sha256()
    if stat.S_ISLNK(mode):
        digest.update(os.fsencode(os.readlink(path)))
    elif stat.S_ISREG(mode):
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return f"{mode:o}:{digest.hexdigest()}"


def _status_paths(raw_status: bytes) -> dict[str, str]:
    records = raw_status.split(b"\0")
    paths: dict[str, str] = {}
    index = 0
    while index < len(records):
        record = records[index]
        if not record:
            break
        if len(record) < 4 or record[2:3] != b" ":
            raise RuntimeError("git status returned an unsupported porcelain record")

        status_code = record[:2].decode("ascii", errors="strict")
        paths[os.fsdecode(record[3:])] = status_code
        if status_code[0] in "RC" or status_code[1] in "RC":
            index += 1
            if index >= len(records) or not records[index]:
                raise RuntimeError("git status returned an incomplete rename record")
            paths[os.fsdecode(records[index])] = status_code
        index += 1
    return paths


def _capture_worktree_snapshot() -> _WorktreeSnapshot:
    root_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if root_result.returncode != 0:
        detail = root_result.stderr.decode(errors="replace").strip()
        raise RuntimeError(f"unable to resolve repository root: {detail or 'unknown git error'}")

    root = Path(os.fsdecode(root_result.stdout).strip()).resolve()
    status_result = _run_git(
        root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    )
    entries: list[tuple[str, _PathState]] = []
    for rel_path, status_code in sorted(_status_paths(status_result.stdout).items()):
        path = _repo_path(root, rel_path)
        index_entry = _run_git(root, "ls-files", "--stage", "-z", "--", rel_path).stdout
        entries.append(
            (
                rel_path,
                _PathState(
                    status=status_code,
                    index_entry=index_entry,
                    worktree_fingerprint=_worktree_fingerprint(path),
                ),
            )
        )
    return _WorktreeSnapshot(root=root, entries=tuple(entries))


def _changed_paths(before: _WorktreeSnapshot, after: _WorktreeSnapshot) -> list[str]:
    if before.root != after.root:
        raise RuntimeError("repository root changed during fast CI")
    before_entries = dict(before.entries)
    after_entries = dict(after.entries)
    return sorted(
        path
        for path in before_entries.keys() | after_entries.keys()
        if before_entries.get(path) != after_entries.get(path)
    )


def _tracked_at_head(root: Path, rel_path: str) -> bool:
    return bool(_run_git(root, "ls-tree", "-z", "HEAD", "--", rel_path).stdout)


def _restore_clean_entry_paths(
    before: _WorktreeSnapshot,
    after: _WorktreeSnapshot,
    changed_paths: list[str],
) -> list[str]:
    before_entries = dict(before.entries)
    after_entries = dict(after.entries)
    restored: list[str] = []
    for rel_path in changed_paths:
        if rel_path in before_entries:
            continue

        path = _repo_path(before.root, rel_path)
        after_state = after_entries.get(rel_path)
        if _tracked_at_head(before.root, rel_path):
            _run_git(
                before.root,
                "restore",
                "--source=HEAD",
                "--staged",
                "--worktree",
                "--",
                rel_path,
            )
        else:
            if after_state is not None and after_state.index_entry:
                _run_git(before.root, "restore", "--staged", "--source=HEAD", "--", rel_path)
            if path.is_symlink() or path.is_file():
                path.unlink()
            elif path.exists():
                raise RuntimeError(f"refusing to remove generated directory: {rel_path!r}")
        restored.append(rel_path)
    return restored


def _print_paths(label: str, paths: list[str]) -> None:
    if not paths:
        return
    print(label, file=sys.stderr, flush=True)
    for path in paths:
        print(f"  - {json.dumps(path, ensure_ascii=True)}", file=sys.stderr, flush=True)


def _preflight_check() -> int:
    try:
        import jsonschema  # noqa: F401
    except ModuleNotFoundError:
        print(
            "Missing test dependency: jsonschema. "
            "Install dev extras first: python -m pip install -e '.[dev]'",
            file=sys.stderr,
            flush=True,
        )
        return 1
    return 0


def _pyright_timeout_seconds() -> int:
    raw = os.environ.get("ABRAXAS_PYRIGHT_TIMEOUT_SECONDS", str(DEFAULT_PYRIGHT_TIMEOUT_SECONDS))
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_PYRIGHT_TIMEOUT_SECONDS
    return value if value > 0 else DEFAULT_PYRIGHT_TIMEOUT_SECONDS


def _resolve_pyright_command() -> tuple[list[str], str]:
    scope = os.environ.get("ABRAXAS_FAST_CI_PYRIGHT_SCOPE", "bounded").strip().lower()
    if scope == ABRAXAS_FAST_CI_PYRIGHT_SCOPE_FULL:
        return (["pyright"], "full")

    targets: list[str] = []
    for rel_path in DEFAULT_FAST_CI_PYRIGHT_TARGETS:
        if Path(rel_path).exists():
            targets.append(rel_path)
        else:
            print(f"[fast-ci] skipping missing pyright target: {rel_path}", flush=True)

    return (["pyright", *targets], "bounded")


def _run_validation_commands() -> int:
    pyright_timeout_seconds = _pyright_timeout_seconds()

    for command in COMMANDS:
        print("+", " ".join(command), flush=True)
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            return completed.returncode

    pyright_command, pyright_scope = _resolve_pyright_command()
    print(f"[fast-ci] pyright scope: {pyright_scope}", flush=True)
    print("+", " ".join(pyright_command), flush=True)
    try:
        completed = subprocess.run(pyright_command, check=False, timeout=pyright_timeout_seconds)
    except subprocess.TimeoutExpired:
        print(
            f"Command timed out after {pyright_timeout_seconds}s: {' '.join(pyright_command)}",
            file=sys.stderr,
            flush=True,
        )
        return 124

    return completed.returncode


def _run_advisory_report_only_gates() -> None:
    """Run WS1.5 boundary/sole-writer checks without affecting exit status.

    Reports may write under out/production_readiness/ws1/. That is intentional
    and happens *after* validation drift accounting so it cannot fail the build.
    """
    print("[fast-ci] advisory report-only gates (fail-open)", flush=True)
    for command in ADVISORY_REPORT_ONLY_COMMANDS:
        print("+", " ".join(command), flush=True)
        try:
            completed = subprocess.run(command, check=False)
        except OSError as exc:
            print(
                f"[fast-ci] advisory gate failed to start (ignored): {' '.join(command)}: {exc}",
                file=sys.stderr,
                flush=True,
            )
            continue
        if completed.returncode != 0:
            print(
                f"[fast-ci] advisory gate non-zero exit (ignored): "
                f"{' '.join(command)} -> {completed.returncode}",
                flush=True,
            )
        else:
            print(
                f"[fast-ci] advisory gate ok: {' '.join(command)}",
                flush=True,
            )


def main() -> int:
    preflight_status = _preflight_check()
    if preflight_status != 0:
        return preflight_status

    try:
        before = _capture_worktree_snapshot()
    except (OSError, RuntimeError) as exc:
        print(f"[fast-ci] unable to capture entry worktree state: {exc}", file=sys.stderr, flush=True)
        return FAST_CI_DRIFT_EXIT_CODE

    validation_status = _run_validation_commands()
    try:
        after = _capture_worktree_snapshot()
        changed = _changed_paths(before, after)
    except (OSError, RuntimeError) as exc:
        print(f"[fast-ci] unable to capture final worktree state: {exc}", file=sys.stderr, flush=True)
        _run_advisory_report_only_gates()
        return validation_status or FAST_CI_DRIFT_EXIT_CODE

    if not changed:
        _run_advisory_report_only_gates()
        return validation_status

    _print_paths("[fast-ci] validation changed worktree paths:", changed)
    protected = [path for path in changed if path in dict(before.entries)]
    try:
        restored = _restore_clean_entry_paths(before, after, changed)
    except (OSError, RuntimeError) as exc:
        print(f"[fast-ci] unable to restore generated drift: {exc}", file=sys.stderr, flush=True)
        _run_advisory_report_only_gates()
        return validation_status or FAST_CI_DRIFT_EXIT_CODE

    _print_paths("[fast-ci] restored paths that were clean at entry:", restored)
    _print_paths("[fast-ci] preserved paths that were dirty at entry:", protected)

    try:
        cleaned = _capture_worktree_snapshot()
        residual = _changed_paths(before, cleaned)
    except (OSError, RuntimeError) as exc:
        print(f"[fast-ci] unable to verify drift cleanup: {exc}", file=sys.stderr, flush=True)
        _run_advisory_report_only_gates()
        return validation_status or FAST_CI_DRIFT_EXIT_CODE

    _print_paths("[fast-ci] residual worktree changes after cleanup:", residual)
    status = validation_status or FAST_CI_DRIFT_EXIT_CODE
    _run_advisory_report_only_gates()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
