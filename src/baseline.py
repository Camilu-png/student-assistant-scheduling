from src.representation import Solution

""" Generate a baseline solution based on predefined assignments in the data. """


def baseline(data):
    baseline = Solution(data)
    for assistant in range(data.num_assistants):
        for day in range(data.num_days):
            for slot in range(data.num_slots):
                if data.baseline[slot, day, assistant] == 1:
                    baseline.assign(slot, day, assistant)
    return baseline
