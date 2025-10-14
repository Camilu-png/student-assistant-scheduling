from src.representation import Solution, TimetableData


def greedy(data: TimetableData) -> Solution:
    solution = Solution(data)
    for assistant in range(data.num_assistants):
        for day in range(data.num_days):
            for slot in range(data.num_slots):
                if data.forbidden[slot, day] == 1:
                    continue  # Slot is forbidden
                if solution.is_assigned(slot, day):
                    continue  # Already assigned
                if data.assistants[slot, day, assistant] == 0:
                    solution.assign(slot, day, assistant)
                    break  # Move to the next assistant
            if solution.assistants_assigned_day(day, assistant):
                break
    return solution
