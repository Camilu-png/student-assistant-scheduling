import numpy as np
import pandas as pd
import itertools


def generate_weight_configurations():
    W_FREE_DAY = np.linspace(0.1, 1, 7)
    W_SLOT_EVE = np.linspace(0.5, 1, 7)
    W_SLOT_DAY = np.linspace(0.1, 1, 7)
    W_WINDSOWS = np.linspace(0.5, 1, 7)
    W_SLOT2 = np.linspace(0.1, 1, 7)

    configs = list(
        itertools.product(W_FREE_DAY, W_SLOT_EVE, W_SLOT_DAY, W_WINDSOWS, W_SLOT2)
    )
    df = pd.DataFrame(
        configs,
        columns=["W_FREE_DAY", "W_SLOT_EVE", "W_SLOT_DAY", "W_WINDSOWS", "W_SLOT2"],
    )

    # Generate all possible combinations of the parameters
    df["config_id"] = [f"cfg_{i + 1:03d}" for i in range(len(df))]

    df["time"] = None
    df["final_fitness"] = None
    df["total"] = None
    df["conflictos"] = None
    df["validity"] = None

    df = df[
        [
            "config_id",
            "W_FREE_DAY",
            "W_SLOT_EVE",
            "W_SLOT_DAY",
            "W_WINDSOWS",
            "W_SLOT2",
            "time",
            "final_fitness",
            "total",
            "conflictos",
            "validity",
        ]
    ]

    output_path = "results/configurations/weight/7.csv"
    df.to_csv(output_path, index=False)

    print(f"Se generaron {len(df)} configuraciones y se guardaron en '{output_path}'.")
    return df


if __name__ == "__main__":
    df_configs = generate_weight_configurations()
    print(df_configs.head())
