from src.data_loader import DataLoader
from src.representation import TimetableData
from src.initial_solution import greedy
from src.moves import day_shift, slot_shift, swap_assistants, random_move
from src.algorithms.simulated_annealing import validate_solution


def test_day_shift(solution):
    print("Move: Day Shift")
    solution.view()
    new_solution = day_shift(solution, slot=0, day=0, assistant=1)
    print("After move:")
    new_solution.view()


def test_slot_shift(solution):
    print("Move: Slot Shift")
    solution.view()
    new_solution = slot_shift(solution, slot=1, day=0, assistant=0)
    print("After move:")
    solution.view()


def test_swap_assistants(solution):
    print("Move: Swap Assistants")
    solution.view()
    new_solution = swap_assistants(solution, 0, 0, 0, 1, 0, 1)
    print("After move:")
    new_solution.view()


if __name__ == "__main__":
    loader = DataLoader()
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    solution = greedy(data)
    print("Initial solution:")
    solution.view()
    print("-" * 40)
    for _ in range(1000):
        print("\nRandom Move")
        solution.view
        new_solution = random_move(solution)
        print("After move:")
        new_solution.view()
        print("-" * 40)
        validate = validate_solution(new_solution)
        if validate[0]:
            solution = new_solution
        else:
            print("Invalid solution:", validate[1])
    print("Final solution:")
    solution.view()
