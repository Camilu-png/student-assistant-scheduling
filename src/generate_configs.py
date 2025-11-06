import pandas as pd
import itertools


def generate_sa_configurations():
    # Definition of parameter ranges for sa_configurations.csv
    initial_temps = [1e5, 5e5, 1e6, 5e6]
    final_temps = [1.0, 10.0, 50.0]
    alphas = [0.95, 0.97, 0.98, 0.99]
    max_iters = [10_000, 50_000, 100_000]

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

    output_path = "results/configurations/sa_configurations2.csv"
    df.to_csv(output_path, index=False)

    print(f"Se generaron {len(df)} configuraciones y se guardaron en '{output_path}'.")
    return df


if __name__ == "__main__":
    df_configs = generate_sa_configurations()
    print(df_configs.head())
