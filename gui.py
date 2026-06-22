import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np

from matrix_tool import (
    parse_matrix,
    compute_result,
    load_matrix_from_csv,
    save_matrix_csv,
)


class MatrixToolGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Matrix Operations Tool")
        self.geometry("900x600")

        self.last_result = None

        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Frame(frm)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = ttk.Frame(frm)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Matrix A
        ttk.Label(left, text="Matrix A:").pack(anchor=tk.W)
        self.txt_a = tk.Text(left, height=10, wrap=tk.NONE)
        self.txt_a.pack(fill=tk.BOTH, expand=True)
        a_buttons = ttk.Frame(left)
        a_buttons.pack(fill=tk.X)
        ttk.Button(a_buttons, text="Load CSV", command=self.load_a_csv).pack(side=tk.LEFT)
        ttk.Button(a_buttons, text="Clear", command=lambda: self.txt_a.delete('1.0', tk.END)).pack(side=tk.LEFT)

        # Matrix B
        ttk.Label(left, text="Matrix B (optional):").pack(anchor=tk.W, pady=(6, 0))
        self.txt_b = tk.Text(left, height=8, wrap=tk.NONE)
        self.txt_b.pack(fill=tk.BOTH, expand=True)
        b_buttons = ttk.Frame(left)
        b_buttons.pack(fill=tk.X)
        ttk.Button(b_buttons, text="Load CSV", command=self.load_b_csv).pack(side=tk.LEFT)
        ttk.Button(b_buttons, text="Clear", command=lambda: self.txt_b.delete('1.0', tk.END)).pack(side=tk.LEFT)

        # Controls
        controls = ttk.Frame(right)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Operation:").grid(row=0, column=0, sticky=tk.W)
        self.op_var = tk.StringVar(value='addition')
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
        ]
        self.op_menu = ttk.Combobox(controls, values=[o[0] for o in ops], state='readonly')
        self.op_menu.current(0)
        self.op_menu.grid(row=0, column=1, sticky=tk.W)

        ttk.Button(controls, text="Compute", command=self.on_compute).grid(row=1, column=0, pady=8)
        ttk.Button(controls, text="Save Result CSV", command=self.save_result).grid(row=1, column=1, pady=8)

        # Result display
        ttk.Label(right, text="Result:").pack(anchor=tk.W)
        self.txt_result = tk.Text(right, height=20, wrap=tk.NONE)
        self.txt_result.pack(fill=tk.BOTH, expand=True)

    def load_a_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV', '*.csv'), ('All', '*.*')])
        if not path:
            return
        try:
            m = load_matrix_from_csv(path)
        except Exception as exc:
            messagebox.showerror('Load error', str(exc))
            return
        self.txt_a.delete('1.0', tk.END)
        self.txt_a.insert(tk.END, '\n'.join(' '.join(str(x) for x in row) for row in m))

    def load_b_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV', '*.csv'), ('All', '*.*')])
        if not path:
            return
        try:
            m = load_matrix_from_csv(path)
        except Exception as exc:
            messagebox.showerror('Load error', str(exc))
            return
        self.txt_b.delete('1.0', tk.END)
        self.txt_b.insert(tk.END, '\n'.join(' '.join(str(x) for x in row) for row in m))

    def on_compute(self):
        op_label = self.op_menu.get()
        # map label to key used by compute_result
        label_to_key = {
            'Addition': 'addition',
            'Subtraction': 'subtraction',
            'Multiplication': 'multiplication',
            'Transpose': 'transpose',
            'Determinant': 'determinant',
            'Inverse': 'inverse',
            'Rank': 'rank',
            'Eigenvalues': 'eigenvalues',
            'Solve Ax=b': 'solve',
        }
        op = label_to_key.get(op_label, 'addition')

        a_text = self.txt_a.get('1.0', tk.END).strip()
        b_text = self.txt_b.get('1.0', tk.END).strip()

        try:
            a = parse_matrix(a_text)
        except Exception as exc:
            messagebox.showerror('Invalid matrix A', str(exc))
            return

        b = None
        if op in {'addition', 'subtraction', 'multiplication'}:
            try:
                b = parse_matrix(b_text)
            except Exception as exc:
                messagebox.showerror('Invalid matrix B', str(exc))
                return
        elif op == 'solve':
            # allow B to be either a vector or matrix; accept space/comma separated
            try:
                # try parse_matrix first; if single row/column, accept
                b = None
                if b_text:
                    try:
                        b = parse_matrix(b_text)
                    except Exception:
                        arr = [float(x) for x in b_text.replace(',', ' ').split() if x]
                        b = np.array(arr)
            except Exception as exc:
                messagebox.showerror('Invalid RHS b', str(exc))
                return

        try:
            res = compute_result(op, a, b)
        except Exception as exc:
            messagebox.showerror('Computation error', str(exc))
            return

        self.last_result = res
        self.txt_result.delete('1.0', tk.END)
        if np.isscalar(res) or isinstance(res, (int, float, complex)):
            self.txt_result.insert(tk.END, str(res))
        else:
            arr = np.atleast_2d(res)
            lines = []

            def fmt(v):
                try:
                    if isinstance(v, complex) or np.iscomplexobj(v):
                        return f"{v.real:.6g}{'+' if v.imag >= 0 else '-'}{abs(v.imag):.6g}j"
                    return f"{v:.6g}"
                except Exception:
                    return str(v)

            for row in arr:
                lines.append('  '.join(fmt(v) for v in row))
            self.txt_result.insert(tk.END, '\n'.join(lines))

    def save_result(self):
        if self.last_result is None:
            messagebox.showinfo('No result', 'Compute a result first')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if not path:
            return
        try:
            arr = np.atleast_2d(self.last_result)
            save_matrix_csv(arr, path)
            messagebox.showinfo('Saved', f'Saved to {path}')
        except Exception as exc:
            messagebox.showerror('Save error', str(exc))


def main():
    app = MatrixToolGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
