test_cases = []

# Test Case 1: Simple function call with parameters and local variables
test_code_1 = """
def add_one(x):
    y = x + 1
    return y

result = add_one(5)
print(result)
"""

test_cases.append({
    'name': 'add_one_function_call',
    'compiler_version': 'V1',
    'code': test_code_1,
    'expected': 'expected_add_one_function_call.asm'
})
