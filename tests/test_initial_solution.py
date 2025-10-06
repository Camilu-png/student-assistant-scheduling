import pytest
from src.data_loader import DataLoader
from src.representation import TimetableData
from src.initial_solution import greedy

@pytest.fixture
def solution():
    loader = DataLoader()
    data_dict = loader.load_all()
    data = TimetableData(**data_dict)
    return greedy(data)

def test_only_one_assistant_per_slot(solution):
    num_slots = solution.data.num_slots
    num_days = solution.data.num_days
    for i in range(num_days):
        for j in range(num_slots):
            assistants = solution.assistants_in_slot(i, j)
            assert len(assistants) <= 1, f"More than one assistant assigned to day {i}, slot {j}"

def test_no_assistant_in_forbidden_slots(solution):
    num_slots = solution.data.num_slots
    num_days = solution.data.num_days
    forbidden = solution.data.forbidden
    for i in range(num_days):
        for j in range(num_slots):
            if forbidden[j][i] == 1:
                assistants = solution.assistants_in_slot(i, j)
                assert len(assistants) == 0, f"Assistant assigned to forbidden slot at day {i}, slot {j}"

def test_assistants_assigned_only_to_free_slots(solution):
    num_slots = solution.data.num_slots
    num_days = solution.data.num_days

    for i in range(num_days):
        for j in range(num_slots):
            if solution.is_assigned(i, j):
                assistant = solution.assistants_in_slot(i, j)[0]
                slot_value = solution.data.assistants[j, i, assistant] 
                assert slot_value == 0, f"Assistant {assistant} assigned to a busy slot on day {i}, slot {j}"
