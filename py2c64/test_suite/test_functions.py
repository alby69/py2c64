test_cases = [
    {
        "name": "Simple function definition and call (no params, no explicit return)",
        "code": "res = 0\ndef my_func():\n  global res\n  res = 10\nmy_func()\n# Expected: res = 10",
        "expected": "functions/output_func_simple_def_call.asm"
    },
    {
        "name": "Function with one parameter and return",
        "code": "def add_one(x):\n  return x + 1\nval = 5\nresult = add_one(val)\n# Expected: result = 6",
        "expected": "functions/output_func_param_return.asm"
    },
    {
        "name": "Function with multiple parameters",
        "code": "def multiply(a, b):\n  return a * b\nres = multiply(3, 4)\n# Expected: res = 12",
        "expected": "functions/output_func_multi_param.asm"
    },
    {
        "name": "Function with empty return (implicit None/0)",
        "code": "def set_val_to_zero():\n  return\nx = 5\nx = set_val_to_zero()\n# Expected: x = 0",
        "expected": "functions/output_func_empty_return.asm"
    },
    {
        "name": "Funzione senza istruzione return (implicito None/0)",
        "code": "y = 0\ndef do_nothing(p):\n  y = p + 1 # Modifica una globale per vedere se viene eseguita\nval = 0\nval = do_nothing(5)\n# Expected: val = 0, y = 6 (y non è il return value)",
        "expected": "functions/output_func_no_return_statement.asm"
    },
    {
        "name": "Function call with constant as argument",
        "code": "def identity(n):\n  return n\nresult = identity(100)\n# Expected: result = 100",
        "expected": "functions/output_func_const_arg.asm"
    },
    {
        "name": "Function call whose argument is an expression",
        "code": "def square(val):\n  return val * val\na = 2\nb = 3\n# Chiamata: square( (a+b) ) -> square(5)\nresult = square(a + b)\n# Expected: result = 25",
        "expected": "functions/output_func_expr_arg.asm"
    },
    {
        "name": "Function calling another function",
        "code": "def inner_func(val):\n  return val * 2\ndef outer_func(x):\n  return inner_func(x + 1)\n# Chiamata: outer_func(3) -> inner_func(4) -> 8\nresult = outer_func(3)\n# Expected: result = 8",
        "expected": "functions/output_func_calls_func.asm"
    },
    {
        "name": "Function with parameters and complex body (if statement)",
        "code": "def check_sign(num):\n  if num > 0:\n    return 1\n  elif num < 0:\n    return -1\n  else:\n    return 0\nres_pos = check_sign(10)\nres_neg = check_sign(-5)\nres_zero = check_sign(0)\n# Expected: res_pos = 1, res_neg = -1, res_zero = 0",
        "expected": "functions/output_func_complex_body.asm"
    },
    {
        "name": "Funzione che modifica variabile globale (non un parametro)",
        "code": "glob_var = 50\ndef modify_global():\n  global glob_var\n  glob_var = 100\nmodify_global()\n# Expected: glob_var = 100",
        "expected": "functions/output_func_modifies_global.asm"
    },
    {
        "name": "Function with parameter whose name collides with a global",
        "code": "x = 10 # Globale\ndef func_with_collision(x): # Parametro x\n  return x * 2 # Dovrebbe usare il parametro x\n# Chiamata: func_with_collision(5) -> 10. La x globale rimane 10.\nresult = func_with_collision(5)\n# Expected: result = 10, x (globale) = 10",
        "expected": "functions/output_func_param_name_collision.asm"
    },
    {
        "name": "Function with two parameters, called with variables",
        "code": "def subtract(a, b):\n  return a - b\nvar1 = 10\nvar2 = 3\nresult = subtract(var1, var2)\n# Expected: result = 7",
        "expected": "functions/output_func_two_params_vars.asm"
    }
]
