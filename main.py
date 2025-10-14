from src.data_loader import DataLoader
from src.representation import TimetableData
from src.initial_solution import greedy
from src.fitness import fitness
from src.algorithms.simulated_annealing import simulated_annealing, validate_solution


def main():
    # Data Load
    loader = DataLoader()
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)

    # Create initial solution
    initial_solution = greedy(data)
    print("Initial Solution Fitness:", fitness(initial_solution, data))
    initial_solution.view()

    # Parameters for Simulated Annealing
    initial_temp = 100_000.0
    final_temp = 1.0
    alpha = 0.98
    max_iter = 100_000

    # Ejecuting Simulated Annealing
    best_solution = simulated_annealing(
        initial_solution, initial_temp, final_temp, alpha, max_iter, data
    )
    print("Best Solution Fitness:", fitness(best_solution, data))
    print("Best Solution Validity:", validate_solution(best_solution))
    best_solution.view()


if __name__ == "__main__":
    main()
