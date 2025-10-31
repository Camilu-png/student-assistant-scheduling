from src.data_loader import DataLoader
from src.representation import Solution, TimetableData
from src.initial_solution import greedy
from src.fitness import fitness
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
    bas_fitness, eligible_students = fitness(baseline_schedule, data)
    print("Baseline Solution Fitness:", bas_fitness)
    print("Students who can attend the assistantship:", eligible_students)
    print("Attendance percentage:", round((eligible_students*100)/data.num_students, 2))
    baseline_schedule.view()
    
    # Create initial solution
    initial_solution = greedy(data)
    val_fitness, eligible_students = fitness(initial_solution, data)
    print("Initial Solution Fitness:", val_fitness)
    print("Students who can attend the assistantship:", eligible_students)
    print("Attendance percentage:", round((eligible_students*100)/data.num_students, 2))
    initial_solution.view()

    print("")
    # Parameters for Simulated Annealing
    initial_temp = 100_000.0
    final_temp = 1.0
    alpha = 0.98
    max_iter = 100_000

    # Ejecuting Simulated Annealing
    best_solution = simulated_annealing(
        initial_solution, initial_temp, final_temp, alpha, max_iter, data
    )
    best_fitness, best_eligible_students = fitness(best_solution, data)
    print("Initial Solution Fitness:", best_fitness)
    print("Students who can attend the assistantship:", best_eligible_students)
    print("Attendance percentage:", round((best_eligible_students*100)/data.num_students, 2))
    best_solution.view()

    data.assistants.view()



if __name__ == "__main__":
    main()
