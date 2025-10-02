import csv
import os
from glob import glob

class DataLoader:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir

    def load_csv_file(self, path):
        """Lee un CSV y devuelve una lista de listas con enteros."""
        data = []
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                data.append([int(cell) for cell in row])
        return data

    def load_folder_matrix(self, folder_name):
        """
        Carga todos los CSV de una carpeta y devuelve una matriz 3D:
        [día][bloque][entidad] con dimensiones automáticas según la data.
        """
        folder_path = os.path.join(self.data_dir, folder_name)
        files = sorted(glob(os.path.join(folder_path, "*.csv")))
        if not files:
            return []

        sample = self.load_csv_file(files[0])
        n_days = len(sample)
        n_blocks = len(sample[0]) if n_days > 0 else 0
        n_entities = len(files)

        matrix = [[[0 for _ in range(n_entities)] for _ in range(n_blocks)] for _ in range(n_days)]

        for idx, f in enumerate(files):
            data = self.load_csv_file(f)
            for day in range(n_days):
                for block in range(n_blocks):
                    matrix[day][block][idx] = data[day][block]

        return matrix

    def load_students_matrix(self):
        return self.load_folder_matrix("students")

    def load_assistants_matrix(self):
        return self.load_folder_matrix("assistants")

    def load_forbidden_matrix(self):
        """Lee forbidden.csv como matriz [día][bloque]"""
        path = os.path.join(self.data_dir, "forbidden.csv")
        return self.load_csv_file(path)

    def load_all(self):
        return {
            "students": self.load_students_matrix(),
            "assistants": self.load_assistants_matrix(),
            "forbidden": self.load_forbidden_matrix()
        }
