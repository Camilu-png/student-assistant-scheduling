import numpy as np
from src.data_loader import DataLoader

def test_load_all_returns_expected_keys():
    loader = DataLoader()
    data = loader.load_all()
    assert isinstance(data, dict)
    assert {"students", "assistants", "forbidden"} <= set(data.keys())

def test_matrices_have_valid_shapes():
    loader = DataLoader()
    data = loader.load_all()
    assert data["students"].ndim == 3
    assert data["assistants"].ndim == 3
    assert data["forbidden"].ndim == 2
