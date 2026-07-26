# tests/test_operator_loop_github_ci_evidence.py
from __future__ import annotations

from core.operator_loop_github_ci_evidence import (
    DEFAULT_PR_CAP,
    build_ci_evidence,
    build_github_evidence,
    not_computable_evidence,
    parse_gh_pr_checks_table,
    summarize_pr_checks,
)


def test_build_github_evidence_caps_and_shapes_open_prs() -> None:
    prs = [
        {
            "number": i,
            "title": f"PR {i}",
            "isDraft": i % 2 == 0,
            "mergeable": "MERGEABLE",
            "headRefName": f"feat/{i}",
            "baseRefName": "main",
            "url": f"https://example.com/{i}",
        }
        for i in range(1, 20)
    ]
    out = build_github_evidence(
        repo="scrimshawlife-ctrl/Abraxas-v2.0",
        main_sha="a" * 40,
        main_branch="main",
        open_prs=prs,
        gathered_at="2026-07-26T00:00:00Z",
        cap=DEFAULT_PR_CAP,
    )
    assert out["status"] == "PRESENT"
    assert out["source"] == "gh_cli"
    assert out["cap"] == 15
    assert out["repo"] == "scrimshawlife-ctrl/Abraxas-v2.0"
    open_items = [i for i in out["items"] if i["kind"] == "open_pr"]
    assert len(open_items) == 15
    assert all(i["authority_implication"] == "none" for i in out["items"])
    tip = next(i for i in out["items"] if i["kind"] == "git_tip")
    assert tip["sha"] == "a" * 40


def test_summarize_pr_checks_counts() -> None:
    rows = parse_gh_pr_checks_table(
        "fast-ci\tpass\t1m\thttps://x\n"
        "lint\tfail\t10s\thttps://y\n"
        "scan\tpending\t0\thttps://z\n"
    )
    summary = summarize_pr_checks(rows)
    assert summary["pass"] == 1
    assert summary["fail"] == 1
    assert summary["pending"] == 1
    assert summary["primary"] == "fail"


def test_not_computable_when_gh_missing() -> None:
    gh = not_computable_evidence(
        surface="github",
        notes=["gh CLI not found on PATH"],
        gathered_at="2026-07-26T00:00:00Z",
    )
    assert gh["status"] == "NOT_COMPUTABLE"
    assert gh["items"] == []
    assert "gh CLI" in gh["notes"][0]


def test_build_ci_evidence_includes_main_and_pr_summaries() -> None:
    out = build_ci_evidence(
        main_runs=[
            {
                "name": "ci",
                "conclusion": "success",
                "status": "completed",
                "headSha": "b" * 40,
                "url": "https://example.com/run/1",
            }
        ],
        pr_check_summaries=[
            {
                "pr_number": 42,
                "pass": 3,
                "fail": 0,
                "pending": 0,
                "primary": "pass",
            }
        ],
        gathered_at="2026-07-26T00:00:00Z",
    )
    assert out["status"] == "PRESENT"
    kinds = {i["kind"] for i in out["items"]}
    assert "main_workflow" in kinds
    assert "pr_checks_summary" in kinds
    assert all(i.get("authority_implication") == "none" for i in out["items"])
