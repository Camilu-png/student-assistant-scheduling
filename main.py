from src.data_loader import DataLoader
from src.representation import TimetableData
from src.initial_solution import greedy
from src.fitness import fitness, fitness_without_soft_contraints
from src.algorithms.simulated_annealing import simulated_annealing
from src.baseline import baseline
import sys


def main():
    print("==========================================")
    print("  Educational Timetabling Solver - v1.0")
    print("==========================================\n")
    path = sys.argv[1]
    print("Data path:", path)

    # Data Load
    loader = DataLoader(path)
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    
    baseline_schedule = baseline(data)
    bas_fitness = fitness(baseline_schedule, data)
    bas_fitness_count = fitness_without_soft_contraints(baseline_schedule, data)
    percentage_bas = (bas_fitness_count*100)/data.num_students

    print(f"Baseline Solution Fitness: {bas_fitness}")
    print(f"Students who can attend the assistantship: {bas_fitness_count}")
    print(f"Attendance percentage: {round(percentage_bas,2)}%")
    baseline_schedule.view()
    
    # Create initial solution
    initial_solution = greedy(data)

    print("")
    # # Parameters for Simulated Annealing
    # initial_temp = 100_000.0
    # final_temp = 1.0
    # alpha = 0.98
    # max_iter = 100_000

    initial_temp = 100_000.0
    final_temp = 50.0
    alpha = 0.95
    max_iter = 100_000

    # Ejecuting Simulated Annealing whitout soft constraints
    print("Starting Simulated Annealing without soft constraints...\n")
    whithout_solution = simulated_annealing(
        initial_solution, initial_temp, final_temp, alpha, max_iter, data, fitness_without_soft_contraints
    )
    whithout_fitness = fitness(whithout_solution, data)
    whithout_fitness_count = fitness_without_soft_contraints(whithout_solution, data)
    percentage_without = (whithout_fitness_count*100)/data.num_students


    print(f"Best Solution Fitness without soft constraints: {round(whithout_fitness, 2)}")
    print(f"Students who can attend the assistantship: {whithout_fitness_count}")
    print(f"Attendance percentage: {round(percentage_without, 2)}%")
    whithout_solution.view()


    # Ejecuting Simulated Annealing
    print("\nStarting Simulated Annealing with constraints...\n")
    best_solution = simulated_annealing(
        initial_solution, initial_temp, final_temp, alpha, max_iter, data, fitness
    )
    best_fitness = fitness(best_solution, data)
    best_fitness_count = fitness_without_soft_contraints(best_solution, data)

    print(f"Best Solution Fitness: {round(best_fitness, 2)}")
    print(f"Students who can attend the assistantship: {best_fitness_count}")
    print(f"Attendance percentage: {round((best_fitness_count*100)/data.num_students, 2)}%")
    best_solution.view()


if __name__ == "__main__":
    main()
