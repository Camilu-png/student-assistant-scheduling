import numpy as np
from dataclasses import dataclass

@dataclass
class TimetableData:
    students: np.ndarray  # 3D array [slot][day][student]
    assistants: np.ndarray  # 3D array [slot][day][assistant]
    forbidden: np.ndarray  # 2D array [slot][day]

    @property
    def num_slots(self):
        return self.students.shape[0]
    @property
    def num_days(self):
        return self.students.shape[1]
    @property
    def num_students(self):
        return self.students.shape[2]
    @property
    def num_assistants(self):
        return self.assistants.shape[2]
    
class Solution:
    def __init__(self, data: TimetableData):
        self.data = data
        self.X = np.zeros((data.num_days, data.num_slots, data.num_assistants), dtype=int)

    def assign(self, day: int, slot: int, assistant: int):
        self.X[day, slot, assistant] = 1

    def unassign(self, day: int, slot: int, assistant: int):
        self.X[day, slot, assistant] = 0

    def is_assigned(self, day: int, slot: int) -> bool:
        return np.sum(self.X[day, slot, :]) > 0
    
    def assistants_in_slot(self, day: int, slot: int) -> np.ndarray:
        return np.where(self.X[day, slot, :] == 1)[0]
    
    def assistants_assigned_day(self,day:int, assistant: int) -> int:
        return np.sum(self.X[day, :, assistant]) == 1
