import random
import numpy as np

def day_shift(solution, slot: int, day: int, assistant: int):
    days = solution.free_slots(slot)
    index = random.choice(days)
    solution.X[slot, day, assistant] = 0
    solution.X[slot, index, assistant] = 1
    return solution

def slot_shift(solution, slot: int, day: int, assistant: int):
    slots = solution.free_days(day)
    index = random.choice(slots)
    solution.X[slot, day, assistant] = 0
    solution.X[index, day, assistant] = 1
    return solution

def swap_assistants(solution, slot1: int, day1: int, assistant1: int, slot2: int, day2: int, assistant2: int):
    solution.X[slot1, day1, assistant1] = 0
    solution.X[slot2, day2, assistant2] = 0
    solution.X[slot1, day1, assistant2] = 1
    solution.X[slot2, day2, assistant1] = 1
    return solution

def random_move(solution):
    move_type = random.choice([day_shift, slot_shift, swap_assistants])
    print(f"Applying move: {move_type.__name__}")
    assistantship = solution.assistantship()
    if move_type in [day_shift, slot_shift]:
        index = random.randint(0, len(assistantship) - 1)
        slot, day = assistantship[index]
        return move_type(solution, slot, day, index)
    else:
        if len(assistantship) < 2:
            return solution  # Not enough assistants assigned to swap
        index1, index2 = random.sample(range(len(assistantship)), 2)
        slot1, day1 = assistantship[index1]
        slot2, day2 = assistantship[index2]
        return move_type(solution, slot1, day1, index1, slot2, day2, index2)