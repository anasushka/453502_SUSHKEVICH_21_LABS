# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""Interactive task 3 menu."""

from __future__ import annotations

from pathlib import Path

from .series_model import TaylorSeriesAnalyzer


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_REPORT_FILE = BASE_DIR / "task3_result.txt"
DEFAULT_PLOT_FILE = BASE_DIR / "task3_plot.png"


def parse_sequence(raw: str) -> list[float]:
    """Parse a comma-separated list of numbers."""
    parts = [item.strip() for item in raw.split(",") if item.strip()]
    if not parts:
        raise ValueError("Sequence cannot be empty.")
    return [float(item) for item in parts]


def read_sequence() -> list[float]:
    """Read a numeric sequence from the user, retrying on invalid input."""
    while True:
        raw = input("Enter x values separated by commas (for example: -2, -1.5, 1.2, 2, 3): ").strip()
        try:
            return parse_sequence(raw)
        except ValueError as exc:
            print(f"Input error: {exc}. Try again.")


def read_eps() -> float:
    """Read epsilon from the user, retrying on invalid input."""
    while True:
        raw = input("Enter eps (for example: 0.001): ").strip()
        try:
            eps = float(raw)
            if eps <= 0:
                print("eps must be greater than 0. Try again.")
                continue
            return eps
        except ValueError:
            print("Invalid number. Try again.")


def run_analysis(sequence: list[float], eps: float) -> None:
    """Run calculations, print table, save report and plot."""
    analyzer = TaylorSeriesAnalyzer()
    rows = analyzer.analyze_sequence(sequence, eps)

    if not rows:
        print("No valid x values. For this task, |x| must be > 1.")
        return

    stats = analyzer.sequence_statistics(sequence)

    table_text = analyzer.table_to_text(rows)
    stats_text = analyzer.statistics_to_text(stats)

    full_report = table_text + "\n\n" + stats_text

    print("\nRESULT TABLE")
    print(full_report)

    analyzer.save_report(DEFAULT_REPORT_FILE, full_report)
    analyzer.save_plot(rows, DEFAULT_PLOT_FILE)

    print(f"\nReport saved to: {DEFAULT_REPORT_FILE}")
    print(f"Plot saved to: {DEFAULT_PLOT_FILE}")


def run() -> None:
    """Run the task 3 menu."""
    while True:
        print("\n" + "=" * 50)
        print("TASK 3 - Taylor series")
        print("1 - Use sample data")
        print("2 - Enter custom data")
        print("0 - Back to main menu")
        print("=" * 50)

        choice = input("Choose an action: ").strip()

        if choice == "1":
            sequence = [-2.0, -1.5, 1.2, 2.0, 3.0]
            eps = 0.001
            run_analysis(sequence, eps)
        elif choice == "2":
            try:
                sequence = read_sequence()
                eps = read_eps()
                run_analysis(sequence, eps)
            except ValueError as exc:
                print(f"Input error: {exc}")
            except ZeroDivisionError:
                print("Input error: x must not be equal to 1 or -1.")
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")