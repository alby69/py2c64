# /workspaces/1586160/py2asm/test_suite/test_float_comparisons.py

test_cases = [
    {
        'name': 'float_comparison_eq_ne',
        'compiler_version': 'V1',
        'code': """
a = 3.5
b = 3.5
c = -2.0

res_eq = (a == b)  # Expected: True (1)
res_ne = (a != c)  # Expected: True (1)
res_lt = (c < a)   # Expected: True (1)
res_gt = (a > c)   # Expected: True (1)
res_le1 = (a <= b) # Expected: True (1)
res_le2 = (c <= a) # Expected: True (1)
res_ge1 = (a >= b) # Expected: True (1)
res_ge2 = (a >= c) # Expected: True (1)
""",
        'expected': 'float_comparisons/float_comparison_eq_ne.asm'
    },
    # Add more tests:
    # - Comparisons with zero
    # - Comparisons involving integer coercion (e.g., float_var < int_literal)
    # - All operators: ==, !=, <, <=, >, >=
]
