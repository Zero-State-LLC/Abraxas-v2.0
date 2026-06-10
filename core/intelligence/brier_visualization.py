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


def format_decomposition(decomp: Dict[str, float]) -> str:
    """Text visualization of Brier decomposition."""
    if not decomp or "reliability" not in decomp:
        return "No decomposition available."

    lines = [
        "Brier Score Decomposition:",
        f"  Reliability : {decomp.get('reliability', 0):.4f}",
        f"  Resolution  : {decomp.get('resolution', 0):.4f}",
        f"  Uncertainty : {decomp.get('uncertainty', 0):.4f}",
        f"  Total Brier : {decomp.get('brier_score', 0):.4f}",
    ]
    # Simple bar representation
    lines.append("")
    lines.append("Components (higher is better for Resolution, lower for Reliability):")
    for key in ["reliability", "resolution", "uncertainty"]:
        val = decomp.get(key, 0)
        bar = "#" * int(val * 30)
        lines.append(f"  {key.capitalize():12} : {val:.4f} | {bar}")

    return "\n".join(lines)
