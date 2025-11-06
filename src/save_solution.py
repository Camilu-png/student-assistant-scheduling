import csv
import pathlib


def save_solution_to_csv(solution, filepath, fitness_value, students_count, percentage):
    """Save solution to CSV file in the same format as view() method"""
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
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
    path_dic = pathlib.Path("results").joinpath(
        "solutions", filepath.replace("/", "_"), timestamp
    )
    path_dic.mkdir(parents=True, exist_ok=True)
    with path_dic.joinpath("configurations.txt").open("a") as f:
        f.write(
            f"Initial temperature: {initial_temp}\nFinal temperature: {final_temp}\nAlpha: {alpha}\nMaximun iterations: {max_iter}\n"
        )
