from src.data_loader import DataLoader
from src.representation import TimetableData
from src.initial_solution import greedy


def debug_greedy_initial_solution():
    loader = DataLoader()
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    solution = greedy(data)
    print("=== Greedy Initial Solution ===")
    for s in range(solution.data.num_slots):
        row = []
        for d in range(solution.data.num_days):
            assistants = solution.assistants_in_slot(s, d)
            if assistants.size == 0:
                row.append("·")
            else:
                row.append("".join(map(str, assistants)))
        print(" ".join(f"{c:2}" for c in row))


if __name__ == "__main__":
    debug_greedy_initial_solution()
