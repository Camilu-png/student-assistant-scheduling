# Version 3.0
def penalty_free_day(data, student, day):
    for slot in range(data.num_slots):
        if data.students[slot, day, student] == 1:
            return 0
    return 0.5  # Penalty for a day without classes


def penalty_slot(slot):
    if slot == 0 or slot == 8 or slot == 9:
        return 0.4
    elif slot == 7:
        return 0.3
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
    return total_windows / 6


def penalty_slot2(data, slot, day, student):
    left = slot - 1 >= 0 and data.students[slot - 1, day, student] == 2
    right = slot + 1 < data.num_slots and data.students[slot + 1, day, student] == 2
    return 0.5 if (left or right) else 0


def fitness(solution, data):
    fitness_count = 0
    for student in range(data.num_students):
        fitness = float("-inf")
        for day in range(data.num_days):
            for slot in range(data.num_slots):
                if data.students[slot, day, student] == 0 and solution.is_assigned(
                    slot, day
                ):
                    w = (
                        penalty_free_day(data, student, day)
                        + penalty_slot(slot)
                        + penalty_windows(data, slot, day, student)
                        + penalty_slot2(data, slot, day, student)
                    )

                    if fitness < 1 - w:
                        fitness = 1 - w
        if fitness != float("-inf"):
            fitness_count += fitness
    return fitness_count


def fitness_without_soft_contraints(solution, data):
    fitness_count = 0
    for student in range(data.num_students):
        assigned = False
        for day in range(data.num_days):
            for slot in range(data.num_slots):
                if data.students[slot, day, student] == 0 and solution.is_assigned(
                    slot, day
                ):
                    assigned = True
                    break
            if assigned:
                fitness_count += 1
                break
    return fitness_count
