# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""Interactive test program for task 4."""

from __future__ import annotations

from pathlib import Path

from matplotlib.colors import is_color_like

from .geometry import Parallelogram


BASE_DIR = Path(__file__).resolve().parent
TEXT_FILE = BASE_DIR / "parallelogram_result.txt"
IMAGE_FILE = BASE_DIR / "parallelogram.png"


def read_positive_float(prompt: str) -> float:
    """Read a positive float value from the user."""
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw)
            if value <= 0:
                print("Value must be greater than 0.")
                continue
            return value
        except ValueError:
            print("Invalid number. Try again.")


def read_angle(prompt: str) -> float:
    """Read the angle between diagonals."""
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw)
            if not 0 < value < 180:
                print("Angle must be between 0 and 180 degrees.")
                continue
            return value
        except ValueError:
            print("Invalid angle. Try again.")


def read_color(prompt: str) -> str:
    """Read and validate a matplotlib color name."""
    while True:
        color = input(prompt).strip()
        if not color:
            print("Color cannot be empty.")
            continue
        if not is_color_like(color):
            print("Invalid color name. Use a matplotlib color name or hex code.")
            continue
        return color


def read_label(prompt: str) -> str:
    """Read a non-empty label."""
    while True:
        label = input(prompt).strip()
        if label:
            return label
        print("Label cannot be empty.")


def save_text_report(file_path: Path, text: str) -> None:
    """Save figure information to a text file."""
    file_path.write_text(text, encoding="utf-8")


def run() -> None:
    """Run the task 4 interactive test with repeat support."""
    while True:
        print("\n" + "=" * 50)
        print("TASK 4 - Parallelogram")
        print("1 - Build a new parallelogram")
        print("0 - Back to main menu")
        print("=" * 50)

        choice = input("Choose an action: ").strip()

        if choice == "0":
            break
        if choice != "1":
            print("Invalid choice. Try again.")
            continue

        print("\nA parallelogram is built by diagonals d1, d2 and the angle between them.")
        print("The figure will be drawn and saved to a file.\n")

        d1 = read_positive_float("Enter d1: ")
        d2 = read_positive_float("Enter d2: ")
        angle = read_angle("Enter angle between diagonals in degrees: ")
        color = read_color("Enter figure color: ")
        label = read_label("Enter figure label: ")

        try:
            figure = Parallelogram(d1=d1, d2=d2, angle_deg=angle, color=color, label=label)
            print("\n" + figure.info())

            save_text_report(TEXT_FILE, figure.info())
            figure.draw(IMAGE_FILE, show=True)

            print(f"\nText saved to: {TEXT_FILE}")
            print(f"Image saved to: {IMAGE_FILE}")

        except (TypeError, ValueError) as exc:
            print(f"Error: {exc}")