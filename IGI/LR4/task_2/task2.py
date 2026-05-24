# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""Interactive menu for task 2."""

from __future__ import annotations

from pathlib import Path

from .text_analyzer import RegexTextAnalyzer


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_FILE = BASE_DIR / "input.txt"
DEFAULT_RESULT_FILE = BASE_DIR / "result.txt"
DEFAULT_ARCHIVE_FILE = BASE_DIR / "result.zip"


def show_archive_info(analyzer: RegexTextAnalyzer, archive_file: Path, member_name: str) -> None:
    """Print information about the file stored in the ZIP archive."""
    print()
    print(analyzer.get_archive_info(archive_file, member_name))


def run_analysis(input_file: Path, result_file: Path, archive_file: Path) -> None:
    """Run text analysis, save results, and create an archive."""
    analyzer = RegexTextAnalyzer()

    try:
        report = analyzer.analyze(input_file)
        report_text = report.to_text()

        analyzer.write_text(result_file, report_text)
        analyzer.archive_file(result_file, archive_file)

        print("\nANALYSIS RESULT")
        print("=" * 60)
        print(report_text)
        print("=" * 60)
        print(f"Result saved to: {result_file}")
        print(f"Archive created: {archive_file}")

        show_archive_info(analyzer, archive_file, result_file.name)

    except FileNotFoundError:
        print("Source file not found.")
    except OSError as exc:
        print(f"File error: {exc}")


def run() -> None:
    """Run the interactive menu for task 2."""
    while True:
        print("\n" + "=" * 50)
        print("TASK 2 - Text analysis")
        print("1 - Analyze default input file")
        print("2 - Analyze custom input file")
        print("0 - Back to main menu")
        print("=" * 50)

        choice = input("Choose an action: ").strip()

        if choice == "1":
            run_analysis(DEFAULT_INPUT_FILE, DEFAULT_RESULT_FILE, DEFAULT_ARCHIVE_FILE)
        elif choice == "2":
            raw_input_file = input("Enter path to input text file: ").strip()
            raw_result_file = input(f"Enter result file path [{DEFAULT_RESULT_FILE}]: ").strip()
            raw_archive_file = input(f"Enter archive file path [{DEFAULT_ARCHIVE_FILE}]: ").strip()

            input_file = Path(raw_input_file)
            result_file = Path(raw_result_file) if raw_result_file else DEFAULT_RESULT_FILE
            archive_file = Path(raw_archive_file) if raw_archive_file else DEFAULT_ARCHIVE_FILE

            run_analysis(input_file, result_file, archive_file)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")