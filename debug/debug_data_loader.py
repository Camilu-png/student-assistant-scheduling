from src.data_loader import DataLoader
import numpy as np

def print_matrix_3d(matrix, name="Matrix"):
    symbols = np.array(["·", "█", "*"])
    if matrix.size == 0:
        print(f"{name} is empty.")
        return
    n_blocks, n_days, n_entities = matrix.shape

    print(f"\n=== {name} ({n_days} days x {n_blocks} slots x {n_entities} entitys) ===")
    for entity_idx in range(n_entities):
        print(f"\nEntity {entity_idx}:")
        entity_matrix = matrix[:, :, entity_idx]
        clipped = np.clip(entity_matrix, 0, len(symbols) - 1)
        symbol_matrix = symbols[clipped]
        for row in symbol_matrix:
            print(" ".join(row))

def print_matrix_2d(matrix, name="Matrix"):
    symbols = np.array(["·", "█"])
    print(f"\n=== {name} ({len(matrix[0]) if matrix.size > 0 else 0} days x {len(matrix)} slots) ===")
    if matrix.size == 0:
        return
    clipped = np.clip(matrix, 0, len(symbols) - 1)
    symbol_matrix = symbols[clipped]
    for row in symbol_matrix:
        print(" ".join(row))

def main():
    loader = DataLoader()
    data = loader.load_all()

    print_matrix_3d(data["students"], "Students")
    print_matrix_3d(data["assistants"], "Assistants")
    print_matrix_2d(data["forbidden"], "Forbidden")

if __name__ == "__main__":
    main()