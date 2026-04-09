"""
Brief: General input validation and initialization methods.
Lab: 3 (LR3)
Version: 1.0
Author: Anastasiya Sushkevich
Date: 2026-03-25
"""

def get_float(prompt: str) -> float:
    """Safely gets a float from user."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Error: Please enter a valid number (e.g., 1.5).")

def get_int(prompt: str) -> int:
    """Safely gets an integer from user."""
    while True:
        try:
            val = input(prompt)
            return int(val)
        except ValueError:
            print("Error: Please enter a whole number (e.g., 5).")

def input_until_positive_gen():
    """Generator for Task 2: yields numbers until a positive one is entered."""
    print("Enter integers (a positive number > 0 will stop the input):")
    while True:
        val = get_int("> ")
        yield val
        if val > 0:
            break