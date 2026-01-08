from pulp import *
from ..data_loader import DataLoader
from ..representation import TimetableData


def solve_lp_problem(asignature, data):
    # Create the LP problem
    model = LpProblem(f"Timetabling_{asignature}", LpMaximize)

    # Parameters
    days = range(data.num_days)
    slots = range(data.num_slots)
    assistants = range(data.num_assistants)
    students = range(data.num_students)
    NOCTURN_SLOTS = {8, 9}
    BORDER_SLOTS = {0, 7}

    M = data.num_slots  # Big M constant

    # Variables
    W = LpVariable.dicts(  # Window penalties
        "Windows",
        ((i, j, l) for i in slots for j in days for l in students),
        lowBound=0,
        cat="Continuous",
    )

    D = LpVariable.dicts( #El estudiante asiste a la universidad exclusivamente por la ayudantía.
        "DayFree", ((j, l) for j in days for l in students), cat="Binary"
    )

    # Solution
    X = LpVariable.dicts(
        "X", ((i, j, k) for i in slots for j in days for k in assistants), cat="Binary"
    )

    # Constraints

    # El ayudante debe estar disponible en el horario (i,j) elegido para su asignación.
    for i in slots:
        for j in days:
            for k in assistants:
                if data.assistants[i, j, k] == 0:
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

    """ Soft constraints """
    # Peso por ventanas
    # for i in slots:
    #     for j in days:
    #         for l in students:
    #             model += W[i, j, l] <= lpSum(data.students[p, j, l] for p in range(0, i))
    #             model += W[i, j, l] <= lpSum(data.students[p, j, l] for p in range(i + 1, data.num_slots))
    #             model += W[i, j, l] >= lpSum(data.students[p, j, l] for p in range(0, i)) \
    #                                 + lpSum(data.students[p, j, l] for p in range(i + 1, data.num_slots)) - 1
    # --- Peso por ventanas corregido según tu fórmula ---
    for j in days:
        for l in students:
            # Extraer el horario del estudiante para ese día como una lista
            # Supongamos que 2 significa clase obligatoria
            student_schedule = [data.students[p, j, l] for p in slots]
            
            for i in slots:
                # Si el estudiante NO tiene clase en el bloque i, calculamos la ventana potencial
                if student_schedule[i] == 0:
                    # Search l
                    clases_antes = [p for p, val in enumerate(student_schedule[:i]) if val == 2]
                    l_block = max(clases_antes) if clases_antes else -1
                    
                    # Search m
                    clases_despues = [p + i + 1 for p, val in enumerate(student_schedule[i+1:]) if val == 2]
                    m_block = min(clases_despues) if clases_despues else -1
                    
                    v_l = (i - l_block - 1) if l_block > -1 else 0
                    v_m = (m_block - i - 1) if m_block > -1 else 0
                    total_ventana = v_l + v_m
                    
                    for k in assistants:
                        model += W[i, j, l] >= total_ventana * X[i, j, k]
                else:
                    model += W[i, j, l] == 0

    # Peso por día libre
    for j in days:
        for l in students:
            # Si hay ayudantía ese día y el estudiante no tiene clases → penaliza
            model += D[j, l] <= lpSum(X[i, j, k] for i in slots for k in assistants)
            model += lpSum(data.students[i, j, l] for i in slots) <= M * (1 - D[j, l])


    nocturnal_penalty = lpSum(
        0.4 * X[i, j, k] for i in NOCTURN_SLOTS for j in days for k in assistants
    )
    border_penalty = lpSum(
        0.3 * X[i, j, k] for i in BORDER_SLOTS for j in days for k in assistants
    )

    adjacency_penalty = lpSum(
    0.5 * X[i, j, k]
    for j in days
    for t in slots
    if any(data.students[t, j, l] == 2 for l in students)
    for i in [t - 1, t + 1]
    if 0 <= i < data.num_slots
    for k in assistants
)

    weights = lpSum((1 / 6) * W[i, j, l] for i in slots for j in days for l in students)
    + 0.5 * lpSum(D[j, l] for j in days for l in students)
    + nocturnal_penalty
    + border_penalty
    + adjacency_penalty

    # Objective function: Maximize the number of students that can attend
    attendance = lpSum(
    X[i, j, k]
    for i in slots
    for j in days
    for k in assistants
    for l in students
    if data.students[i, j, l] == 0
)

    model += M*attendance - weights

    # Solve the problem
    model.solve(PULP_CBC_CMD(msg=0))
    print(f"Status: {LpStatus[model.status]}")
    # Print the assignments
    for i in slots:
        for j in days:
            for k in assistants:
                if value(X[i, j, k]) == 1:
                    print(f"Assistant {k} assigned to slot {i} on day {j}")


def solver(case_path):
    print(f"\nSolving LP problem for case: {case_path}")
    loader = DataLoader(case_path)
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    asignature = case_path.split("/")[-1]
    solve_lp_problem(asignature, data)
    print(f"LP problem solved for case: {case_path}\n")
