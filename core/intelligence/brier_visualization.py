from typing import Any, Dict, List


def format_brier_summary(summary: Dict[str, Any]) -> str:
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


def print_brier_trend(brier_scores: List[float], max_lines: int = 8):
    if not brier_scores:
        print("No scores to visualize.")
        return
    recent = brier_scores[-max_lines:]
    max_val = max(recent) or 1
    print("Brier Score Trend (recent):")
    for i, score in enumerate(recent):
        bar = "#" * int((score / max_val) * 25)
        print(f"  {i+1:2d}: {score:.4f} | {bar}")


def format_decomposition(decomp: Dict[str, float]) -> str:
    if not decomp or "reliability" not in decomp:
        return "No decomposition available."

    lines = [
        "Brier Score Decomposition:",
        f"  Reliability : {decomp.get('reliability', 0):.4f}",
        f"  Resolution  : {decomp.get('resolution', 0):.4f}",
        f"  Uncertainty : {decomp.get('uncertainty', 0):.4f}",
        f"  Total Brier : {decomp.get('brier_score', 0):.4f}",
    ]
    lines.append("")
    lines.append("Lower Reliability = better calibration | Higher Resolution = better discrimination")
    for key in ["reliability", "resolution", "uncertainty"]:
        val = decomp.get(key, 0)
        bar = "#" * int(val * 25)
        lines.append(f"  {key.capitalize():12} : {val:.4f} | {bar}")
    return "\n".join(lines)


def format_reliability_diagram(
    predictions: List[float],
    targets: List[float],
    n_bins: int = 10
) -> str:
    if not predictions or len(predictions) != len(targets):
        return "Insufficient data for reliability diagram."

    bins = [[] for _ in range(n_bins)]
    bin_targets = [[] for _ in range(n_bins)]

    for p, t in zip(predictions, targets):
        bin_idx = min(int(p * n_bins), n_bins - 1)
        bins[bin_idx].append(p)
        bin_targets[bin_idx].append(t)

    lines = ["Reliability Diagram (Predicted vs Observed Frequency):"]
    lines.append(" Bin | Predicted | Observed | Error   | Bar")
    lines.append("-" * 58)

    for i in range(n_bins):
        if bins[i]:
            mean_pred = sum(bins[i]) / len(bins[i])
            mean_obs = sum(bin_targets[i]) / len(bin_targets[i])
            error = abs(mean_pred - mean_obs)
            bar = "#" * int(mean_obs * 20)
            lines.append(
                f" {i:2d} | {mean_pred:.3f}  | {mean_obs:.3f}  | {error:.3f} | {bar}"
            )
    return "\n".join(lines)


def generate_text_report(result: Dict[str, Any]) -> str:
    lines = ["=== Intelligence Report ==="]

    if "brier_summary" in result:
        lines.append(format_brier_summary(result["brier_summary"]))

    if result.get("brier_variants") and "decomposition" in result["brier_variants"]:
        lines.append("")
        lines.append(format_decomposition(result["brier_variants"]["decomposition"]))

    if "brier_variants" in result:
        variants = result["brier_variants"]
        lines.append("")
        lines.append("Key Scores:")
        if "log_score" in variants:
            lines.append(f"  Log Score   : {variants['log_score']:.4f}")
        if "brier_score" in variants:
            lines.append(f"  Brier Score : {variants['brier_score']:.4f}")

    return "\n".join(lines)


class ReportGenerator:
    """
    Generates structured reports from IntelligenceSystem results.
    """

    def __init__(self, style: str = "text"):
        self.style = style

    def generate(self, result: Dict[str, Any]) -> str:
        if self.style == "text":
            return generate_text_report(result)
        return generate_text_report(result)  # default to text for now

    def compare_calibration_methods(self, results: Dict[str, Dict[str, Any]]) -> str:
        """Compare multiple calibration methods side by side."""
        lines = ["Calibration Method Comparison:"]
        lines.append("Method      | Mean Brier | Log Score | Skill Score")
        lines.append("-" * 55)

        for method, res in results.items():
            variants = res.get("brier_variants", {})
            mean_brier = variants.get("brier_score", float('nan'))
            log_score = variants.get("log_score", float('nan'))
            skill = variants.get("brier_skill_score", float('nan'))
            lines.append(f"{method:11} | {mean_brier:9.4f} | {log_score:8.4f} | {skill:10.4f}")

        return "\n".join(lines)
