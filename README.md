# student-assistant-scheduling
An algorithm for planning university assistance schedules

## Project Overview
This project aims to develop algorithms for assigning university assistance schedules to maximize the number of students who can attend. The scheduling problem considers the availability of both students and assistants, as well as forbidden time slots. The implemented methods include Tabu Search, Simulated Annealing, and Evolutionary Algorithms.

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
3. **The output will be a suggested schedule that respects all availability constraints while maximizing student participation**

## Algorithms

- Tabu Search: Explores the solution space while avoiding cycles through a tabu list.

- Simulated Annealing: Accepts worse solutions probabilistically to escape local optima.

- Evolutionary Algorithm: Uses population-based search with selection, crossover, and mutation to evolve solutions.