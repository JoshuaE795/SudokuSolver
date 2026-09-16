from sudoku_solver import Blank, Puzzle
import sys
from time import perf_counter
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, 
    QFrame, 
    QGridLayout, 
    QHBoxLayout, 
    QLabel, 
    QLineEdit, 
    QMainWindow, 
    QMessageBox, 
    QPushButton, 
    QSizePolicy, 
    QVBoxLayout, 
    QWidget
)


class SolverThread(QThread):
    finished_puzzle:pyqtSignal = pyqtSignal(object, float, object)

    def __init__(self, puzzle:Puzzle) -> None:
        super().__init__()
        self.puzzle:Puzzle = puzzle

    def run(self) -> None:
        start:float = perf_counter()

        try:
            self.puzzle.solve()
            elapsed:float = perf_counter() - start
            self.finished_puzzle.emit(self.puzzle, elapsed, None)
        except Exception as exc:
            elapsed = perf_counter() - start
            self.finished_puzzle.emit(self.puzzle, elapsed, exc)


class SudokuWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sudoku Solver")
        self.setFixedSize(920, 700)
        self.setStyleSheet(
            """
            QMainWindow { background: #313131; }
            QWidget { color: #F2F2F2; font-family: Arial; }
            QFrame#card { background: #262626; border-radius: 14px; }
            QLabel#title { font-size: 28px; font-weight: 700; }
            QLabel#subtitle { color: #A9A9A9; font-size: 13px; }
            QLabel#status { color: #A9A9A9; font-size: 13px; }
            QLabel#stat { font-size: 16px; font-weight: 600; }
            QLineEdit#cell { background: #313131; border: 1px solid #4A4A4A; border-radius: 0px; color: #F2F2F2; font-size: 24px; font-weight: 600; }
            QLineEdit#cell:focus { border: 2px solid #4CAF50; background: #363636; }
            QPushButton { background: #3A3A3A; border: none; border-radius: 9px; padding: 11px 18px; font-size: 14px; font-weight: 600; }
            QPushButton:hover { background: #454545; }
            QPushButton#solve { background: #4CAF50; color: white; }
            QPushButton#solve:hover { background: #5ABD5E; }
            """
        )

        self.cells:list[list[QLineEdit]] = []
        self.solver_thread:SolverThread|None = None

        root:QWidget = QWidget()
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(28, 24, 28, 24)
        root_layout.setSpacing(18)

        header:QHBoxLayout = QHBoxLayout()
        title_box:QVBoxLayout = QVBoxLayout()
        title_box.setSpacing(2)

        title:QLabel = QLabel("Sudoku Solver")
        title.setObjectName("title")
        subtitle:QLabel = QLabel("Logical Sudoku solving powered by a multi-technique solver")
        subtitle.setObjectName("subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        root_layout.addLayout(header)

        content:QHBoxLayout = QHBoxLayout()
        content.setSpacing(20)

        board_card:QFrame = QFrame()
        board_card.setObjectName("card")
        board_card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        board_layout:QVBoxLayout = QVBoxLayout(board_card)
        board_layout.setContentsMargins(18, 18, 18, 18)

        board:QWidget = QWidget()
        board_grid:QGridLayout = QGridLayout(board)
        board_grid.setContentsMargins(0, 0, 0, 0)
        board_grid.setSpacing(0)

        for row in range(9):
            row_cells: list[QLineEdit] = []
            for col in range(9):
                cell = QLineEdit()
                cell.setObjectName("cell")
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFixedSize(57, 57)
                cell.setMaxLength(1)
                cell.setFont(QFont("Arial", 24, QFont.Weight.DemiBold))
                cell.textChanged.connect(lambda text, r=row, c=col: self.sanitize_cell(text, r, c))
                board_grid.addWidget(cell, row, col)
                row_cells.append(cell)
            self.cells.append(row_cells)

        board_layout.addWidget(board)
        content.addWidget(board_card)

        side_card:QFrame = QFrame()
        side_card.setObjectName("card")

        side_layout:QVBoxLayout = QVBoxLayout(side_card)
        side_layout.setContentsMargins(22, 22, 22, 22)
        side_layout.setSpacing(14)

        side_title:QLabel = QLabel("Solver")
        side_title.setStyleSheet("font-size: 19px; font-weight: 700;")
        side_layout.addWidget(side_title)

        self.status:QLabel = QLabel("Ready")
        self.status.setObjectName("status")
        side_layout.addWidget(self.status)

        self.time_stat:QLabel = QLabel("Solve time: —")
        self.time_stat.setObjectName("stat")
        side_layout.addWidget(self.time_stat)

        self.filled_stat:QLabel = QLabel("Filled cells: 0 / 81")
        self.filled_stat.setObjectName("stat")
        side_layout.addWidget(self.filled_stat)

        side_layout.addSpacing(10)

        info:QLabel = QLabel("Enter digits 1–9 directly into the grid.\nLeave cells empty when a number is unknown.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #A9A9A9; font-size: 13px; line-height: 1.3;")
        side_layout.addWidget(info)

        side_layout.addStretch()
        content.addWidget(side_card, 1)
        root_layout.addLayout(content)

        buttons:QHBoxLayout = QHBoxLayout()
        buttons.setSpacing(10)

        self.solve_button = QPushButton("Solve Puzzle")
        self.solve_button.setObjectName("solve")
        self.solve_button.clicked.connect(self.solve_puzzle)
        self.check_button = QPushButton("Check")
        self.check_button.clicked.connect(self.check_puzzle)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_board)
        self.example_button = QPushButton("Example")
        self.example_button.clicked.connect(self.load_example)

        buttons.addWidget(self.solve_button)
        buttons.addWidget(self.check_button)
        buttons.addWidget(self.clear_button)
        buttons.addWidget(self.example_button)

        root_layout.addLayout(buttons)

    def sanitize_cell(self, text: str, row: int, col: int) -> None:
        if text and text not in "123456789":
            self.cells[row][col].blockSignals(True)
            self.cells[row][col].clear()
            self.cells[row][col].blockSignals(False)
        self._update_filled_stat()

    def update_filled_stat(self) -> None:
        filled = sum(bool(cell.text()) for row in self.cells for cell in row)
        self.filled_stat.setText(f"Filled cells: {filled} / 81")

    def read_grid(self) -> list[list[int|Blank]]:
        grid: list[list[int | Blank]] = []
        for row in self.cells:
            grid.append([int(cell.text()) if cell.text() else Blank() for cell in row])
        return grid

    def has_duplicate(self, values: list[int]) -> bool:
        return len(values) != len(set(values))

    def validate_grid(self) -> tuple[bool, str]:
        values = [[int(cell.text()) if cell.text() else 0 for cell in row] for row in self.cells]

        for row in range(9):
            nums = [n for n in values[row] if n]
            if self._has_duplicate(nums):
                return False, f"Duplicate number in row {row + 1}."

        for col in range(9):
            nums = [values[row][col] for row in range(9) if values[row][col]]
            if self._has_duplicate(nums):
                return False, f"Duplicate number in column {col + 1}."

        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                nums = [values[row][col] for row in range(box_row, box_row + 3) for col in range(box_col, box_col + 3) if values[row][col]]
                if self._has_duplicate(nums):
                    return False, "Duplicate number inside a 3×3 box."

        return True, "Puzzle is valid."

    def _write_grid(self, puzzle: Puzzle) -> None:
        for row in range(9):
            for col in range(9):
                value = puzzle[row][col]
                self.cells[row][col].setText(str(value) if isinstance(value, int) else "")
        self.update_filled_stat()

    def solve_puzzle(self) -> None:
        valid, message = self.validate_grid()
        if not valid:
            self.status.setText("Invalid puzzle")
            QMessageBox.warning(self, "Invalid Sudoku", message)
            return

        puzzle:Puzzle = Puzzle(self._read_grid())
        self._set_solving_state(True)
        self.status.setText("Solving…")
        self.time_stat.setText("Solve time: running…")

        self.solver_thread:SolverThread = SolverThread(puzzle)
        self.solver_thread.finished_puzzle.connect(self._solver_finished)
        self.solver_thread.finished.connect(self._thread_finished)
        self.solver_thread.start()

    def set_solving_state(self, solving: bool) -> None:
        for row in self.cells:
            for cell in row:
                cell.setReadOnly(solving)
        self.solve_button.setEnabled(not solving)
        self.check_button.setEnabled(not solving)
        self.clear_button.setEnabled(not solving)
        self.example_button.setEnabled(not solving)

    def solver_finished(self, puzzle: Puzzle, elapsed: float, error: object) -> None:
        self.set_solving_state(False)
        self.time_stat.setText(f"Solve time: {elapsed:.5f}s")

        if error is not None:
            self.status.setText("Solver error")
            QMessageBox.critical(self, "Solver Error", f"The solver encountered an error:\n\n{error}")
            return

        self._write_grid(puzzle)
        if puzzle.is_solved():
            self.status.setText("Solved successfully")
        else:
            self.status.setText("Could not solve using current techniques")
            QMessageBox.information(self, "Not Solved", "The current logical solver could not finish this puzzle.")

    def thread_finished(self) -> None:
        if self.solver_thread is not None:
            self.solver_thread.deleteLater()
            self.solver_thread = None

    def check_puzzle(self) -> None:
        valid, message = self._validate_grid()
        self.status.setText(message)
        if valid:
            QMessageBox.information(self, "Sudoku Check", message)
        else:
            QMessageBox.warning(self, "Sudoku Check", message)

    def clear_board(self) -> None:
        for row in self.cells:
            for cell in row:
                cell.clear()
        self.status.setText("Ready")
        self.time_stat.setText("Solve time: —")
        self.update_filled_stat()

    def load_example(self) -> None:
        example = [
            [0, 0, 0, 4, 0, 9, 0, 0, 0],
            [0, 0, 0, 0, 6, 0, 0, 0, 0],
            [2, 0, 0, 5, 0, 0, 0, 4, 0],
            [5, 0, 8, 0, 0, 3, 0, 0, 4],
            [3, 0, 0, 6, 0, 7, 0, 0, 9],
            [0, 0, 7, 0, 0, 0, 0, 3, 6],
            [9, 0, 6, 0, 4, 0, 0, 1, 0],
            [0, 0, 0, 7, 0, 0, 0, 0, 0],
            [0, 0, 3, 8, 0, 0, 5, 0, 0],
        ]
        for row in range(9):
            for col in range(9):
                self.cells[row][col].setText(str(example[row][col]) if example[row][col] else "")
        self.status.setText("Example loaded")
        self.time_stat.setText("Solve time: —")
        self._update_filled_stat()


def main() -> None:
    app:QApplication = QApplication(sys.argv)
    window:SudokuWindow = SudokuWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
