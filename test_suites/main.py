import subprocess
import os
import sys
import shutil
import argparse
import importlib.util
from datetime import datetime

# Add the project root to sys.path to allow imports like 'V1.main' or 'V2.main'
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TEST_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

def _load_tests_from_file(version, examples_path, filename):
    """Helper to load test cases from a single file and inject the compiler version."""
    module_name = filename[:-3]  # Remove .py
    file_path = os.path.join(examples_path, filename)
    loaded_tests = []

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "test_cases") and isinstance(module.test_cases, list):
            print(f"Loaded {len(module.test_cases)} test cases from {version}/{filename}")
            for test_case in module.test_cases:
                test_case['compiler_version'] = version  # Inject the version
                # Standardize expected path to be just the filename
                if 'expected' in test_case:
                    test_case['expected'] = os.path.basename(test_case['expected'])
            loaded_tests.extend(module.test_cases)
        else:
            print(f"Warning: No 'test_cases' list found in {filename}")
    else:
        print(f"Warning: Could not create module spec for {filename}")
    return loaded_tests

def load_test_cases(specific_file_name=None):
    """
    Loads test cases from the `compiler_versions` directory structure.
    """
    all_tests = []
    versions_path = os.path.join(_TEST_DIR, "compiler_versions")

    if not os.path.isdir(versions_path):
        print(f"Error: Main test directory '{versions_path}' not found.")
        return []

    if specific_file_name:
        try:
            # Expecting format "V1/test_arithmetic.py"
            version, filename = specific_file_name.replace("\\", "/").split("/", 1)
        except ValueError:
            print(f"Error: Invalid format for specific test file. Use 'VERSION/filename.py' (e.g., 'V1/test_arithmetic.py').")
            return []

        examples_path = os.path.join(versions_path, version, "examples")
        full_specific_path = os.path.join(examples_path, filename)

        if os.path.isfile(full_specific_path):
            all_tests.extend(_load_tests_from_file(version, examples_path, filename))
        else:
            print(f"Error: Specified test file '{specific_file_name}' not found.")
            return []
    else:
        # Load all tests from all versions
        for version in sorted(os.listdir(versions_path)):
            version_dir = os.path.join(versions_path, version)
            if not os.path.isdir(version_dir):
                continue

            examples_path = os.path.join(version_dir, "examples")
            if not os.path.isdir(examples_path):
                continue

            for filename in sorted(os.listdir(examples_path)):
                if filename.startswith("test_") and filename.endswith(".py"):
                    all_tests.extend(_load_tests_from_file(version, examples_path, filename))

    return all_tests

