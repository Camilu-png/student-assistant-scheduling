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