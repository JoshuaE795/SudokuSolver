# Sudoku Solver

A PyQt6 Sudoku application backed by a custom technique based Sudoku solver.

## Features

- Editable 9×9 Sudoku board
- Sudoku validation for duplicate values
- One-click solve button
- Solve-time measurement
- 1 Example puzzle
- Clear/reset the board
- Custom logical solving engine that shows you each step

## Solver

The solver maintains candidate lists for blank cells and implements multiple Sudoku techniques, including:

- Basic candidate elimination
- Naked/obvious singles
- Naked pairs, triples, and quads
- Hidden singles and hidden subsets
- Pointing pairs and triples
- X-Wing
- XY-Wing
- XYZ-Wing
- Swordfish
- Jellyfish

Main GUI program is kept separate from the solver for indepenent testing

## Run

Install Required Package PyQt6:

`pip install PyQt6`

Then run:

`python main.py`
