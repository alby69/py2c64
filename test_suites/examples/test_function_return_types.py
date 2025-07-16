# /workspaces/1586160/py2asm/test_suite/test_function_return_types.py
test_cases = [
    {
        'name': 'user_func_return_float_literal',
        'compiler_version': 'V1',
        'code': """
def get_pi():
    return 3.14

a = get_pi()
# 'a' should be treated as a float (4 bytes copied from __func_retval)
""",
        'expected': 'function_returns/user_func_return_float_literal.asm'
    },
    {
        'name': 'user_func_return_float_cast',
        'compiler_version': 'V1',
        'code': """
def to_float(x):
    y = 1 # dummy local var
    return float(x)

b_val = 10
b = to_float(b_val)
# 'b' should be treated as a float (4 bytes copied)
""",
        'expected': 'function_returns/user_func_return_float_cast.asm'
    },
    {
        'name': 'user_func_return_int_literal',
        'compiler_version': 'V1',
        'code': """
def get_int():
    return 100

c = get_int()
# 'c' should be treated as an int (2 bytes copied)
""",
        'expected': 'function_returns/user_func_return_int_literal.asm'
    },
    {
        'name': 'user_func_return_mixed_calls',
        'compiler_version': 'V1',
        'code': """
def returns_float():
    val = 0.0 # dummy local
    val = 1.5
    return val # Current analysis might not catch this if 'val' type isn't tracked well

def returns_float_direct():
    return 1.5

def returns_int():
    return 7

f_val = returns_float_direct() # This should be detected as float return
i_val = returns_int()
# f_val is float, i_val is int
""",
        'expected': 'function_returns/user_func_return_mixed_calls.asm'
    },
]
