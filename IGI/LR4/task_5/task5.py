# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""NumPy matrix analysis for task 5."""

from __future__ import annotations

import math

import numpy as np


class BaseMatrixAnalyzer:
    """Base class that creates and stores a random integer matrix."""

    def __init__(self, rows: int, cols: int, low: int = -20, high: int = 21, seed: int = 42) -> None:
        """Initialize matrix dimensions and random seed."""
        self.rows = rows
        self.cols = cols
        self.low = low
        self.high = high
        np.random.seed(seed)

    def create_matrix(self) -> np.ndarray:
        """Create an integer matrix with random values."""
        return np.random.randint(self.low, self.high, size=(self.rows, self.cols))


class MatrixAnalyzer(BaseMatrixAnalyzer):
    """Full analyzer for NumPy matrices.

    Inherits matrix creation from BaseMatrixAnalyzer.
    """

    def demo_numpy_features(self, matrix: np.ndarray) -> dict:
        """Demonstrate array creation, indexing, slicing, and ufuncs."""
        return {
            "array": np.array(matrix),
            "zeros": np.zeros((2, 3), dtype=int),
            "ones": np.ones((2, 3), dtype=int),
            "arange": np.arange(1, 10),
            "linspace": np.linspace(0, 1, 5),
            "first_element": matrix[0, 0],
            "first_row": matrix[0],
            "first_column": matrix[:, 0],
            "abs_matrix": np.abs(matrix),
            "square_matrix": np.square(matrix),
        }

    def statistics_demo(self, matrix: np.ndarray) -> dict:
        """Calculate mean, median, correlation, variance and std."""
        flat = matrix.ravel()
        rev = flat[::-1]
        return {
            "mean": float(np.mean(flat)),
            "median": float(np.median(flat)),
            "corrcoef": float(np.corrcoef(flat, rev)[0, 1]) if flat.size > 1 else 0.0,
            "var": float(np.var(flat)),
            "std": float(np.std(flat)),
        }

    def negative_odd_values(self, matrix: np.ndarray) -> np.ndarray:
        """Return negative odd elements of the matrix."""
        return matrix[(matrix < 0) & (matrix % 2 != 0)]

    def sum_abs_negative_odd(self, matrix: np.ndarray) -> int:
        """Return the sum of absolute values of negative odd elements."""
        return int(np.sum(np.abs(self.negative_odd_values(matrix))))

    def std_by_formula(self, values: np.ndarray) -> float:
        """Calculate population standard deviation using the manual formula."""
        if values.size == 0:
            return 0.0
        mean_val = np.mean(values)
        return float(math.sqrt(float(np.mean((values - mean_val) ** 2))))

    def build_report(self, matrix: np.ndarray) -> str:
        """Build a text report for console output."""
        values = self.negative_odd_values(matrix)
        sum_abs = self.sum_abs_negative_odd(matrix)
        std_numpy = round(float(np.std(values)), 2) if values.size else 0.0
        std_formula = round(self.std_by_formula(values), 2) if values.size else 0.0

        demo = self.demo_numpy_features(matrix)
        stats = self.statistics_demo(matrix)

        lines = [
            "SOURCE MATRIX:",
            str(matrix),
            "",
            "NUMPY DEMO:",
            f"array():\n{demo['array']}",
            f"zeros():\n{demo['zeros']}",
            f"ones():\n{demo['ones']}",
            f"arange():\n{demo['arange']}",
            f"linspace():\n{demo['linspace']}",
            f"index [0, 0]: {demo['first_element']}",
            f"first row: {demo['first_row']}",
            f"first column: {demo['first_column']}",
            f"abs(matrix):\n{demo['abs_matrix']}",
            f"square(matrix):\n{demo['square_matrix']}",
            "",
            "MATH AND STATISTICS:",
            f"mean = {stats['mean']:.2f}",
            f"median = {stats['median']:.2f}",
            f"corrcoef = {stats['corrcoef']:.2f}",
            f"var = {stats['var']:.2f}",
            f"std = {stats['std']:.2f}",
            "",
            "TASK CONDITION:",
            f"Negative odd values: {values.tolist()}",
            f"Sum of absolute values of negative odd elements: {sum_abs}",
            f"Standard deviation by NumPy: {std_numpy:.2f}",
            f"Standard deviation by formula: {std_formula:.2f}",
        ]
        return "\n".join(lines)


def read_int(prompt: str, min_value: int = 1) -> int:
    """Read a valid integer from the user."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            return value
        except ValueError:
            print("Invalid integer. Try again.")


def run() -> None:
    """Run the task 5 interactive program with repeat support."""
    while True:
        print("\n" + "=" * 50)
        print("TASK 5 - NumPy matrix analysis")
        print("1 - Create matrix and analyze")
        print("0 - Back to main menu")
        print("=" * 50)

        choice = input("Choose an action: ").strip()

        if choice == "0":
            break
        if choice != "1":
            print("Invalid choice. Try again.")
            continue

        rows = read_int("Enter number of rows n: ")
        cols = read_int("Enter number of columns m: ")

        analyzer = MatrixAnalyzer(rows, cols)
        matrix = analyzer.create_matrix()
        print("\n" + analyzer.build_report(matrix))
