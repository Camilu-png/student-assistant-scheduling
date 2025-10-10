import numpy as np

def penalty_windows(solution, data):
    total_windows = 0
    for day in range(data.num_days):
        for student in range(data.num_students):
            window_l = 0
            window_m = 0
            found_assignment = False
            for slot in range(data.num_slots):
                if data.students[slot, day, student] == 1:
                    if solution.is_assigned(day, slot):
                        found_assignment = True
                        total_windows += window_l + window_m
                        window_l = 0
                        window_m = 0
                    else:
                        if not found_assignment:
                            window_l += 1
                        else:
                            window_m += 1
    return total_windows

def penalty_free(solution, data):
    penalty = 0
    assigned_days = [day for day in range(data.num_days) if np.any(solution.X[day, :, :])]
    for student in range(data.num_students):
        if len(assigned_days) == 0:
            return 0
        else:
            if all(np.sum(data.students[:, day, student]) == 0 for day in assigned_days):
                penalty += 1
    return penalty

def penalty_undesired_blocks(solution, data):
    penalty = 0
    for day in range(data.num_days):
        for slot in range(data.num_slots):
            if data.forbidden[slot, day] == 1 and solution.is_assigned(day, slot):
                penalty += 1
    return penalty

def penalty_solt7(solution):
    penalty = 0
    for day in range(solution.data.num_days):
        if np.sum(solution.X[day, 7, :]) > 0:
            penalty += 1
    return penalty

def count_students(solution, data):
    count = 0
    for student in range(data.num_students):
        can_attend = False
        for day in range(data.num_days):
            for slot in range(data.num_slots):
                if data.students[slot, day, student] == 1 and solution.is_assigned(day, slot):
                    can_attend = True
                    break
            if can_attend:
                break
        if can_attend:
            count += 1
    return count

def fitness(solution, data):
    w1 = penalty_windows(solution, data)/5
    w2 = penalty_free(solution,data)*0.5
    w3 = penalty_undesired_blocks(solution, data)*0.6
    w4 = penalty_solt7(solution)*0.4

    fitness_value = count_students(solution, data) - (w1 + w2 + w3 + w4)
    return fitness_value


