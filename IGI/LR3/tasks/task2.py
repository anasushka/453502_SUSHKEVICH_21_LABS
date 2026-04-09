"""
Brief: Multiplication of integers until a positive number is entered.
Lab: 3 (LR3), Task: 2
Version: 1.0
Author: Anastasiya Sushkevich
Date: 2026-03-25
"""

def run_task(generator):
    """
    Business function: multiplies sequence from generator.
    The positive number is used as a stop signal and is NOT included in the product.
    """
    product = 1
    count = 0
    
    for num in generator:
        if num > 0:
            # Число положительное — это сигнал к выходу. 
            # Мы его НЕ умножаем.
            break
        
        product *= num
        count += 1
        
    if count == 0:
        print("\nNotice: No non-positive numbers were entered before the stop signal.")
    else:
        print(f"\nResult of multiplication (of {count} numbers): {product}")