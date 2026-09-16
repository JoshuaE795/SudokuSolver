# Sudoku Solver

A PyQt6 Sudoku application backed by a custom logical Sudoku solver.

## Features

- Editable 9×9 Sudoku board
- Direct keyboard input
- Sudoku validation for duplicate values
- One-click solving
- Solve-time measurement
- Example puzzle loader
- Clear/reset controls
- Custom logical solving engine rather than a simple brute-force-only implementation

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

The GUI is intentionally separated from the solving engine so the algorithm can be tested independently.

## Run

Install PyQt6:

`pip install PyQt6`

Then run:

`python main.py`
