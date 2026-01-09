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
    W_FREE_DAY = 0.1
    W_SLOT_EVE = 1.0
    W_SLOT_DAY = 0.1
    W_WINDOWS = 0.5
    W_SLOT2 = 0.7
    # Variables

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

    # Objective function with penalties
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
