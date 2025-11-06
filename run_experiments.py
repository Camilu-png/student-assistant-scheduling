import sys
import pandas as pd
import time
from src.data_loader import DataLoader
from src.representation import TimetableData
from src.initial_solution import greedy
from src.fitness import fitness
from src.algorithms.simulated_annealing import simulated_annealing, validate_solution


def run_sa_experiments(config_path="results/configurations/sa_configurations2.csv"):
    # Cargar configuraciones
    df = pd.read_csv(config_path)
    path = sys.argv[1]

    # Cargar datos base
    loader = DataLoader(path)
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    initial_solution = greedy(data)

    # Recorrer todas las configuraciones
    for idx, cfg in df.iterrows():
        print(f"\n🚀 Ejecutando {cfg.config_id}...")

        start = time.time()

        best_solution = simulated_annealing(
            initial_solution,
            cfg.initial_temp,
            cfg.final_temp,
            cfg.alpha,
            int(cfg.max_iter),
            data,
            fitness,
        )

        elapsed = time.time() - start
        final_fit = fitness(best_solution, data)[0]
        valid = validate_solution(best_solution)[0]

        # Guardar resultados en el DataFrame
        df.at[idx, "time"] = round(elapsed, 2)
        df.at[idx, "final_fitness"] = final_fit
        df.at[idx, "validity"] = valid

        print(
            f"✅ {cfg.config_id}: fitness={final_fit:.2f}, time={elapsed:.2f}s, valid={valid}"
        )

        # Guardar el CSV actualizado cada vez (por si se interrumpe el proceso)
        df.to_csv(config_path, index=False)

    print("\n🏁 Experimentos completados.")
    return df


if __name__ == "__main__":
    run_sa_experiments()
