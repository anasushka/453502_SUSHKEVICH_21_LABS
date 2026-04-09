"""
Brief: Main entry point for the Lab work.
Lab: 3, Title: Multi-task Application
Version: 1.0
Author: Anastasiya Sushkevich
Date: 2026-03-25
"""
import initialization as init
from tasks import task1, task2, task3, task4, task5

def main():
    while True:
        print("\n" + "="*30)
        print("  LAB 3 - MAIN MENU")
        print("="*30)
        print("1. Taylor Series (Task 1)")
        print("2. Sequence Multiplication (Task 2)")
        print("3. Text Analysis (Task 3)")
        print("4. Analysis of a predefined string (Task 4)")
        print("5. Processing a list of real numbers  (Task 5)")
        print("0. Exit")
        
        choice = input("\nSelect task: ")
        
        if choice == '1':
            size = init.get_int("Enter list size: ")
            eps = init.get_float("Enter precision (eps): ")
            # Для примера используем ручной ввод
            seq = [init.get_float(f"x[{i}]: ") for i in range(size)]
            task1.run_task(seq, eps) 
            
        elif choice == '2':
            gen = init.input_until_positive_gen()
            task2.run_task(gen)
            
        elif choice == '3':
            task3.run_task()

        elif choice == '4':
            task4.run_task()   

        elif choice == '5':
            task5.run_task()

        elif choice == '0':
            break
        else:
            print("Invalid choice!")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()