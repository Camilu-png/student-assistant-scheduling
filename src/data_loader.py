import csv
import os
import numpy as np

from glob import glob


class DataLoader:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def load_csv_file(self, path):
        """Lee un CSV y devuelve un array numpy de enteros."""
        with open(path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            data = [list(map(int, row)) for row in reader]
        return np.array(data, dtype=int)

    def load_folder_matrix(self, folder_name):
        """
        Carga todos los CSV de una carpeta y devuelve una matriz 3D:
        [day][slot][entity] con dimensiones automáticas según la data.
        """
        folder_path = os.path.join(self.data_dir, folder_name)
        files = sorted(
            glob(os.path.join(folder_path, "*.csv")),
            key=lambda x: int(os.path.splitext(os.path.basename(x))[0]),
        )
        if not files:
            print(f"No CSV files found in {folder_path}")
            return np.array([])

        matrices = [self.load_csv_file(f) for f in files]
        matrix_3d = np.stack(matrices, axis=2)
        return matrix_3d

    def load_students_matrix(self):
        return self.load_folder_matrix("students")

    def load_assistants_matrix(self):
        return self.load_folder_matrix("assistants")

    def load_baseline_matrix(self):
        return self.load_folder_matrix("baseline")

    def load_forbidden_matrix(self):
        """Lee forbidden.csv como matriz numpy [day][slot]"""
        path = os.path.join(self.data_dir, "forbidden.csv")
        return self.load_csv_file(path)

    def load_all(self):
        return {
            "students": self.load_students_matrix(),
            "assistants": self.load_assistants_matrix(),
            "forbidden": self.load_forbidden_matrix(),
            "baseline": self.load_baseline_matrix(),
        }
