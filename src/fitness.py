import numpy as np

def penalty_free_day(data, student, day):
    for slot in range(data.num_slots):
        if data.students[slot, day, student] == 1:
            return 0
    return 0.5 # Penalty for a day without classes

def penalty_slot(slot):
    if slot == 0 or slot == 8 or slot == 9:
        return 0.8
    elif slot == 7:
        return 0.4
    else:
        return 0
def penalty_windows(data, slot_, day, student):
    total_windows = 0
    window_l = 0
    window_m = 0
    found_assignment = False 
    for slot in range(data.num_slots):
        if slot_ == slot:
            found_assignment = True
            if window_l == slot_:
                continue
            else:
                total_windows = window_l
        elif found_assignment:
            if data.students[slot, day, student] == 1:
                total_windows += window_m
                break
            else:
                window_m += 1
        else:
            if data.students[slot, day, student] == 1:
                window_l = 0
            else:
                window_l += 1
    return total_windows/5

def fitness(solution, data):
    fitness_count = 0
    for student in range(data.num_students):
        fitness = float('-inf')
        for day in range(data.num_days):
            for slot in range(data.num_slots):
                if data.students[slot, day, student] == 0 and solution.is_assigned(day, slot):
                    w = penalty_free_day(data, student, day) + penalty_slot(slot) + penalty_windows(data, slot, day, student)
                if fitness < 1 - w:
                    fitness = 1 - w
        fitness_count += fitness
    return fitness_count