# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""Taylor series calculation and plotting for task 3."""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


@dataclass
class SeriesRow:
    """A single row of the output table."""

    x: float
    n: int
    fx: float
    math_fx: float
    eps: float


class BaseAnalyzer:
    """Base class that provides file report saving."""

    def save_report(self, file_path: str | Path, text: str) -> None:
        """Save a text report to file."""
        Path(file_path).write_text(text, encoding="utf-8")


class TaylorSeriesAnalyzer(BaseAnalyzer):
    """Analyzer for the series ln((x+1)/(x-1)).

    Inherits save_report from BaseAnalyzer.
    """

    def calculate_series(self, x: float, eps: float, max_iter: int = 500) -> tuple[float, int]:
        """Calculate the series value and the number of summed terms."""
        if abs(x) <= 1:
            raise ValueError("For this series, |x| must be > 1.")
        sum_val = 0.0
        n = 0
        while n < max_iter:
            term = 1.0 / ((2 * n + 1) * (x ** (2 * n + 1)))
            sum_val += term
            if abs(2 * term) < eps:
                break
            n += 1
        return 2 * sum_val, n + 1

    def calculate_math_value(self, x: float) -> float:
        """Calculate the same function using math.log."""
        return math.log((x + 1) / (x - 1))

    def analyze_sequence(self, sequence: Sequence[float], eps: float) -> List[SeriesRow]:
        """Build the table rows for a sequence of x values."""
        rows: List[SeriesRow] = []
        for x in sequence:
            if abs(x) <= 1:
                continue
            fx, n = self.calculate_series(x, eps)
            math_fx = self.calculate_math_value(x)
            rows.append(SeriesRow(x=x, n=n, fx=fx, math_fx=math_fx, eps=eps))
        return rows

    def sequence_statistics(self, sequence: Sequence[float]) -> dict:
        """Calculate mean, median, mode, variance and standard deviation."""
        data = list(sequence)
        if not data:
            raise ValueError("Sequence is empty.")
        modes = statistics.multimode(data)
        mode_value = modes[0] if len(modes) == 1 else modes
        return {
            "mean": statistics.fmean(data),
            "median": statistics.median(data),
            "mode": mode_value,
            "variance": statistics.pvariance(data),
            "stdev": statistics.pstdev(data),
        }

    def table_to_text(self, rows: Sequence[SeriesRow]) -> str:
        """Convert rows into a printable text table."""
        lines = [
            f"{'x':>8} | {'n':>4} | {'F(x)':>15} | {'Math F(x)':>15} | {'eps':>8}",
            "-" * 65,
        ]
        for row in rows:
            lines.append(
                f"{row.x:8.2f} | {row.n:4d} | {row.fx:15.6f} | "
                f"{row.math_fx:15.6f} | {row.eps:8.4f}"
            )
        return "\n".join(lines)

    def statistics_to_text(self, stats: dict) -> str:
        """Convert statistics into readable text."""
        mode_value = stats["mode"]
        mode_text = (
            ", ".join(str(i) for i in mode_value)
            if isinstance(mode_value, list)
            else str(mode_value)
        )
        return "\n".join([
            f"Arithmetic mean: {stats['mean']:.6f}",
            f"Median: {stats['median']:.6f}",
            f"Mode: {mode_text}",
            f"Variance: {stats['variance']:.6f}",
            f"Standard deviation: {stats['stdev']:.6f}",
        ])

    def save_plot(self, rows: Sequence[SeriesRow], file_path: str | Path) -> None:
        """Plot series results and math results on one coordinate axis."""
        path = Path(file_path)
        xs = [row.x for row in rows]
        series_vals = [row.fx for row in rows]
        math_vals = [row.math_fx for row in rows]

        plt.figure(figsize=(10, 6))
        plt.plot(xs, series_vals, marker="o", color="blue", label="Series F(x)")
        plt.plot(xs, math_vals, marker="s", color="red", label="Math F(x)")
        plt.axhline(0, color="black", linewidth=1)
        plt.axvline(0, color="black", linewidth=1)
        plt.title("Taylor series vs math.log")
        plt.xlabel("x")
        plt.ylabel("F(x)")
        plt.grid(True, alpha=0.3)
        plt.legend()

        if xs and series_vals:
            mid = len(xs) // 2
            plt.text(xs[mid], series_vals[mid], "Series point", fontsize=9)
            plt.annotate(
                "Math function",
                xy=(xs[mid], math_vals[mid]),
                xytext=(xs[mid], math_vals[mid] + 0.5),
                arrowprops=dict(arrowstyle="->"),
            )

        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
