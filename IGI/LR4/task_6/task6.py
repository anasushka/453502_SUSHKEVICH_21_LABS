# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""Pandas task for the Weather Dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from IPython.display import display
except ImportError:
    display = print


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "weatherHistory.csv"
RESULT_A_FILE = BASE_DIR / "task6a_result.txt"
RESULT_B_FILE = BASE_DIR / "task6b_result.txt"


class BaseDataAnalyzer:
    """Base class that loads a CSV dataset."""

    def __init__(self, file_path: Path) -> None:
        """Load the dataset from file."""
        self.file_path = Path(file_path)
        self.data: pd.DataFrame = pd.read_csv(self.file_path)


class WeatherDataAnalyzer(BaseDataAnalyzer):
    """Analyzer for the Kaggle weather dataset.

    Inherits CSV loading from BaseDataAnalyzer.
    """

    def show_series_examples(self) -> None:
        """Demonstrate Series creation, display, .loc and .iloc."""
        print("\nSERIES EXAMPLES")
        print("=" * 60)

        temperatures = self.data["Temperature (C)"]
        display(pd.Series(temperatures.head(5), name="Temperature (C)"))

        print("\nAccess by iloc:")
        print("First element:", temperatures.iloc[0])

        print("\nAccess by loc:")
        print("First row value by index label 0:", temperatures.loc[0])

    def create_custom_dataframe(self) -> pd.DataFrame:
        """Create a DataFrame from the first 7 days with temperature and humidity."""
        df = self.data.copy()
        df["Formatted Date"] = pd.to_datetime(df["Formatted Date"], utc=True, errors="coerce")
        df = df.dropna(subset=["Formatted Date"])
        df["Date"] = df["Formatted Date"].dt.date

        first_7_days = df["Date"].drop_duplicates().head(7)
        seven_df = df[df["Date"].isin(first_7_days)].drop_duplicates(subset=["Date"]).head(7)

        result = seven_df[["Temperature (C)", "Humidity"]].copy()
        result.index = seven_df["Formatted Date"].dt.day_name().values
        result.index.name = "Day"
        return result

    def show_dataframe_info(self) -> None:
        """Show basic DataFrame information."""
        print("\nDATAFRAME INFO")
        print("=" * 60)
        print(self.data.info())
        print("\nDESCRIBE:")
        display(self.data.describe(include="all"))

    def hot_vs_cold_decile_ratio(self) -> str:
        """Calculate ratio of avg temperature: hottest vs coldest decile days."""
        df = self.data.copy()
        df["Formatted Date"] = pd.to_datetime(df["Formatted Date"], utc=True, errors="coerce")
        df = df.dropna(subset=["Formatted Date"])
        df["Date"] = df["Formatted Date"].dt.date

        daily_temp = df.groupby("Date", as_index=False)["Temperature (C)"].mean()
        upper = daily_temp["Temperature (C)"].quantile(0.9)
        lower = daily_temp["Temperature (C)"].quantile(0.1)

        hottest_mean = daily_temp[daily_temp["Temperature (C)"] >= upper]["Temperature (C)"].mean()
        coldest_mean = daily_temp[daily_temp["Temperature (C)"] <= lower]["Temperature (C)"].mean()

        ratio = hottest_mean / abs(coldest_mean) if coldest_mean != 0 else float("inf")
        return (
            f"Average temperature in hottest days (upper decile): {hottest_mean:.2f}\n"
            f"Average temperature in coldest days (lower decile): {coldest_mean:.2f}\n"
            f"Hottest / coldest ratio: {ratio:.2f}"
        )

    def run_a(self) -> None:
        """Run task 6A."""
        print("\nTASK 6A - PANDAS STRUCTURES")
        print("=" * 60)
        print("DATASET HEAD:")
        display(self.data.head())

        self.show_series_examples()

        result_df = self.create_custom_dataframe()
        print("\nCUSTOM DATAFRAME (first 7 days, temperature + humidity):")
        display(result_df)

        RESULT_A_FILE.write_text(result_df.to_string(), encoding="utf-8")
        print(f"\nResult saved to: {RESULT_A_FILE}")

    def run_b(self) -> None:
        """Run task 6B."""
        print("\nTASK 6B - PANDAS STATISTICS")
        print("=" * 60)
        self.show_dataframe_info()

        result_text = self.hot_vs_cold_decile_ratio()
        print("\nSTATISTICAL TASK:")
        print(result_text)

        RESULT_B_FILE.write_text(result_text, encoding="utf-8")
        print(f"\nResult saved to: {RESULT_B_FILE}")


def _get_analyzer() -> WeatherDataAnalyzer | None:
    """Create and return a WeatherDataAnalyzer, or None if file is missing."""
    if not DATA_FILE.exists():
        print(f"File not found: {DATA_FILE}")
        return None
    return WeatherDataAnalyzer(DATA_FILE)


def run_a() -> None:
    """Entry point for task 6A with repeat support."""
    while True:
        print("\n" + "=" * 50)
        print("TASK 6A - Pandas Series / DataFrame")
        print("1 - Run analysis")
        print("0 - Back to main menu")
        print("=" * 50)

        choice = input("Choose an action: ").strip()
        if choice == "0":
            break
        if choice != "1":
            print("Invalid choice. Try again.")
            continue

        analyzer = _get_analyzer()
        if analyzer is None:
            break
        try:
            analyzer.run_a()
        except (KeyError, ValueError) as exc:
            print(f"Analysis error: {exc}")


def run_b() -> None:
    """Entry point for task 6B with repeat support."""
    while True:
        print("\n" + "=" * 50)
        print("TASK 6B - Pandas statistics")
        print("1 - Run analysis")
        print("0 - Back to main menu")
        print("=" * 50)

        choice = input("Choose an action: ").strip()
        if choice == "0":
            break
        if choice != "1":
            print("Invalid choice. Try again.")
            continue

        analyzer = _get_analyzer()
        if analyzer is None:
            break
        try:
            analyzer.run_b()
        except (KeyError, ValueError) as exc:
            print(f"Analysis error: {exc}")
