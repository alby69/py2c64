# /workspaces/1586160/py2asm/test_suite/test_float_assignments_literals.py

test_cases = [
    {
        'name': 'assign_positive_float_literal',
        'compiler_version': 'V1',
        'code': """
x = 3.5
y = -0.25
z = 0.0
# Verification of byte patterns for x, y, z in the .asm data section
# would be done by inspecting the generated expected_outputs/float_assignments_literals/assign_positive_float_literal.asm
""",
        'expected': 'float_assignments_literals/assign_positive_float_literal.asm'
    },
    # Add more tests:
    # - Common fractions: 0.5, 0.75, 1.0, 1.75
    # - Numbers requiring more precision within Wozniak limits
    # - Negative numbers
    # - Zero
]
