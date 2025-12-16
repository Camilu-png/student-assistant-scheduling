import sys
import os
from datetime import datetime
from src.baseline import baseline
from src.data_loader import DataLoader
from src.representation import TimetableData
from src.initial_solution import greedy
from src.fitness import fitness, fitness_without_soft_contraints
from src.algorithms.simulated_annealing import simulated_annealing
from src.save_solution import save_configuration, save_solution_to_csv
from src.save_solution import save_mapper

def run_solver(case_path):
    """
    Ejecuta el solver sobre una carpeta con estructura:
    assistants/, baseline/, students/, forbidden.csv
    y crea case_path/solution/ para guardar los resultados.
    """

    print("===================================================")
    print(f" Ejecutando solver para el caso: {case_path}")
    print("===================================================\n")

    # Crear carpeta solution/
    solution_dir = os.path.join(case_path, "solution")
    os.makedirs(solution_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    # Parámetros SA
    initial_temp = 100_000.0
    final_temp = 50.0
    alpha = 0.95
    max_iter = 100_000

    save_configuration(
        initial_temp,
        final_temp,
        alpha,
        max_iter,
        solution_dir,
        timestamp,
    )

    # Data Load
    loader = DataLoader(case_path)
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)

    baseline_schedule = baseline(data)
    bas_fitness = fitness(baseline_schedule, data)
    bas_count = fitness_without_soft_contraints(baseline_schedule, data)

    print(f"Baseline fitness: {bas_fitness}")
    print(f"Estudiantes que pueden asistir: {bas_count}")
    print(f"Porcentaje: {round((bas_count * 100) / data.num_students, 2)}%")

    save_solution_to_csv(baseline_schedule, solution_dir, timestamp, "baseline_solution")

    # Initial solution
    initial_solution = greedy(data)

    # SA whitout soft constraints
    print("\n--- Simulated Annealing SIN restricciones suaves ---\n")
    sa_no_soft = simulated_annealing(
        initial_solution, initial_temp, final_temp, alpha, max_iter, data, fitness_without_soft_contraints
    )

    sa_no_fitness = fitness(sa_no_soft, data)
    sa_no_count = fitness_without_soft_contraints(sa_no_soft, data)

    print(f"Fitness (sin soft): {sa_no_fitness}")
    print(f"Estudiantes que pueden asistir: {sa_no_count}")
    print(f"Porcentaje: {round((sa_no_count * 100) / data.num_students, 2)}%")

    save_solution_to_csv(sa_no_soft, solution_dir, timestamp, "sa_without_soft_constraints_solution")

    # SA con restricciones
    print("\n--- Simulated Annealing CON restricciones ---\n")
    sa_best = simulated_annealing(
        initial_solution, initial_temp, final_temp, alpha, max_iter, data, fitness
    )

    best_fit = fitness(sa_best, data)
    best_count = fitness_without_soft_contraints(sa_best, data)

    print(f"Fitness final: {best_fit}")
    print(f"Estudiantes que pueden asistir: {best_count}")
    print(f"Porcentaje: {round((best_count * 100) / data.num_students, 2)}%")

    save_solution_to_csv(sa_best, solution_dir, timestamp, "sa_with_constraints_solution")
    save_mapper(data.mapper, solution_dir, "mapper")



def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <path>")
        sys.exit(1)

    root_path = sys.argv[1]

    if not os.path.isdir(root_path):
        print("✘ El path no es una carpeta válida.")
        sys.exit(1)

    # Detectar carpetas tipo casoX
    cases = [
        os.path.join(root_path, folder)
        for folder in os.listdir(root_path)
        if os.path.isdir(os.path.join(root_path, folder))
    ]

    if len(cases) == 0:
        print("⚠ No se encontraron carpetas de casos. Procesando la carpeta directamente.")
        run_solver(root_path)
        return

    print(f"✔ Se encontraron {len(cases)} casos.\n")

    for case in cases:
        run_solver(case)


if __name__ == "__main__":
    main()
