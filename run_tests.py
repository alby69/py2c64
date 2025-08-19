import os
import sys
import importlib.util
from lib import Py2C64Compiler, CompilerError

def load_test_cases(test_suite_dir):
    """Loads all test cases from modules in the specified directory."""
    all_tests = []
    suite_path = os.path.join(os.path.dirname(__file__), test_suite_dir)

    if not os.path.isdir(suite_path):
        print(f"Error: Test suite directory '{suite_path}' not found.", file=sys.stderr)
        return []

    for filename in sorted(os.listdir(suite_path)):
        if filename.startswith("test_") and filename.endswith(".py"):
            file_path = os.path.join(suite_path, filename)
            module_name = f"{test_suite_dir}.{filename[:-3]}"

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "test_cases") and isinstance(module.test_cases, list):
                    print(f"Loaded {len(module.test_cases)} test cases from {filename}")
                    # Add filename to each test case for context
                    for tc in module.test_cases:
                        tc['source_file'] = filename
                    all_tests.extend(module.test_cases)
    return all_tests

def run_all_tests():
    """Runs all test cases and reports their status."""
    test_cases = load_test_cases("test_suites/examples")

    if not test_cases:
        print("No test cases found.", file=sys.stderr)
        return False

    passed_count = 0
    failed_count = 0

    print("\n--- Running All Tests ---")
    for i, test_case in enumerate(test_cases):
        name = test_case.get('name', f'Unnamed Test {i+1}')
        code = test_case.get('code', '')
        source_file = test_case.get('source_file', 'unknown')

        print(f"\n[{i+1}/{len(test_cases)}] Running test: {name} (from {source_file})")

        try:
            compiler = Py2C64Compiler()
            assembly_code = compiler.compile_code(code)

            # Simple success check: if it compiles without error and produces output
            if assembly_code and isinstance(assembly_code, str):
                print(f"  -> PASSED: Compiled successfully.")
                passed_count += 1
            else:
                print(f"  -> FAILED: Compiler returned empty output.")
                failed_count += 1

        except CompilerError as e:
            print(f"  -> FAILED: Compilation error: {e}")
            failed_count += 1
        except Exception as e:
            print(f"  -> FAILED: An unexpected error occurred: {e}")
            failed_count += 1

    print("\n--- Test Summary ---")
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")

    return failed_count == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
