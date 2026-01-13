import csv
import os
import pathlib
from pulp import *
from ..data_loader import DataLoader
from ..representation import TimetableData
from ..fitness import penalty_windows

path = "datos_sensibles/solver/experiment32"


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

    """ Auxiliary variables for penalties """
    # Free day penalty variables
    D = LpVariable.dicts(
        "D",
        ((student, day) for student in students for day in days),
        cat="Binary",
    )

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
        model += Z[student] <= total_student_attendance
        model += Z[student] >= total_student_attendance  # If attendance > 0, Z = 1

    # Pre-calculate window penalties for each possible assignment
    window_penalties = {}
    for student in students:
        for slot in slots:
            for day in days:
                if data.students[slot, day, student] == 0:  # Student is free
                    penalty = penalty_windows(data, slot, day, student)
                    window_penalties[(student, slot, day)] = penalty
                else:
                    window_penalties[(student, slot, day)] = 0

    """ Hard constraints """
    # The assistant cannot be assigned if they are not available
    for slot in slots:
        for day in days:
            for assistant in assistants:
                if data.assistants[slot, day, assistant] == 1:
                    model += X[slot, day, assistant] == 0

    # Cannot assign more than one assistant to the same time block
    for slot in slots:
        for day in days:
            model += lpSum(X[slot, day, assistant] for assistant in assistants) <= 1

    # The chosen schedule cannot be a forbidden schedule
    for slot in slots:
        for day in days:
            if data.forbidden[slot, day] == 1:
                model += lpSum(X[slot, day, assistant] for assistant in assistants) == 0

    # Each assistant must be assigned exactly once
    for assistant in assistants:
        model += lpSum(X[slot, day, assistant] for slot in slots for day in days) == 1

    # Student attendance logic
    for student in students:
        for slot in slots:
            for day in days:
                if data.students[slot, day, student] == 0:
                    model += Y[student, slot, day] <= lpSum(
                        X[slot, day, assistant] for assistant in assistants
                    )
                else:
                    model += Y[student, slot, day] == 0

    # The student can attend at most one tutorial per week
    for student in students:
        model += lpSum(Y[student, slot, day] for slot in slots for day in days) <= 1

    student_attendance = lpSum(Z[student] for student in students)

    """Auxiliary constraints for penalty modeling"""
    # Free day penalty: D[student, day] = 1 if student has no classes on that day AND attends tutorial
    for student in students:
        for day in days:
            # Check if student has any classes on this day
            has_classes_today = any(
                data.students[slot, day, student] == 1 for slot in slots
            )

            if not has_classes_today:  # Student is free all day
                total_attendance_day = lpSum(Y[student, slot, day] for slot in slots)
                model += D[student, day] == total_attendance_day
            else:
                model += D[student, day] == 0

    """ Objective function with penalties """
    # 1. Free day penalty
    free_day_penalty = (
        W_FREE_DAY
        * 0.5
        * lpSum(D[student, day] for student in students for day in days)
    )

    # 2. Evening slot penalty (slots 8, 9)
    eve_slot_penalty = (
        W_SLOT_EVE
        * 0.4
        * lpSum(
            Y[student, slot, day]
            for student in students
            for slot in [8, 9]
            for day in days
        )
    )

    # 3. Day slot penalty (slots 0, 7)
    day_slot_penalty = (
        W_SLOT_DAY
        * 0.3
        * lpSum(
            Y[student, slot, day]
            for student in students
            for slot in [0, 7]
            for day in days
        )
    )

    # 4. Slot2 penalty
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

    # 5. Window penalty - using pre-calculated values
    window_penalty = W_WINDOWS * lpSum(
        window_penalties.get((student, slot, day), 0) * Y[student, slot, day]
        for student in students
        for slot in slots
        for day in days
    )

    # Combined objective: maximize student attendance (primary), minimize penalties (secondary)
    # Use same penalty scale as SA for fair comparison
    model += student_attendance - (
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

    save_solution(model, X, slots, days, assistants, asignature)


def solver(case_path):
    print(f"\nSolving LP problem for case: {case_path}")
    loader = DataLoader(case_path)
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    asignature = case_path.split("/")[-1]
    solve_lp_problem(asignature, data)
    print(f"LP problem solved for case: {case_path}\n")
