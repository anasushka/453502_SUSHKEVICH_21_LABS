"""
Brief: Count uppercase English letters and digits in a string.
Lab: 3, Task: 3
Version: 1.0
Author: Anastasiya Sushkevich
Date: 2026-03-25
"""

def run_task():
    """Business function: analyzes text input."""
    text = input("Enter text for analysis: ")
    
    upper_count = 0
    digit_count = 0
    
    # Английские заглавные буквы через ASCII коды или строку
    english_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    
    for char in text:
        if char in english_upper:
            upper_count += 1
        elif char in digits:
            digit_count += 1
            
    print(f"\nAnalysis results:")
    print(f"Uppercase English letters: {upper_count}")
    print(f"Digits: {digit_count}")