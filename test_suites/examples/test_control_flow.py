test_cases = [
    {
        "name": "For loop over list",
        
        "code": "my_list = [1, 2, 3]\nfor item in my_list:\n  x = item * 2",
        "expected": "control_flow/output_for_list.asm"
    },
    {
        "name": "Simple while loop",
        
        "code": "i = 0\nwhile i < 5:\n  i = i + 1",
        "expected": "control_flow/output_while_simple.asm"
    },
    {
        "name": "Simple If (true condition)",
        
        "code": "x = 10\nres = 0\nif x == 10:\n  res = 1\n# Expected: res = 1",
        "expected": "control_flow/output_if_simple_true.asm"
    },
    {
        "name": "Simple If (false condition)",
        
        "code": "x = 5\nres = 0\nif x == 10:\n  res = 1\n# Expected: res = 0",
        "expected": "control_flow/output_if_simple_false.asm"
    },
    {
        "name": "If-Else (if branch)",
        
        "code": "x = 10\nres = 0\nif x > 5:\n  res = 1\nelse:\n  res = 2\n# Expected: res = 1",
        "expected": "control_flow/output_if_else_if_branch.asm"
    },
    {
        "name": "If-Else (else branch)",
        
        "code": "x = 3\nres = 0\nif x > 5:\n  res = 1\nelse:\n  res = 2\n# Expected: res = 2",
        "expected": "control_flow/output_if_else_else_branch.asm"
    },
    {
        "name": "If-Elif-Else (if branch)",
        
        "code": "x = 15\nres = 0\nif x > 10:\n  res = 1\nelif x > 5:\n  res = 2\nelse:\n  res = 3\n# Expected: res = 1",
        "expected": "control_flow/output_if_elif_else_if.asm"
    },
    {
        "name": "If-Elif-Else (elif branch)",
        
        "code": "x = 7\nres = 0\nif x > 10:\n  res = 1\nelif x > 5:\n  res = 2\nelse:\n  res = 3\n# Expected: res = 2",
        "expected": "control_flow/output_if_elif_else_elif.asm"
    },
    {
        "name": "If-Elif-Else (else branch)",
        
        "code": "x = 3\nres = 0\nif x > 10:\n  res = 1\nelif x > 5:\n  res = 2\nelse:\n  res = 3\n# Expected: res = 3",
        "expected": "control_flow/output_if_elif_else_else.asm"
    },
    {
        "name": "If-Elif (if branch, no else)",
        
        "code": "x = 12\nres = 0\nif x > 10:\n  res = 1\nelif x > 5:\n  res = 2\n# Expected: res = 1",
        "expected": "control_flow/output_if_elif_if.asm"
    },
    {
        "name": "If-Elif (elif branch, no else)",
        
        "code": "x = 8\nres = 0\nif x > 10:\n  res = 1\nelif x > 5:\n  res = 2\n# Expected: res = 2",
        "expected": "control_flow/output_if_elif_elif.asm"
    },
    {
        "name": "If with <= operator",
        
        "code": "x = 5\ny = 5\nres = 0\nif x <= y:\n  res = 1\n# Expected: res = 1",
        "expected": "control_flow/output_if_lte_true.asm"
    },
    {
        "name": "If with < operator (false)",
        
        "code": "x = 5\ny = 5\nres = 0\nif x < y:\n  res = 1\n# Expected: res = 0",
        "expected": "control_flow/output_if_lt_false.asm"
    },
    {
        "name": "Nested If",
        
        "code": "x = 10\ny = 5\nres = 0\nif x > 5:\n  if y < 10:\n    res = 1\n  else:\n    res = 2\nelse:\n  res = 3\n# Expected: res = 1",
        "expected": "control_flow/output_if_nested.asm"
    },
    {
        "name": "If with constant True condition",
        
        "code": "res = 0\nif True:\n  res = 1\n# Expected: res = 1",
        "expected": "control_flow/output_if_true_const.asm"
    },
    {
        "name": "If with constant False condition and Else",
        
        "code": "res = 0\nif False:\n  res = 1\nelse:\n  res = 2\n# Expected: res = 2",
        "expected": "control_flow/output_if_false_const_else.asm"
    },
    {
        "name": "If with BinOp operand on the left",
        
        "code": "x = 5\ny = 10\nres = 0\nif x + 2 > y - 5:\n  res = 1\n# Expected: 7 > 5 -> res = 1",
        "expected": "control_flow/output_if_binop_left.asm"
    },
    {
        "name": "If with BinOp operand on right and left",
        
        "code": "x = 3\ny = 1\nres = 0\nif x * 2 == y + 5:\n  res = 1\n# Expected: 6 == 6 -> res = 1",
        "expected": "control_flow/output_if_binop_both.asm"
    },
    {
        "name": "NOT operator (True)",
        
        "code": "x = 0\nres = 0\nif not x:\n  res = 1\n# Expected: not 0 -> True -> res = 1",
        "expected": "control_flow/output_bool_not_true.asm"
    },
    {
        "name": "NOT operator (False)",
        
        "code": "x = 5\nres = 0\nif not x:\n  res = 1\n# Expected: not 5 -> False -> res = 0",
        "expected": "control_flow/output_bool_not_false.asm"
    },
    {
        "name": "AND operator (True and True)",
        
        "code": "x = 5\ny = 10\nres = 0\nif x > 0 and y > 0:\n  res = 1\n# Expected: True and True -> res = 1",
        "expected": "control_flow/output_bool_and_tt.asm"
    },
    {
        "name": "AND operator (True and False)",
        
        "code": "x = 5\ny = 0\nres = 0\nif x > 0 and y > 0:\n  res = 1\n# Expected: True and False -> res = 0",
        "expected": "control_flow/output_bool_and_tf.asm"
    },
    {
        "name": "AND operator (False and True - Short Circuit)",
        
        "code": "x = 0\ny = 10\nres = 0\nif x > 0 and y > 0: # y > 0 should not be evaluated if the compiler is smart\n  res = 1\n# Expected: False and True -> res = 0",
        "expected": "control_flow/output_bool_and_ft_short_circuit.asm"
    },
    {
        "name": "OR operator (True or False - Short Circuit)",
        
        "code": "x = 5\ny = 0\nres = 0\nif x > 0 or y > 0: # y > 0 should not be evaluated\n  res = 1\n# Expected: True or False -> res = 1",
        "expected": "control_flow/output_bool_or_tf_short_circuit.asm"
    },
    {
        "name": "OR operator (False or True)",
        
        "code": "x = 0\ny = 10\nres = 0\nif x > 0 or y > 0:\n  res = 1\n# Expected: False or True -> res = 1",
        "expected": "control_flow/output_bool_or_ft.asm"
    },
    {
        "name": "OR operator (False or False)",
        
        "code": "x = 0\ny = 0\nres = 0\nif x > 0 or y > 0:\n  res = 1\n# Expected: False or False -> res = 0",
        "expected": "control_flow/output_bool_or_ff.asm"
    },
    {
        "name": "NOT and AND combination",
        
        "code": "x = 5\ny = 0\nres = 0\nif not (x == 0 and y == 0):\n  res = 1\n# Expected: not (False and True) -> not False -> True -> res = 1",
        "expected": "control_flow/output_bool_not_and.asm"
    },
    {
        "name": "NOT and OR combination",
        
        "code": "x = 0\ny = 0\nres = 0\nif not (x > 0 or y > 0):\n  res = 1\n# Expected: not (False or False) -> not False -> True -> res = 1",
        "expected": "control_flow/output_bool_not_or.asm"
    },
    {
        "name": "AND with boolean constants",
        
        "code": "res = 0\nif True and False:\n  res = 1\n# Expected: res = 0",
        "expected": "control_flow/output_bool_and_const.asm"
    },
    {
        "name": "XOR operator in IF condition (True)",
        
        "code": "a = 10\nb = 5\nres = 0\nif (a ^ b): # 10^5 = 15 (non-zero, quindi True)\n  res = 1\n# Expected: res = 1",
        "expected": "control_flow/output_operator_xor_if_true.asm"
    },
    {
        "name": "XOR operator in IF condition (False)",
        
        "code": "a = 7\nb = 7\nres = 0\nif (a ^ b): # 7^7 = 0 (zero, quindi False)\n  res = 1\n# Expected: res = 0",
        "expected": "control_flow/output_operator_xor_if_false.asm"
    },
    {
        "name": "While loop with break",
        
        "code": "i = 0\nres = 0\nwhile i < 10:\n  res = res + i\n  i = i + 1\n  if i == 5:\n    break\n# Expected: res = 0+1+2+3+4 = 10, i = 5",
        "expected": "control_flow/output_while_break.asm"
    },
    {
        "name": "While loop with continue",
        
        "code": "i = 0\nres = 0\nwhile i < 5:\n  i = i + 1\n  if i == 3:\n    continue\n  res = res + i\n# Expected: i=5, res = 1+2+4+5 = 12",
        "expected": "control_flow/output_while_continue.asm"
    },
    {
        "name": "For loop with break",
        
        "code": "my_list = [1, 2, 3, 4, 5]\nres = 0\nfor item in my_list:\n  if item == 4:\n    break\n  res = res + item\n# Expected: res = 1+2+3 = 6",
        "expected": "control_flow/output_for_break.asm"
    },
    {
        "name": "For loop with continue",
        
        "code": "my_list = [1, 2, 3, 4, 5]\nres = 0\nfor item in my_list:\n  if item == 3:\n    continue\n  res = res + item\n# Expected: res = 1+2+4+5 = 12",
        "expected": "control_flow/output_for_continue.asm"
    },
    {
        "name": "Break in nested loop (while in for)",
        
        "code": """
outer_sum = 0
my_list = [1, 2, 3]
for x in my_list: # x = 1, 2, 3
    outer_sum = outer_sum + x
    y = 0
    while y < 2: # y = 0, 1
        y = y + 1 # In Python, this would be inside the loop
        if x == 2:
            break # Exits the inner while if x is 2
    # Se x=1, y arriva a 2. outer_sum = 1
    # Se x=2, y=1, break. outer_sum = 1+2=3
    # Se x=3, y arriva a 2. outer_sum = 3+3=6
# Expected: outer_sum = 6
""",
        "expected": "control_flow/output_nested_for_while_break.asm"
    }
]
