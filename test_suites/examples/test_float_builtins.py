# /workspaces/1586160/py2asm/test_suite/test_float_builtins.py

test_cases = [
    { # Test case 1: float_abs_sgn_log
        'name': 'float_abs_sgn_log (V1)',
        'compiler_version': 'V1',
        'code': """a = -5.25
abs_a = abs(a)  # Expected: 5.25
b = 0.0
sgn_a = sgn(a)    # Expected: -1.0
sgn_b = sgn(b)    # Expected: 0.0
sgn_c = sgn(10.0) # Expected: 1.0
d = 2.0 # Placeholder for log, as FP_LOG is a stub
log_d = log(d)
log_int = log(1) # Test coercion""",
        'expected': 'float_builtins/float_abs_sgn_log.asm'
    },

    {
            'name': 'float_exp_stub (V1)',
            'compiler_version': 'V1',
            'code': """# Test exp() stub - should call FP_EXP and handle type.
# FP_EXP itself will signal NotImplementedError at runtime.
# We are testing the compilation path to FP_EXP.
res_exp_float = exp(1.0)
res_exp_int = exp(2) # Test integer to float coercion for argument""",
            'expected': 'float_builtins/float_exp_stub.asm'
    },

]
