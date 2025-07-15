
"""
test_cases = [
    {
        'name': 'Simple Addition (V1)',
        'compiler_version': 'V1',  # ADD THIS
        'code': 'x = 5 + 3',
        'expected': 'simple_addition.asm'  # SIMPLIFY THIS
    },
    # ... other test cases for V1 ...
]
"""



test_cases = [
    {
        "name": "Simple assignment",
        "code": "x1 = 10\nx2 = 20\nz = x1 + x2",
        "expected": "arithmetic/output_assign_simple.asm",
    },
    {
        "name": "Mixed arithmetic operations",
        "code": "a1 = 5\nb = 3\nc = a1 * b + (a1 - b) // 2",
        "expected": "arithmetic/output_arithmetic_mixed.asm",
    },
    {
        "name": "Arithmetic overflow (sum)",
        "code": "x1 = 250\nx2 = 10\nz = x1 + x2",
        "expected": "arithmetic/output_overflow_sum.asm"
    },
    {
        "name": "Division by zero",
        "code": "x1 = 10\nx2 = 0\nz = x1 // x2",
        "expected": "arithmetic/output_division_by_zero.asm"
    },
    {
        "name": "XOR operator (assignment)",
        "code": "a = 10 # 00001010\nb = 5  # 00000101\nc = a ^ b # Expected result: 15 (00001111)",
        "expected": "arithmetic/output_operator_xor_assign.asm"
    },
    {
        "name": "Operatore XOR (valori diversi)",
        "code": "val1 = 255 # 11111111 00000000\nval2 = 85  # 01010101 00000000\n# 255 (00FF) ^ 85 (0055) = 170 (00AA)\nres_xor = val1 ^ val2",
        "expected": "arithmetic/output_operator_xor_assign_alt.asm"
    },
    {
        "name": "Constant Folding: Simple multiplication",
        "code": "x = 2 * 5",
        "expected": "arithmetic/output_constant_folding_mult.asm"
    },
    {
        "name": "Constant Folding: Integer division by zero (compile-time error)",
        "code": "y = 10 // 0",
        "expected": "arithmetic/output_constant_folding_div_by_zero.asm"
    },
    {
        "name": "Constant Folding: Mixed type addition (int + float)",
        "code": "z = 5 + 3.14",
        "expected": "arithmetic/output_constant_folding_int_float_add.asm"
    },
]
