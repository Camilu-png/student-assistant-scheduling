from src.representation import Solution

def baseline(data):
    # Genera solución inicial vacía
    baseline = Solution(data)
    # Recorre los archivos por ayudante y asigna el bloque que tiene asignado
    for assistant in range(data.num_assistants):
        for day in range(data.num_days):
            for slot in range(data.num_slots):
                if data.baseline[slot, day, assistant] == 1:
                    baseline.assign(slot,day,assistant)
    return baseline

