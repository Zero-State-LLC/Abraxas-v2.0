from typing import Any, Dict, List


def format_brier_summary(summary: Dict[str, Any]) -> str:
    """Simple text-based Brier visualization."""
    if summary.get("status") == "no_scores_yet":
        return "No Brier scores recorded yet."

    lines = [
        "Brier Score Summary:",
        f"  Samples     : {summary.get('n_scores', 0)}",
        f"  Mean Brier  : {summary.get('mean_brier', 0):.4f}",
        f"  Latest      : {summary.get('latest_brier', 0):.4f}",
        f"  Min         : {summary.get('min_brier', 0):.4f}",
        f"  Max         : {summary.get('max_brier', 0):.4f}",
    ]
    return "\n".join(lines)


def print_brier_trend(brier_scores: List[float], max_lines: int = 5):
    """Simple ASCII sparkline-style trend."""
    if not brier_scores:
        print("No scores to visualize.")
        return
    recent = brier_scores[-max_lines:]
    max_val = max(recent) or 1
    for score in recent:
        bar = "#" * int((score / max_val) * 20)
        print(f"{score:.3f} | {bar}")
