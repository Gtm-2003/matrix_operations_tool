import argparse
import csv
from typing import Optional, Tuple, List

import numpy as np
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()


def parse_matrix(input_str: str) -> np.ndarray:
    """Parse a matrix from a string. Rows may be separated by ';' or newlines.

    Values can be space- or comma-separated. Example: "1 2 3; 4 5 6" or
    "1,2,3\n4,5,6".
    """
    if not input_str or not input_str.strip():
        raise ValueError("Matrix cannot be empty.")

    # Normalize separators
    rows = [r.strip() for r in input_str.strip().replace('\n', ';').split(';') if r.strip()]
    parsed_rows: List[List[float]] = []
    for row in rows:
        # allow comma or whitespace separators
        parts = [p for p in row.replace(',', ' ').split() if p]
        parsed_rows.append([float(p) for p in parts])

    if not parsed_rows:
        raise ValueError("No data parsed for matrix.")

    width = len(parsed_rows[0])
    if any(len(r) != width for r in parsed_rows):
        raise ValueError("All rows must have the same number of values.")

    return np.array(parsed_rows, dtype=float)


def load_matrix_from_csv(path: str) -> np.ndarray:
    with open(path, 'r', newline='') as f:
        reader = csv.reader(f)
        data = [[float(cell) for cell in row] for row in reader if row]
    if not data:
        raise ValueError("CSV file contains no data")
    width = len(data[0])
    if any(len(r) != width for r in data):
        raise ValueError("CSV rows have inconsistent lengths")
    return np.array(data)


def format_matrix_rich(matrix: np.ndarray, title: Optional[str] = None) -> Table:
    table = Table(title=title)
    cols = matrix.shape[1]
    for i in range(cols):
        table.add_column(f"C{i}", justify="right")
    for row in matrix:
        table.add_row(*[f"{v:.6g}" for v in row])
    return table


def compute_result(operation: str, a: np.ndarray, b: Optional[np.ndarray] = None):
    if operation == 'addition':
        return a + b
    if operation == 'subtraction':
        return a - b
    if operation == 'multiplication':
        return a.dot(b)
    if operation == 'transpose':
        return a.T
    if operation == 'determinant':
        return float(np.linalg.det(a))
    if operation == 'inverse':
        return np.linalg.inv(a)
    if operation == 'rank':
        return int(np.linalg.matrix_rank(a))
    if operation == 'eigenvalues':
        return np.linalg.eigvals(a)
    if operation == 'solve':
        # b is expected to be a vector or matrix of right-hand side(s)
        return np.linalg.solve(a, b)
    raise ValueError(f"Unsupported operation: {operation}")


def save_matrix_csv(matrix: np.ndarray, path: str):
    np.savetxt(path, matrix, delimiter=',')


def read_matrix_interactive(prompt_text: str) -> np.ndarray:
    console.print(f"[bold]{prompt_text}[/bold]")
    example = "Format: 1 2 3; 4 5 6 or lines/CSV"
    while True:
        raw = Prompt.ask("Enter matrix")
        try:
            return parse_matrix(raw)
        except Exception as exc:
            console.print(f"[red]Invalid matrix:[/red] {exc}")
            console.print(example)


def main_interactive():
    console.print("[bold green]Welcome to Matrix Operations Tool (interactive)[/bold green]")
    ops = [
        ("Addition", 'addition'),
        ("Subtraction", 'subtraction'),
        ("Multiplication", 'multiplication'),
        ("Transpose", 'transpose'),
        ("Determinant", 'determinant'),
        ("Inverse", 'inverse'),
        ("Rank", 'rank'),
        ("Eigenvalues", 'eigenvalues'),
        ("Solve Ax=b", 'solve'),
        ("Exit", 'exit'),
    ]

    history: List[Tuple[str, object]] = []

    while True:
        table = Table(title="Operations")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Operation")
        for i, (label, _) in enumerate(ops, start=1):
            table.add_row(str(i), label)
        console.print(table)

        choice = Prompt.ask("Choose an operation (number)")
        try:
            idx = int(choice) - 1
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
            continue
        if idx < 0 or idx >= len(ops):
            console.print("[red]Invalid choice[/red]")
            continue
        op_label, op_key = ops[idx]
        if op_key == 'exit':
            console.print("Goodbye!")
            break

        a = read_matrix_interactive("Matrix A (rows separated by ';')")
        b = None
        if op_key in {'addition', 'subtraction', 'multiplication'}:
            b = read_matrix_interactive("Matrix B (rows separated by ';')")
        elif op_key == 'solve':
            bvec = Prompt.ask("Enter right-hand side vector b (comma/space separated)")
            barr = [float(x) for x in bvec.replace(',', ' ').split()]
            b = np.array(barr)

        try:
            result = compute_result(op_key, a, b)
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")
            continue

        console.print(f"[bold blue]Result: {op_label}[/bold blue]")
        if np.isscalar(result) or isinstance(result, (int, float)):
            console.print(str(result))
        elif isinstance(result, np.ndarray) and result.ndim == 1:
            console.print(
                Table("Index", "Value")
            )
            arr_table = Table()
            arr_table.add_column("Index")
            arr_table.add_column("Value", justify="right")
            for i, v in enumerate(result):
                arr_table.add_row(str(i), f"{v:.6g}")
            console.print(arr_table)
        else:
            console.print(format_matrix_rich(np.atleast_2d(result)))

        history.append((op_key, result))


def cli_entry():
    parser = argparse.ArgumentParser(description="Matrix Operations Tool")
    parser.add_argument('--interactive', '-i', action='store_true', help='Run interactive TUI')
    parser.add_argument('--op', choices=['add', 'sub', 'mul', 'trans', 'det', 'inv', 'rank', 'eig', 'solve'], help='Operation to run')
    parser.add_argument('--a', help='Matrix A as string (e.g. "1 2;3 4")')
    parser.add_argument('--b', help='Matrix B or vector as string')
    parser.add_argument('--afile', help='Load matrix A from CSV file')
    parser.add_argument('--bfile', help='Load matrix B from CSV file')
    parser.add_argument('--save', help='Save result to CSV file')
    args = parser.parse_args()

    if args.interactive:
        main_interactive()
        return

    if not args.op:
        parser.print_help()
        return

    op_map = {
        'add': 'addition',
        'sub': 'subtraction',
        'mul': 'multiplication',
        'trans': 'transpose',
        'det': 'determinant',
        'inv': 'inverse',
        'rank': 'rank',
        'eig': 'eigenvalues',
        'solve': 'solve',
    }

    operation = op_map[args.op]

    if args.afile:
        a = load_matrix_from_csv(args.afile)
    elif args.a:
        a = parse_matrix(args.a)
    else:
        raise SystemExit('Matrix A is required (--a or --afile)')

    b = None
    if args.bfile:
        b = load_matrix_from_csv(args.bfile)
    elif args.b:
        b = parse_matrix(args.b)

    try:
        result = compute_result(operation, a, b)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)

    if isinstance(result, np.ndarray):
        console.print(format_matrix_rich(np.atleast_2d(result), title='Result'))
    else:
        console.print(f"Result: {result}")

    if args.save and isinstance(result, np.ndarray):
        save_matrix_csv(result, args.save)
        console.print(f"Saved result to {args.save}")


if __name__ == '__main__':
    cli_entry()
