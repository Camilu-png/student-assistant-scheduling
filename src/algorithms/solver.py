import csv
import os
import pathlib
from pulp import *
from ..data_loader import DataLoader
from ..representation import TimetableData

path = "datos_sensibles/solver/experiment27"


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

    # Auxiliary variables for penalties
    # Free day penalty variables
    D = LpVariable.dicts(
        "D",
        ((student, day) for student in students for day in days),
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

    # Auxiliary constraints for penalty modeling
    # Free day penalty: D[student, day] = 1 if student has no tutorial on that day
    for student in students:
        for day in days:
            total_attendance_day = lpSum(Y[student, slot, day] for slot in slots)
            # D = 1 if total_attendance_day = 0, D = 0 otherwise
            model += D[student, day] >= 1 - total_attendance_day  # If attendance=0, D>=1
            model += D[student, day] <= 1 - total_attendance_day  # If attendance>0, D=0

    # Objective function: Maximize attendance with properly modeled penalties

    # Base attendance
    attendance = lpSum(
        Y[student, slot, day] for student in students for slot in slots for day in days
    )

    # 1. Free day penalty - properly linearized
    free_day_penalty = W_FREE_DAY * 0.5 * lpSum(
        D[student, day] for student in students for day in days
    )

    # 2. Evening slot penalty (slots 8, 9) - direct linear penalty
    eve_slot_penalty = W_SLOT_EVE * 0.4 * lpSum(
        Y[student, slot, day] 
        for student in students 
        for slot in [8, 9]
        for day in days
    )

    # 3. Day slot penalty (slots 0, 7) - direct linear penalty  
    day_slot_penalty = W_SLOT_DAY * 0.3 * lpSum(
        Y[student, slot, day]
        for student in students
        for slot in [0, 7]
        for day in days
    )

    # 4. Slot2 penalty - adjacent to subject-related activities
    slot2_penalty = 0
    for student in students:
        for slot in slots:
            for day in days:
                adjacent_penalty = 0
                # Check if adjacent slots have subject-related activities (value 2)
                if slot > 0 and data.students[slot - 1, day, student] == 2:
                    adjacent_penalty += W_SLOT2 * 0.5
                if slot < data.num_slots - 1 and data.students[slot + 1, day, student] == 2:
                    adjacent_penalty += W_SLOT2 * 0.5
                
                if adjacent_penalty > 0:
                    slot2_penalty += adjacent_penalty * Y[student, slot, day]

    # Combined objective: maximize attendance, minimize penalties
    model += (
        attendance
        - free_day_penalty
        - eve_slot_penalty
        - day_slot_penalty
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