def run_test(test_case, regenerate_mode=False):
    """Executes a single test case."""
    print(f"\n--- Starting test: {test_case['name']} ---")
    print(f"Test code:")
    print(test_case['code'])
    temp_output_filename = "temp_output.asm"

    compilation_errors = []
    def test_error_handler(message, lineno):
        compilation_errors.append(f"L{lineno}: {message}")

    compiler_version = test_case.get("compiler_version")
    if not compiler_version:
        print(f"Test '{test_case['name']}' FAILED: Missing 'compiler_version' key in test case.")
        return False

    try:
        # Dynamically import the correct compiler's main module
        compiler_module_name = f"{compiler_version}.main"
        compiler_main = importlib.import_module(compiler_module_name)

        # If the compiler has a reset function, call it. Assumes object-oriented or global reset.
        if hasattr(compiler_main, "reset_globals"): # For V1-like structure
            compiler_main.reset_globals()

        result_assembly_string = compiler_main.python_to_assembly(
            test_case['code'], temp_output_filename, test_error_handler
        )

        if compilation_errors or result_assembly_string is None:
            print(f"Test '{test_case['name']}' FAILED: Error during compilation.")
            for error in compilation_errors:
                print(f"  - {error}")
            return False

        if "expected" in test_case and test_case["expected"]:
            base_expected_path = os.path.join(_TEST_DIR, "compiler_versions", compiler_version, "expected_outputs")
            expected_filename = os.path.join(base_expected_path, test_case["expected"])

            if regenerate_mode:
                try:
                    os.makedirs(os.path.dirname(expected_filename), exist_ok=True)
                    with open(expected_filename, "w") as f_expected:
                        f_expected.write(result_assembly_string)
                    return True
                except Exception as e:
                    print(f"Error during file regeneration '{expected_filename}': {e}")
                    return False
            else:
                if not os.path.exists(expected_filename):
                    print(f"Test '{test_case['name']}' SKIPPED: Expected file '{expected_filename}' not found.")
                    return False

                with open(expected_filename, "r") as f:
                    expected_content = f.read()

                # Simple normalization for comparison
                expected_norm = expected_content.replace('\r\n', '\n').strip()
                generated_norm = result_assembly_string.replace('\r\n', '\n').strip()

                if expected_norm != generated_norm:
                    print(f"Test '{test_case['name']}' FAILED: Generated output does not match expected output.")
                    try:
                        with open(temp_output_filename, 'w') as f_gen:
                            f_gen.write(result_assembly_string)
                        diff_result = subprocess.run(
                            ["diff", "-u", expected_filename, temp_output_filename],
                            capture_output=True, text=True, check=False
                        )
                        print("--- Differences ---")
                        print(diff_result.stdout if diff_result.stdout else "No differences found by 'diff', check whitespace/endings.")
                    except FileNotFoundError:
                        print("Could not find 'diff'. Raw comparison failed.")
                    return False
        else:
            print("Test without expected output, showing generated content:")
            print(result_assembly_string)

        print(f"Test '{test_case['name']}' PASSED.")
        return True

    except ImportError:
        print(f"Test '{test_case['name']}' FAILED: Could not import compiler '{compiler_module_name}'.")
        return False
    except Exception as e:
        print(f"Test '{test_case['name']}' FAILED: Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(temp_output_filename):
            os.remove(temp_output_filename)
        print("--- Ending test ---")

def _log_test_result(test_name, status, version, message="", log_file_handle=None):
    """Logs the test result to the specified file handle."""
    if log_file_handle:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file_handle.write(f"[{timestamp}] {status}: {test_name} (Compiler: {version}) - {message}\n")
        log_file_handle.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run compiler tests and optionally regenerate expected outputs.")
    parser.add_argument(
        "--regenerate", action="store_true", help="Regenerate expected output files instead of comparing."
    )
    parser.add_argument(
        "test_file", nargs="?", default=None,
        help="Optional: specific test file to run in 'VERSION/filename.py' format (e.g., V1/test_arithmetic.py)."
    )
    args = parser.parse_args()

    LOGS_DIR = os.path.join(_TEST_DIR, "logs")
    PASSED_LOG_FILENAME = "passed_tests.log"
    FAILED_LOG_FILENAME = "failed_tests.log"

    os.makedirs(LOGS_DIR, exist_ok=True)

    passed_log_file = None
    failed_log_file = None

    try:
        passed_log_file = open(os.path.join(LOGS_DIR, PASSED_LOG_FILENAME), 'w')
        failed_log_file = open(os.path.join(LOGS_DIR, FAILED_LOG_FILENAME), 'w')
    except IOError as e:
        print(f"Error opening log files: {e}", file=sys.stderr)
        sys.exit(1)

    test_cases = load_test_cases(specific_file_name=args.test_file)

    num_tests = len(test_cases)
    num_passed = 0
    num_regenerated = 0
    num_failed_regeneration = 0

    try:
        for test_case in test_cases:
            version = test_case.get('compiler_version', 'UNKNOWN')
            if args.regenerate:
                if "expected" in test_case and test_case["expected"]:
                    if run_test(test_case, regenerate_mode=True):
                        num_regenerated += 1
                        _log_test_result(test_case['name'], "REGENERATED", version, "File regenerated successfully", passed_log_file)
                    else:
                        _log_test_result(test_case['name'], "REGENERATION FAILED", version, "Error during regeneration", failed_log_file)
                        num_failed_regeneration += 1
                else:
                    # Test without 'expected' file, just run it
                    run_test(test_case, regenerate_mode=True)
            else:
                if run_test(test_case, regenerate_mode=False):
                    num_passed += 1
                    _log_test_result(test_case['name'], "PASSED", version, "Test completed successfully", passed_log_file)
                else:
                    _log_test_result(test_case['name'], "FAILED", version, "Test did not pass or had an error", failed_log_file)
    finally:
        if passed_log_file: passed_log_file.close()
        if failed_log_file: failed_log_file.close()

    if not test_cases:
        print(f"\nNo tests found or executed.")
        sys.exit(0 if not args.test_file else 1)

    print(f"\n--- Test Summary ---")
    if args.regenerate:
        processed_count = num_regenerated + num_failed_regeneration
        print(f"Test cases processed for regeneration: {processed_count}")
        print(f"Files successfully regenerated: {num_regenerated}")
        print(f"Files failed to regenerate: {num_failed_regeneration}")
        sys.exit(0 if num_failed_regeneration == 0 else 1)
    else:
        failed_count = num_tests - num_passed
        print(f"Total tests run: {num_tests}")
        print(f"Tests passed: {num_passed}")
        print(f"Tests failed: {failed_count}")
        sys.exit(0 if failed_count == 0 else 1)