"""
Brief: Processing a list of real numbers (min by modulus, sum after first positive).
Lab: 3 (LR3), Task: 5
Version: 1.0
Author: Anastasiya Sushkevich
Date: 2026-03-25
"""
import initialization as init

def input_real_list():
    """User input with data validation."""
    positive_number = True
    while(positive_number ):
        size = init.get_int("Enter the number of elements in the list: ")
        if size <= 0:
            print("List size must be positive. Creating an empty list.")
            continue
        break
        
    lst = []
    for i in range(size):
        val = init.get_float(f"Enter element {i+1}: ")
        lst.append(val)
    return lst

def display_list(lst: list, title="Current list"):
    """Displays the list on the screen."""
    if not lst:
        print(f"{title}: [Empty]")
    else:
        # Форматируем числа до 2 знаков после запятой для красоты
        formatted_lst = [f"{x:.2f}" for x in lst]
        print(f"{title}: {formatted_lst}")

def find_min_modulus_index(lst: list) -> int:
    """Finds the index of the element with the minimum absolute value."""
    if not lst:
        return -1
    
    min_val = abs(lst[0])
    min_idx = 0
    
    for i in range(1, len(lst)):
        if abs(lst[i]) < min_val:
            min_val = abs(lst[i])
            min_idx = i
            
    return min_idx

def sum_after_first_positive(lst: list) -> float:
    """Calculates the sum of elements located after the first positive element."""
    first_pos_idx = -1
    
    # Ищем индекс первого положительного элемента
    for i in range(len(lst)):
        if lst[i] > 0:
            first_pos_idx = i
            break
            
    if first_pos_idx == -1 or first_pos_idx == len(lst) - 1:
        # Если положительных нет или это последний элемент — сумма 0
        return 0.0
    
    # Считаем сумму среза списка от следующего элемента до конца
    return sum(lst[first_pos_idx + 1:])

def run_task():
    """ Main logic execution and results output."""
    print("\n--- Task 5: Real List Processing ---")
    
    # 1. Ввод данных
    my_list = input_real_list()
    
    if not my_list:
        print("The list is empty. Nothing to process.")
        return

    # 2. Вывод списка
    display_list(my_list)

    # 3. Поиск минимального по модулю
    min_idx = find_min_modulus_index(my_list)
    print(f"\n1) Minimum element by modulus: {my_list[min_idx]:.2f}")
    print(f"   Index (0-based): {min_idx}")
    print(f"   Position (1-based): {min_idx + 1}")

    # 4. Сумма после первого положительного
    total_sum = sum_after_first_positive(my_list)
    print(f"2) Sum of elements after the first positive: {total_sum:.4f}")