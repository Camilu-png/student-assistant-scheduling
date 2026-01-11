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

path = "datos_sensibles/solver/experiment23"

def save_solution(model, X, slots, days, assistants, case_path):
    solution_dir = os.path.join(path, case_path)
    os.makedirs(solution_dir, exist_ok=True)
    path_dic = pathlib.Path(solution_dir)
    print(f"Status: {LpStatus[model.status]}")
    with path_dic.joinpath(f"solver.csv").open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Print the assignments
        for slot in slots:
            row = []
            for day in days:
                assigned = "·"
                for assistant in assistants:
                    if value(X[slot, day, assistant]) == 1:
                        print(f"Assistant {assistant} assigned to slot {slot} on day {day}")
                        assigned = assistant
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
        "X",
        (
            (slot, day, assistant)
            for slot in slots
            for day in days
            for assistant in assistants
        ),
        cat="Binary",
    )

    # Constraints

    # El ayudante no puede asignarse si no está disponible
    for slot in slots:
        for day in days:
            for assistant in assistants:
                # El ayudante está disponible
                if data.assistants[slot, day, assistant] == 1:
                    model += X[slot, day, assistant] == 0

    # No puede asignarse más de un ayudante a un mismo bloque de tiempo.
    for slot in slots:
        for day in days:
            model += lpSum(X[slot, day, assistant] for assistant in assistants) <= 1

    # El horario elegido no puede ser un horario prohibido
    for slot in slots:
        for day in days:
            if data.forbidden[slot, day] == 1:
                model += lpSum(X[slot, day, assistant] for assistant in assistants) == 0

    """ Extra constraints """
    # Cada ayudante debe ser asignado
    for assistant in assistants:
        model += lpSum(X[i, j, assistant] for i in slots for j in days) == 1

    # Objective function with penalties
    model += lpSum(
        1
        - penalty_free_day(data, student, day) * W_FREE_DAY
        - penalty_slot_eve(slot) * W_SLOT_EVE
        - penalty_slot_day(slot) * W_SLOT_DAY
        - penalty_windows(data, slot, day, student) * W_WINDOWS
        - penalty_slot2(data, slot, day, student) * W_SLOT2
        for student in students
        for day in days
        for slot in slots
        if data.students[slot, day, student] == 0 and lpSum(X[slot, day, assistant] for assistant in assistants) == 1
    )

    # Solve the problem
    model.solve()
    save_solution(model, X, slots, days, assistants, asignature)


def solver(case_path):
    print(f"\nSolving LP problem for case: {case_path}")
    loader = DataLoader(case_path)
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    asignature = case_path.split("/")[-1]
    solve_lp_problem(asignature, data)
    print(f"LP problem solved for case: {case_path}\n")
