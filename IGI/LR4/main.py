# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05
"""Main entry point with menu for all tasks."""

from task_1.task1 import run as run_task_1
from task_2.task2 import run as run_task_2
from task_3.task3 import run as run_task_3
from task_4.task4 import run as run_task_4
from task_5.task5 import run as run_task_5
from task_6.task6 import run_a as run_task_6a, run_b as run_task_6b


def main() -> None:
    """Run the main interactive menu for all laboratory tasks."""
    while True:
        print("\n" + "=" * 50)
        print("MAIN MENU")
        print("1 - Task 1")
        print("2 - Task 2")
        print("3 - Task 3")
        print("4 - Task 4")
        print("5 - Task 5")
        print("6A - Task 6A (Pandas: Series/DataFrame)")
        print("6B - Task 6B (Pandas: statistics)")
        print("0 - Exit")
        print("=" * 50)

        choice = input("Choose an option: ").strip().upper()

        if choice == "1":
            run_task_1()
        elif choice == "2":
            run_task_2()
        elif choice == "3":
            run_task_3()
        elif choice == "4":
            run_task_4()
        elif choice == "5":
            run_task_5()
        elif choice == "6A":
            run_task_6a()
        elif choice == "6B":
            run_task_6b()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()