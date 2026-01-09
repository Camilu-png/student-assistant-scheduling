import sys
import pandas as pd
import time
from src.data_loader import DataLoader
from src.representation import TimetableData
from src.initial_solution import greedy
from src.fitness import fitness
from src.algorithms.simulated_annealing import simulated_annealing, validate_solution


def run_sa_experiments(config_path="results/configurations/experimento3-INF295.csv"):
    # Load configurations
    df = pd.read_csv(config_path)
    path = sys.argv[1]

    # Load data and generate initial solution
    loader = DataLoader(path)
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    initial_solution = greedy(data)

    # Run experiments
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
        final_fit = fitness(best_solution, data)
        valid = validate_solution(best_solution)[0]

        # Update results in DataFrame
        df.at[idx, "time"] = round(elapsed, 2)
        df.at[idx, "final_fitness"] = final_fit
        df.at[idx, "validity"] = valid

        print(
            f"✅ {cfg.config_id}: fitness={final_fit:.2f}, time={elapsed:.2f}s, valid={valid}"
        )

        # Save intermediate results
        df.to_csv(config_path, index=False)

    print("\n🏁 Experimentos completados.")
    return df


if __name__ == "__main__":
    run_sa_experiments()
