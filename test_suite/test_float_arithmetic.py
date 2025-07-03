# /workspaces/1586160/py2asm/test_suite/test_float_arithmetic.py

test_cases = [
    {
        'name': 'int_plus_float_literal',
        'code': """
a_int = 10
b_float_literal = 1.5
c_float_result = a_int + b_float_literal
# To observe the result, you might add: print(c_float_result)
# For now, we primarily verify the generated assembly for the calculation.
""",
        'expected': 'float_arithmetic/int_plus_float_literal.asm'
    },
    # Add more arithmetic test cases here:
    # - float + float
    # - float - int
    # - int * float
# - operations involving negative numbers and zero.
# - float comparisons
]

test_cases.extend([
    {
        'name': 'float_less_than_comparison',
        'code': """
a_float = 3.14
b_float = 2.71
result = a_float < b_float
""",
        'expected': 'float_arithmetic/float_less_than_comparison.asm'
    },
    {
        'name': 'float_equal_comparison',
        'code': """
x_float = 1.5
y_float = 1.5
is_equal = x_float == y_float
""",
        'expected': 'float_arithmetic/float_equal_comparison.asm'
    },
    {
        'name': 'float_not_equal_comparison',
        'code': """
p_float = 10.0
q_float = 10.000001
is_not_equal = p_float != q_float
""",
        'expected': 'float_arithmetic/float_not_equal_comparison.asm'
    },
    {
        'name': 'int_float_greater_than_comparison',
        'code': """
int_val = 5
float_val = 4.99
is_greater = int_val > float_val
""",
        'expected': 'float_arithmetic/int_float_greater_than_comparison.asm'
    },
])
