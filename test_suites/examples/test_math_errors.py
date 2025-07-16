test_cases = [
    {
        "name": "log_zero_error (V1)",
        "compiler_version": "V1",
        "code": """
try:
    x = log(0.0)
except ValueError:
    print("Caught ValueError for log(0)")
""",
        "expected": "expected_outputs/math_errors/log_zero_error.asm"
    },
    {
        "name": "log_negative_error (V1)",
        "compiler_version": "V1",
        "code": """
try:
    y = log(-1.0)
except ValueError:
    print("Caught ValueError for log(-1)")
""",
        "expected": "expected_outputs/math_errors/log_negative_error.asm"
    },
    {
        "name": "log_positive_stub (V1)",
        "compiler_version": "V1",
        "code": """
x = log(2.718) # Input > 0
print(x) # Stub should return 0.0
""",
        "expected": "expected_outputs/math_errors/log_positive_stub.asm"
        # Expected output will involve FP_LOG returning 0.0 and then printing that.
    },
    {
        "name": "exp_stub (V1)",
        "compiler_version": "V1",
        "code": """
y = exp(1.0) # Any input
print(y) # Stub should return 1.0
""",
        "expected": "expected_outputs/math_errors/exp_stub.asm"
        # Expected output will involve FP_EXP returning 1.0 and then printing that.
    }
]
