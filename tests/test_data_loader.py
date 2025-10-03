from src.data_loader import DataLoader

def print_matrix_3d(matrix, name="Matrix"):
    """
    Imprime una matriz 3D [day][slot][entity] de manera visual.
    Cada entity se muestra con un símbolo.
    """
    symbols = {0: "·", 1: "█", 2: "*"}
    n_days = len(matrix)
    if n_days == 0:
        print(f"{name} is empty.")
        return
    n_blocks = len(matrix[0])
    n_entities = len(matrix[0][0])

    print(f"\n=== {name} ({n_days} days x {n_blocks} slots x {n_entities} entitys) ===")
    for entity_idx in range(n_entities):
        print(f"\nEntity {entity_idx}:")
        for day in range(n_days):
            row_symbols = [symbols.get(matrix[day][block][entity_idx], "?") for block in range(n_blocks)]
            print(" ".join(row_symbols))

def print_matrix_2d(matrix, name="Matrix"):
    """Imprime una matriz 2D [day][slot] de manera visual"""
    symbols = {0: "·", 1: "█"}
    print(f"\n=== {name} ({len(matrix)} days x {len(matrix[0]) if matrix else 0} slots) ===")
    for day in range(len(matrix)):
        row_symbols = [symbols.get(cell, "?") for cell in matrix[day]]
        print(" ".join(row_symbols))

def main():
    loader = DataLoader()
    data = loader.load_all()

    print_matrix_3d(data["students"], "Students")
    print_matrix_3d(data["assistants"], "Assistants")
    print_matrix_2d(data["forbidden"], "Forbidden")

if __name__ == "__main__":
    main()
