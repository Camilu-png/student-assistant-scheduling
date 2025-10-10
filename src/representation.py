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
        self.X = np.zeros((data.num_slots, data.num_days, data.num_assistants), dtype=int)

    def assign(self, slot: int, day: int, assistant: int):
        self.X[slot, day, assistant] = 1

    def unassign(self, slot: int, day: int, assistant: int):
        self.X[slot, day, assistant] = 0

    def is_assigned(self, slot: int, day: int) -> bool:
        return self.X[slot, day, :].any()
    
    def assistants_in_slot(self, slot: int, day: int) -> np.ndarray:
        return np.where(self.X[slot, day, :] == 1)[0]
    
    def assistants_assigned_day(self, day: int, assistant: int) -> bool:
        return self.X[:, day, assistant].sum() == 1
    
    def free_slots(self, slot: int) -> list:
        return np.where(np.sum(self.X[slot, :, :], axis=1) == 0)[0]
    
    def free_days(self, day: int) -> list:
        return np.where(np.sum(self.X[:, day, :], axis=1) == 0)[0]
    
    def assistantship(self) -> np.array:
        assistantship = np.zeros((self.data.num_assistants,), dtype=tuple)
        for day in range(self.data.num_days):
            for slot in range(self.data.num_slots):
                if self.is_assigned(slot, day):
                    assistant = self.assistants_in_slot(slot, day)[0]
                    assistantship[assistant] = (slot, day)
        return assistantship