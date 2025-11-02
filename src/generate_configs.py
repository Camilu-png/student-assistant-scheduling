import pandas as pd
import itertools

def generate_sa_configurations():
    # Definición de los rangos de parámetros sa_configurations.csv
    initial_temps = [1e5, 5e5, 1e6, 5e6]
    final_temps = [1.0, 10.0, 50.0]
    alphas = [0.95, 0.97, 0.98, 0.99]
    max_iters = [10_000,50_000, 100_000]

    # initial_temps = [1e-1, 1, 10, 50, 100, 500]
    # final_temps = [1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1]
    # alphas = [0.85, 0.90, 0.93, 0.95, 0.97, 0.99, 0.995]
    # max_iters = [1e3, 5e3, 1e4, 5e4, 1e5, 5e5]
    # Generar todas las combinaciones posibles
    configs = list(itertools.product(initial_temps, final_temps, alphas, max_iters))

    # Crear DataFrame con nombres claros
    df = pd.DataFrame(configs, columns=["initial_temp", "final_temp", "alpha", "max_iter"])

    # Agregar un ID único para cada configuración
    df["config_id"] = [f"cfg_{i+1:03d}" for i in range(len(df))]

    # Agregar columnas para registrar resultados experimentales
    df["time"] = None
    df["final_fitness"] = None
    df["validity"] = None  # True / False si la mejor solución es válida

    # Reordenar columnas
    df = df[[
        "config_id",
        "initial_temp",
        "final_temp",
        "alpha",
        "max_iter",
        "time",
        "final_fitness",
        "validity"
    ]]

    # Guardar el CSV en la carpeta deseada
    output_path = "results/sa_configurations2.csv"
    df.to_csv(output_path, index=False)

    print(f"✅ Se generaron {len(df)} configuraciones y se guardaron en '{output_path}'.")
    return df


if __name__ == "__main__":
    df_configs = generate_sa_configurations()
    print(df_configs.head())