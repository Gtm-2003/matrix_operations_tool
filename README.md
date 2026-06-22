# Matrix Operations Tool

Command-line and interactive matrix operations utility using NumPy and Rich.

Features:
- Addition, subtraction, multiplication
- Transpose, determinant, inverse
- Rank, eigenvalues, solve Ax=b
- Interactive TUI with pretty-printed results
- CSV load/save support

Quick start:

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Interactive mode:

```bash
python matrix_tool.py --interactive
```

3. Command-line example:

```bash
python matrix_tool.py --op add --a "1 2;3 4" --b "5 6;7 8"
```

Save result to CSV:

```bash
python matrix_tool.py --op mul --a "1 2;3 4" --b "5 6;7 8" --save result.csv
```

Contributing and tests:

```bash
pip install -r requirements.txt
pytest -q
```

GUI (Tkinter)
----------------

A lightweight GUI is available via `gui.py`. It lets you load matrices from CSV, paste or type matrices, choose an operation, compute results, and save results to CSV.

Run the GUI from the project root:

```bash
python gui.py
```

Notes:
- `Tkinter` is bundled with standard Python on Windows. If you see import errors, ensure your Python installation includes Tcl/Tk.
- The GUI uses the same parsing rules as the CLI: rows can be separated by `;` or newlines, values by spaces or commas.

# Matrix Operations Tool

A simple Python interactive tool for matrix operations using NumPy.

## Features

- Matrix addition
- Matrix subtraction
- Matrix multiplication
- Matrix transpose
- Matrix determinant calculation

## Usage

1. Install NumPy if needed:
   ```bash
   pip install numpy
   ```

2. Run the tool:
   ```bash
   python matrix_tool.py
   ```

3. Enter matrices using rows separated by semicolons. Example:
   ```text
   1 2 3; 4 5 6; 7 8 9
   ```

4. Choose the operation from the menu and view the result.
