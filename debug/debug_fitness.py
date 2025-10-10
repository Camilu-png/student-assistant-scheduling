from src.data_loader import DataLoader
from src.fitness import fitness
from src.representation import TimetableData
from src.initial_solution import greedy
import numpy as np

def test_fitness():
    loader = DataLoader()
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    solution = greedy(data)
    print(f"Objective Function {fitness(solution, data)}")

if __name__ == "__main__":
    test_fitness()