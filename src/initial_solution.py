from src.representation import Solution, TimetableData
import numpy as np

def greedy(data: TimetableData) -> Solution:
    solution = Solution(data)
    for assistant in range(data.num_assistants):
        for day in range(data.num_days):
            for slot in range(data.num_slots):
                if data.forbidden[day, slot] == 1:
                    continue  # Slot is forbidden
                if solution.is_assigned(day, slot):
                    continue  # Already assigned
                solution.assign(day, slot, assistant)
                break
            if solution.assistants_assigned_day(day, assistant):
                break
    return solution

