# Student Assistant Scheduling
An algorithm for planning university assistance schedules

## Project Overview
This project seeks to develop an algorithm for assigning university assistance schedules to maximize the number of students who can attend. The scheduling problem considers the availability of both students and assistants, as well as forbidden time slots. The implemented method is simulated annealing.

## Data
The data folder contains CSV files representing the availability of assistants, students, and forbidden time slots. Each file has 50 cells, where each cell corresponds to a day and a time block.

#### Files for students:
- 0: The slot is free
- 1: The slot is occupied
- 2: The slot is occupied with an activity related to the subject

#### Files for assistants:
- 0: The slot is free
- 1: The slot is occupied

#### forbidden.csv file:
- 0: The slot is available for assignment
- 1: The slot is forbidden, so no schedule can be assigned in this slot

## Usage

1. Place the CSV files in the data folder
2. Run the algorithm scripts to generate optimized schedules
3. **The result will be an analysis of the suggested schedule and two proposals obtained by the algorithm, one that maximizes attendance and another that also respects all availability restrictions.**

## Environment Setup with uv

```bash
# Install all required
uv sync

# Run Python scripts
uv run python main.py {data path}
```

## Analysis

For further analysis of the solutions, review the Jupyter notebooks located in the notebooks folder.