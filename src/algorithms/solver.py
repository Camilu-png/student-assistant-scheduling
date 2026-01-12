import csv
import os
import pathlib
from pulp import *
from ..data_loader import DataLoader
from ..representation import TimetableData

path = "datos_sensibles/solver/experiment25"


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
                        print(
                            f"Assistant {assistant} assigned to slot {slot} on day {day}"
                        )
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

    # Penalty weights (same as SA)
    W_FREE_DAY = 0.1
    W_SLOT_EVE = 1.0
    W_SLOT_DAY = 0.1
    W_WINDOWS = 0.5
    W_SLOT2 = 0.7

    # Main decision variables
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

    # Student attendance variables
    Y = LpVariable.dicts(
        "Y",
        (
            (student, slot, day)
            for student in students
            for slot in slots
            for day in days
        ),
        cat="Binary",
    )

    # Hard constraints
    # El ayudante no puede asignarse si no está disponible
    for slot in slots:
        for day in days:
            for assistant in assistants:
                if data.assistants[slot, day, assistant] == 1:
                    model += X[slot, day, assistant] == 0

    # No puede asignarse más de un ayudante a un mismo bloque de tiempo
    for slot in slots:
        for day in days:
            model += lpSum(X[slot, day, assistant] for assistant in assistants) <= 1

    # El horario elegido no puede ser un horario prohibido
    for slot in slots:
        for day in days:
            if data.forbidden[slot, day] == 1:
                model += lpSum(X[slot, day, assistant] for assistant in assistants) == 0

    # Cada ayudante debe ser asignado exactamente una vez
    for assistant in assistants:
        model += lpSum(X[slot, day, assistant] for slot in slots for day in days) == 1

    # Student attendance logic
    for student in students:
        for slot in slots:
            for day in days:
                if data.students[slot, day, student] == 0:  # Student is free
                    model += Y[student, slot, day] <= lpSum(
                        X[slot, day, assistant] for assistant in assistants
                    )
                else:
                    model += Y[student, slot, day] == 0

    # El estudiante puede asistir a lo más a una ayudantía por semana
    for student in students:
        model += lpSum(Y[student, slot, day] for slot in slots for day in days) <= 1

    # Objective function: Maximize attendance with penalty terms (like SA)

    # Base attendance
    attendance = lpSum(
        Y[student, slot, day] for student in students for slot in slots for day in days
    )

    # Penalty terms (converted to linear expressions)

    # 1. Free day penalty - penalize students with no classes on a day
    free_day_penalty = 0
    for student in students:
        for day in days:
            total_attendance_day = lpSum(Y[student, slot, day] for slot in slots)
            # If total_attendance_day == 0, add penalty of 0.5
            # Using: penalty = 0.5 * (1 - min(1, total_attendance_day))
            # Linearized as: penalty = 0.5 * max(0, 1 - total_attendance_day)
            # Since total_attendance_day is binary sum, this becomes:
            if total_attendance_day == 0:
                free_day_penalty += (
                    W_FREE_DAY * 0.5 
                )

    # 2. Evening slot penalty (slots 8, 9)
    eve_slot_penalty = 0
    for student in students:
        for slot in [8, 9]:
            for day in days:
                eve_slot_penalty += W_SLOT_EVE * 0.4 * Y[student, slot, day]

    # 3. Day slot penalty (slots 0, 7)
    day_slot_penalty = 0
    for student in students:
        for slot in [0, 7]:
            for day in days:
                day_slot_penalty += W_SLOT_DAY * 0.3 * Y[student, slot, day]

    # 4. Window penalty - simplified linear version
    window_penalty = 0
    for student in students:
        for day in days:
            for slot1 in slots:
                for slot2 in range(slot1 + 2, data.num_slots):
                    # Penalty for having classes at slot1 and slot2 but not slot1+1
                    gap_penalty = (
                        Y[student, slot1, day]
                        + Y[student, slot2, day]
                        - Y[student, slot1 + 1, day]
                    )
                    # Only penalize if gap_penalty > 1 (i.e., there's a gap)
                    window_penalty += W_WINDOWS * (1.0 / 6.0) * gap_penalty

    # 5. Slot2 penalty - adjacent to subject-related activities
    slot2_penalty = 0
    for student in students:
        for slot in slots:
            for day in days:
                if (slot > 0 and data.students[slot - 1, day, student] == 2) or (
                    slot < data.num_slots - 1
                    and data.students[slot + 1, day, student] == 2
                ):
                    slot2_penalty += W_SLOT2 * 0.5 * Y[student, slot, day]

    # Combined objective: maximize attendance, minimize penalties
    model += (
        attendance
        - free_day_penalty
        - eve_slot_penalty
        - day_slot_penalty
        - window_penalty
        - slot2_penalty
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
