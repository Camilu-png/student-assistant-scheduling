# Student Assistant Scheduling

Optimization-based approach for university teaching assistant scheduling.

## Project Overview

This project addresses the **University Teaching Assistant Scheduling Problem**, aiming to assign assistance sessions in a way that maximizes student attendance while respecting availability constraints of both students and assistants, as well as institutionally forbidden time slots.

The problem is modeled as a combinatorial optimization problem and solved using **Simulated Annealing**, allowing an effective exploration of the solution space and avoiding poor local optima.

This work is part of an academic research project focused on educational timetabling.

---

## Problem Description

Universities often face difficulties when scheduling teaching assistant sessions due to:

- Heterogeneous student availability
- Limited assistant availability
- Forbidden time slots (e.g., institutional restrictions)
- Conflicts with subject-related activities

A poorly designed schedule can significantly reduce attendance, negatively impacting student learning. This project proposes an algorithmic solution to mitigate this issue.

---

## Methodology

- **Problem type:** Educational Timetabling Problem
- **Optimization approaches:**
  - **Simulated Annealing**, used to explore the solution space and generate high-quality feasible schedules.
  - **Mathematical Programming**, implemented using the **PuLP** library to formulate the problem as a constrained optimization model.
- **Objective:** Maximize student attendance while respecting hard constraints
- **Constraints considered:**
  - Student availability
  - Assistant availability
  - Forbidden time slots
  - Subject-related activities (weighted preferences)

---

## Data Format

The `data/` folder contains CSV files encoding availability information.  
Each file consists of **50 cells**, corresponding to combinations of days and time blocks.

### Student availability files

- `0`: Free slot
- `1`: Occupied slot
- `2`: Occupied with subject-related activity

### Assistant availability files

- `0`: Free slot
- `1`: Occupied slot

### `forbidden.csv`

- `0`: Slot available for assignment
- `1`: Forbidden slot (no assignment allowed)

---

## Project Structure

```text
.
├── data/          # Input CSV files
├── results/       # Experimental results and parameter configuration outputs
├── notebooks/     # Analysis and visualization notebooks
├── src/           # Core algorithm and utilities
├── main.py        # Entry point
├── pyproject.toml
└── README.md
```

## Usage

1. Place all required CSV files in the `data/` folder
2. Run the algorithm scripts to generate optimized schedules
3. The program generates:
   - One that maximizes student attendance
   - One that strictly respects all availability constraints

## Environment Setup with uv

```bash
# Install  dependencies
uv sync

# Run the algorithm
uv run python main.py <path_to_data_folder>
```

## Analysis

Additional analysis, comparisons, and visualizations are available in the Jupyter notebooks located in the `notebooks/` folder.

## Technologies

- Python
- PuLP (Linear Programming / Optimization Modeling)
- Simulated Annealing
- NumPy / Pandas
- Jupyter Notebook
- uv
