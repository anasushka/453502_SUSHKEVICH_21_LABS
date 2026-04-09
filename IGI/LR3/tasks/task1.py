"""
Brief: Taylor series calculation with a decorator.
Lab: 3 (LR3), Task: 1
Version: 1.0
Author: Anastasiya Sushkevich
Date: 2026-03-25
"""
import math

def table_decorator(func):
    """Decorator to print table headers."""
    def wrapper(*args, **kwargs):
        print(f"\n{'x':>8} | {'n':>4} | {'F(x)':>15} | {'Math F(x)':>15} | {'eps':>8}")
        print("-" * 65)
        return func(*args, **kwargs)
    return wrapper

@table_decorator
def run_task(sequence: list, eps: float):
    """Calculates ln((x+1)/(x-1)) and prints results."""
    for x in sequence:
        if abs(x) <= 1:
            print(f"{x:8.2f} | Error: |x| must be > 1")
            continue
            
        sum_val = 0.0
        n = 0
        max_iter = 500
        
        while n < max_iter:
            # Формула: 1 / ((2n+1) * x^(2n+1))
            term = 1.0 / ((2 * n + 1) * (x ** (2 * n + 1)))
            sum_val += term
            if abs(2 * term) < eps: # Проверка точности (с учетом множителя 2)
                break
            n += 1
            
        f_x = 2 * sum_val
        math_f_x = math.log((x + 1) / (x - 1))
        print(f"{x:8.2f} | {n+1:4d} | {f_x:15.6f} | {math_f_x:15.6f} | {eps:8.4f}")