import csv
import os
import pathlib
from pulp import *
from ..data_loader import DataLoader
from ..representation import TimetableData
from ..fitness import (
    penalty_windows,
    penalty_free_day,
    penalty_slot_eve,
    penalty_slot_day,
    penalty_slot2,
)

path = "datos_sensibles/solver/experiment18"


def save_solution(model, X, slots, days, assistants, case_path):
    solution_dir = os.path.join(path, case_path)
    os.makedirs(solution_dir, exist_ok=True)
    path_dic = pathlib.Path(solution_dir)
    print(f"Status: {LpStatus[model.status]}")
    with path_dic.joinpath(f"solver.csv").open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Print the assignments
        for i in slots:
            row = []
            for j in days:
                assigned = "·"
                for k in assistants:
                    if value(X[i, j, k]) == 1:
                        print(f"Assistant {k} assigned to slot {i} on day {j}")
                        assigned = k
                        break
                row.append(assigned)
            writer.writerow(row)


def solve_lp_problem(asignature, data):
    # Create the LP problem
    model = LpProblem(f"Timetabling_{asignature}", LpMaximize)

    # Parameters
    days = range(data.num_days)
    slots = range(data.num_slots)
    assistants = range(data.num_assistants)
    students = range(data.num_students)
    # NOCTURN_SLOTS = {8, 9}
    # BORDER_SLOTS = {0, 7}
    W_FREE_DAY = 0.1
    W_SLOT_EVE = 1.0
    W_SLOT_DAY = 0.1
    W_WINDOWS = 0.5
    W_SLOT2 = 0.7
    # Variables
    # W = LpVariable.dicts(
    #     "Windows",
    #     ((i, j, l) for i in slots for j in days for l in students),
    #     lowBound=0,
    #     cat="Continuous",
    # )

    # D = LpVariable.dicts(  # El estudiante asiste a la universidad exclusivamente por la ayudantía.
    #     "DayFree", ((j, l) for j in days for l in students), cat="Continuous"
    # )

    # Solution
    X = LpVariable.dicts(
        "X", ((i, j, k) for i in slots for j in days for k in assistants), cat="Binary"
    )

    # Constraints

    # El ayudante debe estar disponible en el horario (i,j) elegido para su asignación.
    for i in slots:
        for j in days:
            for k in assistants:
                # El ayudante está disponible
                if data.assistants[i, j, k] == 0:
                    # Se puede o no asignar a este bloque
                    model += X[i, j, k] <= 1
                # El ayudante no está disponible
                elif data.assistants[i, j, k] == 1:
                    model += X[i, j, k] == 0

    # No puede asignarse más de un ayudante a un mismo bloque de tiempo.
    for i in slots:
        for j in days:
            model += lpSum(X[i, j, k] for k in assistants) <= 1

    # El horario elegido no puede coincidir con las clases obligatorias de ningún estudiante matriculado en la asignatura.
    for i in slots:
        for j in days:
            if any(data.students[i, j, l] == 2 for l in students):
                for k in assistants:
                    model += X[i, j, k] == 0

    # El horario elegido no puede ser un horario prohibido
    for i in slots:
        for j in days:
            if data.forbidden[i, j] == 1:
                for k in assistants:
                    model += X[i, j, k] == 0

    """ Extra constraints """
    # Cada ayudante debe ser asignado
    for k in assistants:
        model += lpSum(X[i, j, k] for i in slots for j in days) == 1

    # """ Soft constraints """
    # # Peso por ventanas
    # for l in students:
    #     for j in days:
    #         for i in slots:
    #             if data.students[i, j, l] == 0:
    #                 model += W[i, j, l] == penalty_windows(
    #                         data=data, slot_=i, day=j, student=l
    #                     )

    # # Peso por día libre
    # for j in days:
    #     for l in students:
    #         # Contar si el estudiante tiene clases ese día (2 = obligatorio)
    #         # tiene_clase = 1 if any(data.students[i, j, l] == 2 or data.students[i,j,l] == 0 for i in slots) else 0

    #         # if tiene_clase == 0:
    #         #     # Si no tiene clase, D es 1 si se asigna una ayudantía ese día
    #         #     model += D[(j, l)] == lpSum(
    #         #         X[(i, j, k)] for i in slots for k in assistants
    #         #     )
    #         # else:
    #         #     # Si tiene clase, no hay penalización por día libre
    #         model += D[(j, l)] == penalty_free_day(
    #             data=data, student=l, day=j
    #         )

    # nocturnal_penalty = lpSum(
    #     0.4 * X[i, j, k] for i in NOCTURN_SLOTS for j in days for k in assistants
    # )
    # border_penalty = lpSum(
    #     0.3 * X[i, j, k] for i in BORDER_SLOTS for j in days for k in assistants
    # )

    # adjacency_penalty = lpSum(
    #     0.5 * X[i, j, k]
    #     for j in days
    #     for t in slots
    #     if any(data.students[t, j, l] == 2 for l in students)
    #     for i in [t - 1, t + 1]
    #     if 0 <= i < data.num_slots
    #     for k in assistants
    # )

    # total_weights = (
    #     lpSum(W[i, j, l] for l in students) * 0.5
    #     + lpSum(D[j, l]  for l in students) * 0.1
    #     + nocturnal_penalty * 1.0
    #     + border_penalty * 0.1
    #     + adjacency_penalty * 0.7
    # )

    # # Objective function: Maximize the number of students that can attend
    # attendance = lpSum(
    #     X[i, j, k]
    #     for i in slots
    #     for j in days
    #     for k in assistants
    #     for l in students
    #     if data.students[i, j, l] == 0
    # )

    # model += attendance - total_weights

    model += lpSum(
        X[i, j, k]
        - penalty_free_day(data=data, student=l, day=j) * W_FREE_DAY
        - penalty_slot_eve(slot=i) * W_SLOT_EVE
        - penalty_slot_day(slot=i) * W_SLOT_DAY
        - penalty_windows(data=data, slot_=i, day=j, student=l) * W_WINDOWS
        - penalty_slot2(data=data, slot=i, day=j, student=l) * W_SLOT2
        for i in slots
        for j in days
        for k in assistants
        for l in students
    )

    # Solve the problem
    model.solve(PULP_CBC_CMD(msg=1))
    save_solution(model, X, slots, days, assistants, asignature)


def solver(case_path):
    print(f"\nSolving LP problem for case: {case_path}")
    loader = DataLoader(case_path)
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    asignature = case_path.split("/")[-1]
    solve_lp_problem(asignature, data)
    print(f"LP problem solved for case: {case_path}\n")
