import numpy as np
from src.moves import random_move
from src.fitness import fitness


def validate_solution(solution) -> tuple[bool, str]:
    num_slots = solution.data.num_slots
    num_days = solution.data.num_days
    forbidden = solution.data.forbidden
    for i in range(num_days):
        for j in range(num_slots):
            if solution.is_assigned(j, i):
                assistants = solution.assistants_in_slot(j, i)
                if len(assistants) > 1:
                    return (
                        False,
                        f"More than one assistant assigned to day {i}, slot {j}",
                    )
                if forbidden[j][i] == 1:
                    return (
                        False,
                        f"Assistant assigned to forbidden slot at day {i}, slot {j}",
                    )
                if solution.data.assistants[j, i, assistants[0]] == 1:
                    return (
                        False,
                        f"Assistant {assistants[0]} assigned to a busy slot on day {i}, slot {j}",
                    )
    return (True, "Solution is valid")


def simulated_annealing(
    solution, initial_temp: float, final_temp: float, alpha: float, max_iter: int, data
):
    current_solution = solution
    current_fitness,_ = fitness(current_solution, data)
    best_solution = current_solution
    best_fitness = current_fitness
    temperature = initial_temp

    iteration = 0
    while temperature > final_temp or iteration < max_iter:
        new_solution = random_move(current_solution)
        if validate_solution(new_solution)[0] == False:
            new_fitness = -np.inf
        else:
            new_fitness,_ = fitness(new_solution, data)
        delta_fitness = new_fitness - current_fitness

        if delta_fitness > 0 or np.exp(delta_fitness / temperature) > np.random.rand():
            current_solution = new_solution
            current_fitness = new_fitness

            if current_fitness > best_fitness:
                best_solution = current_solution
                best_fitness = current_fitness

        temperature *= alpha
        iteration += 1
    print(f"Iterations: {iteration}")
    return best_solution
