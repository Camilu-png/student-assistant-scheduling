import numpy as np
import pandas as pd
import itertools


def generate_sa_configurations():
    # Definition of parameter ranges for sa_configurations.csv
    # initial_temps = [1e2, 1e3, 1e4, 1e5, 1e6]
    # final_temps = [1e-3, 1e-2, 1e-1, 1, 10]
    # alphas = [0.90, 0.93, 0.95, 0.97, 0.98, 0.99, 0.995, 0.999]
    # max_iters = [5_000, 10_000, 50_000, 100_000, 250_000]

    # initial_temps = [1e-1, 1, 10, 50, 100, 500]
    # final_temps = [1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1]
    # alphas = [0.85, 0.90, 0.93, 0.95, 0.97, 0.99, 0.995]
    # max_iters = [1e3, 5e3, 1e4, 5e4, 1e5, 5e5]

    initial_temps = np.logspace(2, 6, num=6)  # [1e2, 1e3, 1e4, 1e5, 1e6]
    final_temps = np.logspace(-3, 1, num=5)  # [1e-3, 1e-2, 1e-1, 1, 10]
    alphas = [0.90, 0.93, 0.95, 0.97, 0.98, 0.99, 0.995, 0.999]
    max_iters = [5_000, 10_000, 50_000, 100_000, 250_000]

    configs = list(itertools.product(initial_temps, final_temps, alphas, max_iters))

    df = pd.DataFrame(
        configs, columns=["initial_temp", "final_temp", "alpha", "max_iter"]
    )

    # Generate all possible combinations of the parameters
    df["config_id"] = [f"cfg_{i + 1:03d}" for i in range(len(df))]

    df["time"] = None
    df["final_fitness"] = None
    df["validity"] = None

    df = df[
        [
            "config_id",
            "initial_temp",
            "final_temp",
            "alpha",
            "max_iter",
            "time",
            "final_fitness",
            "validity",
        ]
    ]

    output_path = "results/configurations/experimento3-INF285.csv"
    df.to_csv(output_path, index=False)

    print(f"Se generaron {len(df)} configuraciones y se guardaron en '{output_path}'.")
    return df


if __name__ == "__main__":
    df_configs = generate_sa_configurations()
    print(df_configs.head())
