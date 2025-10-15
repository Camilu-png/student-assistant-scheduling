import pytest
from src.data_loader import DataLoader


@pytest.fixture
def loader():
    """Create an instance of DataLoader."""
    return DataLoader()


def test_load_all_returns_dict(loader):
    """Check that load_all returns a dictionary."""
    data = loader.load_all()
    assert isinstance(data, dict)


def test_load_all_has_expected_keys(loader):
    """Check that the dictionary contains the expected keys."""
    data = loader.load_all()
    expected_keys = {"students", "assistants", "forbidden"}
    assert expected_keys <= set(data.keys())


def test_students_assistants_shapes(loader):
    """Check that students and assistants are 3D arrays with valid shapes."""
    data = loader.load_all()
    students = data["students"]
    assistants = data["assistants"]
    assert students.ndim == 3
    assert assistants.ndim == 3
    # Ensure each dimension has at least one element
    assert all(s > 0 for s in students.shape)
    assert all(a > 0 for a in assistants.shape)


def test_forbidden_shape(loader):
    """Check that forbidden is a 2D array with valid dimensions."""
    data = loader.load_all()
    forbidden = data["forbidden"]
    assert forbidden.ndim == 2
    assert all(f > 0 for f in forbidden.shape)
