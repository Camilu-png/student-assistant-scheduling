import csv
import pathlib
from datetime import timedelta


def save_solution_to_csv(solution, filepath, name):
    path_dic = pathlib.Path(filepath)
    with path_dic.joinpath(f"{name}.csv").open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Write solution data
        for s in range(solution.data.num_slots):
            row = []
            for d in range(solution.data.num_days):
                assistants = solution.assistants_in_slot(s, d)
                if assistants.size == 0:
                    row.append("·")
                else:
                    row.append("".join(map(str, assistants)))
            writer.writerow(row)


def save_configuration(initial_temp, final_temp, alpha, max_iter, filepath, timestamp):
    path_dic = pathlib.Path(filepath)
    path_dic.mkdir(parents=True, exist_ok=True)
    with path_dic.joinpath("configurations.txt").open("a") as f:
        f.write(
            f"Initial temperature: {initial_temp}\nFinal temperature: {final_temp}\nAlpha: {alpha}\nMaximun iterations: {max_iter}\n"
        )


def save_solution_mapper(solution, mapper, filepath, name):
    path_dic = pathlib.Path(filepath)
    with path_dic.joinpath(f"{name}.csv").open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Write solution data
        for s in range(solution.data.num_slots):
            row = []
            for d in range(solution.data.num_days):
                assistants = solution.assistants_in_slot(s, d)
                if assistants.size == 0:
                    row.append("·")
                else:
                    assistants = [
                        mapper["assistants_" + str(assistants[i])]
                        for i in range(len(assistants))
                    ]
                    row.append(assistants)
            writer.writerow(row)


def save_mapper(mapper, filepath, name):
    path_dic = pathlib.Path(filepath)
    with path_dic.joinpath(f"{name}_mapper.csv").open("w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")

        # Write mapper data
        for key in mapper:
            writer.writerow([key, mapper[key]])


def save_runtime(filepath, start_iso, end_iso, duration_seconds):
    """Guarda en filepath/runtime.txt el inicio, fin y duración en segundos y formato hh:mm:ss."""
    path_dic = pathlib.Path(filepath)
    path_dic.mkdir(parents=True, exist_ok=True)
    with path_dic.joinpath("runtime.txt").open("a") as f:
        f.write(f"Start: {start_iso}\n")
        f.write(f"End: {end_iso}\n")
        f.write(f"Duration_seconds: {duration_seconds:.6f}\n")
        f.write(f"Duration_hms: {str(timedelta(seconds=duration_seconds))}\n\n")
