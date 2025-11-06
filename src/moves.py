import random


def day_shift(solution, slot: int, day: int, assistant: int):
    days = solution.free_slots(slot)
    index = random.choice(days)
    new_solution = solution.copy()
    new_solution.X[slot, day, assistant] = 0
    new_solution.X[slot, index, assistant] = 1
    return new_solution


def slot_shift(solution, slot: int, day: int, assistant: int):
    slots = solution.free_days(day)
    index = random.choice(slots)
    new_solution = solution.copy()
    new_solution.X[slot, day, assistant] = 0
    new_solution.X[index, day, assistant] = 1
    return new_solution


def swap_assistants(
    solution,
    slot1: int,
    day1: int,
    assistant1: int,
    slot2: int,
    day2: int,
    assistant2: int,
):
    new_solution = solution.copy()
    new_solution.X[slot1, day1, assistant1] = 0
    new_solution.X[slot2, day2, assistant2] = 0
    new_solution.X[slot1, day1, assistant2] = 1
    new_solution.X[slot2, day2, assistant1] = 1
    return new_solution


def random_move(solution):
    new_solution = solution.copy()
    move_type = random.choice([day_shift, slot_shift, swap_assistants])
    assistantship = new_solution.assistantship()
    if move_type in [day_shift, slot_shift] or len(assistantship) < 2:
        if move_type.__name__ == "swap_assistants":
            move_type = random.choice([day_shift, slot_shift])

        index = random.randint(0, len(assistantship) - 1)
        slot, day = assistantship[index]
        return move_type(new_solution, slot, day, index)
    else:
        index1, index2 = random.sample(range(len(assistantship)), 2)
        slot1, day1 = assistantship[index1]
        slot2, day2 = assistantship[index2]
        return move_type(new_solution, slot1, day1, index1, slot2, day2, index2)
