# /workspaces/1586160/py2asm/test_suite/test_float_conversions.py

test_cases = [
    {
        'name': 'int_to_float_and_float_to_int_conversion',
        'compiler_version': 'V1',
        'code': """
a_int = 5
b_float = float(a_int)

c_float = -3.75
d_int = int(c_float)

# Expected (for verification via print or debugger if available):
# b_float should be 5.0
# d_int should be -3 (due to truncation towards zero)
""",
        'expected': 'float_conversions/int_to_float_and_float_to_int_conversion.asm'
    },
    # Add more tests:
    # - float(integer_literal), int(float_literal)
    # - Test truncation with various positive and negative floats for int()
]
