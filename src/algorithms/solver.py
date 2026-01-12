import csv
import os
import pathlib
from pulp import *
from ..data_loader import DataLoader
from ..representation import TimetableData
from ..fitness import penalty_windows

path = "datos_sensibles/solver/experiment30"


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

    # Additional auxiliary variables
    # Z[student] = 1 if student attends any tutorial, 0 otherwise
    Z = LpVariable.dicts(
        "Z",
        (student for student in students),
        cat="Binary",
    )

    # Link Z to Y: Z[student] = 1 if student attends any tutorial
    for student in students:
        total_student_attendance = lpSum(
            Y[student, slot, day] for slot in slots for day in days
        )
        model += Z[student] <= total_student_attendance  # If no attendance, Z = 0
        model += (
            Z[student] >= total_student_attendance
        )  # If attendance > 0, Z = 1 (since max attendance = 1)

    # Pre-calculate window penalties for each possible assignment (Opción 2)
    print("Pre-calculating window penalties...")
    window_penalties = {}
    for student in students:
        for slot in slots:
            for day in days:
                if data.students[slot, day, student] == 0:  # Student is free
                    penalty = penalty_windows(data, slot, day, student)
                    window_penalties[(student, slot, day)] = penalty
                else:
                    window_penalties[(student, slot, day)] = 0

    print(f"Calculated {len(window_penalties)} window penalty values")

    # Hard constraints
    # El ayudante no puede asignarse si no está disponible
    # CORREGIDO: 1 = ocupado/no disponible, 0 = libre/disponible
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
            # Correct modeling: D >= 1 - total_attendance_day and D <= 1 - total_attendance_day
            # But since total_attendance_day can be 0 or 1 (student attends at most 1 tutorial per week)
            # We need: D = 1 - total_attendance_day for this day
            model += D[student, day] == 1 - total_attendance_day

    # Objective function: Maximize number of students who can attend (like SA)

    # Primary objective: number of students who attend at least one tutorial
    student_attendance = lpSum(Z[student] for student in students)

    # Secondary objectives: penalties (weighted much lower to be tiebreakers)

    # 1. Free day penalty - properly linearized
    free_day_penalty = (
        W_FREE_DAY
        * 0.5
        * lpSum(D[student, day] for student in students for day in days)
    )

    # 2. Evening slot penalty (slots 8, 9) - direct linear penalty
    eve_slot_penalty = (
        W_SLOT_EVE
        * 0.4
        * lpSum(
            Y[student, slot, day]
            for student in students
            for slot in [8, 9]
            if slot < data.num_slots  # Only include existing slots
            for day in days
        )
    )

    # 3. Day slot penalty (slots 0, 7) - direct linear penalty
    day_slot_penalty = (
        W_SLOT_DAY
        * 0.3
        * lpSum(
            Y[student, slot, day]
            for student in students
            for slot in [0, 7]
            if slot < data.num_slots  # Only include existing slots
            for day in days
        )
    )

    # 4. Slot2 penalty - adjacent to subject-related activities (FIXED)
    slot2_penalty = 0
    for student in students:
        for slot in slots:
            for day in days:
                penalty_coefficient = 0
                # Check if adjacent slots have subject-related activities (value 2)
                if slot > 0 and data.students[slot - 1, day, student] == 2:
                    penalty_coefficient += W_SLOT2 * 0.5
                if (
                    slot < data.num_slots - 1
                    and data.students[slot + 1, day, student] == 2
                ):
                    penalty_coefficient += W_SLOT2 * 0.5

                if penalty_coefficient > 0:
                    slot2_penalty += penalty_coefficient * Y[student, slot, day]

    # 5. Window penalty - using pre-calculated values (Opción 2)
    window_penalty = W_WINDOWS * lpSum(
        window_penalties.get((student, slot, day), 0) * Y[student, slot, day]
        for student in students
        for slot in slots
        for day in days
    )

    # Combined objective: maximize student attendance (primary), minimize penalties (secondary)
    # Scale penalties down so they act as tiebreakers, not primary objectives
    penalty_scale = 0.01  # Make penalties much smaller than student count
    model += student_attendance - penalty_scale * (
        free_day_penalty
        + eve_slot_penalty
        + day_slot_penalty
        + slot2_penalty
        + window_penalty
    )

    # Solve the problem
    model.solve()

    # Debug information
    print(f"Solver status: {LpStatus[model.status]}")
    print(f"Objective value: {value(model.objective)}")

    # Calculate actual metrics like SA does
    students_attending = sum(
        1
        for student in students
        if any(value(Y[student, slot, day]) == 1 for slot in slots for day in days)
    )
    print(f"Students who can attend: {students_attending}")
    print(f"Percentage: {round((students_attending * 100) / data.num_students, 2)}%")

    # Show penalty breakdown
    if model.status == LpStatusOptimal:
        free_penalty_val = (
            sum(value(D[student, day]) for student in students for day in days)
            * W_FREE_DAY
            * 0.5
        )
        eve_penalty_val = (
            sum(
                value(Y[student, slot, day])
                for student in students
                for slot in [8, 9]
                if slot < data.num_slots
                for day in days
            )
            * W_SLOT_EVE
            * 0.4
        )
        day_penalty_val = (
            sum(
                value(Y[student, slot, day])
                for student in students
                for slot in [0, 7]
                if slot < data.num_slots
                for day in days
            )
            * W_SLOT_DAY
            * 0.3
        )

        # Calculate window penalty value
        window_penalty_val = W_WINDOWS * sum(
            window_penalties.get((student, slot, day), 0) * value(Y[student, slot, day])
            for student in students
            for slot in slots
            for day in days
        )

        print(f"Free day penalty: {free_penalty_val}")
        print(f"Evening slot penalty: {eve_penalty_val}")
        print(f"Day slot penalty: {day_penalty_val}")
        print(f"Window penalty: {window_penalty_val}")

        total_penalty = (
            free_penalty_val + eve_penalty_val + day_penalty_val + window_penalty_val
        )
        print(f"Total penalty: {total_penalty}")
        print(
            f"Final fitness (students - penalties): {students_attending - total_penalty}"
        )

    save_solution(model, X, slots, days, assistants, asignature)


def solver(case_path):
    print(f"\nSolving LP problem for case: {case_path}")
    loader = DataLoader(case_path)
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    asignature = case_path.split("/")[-1]
    solve_lp_problem(asignature, data)
    print(f"LP problem solved for case: {case_path}\n")
