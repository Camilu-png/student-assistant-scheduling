import sys
import pandas as pd
import time
from src.data_loader import DataLoader
from src.representation import TimetableData
from src.initial_solution import greedy
from src.fitness import fitness, fitness_without_soft_constraints
from src.algorithms.simulated_annealing import simulated_annealing, validate_solution


def run_weight_experiments(config_path="results/configurations/weight/7.csv"):
    # Load configurations
    df = pd.read_csv(config_path)
    path = sys.argv[1]

    # Ensure result columns exist
    result_cols = ["time", "final_fitness", "validity", "total", "conflictos"]
    for col in result_cols:
        if col not in df.columns:
            df[col] = pd.NA

    # Determine first row without results (use 'final_fitness' as marker)
    not_done = df["final_fitness"].isna()
    if not not_done.any():
        print(
            "\nℹ️ Todos los experimentos ya tienen resultados. No hay nada que ejecutar."
        )
        return df

    # Find integer location of first not-done row
    start_loc = df.index.get_loc(not_done[not_done].index[0])
    if start_loc > 0:
        try:
            cfg_id = df.iloc[start_loc].config_id
        except Exception:
            cfg_id = start_loc
        print(
            f"\n⏭️ Saltando {start_loc} experimentos ya completados. Reanudando en la fila {start_loc} (config_id={cfg_id})."
        )

    # Load data and generate initial solution
    loader = DataLoader(path)
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    initial_solution = greedy(data)

    # Run experiments starting from first not-done row
    for idx, cfg in df.iloc[start_loc:].iterrows():
        print(f"\n🚀 Ejecutando {cfg.config_id}...")

        start = time.time()

        # Build a fitness wrapper with the weights from the configuration.
        # Note: the generated CSV uses the column name `W_WINDSOWS` (typo),
        # map it to the `W_WINDOWS` parameter expected by `fitness`.
        w_free = float(cfg.W_FREE_DAY)
        w_slot_eve = float(cfg.W_SLOT_EVE)
        w_slot_day = float(cfg.W_SLOT_DAY)
        # support both possible spellings just in case
        if "W_WINDOWS" in df.columns:
            w_windows = float(cfg.W_WINDOWS)
        else:
            w_windows = float(cfg.W_WINDSOWS)
        w_slot2 = float(cfg.W_SLOT2)

        weighted_fitness = (
            lambda sol,
            data,
            W_FREE_DAY=w_free,
            W_SLOT_EVE=w_slot_eve,
            W_SLOT_DAY=w_slot_day,
            W_WINDOWS=w_windows,
            W_SLOT2=w_slot2: fitness(
                sol, data, W_FREE_DAY, W_SLOT_EVE, W_SLOT_DAY, W_WINDOWS, W_SLOT2
            )
        )

        # SA hyperparameter sets: use the same defaults as in `main.py`.
        # Set 1 (main.py): initial_temp1=100.0, final_temp1=1.0, alpha1=0.9, max_iter1=10000
        # Set 2 (main.py): initial_temp2=10.0, final_temp2=1.0, alpha2=0.85, max_iter2=10000
        # Command-line overrides:
        # - 4 extra args: initial1 final1 alpha1 max1 (applies to both sets)
        # - 8 extra args: initial1 final1 alpha1 max1 initial2 final2 alpha2 max2
        if len(sys.argv) >= 6:
            # 4 args provided -> override set1 and apply to both
            initial_temp1 = float(sys.argv[2])
            final_temp1 = float(sys.argv[3])
            alpha1 = float(sys.argv[4])
            max_iter1 = int(sys.argv[5])
            initial_temp2 = initial_temp1
            final_temp2 = final_temp1
            alpha2 = alpha1
            max_iter2 = max_iter1
            if len(sys.argv) >= 10:
                # Full override of both sets
                initial_temp2 = float(sys.argv[6])
                final_temp2 = float(sys.argv[7])
                alpha2 = float(sys.argv[8])
                max_iter2 = int(sys.argv[9])
        else:
            initial_temp1 = 100.0
            final_temp1 = 1.0
            alpha1 = 0.9
            max_iter1 = 10000
            initial_temp2 = 10.0
            final_temp2 = 1.0
            alpha2 = 0.85
            max_iter2 = 10000

        # Run two SA experiments (like `main.py`) and pick the best
        sa_best1 = simulated_annealing(
            initial_solution,
            initial_temp1,
            final_temp1,
            alpha1,
            int(max_iter1),
            data,
            weighted_fitness,
        )

        sa_best2 = simulated_annealing(
            initial_solution,
            initial_temp2,
            final_temp2,
            alpha2,
            int(max_iter2),
            data,
            weighted_fitness,
        )

        option1 = (
            weighted_fitness(sa_best1, data),
            fitness_without_soft_constraints(sa_best1, data),
            sa_best1,
        )
        option2 = (
            weighted_fitness(sa_best2, data),
            fitness_without_soft_constraints(sa_best2, data),
            sa_best2,
        )

        print("Option 1:")
        sa_best1.view()
        print(f"Fitness final: {option1[0]}")
        print(f"Estudiantes que pueden asistir: {option1[1]}")
        print(f"Porcentaje: {round((option1[1] * 100) / data.num_students, 2)}%")

        print("Option 2:")
        sa_best2.view()
        print(f"Fitness final: {option2[0]}")
        print(f"Estudiantes que pueden asistir: {option2[1]}")
        print(f"Porcentaje: {round((option2[1] * 100) / data.num_students, 2)}%")

        # Choose best by fitness (primary), then by count (secondary). Avoid comparing Solution objects directly.
        if option1[0] > option2[0]:
            best_fit, best_count, best_solution = option1
        elif option2[0] > option1[0]:
            best_fit, best_count, best_solution = option2
        else:
            # fitness tie -> use count as tiebreaker
            if option1[1] > option2[1]:
                best_fit, best_count, best_solution = option1
            elif option2[1] > option1[1]:
                best_fit, best_count, best_solution = option2
            else:
                # full tie -> pick option1 by default
                best_fit, best_count, best_solution = option1

        print(f"Fitness final: {best_fit}")
        print(f"Estudiantes que pueden asistir: {best_count}")
        print(f"Porcentaje: {round((best_count * 100) / data.num_students, 2)}%")

        elapsed = time.time() - start
        final_fit = weighted_fitness(best_solution, data)
        valid = validate_solution(best_solution)[0]

        # Update results in DataFrame
        df.at[idx, "time"] = round(elapsed, 2)
        df.at[idx, "final_fitness"] = final_fit
        df.at[idx, "validity"] = valid
        df.at[idx, "total"] = data.num_students
        df.at[idx, "conflictos"] = data.num_students - fitness_without_soft_constraints(
            best_solution, data
        )

        print(
            f"✅ {cfg.config_id}: fitness={final_fit:.2f}, time={elapsed:.2f}s, valid={valid}"
        )

        # Save intermediate results
        df.to_csv(config_path, index=False)

    print("\n🏁 Experimentos completados.")
    return df


if __name__ == "__main__":
    run_weight_experiments()
