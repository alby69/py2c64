test_cases = [
    {
        "name": "String slicing",
        "code": 's = "hello"\nt = s[1:4]',
        "expected": "strings/output_string_slice.asm"
    },
    {
        "name": "String concatenation (f-string)",
        "code": 'x1 = "world"\ns = f"hello {x1}"',
        "expected": "strings/output_fstring.asm"
    },
    {
        "name": "String concatenation (f-string) and print",
        "code": 'x1 = "world"\ns = f"hello {x1}"\nprint(s)',
        "expected": "strings/output_fstring_print.asm"
    },
    {
        "name": "Print string variable",
        "code": "msg = 'hello, how are you?'\nprint(msg)",
        "expected": "strings/output_print_string.asm"
    },
    {
        "name": "Print string literal",
        "code": "print('Hello, world!')",
        "expected": "strings/output_print_literal.asm"
    },
]
