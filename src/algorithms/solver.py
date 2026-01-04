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

    # I = slots        # i
    # J = days           # j
    # K = assistants      # k
    # L = students        # l

    # Variable
        # Solution
    X = LpVariable.dicts(
    "X",
    ((i, j, k) for i in slots for j in days for k in assistants),
    cat="Binary"
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
    if any(data.students[i, j, l] == 1 for l in students):
        for k in assistants:
            model += X[i, j, k] == 0


        # El horario elegido no puede ser un horario prohibido
    for i in slots:
        for j in days:
            if data.forbidden[i, j] == 1:
                for k in assistants:
                    model += X[i, j, k] == 0


    ''' Cositas extras '''
        # Cada ayudante debe ser asignado
    for k in assistants:
        model += lpSum(X[i, j, k] for i in slots for j in days) == 1


    # Objective function: Maximize the number of students that can attend
    model += 0

    # Solve the problem
    model.solve()
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