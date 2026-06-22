import numpy as np
from matrix_tool import parse_matrix, compute_result


def test_parse_matrix_basic():
    m = parse_matrix("1 2 3;4 5 6")
    assert isinstance(m, np.ndarray)
    assert m.shape == (2, 3)
    assert m[0, 0] == 1


def test_addition():
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    r = compute_result('addition', a, b)
    expected = np.array([[6, 8], [10, 12]])
    assert np.allclose(r, expected)


def test_determinant():
    a = np.array([[1, 2], [3, 4]])
    det = compute_result('determinant', a)
    assert abs(det - (-2.0)) < 1e-9
