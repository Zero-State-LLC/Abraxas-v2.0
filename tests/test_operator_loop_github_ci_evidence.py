# tests/test_operator_loop_github_ci_evidence.py
from __future__ import annotations

import json

from core.operator_loop_github_ci_evidence import (
    DEFAULT_PR_CAP,
    build_ci_evidence,
    build_github_evidence,
    gather_and_write,
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


def test_gather_writes_not_computable_when_gh_missing(tmp_path, monkeypatch) -> None:
    from scripts.viz import gather_operator_loop_github_ci_evidence as gather

    monkeypatch.setattr(gather, "gh_available", lambda: False)
    code = gather.main(["--evidence-dir", str(tmp_path), "--repo", "o/r"])
    assert code == 0
    github = json.loads((tmp_path / "github.v1.json").read_text(encoding="utf-8"))
    ci = json.loads((tmp_path / "ci.v1.json").read_text(encoding="utf-8"))
    assert github["status"] == "NOT_COMPUTABLE"
    assert ci["status"] == "NOT_COMPUTABLE"


def test_gather_with_fake_gh(tmp_path) -> None:
    def fake(argv: list[str]) -> tuple[int, str, str]:
        if argv[:3] == ["gh", "repo", "view"]:
            return 0, "owner/repo\n", ""
        if "pr" in argv and "list" in argv:
            return 0, json.dumps(
                [
                    {
                        "number": 7,
                        "title": "feat x",
                        "isDraft": False,
                        "mergeable": "MERGEABLE",
                        "headRefName": "feat/x",
                        "baseRefName": "main",
                        "url": "https://example.com/7",
                    }
                ]
            ), ""
        if "checks" in argv:
            return 0, "fast-ci\tpass\t1s\thttps://x\n", ""
        if "run" in argv and "list" in argv:
            return 0, json.dumps(
                [
                    {
                        "name": "fast-ci",
                        "conclusion": "success",
                        "status": "completed",
                        "headSha": "c" * 40,
                        "url": "https://example.com/run",
                        "workflowName": "ci",
                    }
                ]
            ), ""
        if "commits" in argv or (len(argv) > 2 and "api" in argv):
            return 0, "d" * 40 + "\n", ""
        return 1, "", "unknown"

    paths = gather_and_write(
        evidence_dir=tmp_path,
        gh_runner=fake,
        gh_on_path=True,
        now_iso="2026-07-26T12:00:00Z",
        repo="owner/repo",
    )
    github = json.loads(paths["github"].read_text(encoding="utf-8"))
    ci = json.loads(paths["ci"].read_text(encoding="utf-8"))
    assert github["status"] == "PRESENT"
    assert github["gathered_at"] == "2026-07-26T12:00:00Z"
    assert any(i["kind"] == "open_pr" and i["number"] == 7 for i in github["items"])
    assert any(i["kind"] == "git_tip" and i["sha"] == "d" * 40 for i in github["items"])
    assert ci["status"] == "PRESENT"
    assert any(i["kind"] == "main_workflow" for i in ci["items"])
    assert any(
        i["kind"] == "pr_checks_summary" and i["pr_number"] == 7 for i in ci["items"]
    )
    assert all(i.get("authority_implication") == "none" for i in github["items"])
    assert all(i.get("authority_implication") == "none" for i in ci["items"])
