# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""Interactive menu for task 1."""

from __future__ import annotations

from pathlib import Path

from .models import Candidate, ElectionTable
from .serializers import CSVSerializer, PickleSerializer


SAMPLE_DATA = {
    "Ivanov": 780,
    "Petrov": 610,
    "Sidorov": 340,
    "Smirnov": 270,
}


BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "elections.csv"
PICKLE_FILE = BASE_DIR / "elections.pkl"


def create_sample_table() -> ElectionTable:
    """Create the initial election table from a dictionary."""
    return ElectionTable.from_dict(SAMPLE_DATA)


def choose_serializer() -> BaseException | object:
    """Ask the user to choose a serializer."""
    while True:
        print("\nChoose serializer:")
        print("1 - CSV")
        print("2 - Pickle")
        choice = input("Your choice: ").strip()

        if choice == "1":
            return CSVSerializer()
        if choice == "2":
            return PickleSerializer()

        print("Invalid choice. Try again.")


def print_table(table: ElectionTable) -> None:
    """Print the full table and election result."""
    print()
    print(table)
    print(table.result_text())


def save_table(table: ElectionTable) -> None:
    """Save table using selected serializer."""
    serializer = choose_serializer()
    default_path = CSV_FILE if isinstance(serializer, CSVSerializer) else PICKLE_FILE

    raw_path = input(f"Enter file path [{default_path}]: ").strip()
    path = Path(raw_path) if raw_path else default_path

    try:
        serializer.save(table, path)
        print(f"Saved to: {path}")
    except (OSError, PermissionError) as exc:
        print(f"File saving error: {exc}")


def load_table() -> ElectionTable:
    """Load table using selected serializer."""
    serializer = choose_serializer()
    default_path = CSV_FILE if isinstance(serializer, CSVSerializer) else PICKLE_FILE

    raw_path = input(f"Enter file path [{default_path}]: ").strip()
    path = Path(raw_path) if raw_path else default_path

    try:
        table = serializer.load(path)
        print(f"Loaded from: {path}")
        return table
    except FileNotFoundError:
        print("File not found.")
    except (OSError, PermissionError) as exc:
        print(f"File reading error: {exc}")
    except (ValueError, KeyError, TypeError) as exc:
        print(f"Data format error: {exc}")

    return ElectionTable()


def search_candidate(table: ElectionTable) -> None:
    """Search for a candidate by surname entered from keyboard."""
    surname = input("Enter candidate surname: ").strip()
    try:
        candidate = table.search(surname)
        if candidate:
            print("Candidate found:")
            print(candidate)
        else:
            print("Candidate not found.")
    except (TypeError, ValueError) as exc:
        print(f"Search error: {exc}")


def show_sorted_table(table: ElectionTable) -> None:
    """Print candidates sorted by votes."""
    print("\nSORTED TABLE")
    print("-" * 55)
    print(f"{'Surname':20} | {'Votes':>5} | Status")
    print("-" * 55)

    for candidate in table.sort_by_votes():
        print(candidate)

    print("-" * 55)


def show_result(table: ElectionTable) -> None:
    """Show whether candidates passed or runoff is required."""
    print()
    print(table.result_text())


def add_candidate(table: ElectionTable) -> None:
    """Add a candidate manually."""
    surname = input("Enter surname: ").strip()
    votes_raw = input("Enter votes: ").strip()

    try:
        votes = int(votes_raw)
        table.add_candidate(Candidate(surname, votes))
        print("Candidate added.")
    except ValueError:
        print("Votes must be an integer.")
    except (TypeError, Exception) as exc:
        print(f"Cannot add candidate: {exc}")


def run() -> None:
    """Run the task 1 interactive menu."""
    table = create_sample_table()

    while True:
        print("\n" + "=" * 50)
        print("TASK 1 - Election table")
        print("1 - Show table")
        print("2 - Sort by votes")
        print("3 - Search candidate")
        print("4 - Show election result")
        print("5 - Save to file")
        print("6 - Load from file")
        print("7 - Add candidate")
        print("8 - Restore sample data")
        print("0 - Back to main menu")
        print("=" * 50)

        choice = input("Choose an action: ").strip()

        if choice == "1":
            print_table(table)
        elif choice == "2":
            show_sorted_table(table)
        elif choice == "3":
            search_candidate(table)
        elif choice == "4":
            show_result(table)
        elif choice == "5":
            save_table(table)
        elif choice == "6":
            table = load_table()
        elif choice == "7":
            add_candidate(table)
        elif choice == "8":
            table = create_sample_table()
            print("Sample data restored.")
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")