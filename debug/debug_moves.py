from src.data_loader import DataLoader
from src.representation import TimetableData
from src.initial_solution import greedy
from src.moves import day_shift, slot_shift, swap_assistants, random_move
import numpy as np

def visualize_solution(solution):
    for s in range(solution.data.num_slots):
        row = []
        for d in range(solution.data.num_days):
            assistants = solution.assistants_in_slot(s, d)
            if assistants.size == 0:
                row.append("·")
            else:
                row.append("".join(map(str, assistants)))
        print(" ".join(f"{c:2}" for c in row))

def test_day_shift(solution):
    print("Move: Day Shift")
    visualize_solution(solution)
    new_solution = day_shift(solution, slot=0, day=0, assistant=1)
    print("After move:")
    visualize_solution(new_solution)

def test_slot_shift(solution):
    print("Move: Slot Shift")
    visualize_solution(solution)
    new_solution = slot_shift(solution, slot=1, day=0, assistant=0)
    print("After move:")
    visualize_solution(new_solution)

def test_swap_assistants(solution):
    print("Move: Swap Assistants")
    visualize_solution(solution)
    new_solution = swap_assistants(solution, 0, 0, 0, 1, 0, 1)
    print("After move:")
    visualize_solution(new_solution)

if __name__ == "__main__":
    loader = DataLoader()
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    solution = greedy(data)
    for _ in range(5):
        print("\nRandom Move")
        visualize_solution(solution)
        solution = random_move(solution)
        print("After move:")
        visualize_solution(solution)
        print("-" * 40)