# test.py
import subprocess
import os
import sys # For sys.path and sys.exit
import shutil  # Per copiare i file
import argparse  # Per gli argomenti a riga di comando
import V1.globals as compiler_globals # Import globals for default paths
import importlib.util # Per caricare moduli dinamicamente
from datetime import datetime # Per i timestamp nei log

# Add the parent directory of 'py2asm' to sys.path
# This allows 'py2asm' to be treated as a package when test.py is run directly.
_CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CURRENT_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import V2.main as compiler_main  # Update for V2
# If V2 handles globals differently or doesn't need it:
# from V2 import compiler_globals  # Or remove if not used


def load_test_cases(test_suite_dir="test_suite", specific_file_name=None):
    """
    Loads test cases.
    If specific_file_name is provided, loads only from that file.
    Otherwise, loads all test cases from modules in the specified directory.
    """
    all_tests = []
    # The path to test_suite_dir is relative to the location of test.py
    suite_path = os.path.join(os.path.dirname(__file__), test_suite_dir)

    if not os.path.isdir(suite_path):
        print(f"Error: Test suite directory '{suite_path}' not found.")
        return [] # pragma: no cover

    files_to_process = []
    if specific_file_name:
        # Validate that the specific file exists and is a test file
        full_specific_path = os.path.join(suite_path, specific_file_name)
        if os.path.isfile(full_specific_path) and specific_file_name.startswith("test_") and specific_file_name.endswith(".py"):
            files_to_process.append(specific_file_name)
        else:
            print(f"Error: Specified test file '{specific_file_name}' not found or not a valid test file in '{suite_path}'.")
            return []
    else:
        # Load all test files
        for filename in sorted(os.listdir(suite_path)):
            if filename.startswith("test_") and filename.endswith(".py"):
                files_to_process.append(filename)

    if not files_to_process:
        if not specific_file_name: # Only print if we weren't looking for a specific file
            print(f"No test files found in '{suite_path}'.")
        return []

    for filename in files_to_process:
            module_name = f"{test_suite_dir}.{filename[:-3]}" # es. test_suite.test_arithmetic
            file_path = os.path.join(suite_path, filename)

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module) # Load the module
                if hasattr(module, "test_cases") and isinstance(module.test_cases, list):
                    print(f"Loaded {len(module.test_cases)} test cases from {filename}")
                    all_tests.extend(module.test_cases)
                else:
                    print(f"Warning: No 'test_cases' list found or it's not a list in {filename}") # pragma: no cover
            else:
                print(f"Warning: Could not create module spec for {filename}") # pragma: no cover
    return all_tests


def run_test(test_case, regenerate_mode=False):
    """Esegue un singolo caso di test."""
    print(f"\n--- Starting test: {test_case['name']} ---")
    print(f"Test code:") # Modificato per rimuovere spazi iniziali e mettere il codice a capo
    print(test_case['code']) # Print the test code on separate lines
    # Adjust or remove the following line based on how V2 handles global state:
    # compiler_globals.reset_globals()
    # If V2 has a reset method on the compiler object, use that instead.
    temp_output_filename = "temp_output.asm"  # Define once

    # Define a simple error handler to pass to the compiler.
    # It will collect any errors reported during compilation.
    compilation_errors = []
    def test_error_handler(message, lineno):
        compilation_errors.append(f"L{lineno}: {message}")

    try:
        # Generate assembly
        # The function signature has changed. Pass the error handler.
        result_assembly_string = compiler_main.python_to_assembly(
            test_case['code'],
            temp_output_filename,
            test_error_handler
        )

        # Check for compilation errors
        if compilation_errors or result_assembly_string is None:
            print(f"Test '{test_case['name']}' FAILED: Error during compilation.")
            for error in compilation_errors:
                print(f"  - {error}")
            return False

        # Check if an expected file is specified
        if "expected" in test_case and test_case["expected"]:
            # Costruisci il percorso completo al file atteso
            # _CURRENT_SCRIPT_DIR è la directory di test.py (py2asm/)
            # py2asm_globals.TEST_SUITE_DIR è "test_suite"
            # py2asm_globals.EXPECTED_OUTPUTS_SUBDIR è "expected_outputs"
            base_expected_path = os.path.join(_CURRENT_SCRIPT_DIR, compiler_globals.TEST_SUITE_DIR, args.expected_dir) # Use the configurable path
            expected_filename = os.path.join(base_expected_path, test_case["expected"])

            if regenerate_mode: # Regeneration mode
                # In regeneration mode, copy temp_output.asm to the expected file
                try:
                    # Ensure the destination directory exists
                    expected_dir = os.path.dirname(expected_filename)
                    if expected_dir: # Controlla se expected_dir non è una stringa vuota
                        os.makedirs(expected_dir, exist_ok=True)

                    # result_assembly_string ora contiene l'intero output formattato,
                    # inclusi i commenti del codice Python.
                    assembly_content = result_assembly_string

                    # Write the entire content (which already includes Python code comments)
                    # to the expected file.
                    with open(expected_filename, "w") as f_expected:
                        f_expected.write(assembly_content)

                    # print(f"File '{expected_filename}' RIGENERATO.") # Silenzioso in caso di successo
                    return True # Consider it a success for regeneration
                except Exception as e:
                    print(f"Error during file regeneration '{expected_filename}': {e}")
                    return False
            else: # Normal test mode
                if not os.path.exists(expected_filename):
                    print(f"Test '{test_case['name']}' SKIPPED: Expected file '{expected_filename}' not found.")
                    return False # pragma: no cover

                with open(expected_filename, "r") as expected_file:
                    expected_content = expected_file.read()

                generated_content = result_assembly_string

                # Rimuovi commenti e spazi extra per un confronto più robusto
                expected_content_processed = "\n".join(
                    [line.split(";")[0].strip() for line in expected_content.splitlines() if line.split(";")[0].strip()])
                generated_content_processed = "\n".join(
                    [line.split(";")[0].strip() for line in generated_content.splitlines() if line.split(";")[0].strip()])

                # Normalize line endings
                expected_content_processed = expected_content_processed.replace('\r\n', '\n')
                generated_content_processed = generated_content_processed.replace('\r\n', '\n')

                if expected_content_processed != generated_content_processed:
                    print(f"Test '{test_case['name']}' FALLITO: l'output generato non corrisponde all'output atteso.")
                    print("--- Differences ---")
                    # Usa diff per mostrare le differenze (se disponibile)
                    # To use diff, we need to write generated_content to a temporary file
                    # se non vogliamo usare temp_output_filename (che potrebbe essere obsoleto se python_to_assembly non lo aggiorna più in modo affidabile)
                    try:
                        # temp_output_filename è ancora scritto da python_to_assembly, quindi possiamo usarlo per diff
                        diff_result = subprocess.run(["diff", "-u", expected_filename, temp_output_filename],
                                                     capture_output=True, text=True, check=False)
                        print(diff_result.stdout)
                    except (FileNotFoundError, subprocess.CalledProcessError): # pragma: no cover
                        print("Could not find 'diff'. Differences not shown.")
                        print("Expected Output (processed):\n", expected_content_processed)
                        print("Generated Output (processed):\n", generated_content_processed)
                    return False
        else:
            print("Test without expected output, showing generated content:")
            print(result_assembly_string)

        print(f"Test '{test_case['name']}' PASSED.")
        return True # Traduzione: il test è passato

    except Exception as e:
        print(f"Test '{test_case['name']}' FAILED: Error during execution: {e}")
        import traceback
        traceback.print_exc() # Print the full traceback for easier debugging
        return False
    finally:
        # Cleanup (remove temporary files)
        try:
            if os.path.exists(temp_output_filename):
                os.remove(temp_output_filename)
        except FileNotFoundError: # pragma: no cover
            pass # Traduzione: non fare nulla se il file non esiste già
        print("--- Ending test ---")


def _log_test_result(test_name, status, message="", log_file_handle=None):
    """Logs the test result to the specified file handle."""
    if log_file_handle:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file_handle.write(f"[{timestamp}] {status}: {test_name} - {message}\n")
        log_file_handle.flush() # Forza la scrittura del buffer su disco

# --- Run all tests ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run py2asm tests and optionally regenerate expected outputs.")
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Regenerate the expected output files instead of comparing."
    )
    parser.add_argument(
        "test_file",
        nargs="?",
        default=None,
        help="Optional: specific test file to run/regenerate (e.g., test_arithmetic.py)"
    )
    parser.add_argument(
        "--expected-dir",
        default=compiler_globals.EXPECTED_OUTPUTS_SUBDIR, # Default to V1 expected outputs
        help="Directory containing expected output files (relative to test_suite). Defaults to 'expected_outputs'."
    )


    args = parser.parse_args()

    # Define log file paths
    LOGS_DIR = "logs"
    PASSED_LOG_FILENAME = "passed_tests.log"
    FAILED_LOG_FILENAME = "failed_tests.log"

    logs_full_path = os.path.join(_CURRENT_SCRIPT_DIR, compiler_globals.TEST_SUITE_DIR, LOGS_DIR)
    os.makedirs(logs_full_path, exist_ok=True)

    passed_log_file = None
    failed_log_file = None

    try:
        passed_log_file = open(os.path.join(logs_full_path, PASSED_LOG_FILENAME), 'w')
        failed_log_file = open(os.path.join(logs_full_path, FAILED_LOG_FILENAME), 'w')
    except IOError as e:
        print(f"Error opening log files: {e}", file=sys.stderr)
        sys.exit(1) # Exit if logging cannot be set up

    test_cases = load_test_cases(specific_file_name=args.test_file)

    num_tests = len(test_cases)
    num_passed = 0
    num_regenerated = 0
    num_failed_regeneration = 0

    try: # Use a try-finally block to ensure log files are closed
        for test_case in test_cases:
            if args.regenerate:
                if "expected" in test_case and test_case["expected"]:
                    # run_test will handle printing Starting/Ending/Code
                    # and any regeneration error.
                    # It will no longer print regeneration success.
                    if run_test(test_case, regenerate_mode=True): # True se rigenerazione OK
                        num_regenerated += 1
                        _log_test_result(test_case['name'], "REGENERATED", "File regenerated successfully", passed_log_file)
                    else:
                        # Error already printed by run_test, log it as a failure
                        _log_test_result(test_case['name'], "REGENERATION FAILED", "Error during regeneration", failed_log_file)
                        num_failed_regeneration +=1
                else:
                    # Test without 'expected' file. run_test will handle Starting/Ending/Code.
                    # No regeneration counters to update.
                    run_test(test_case, regenerate_mode=True) # Called to print Starting/Ending/Code

            else: # Normal test mode
                test_passed = run_test(test_case, regenerate_mode=False)
                if test_passed: # pragma: no branch
                    num_passed += 1
                    _log_test_result(test_case['name'], "PASSED", "Test completed successfully", passed_log_file)
                else:
                    _log_test_result(test_case['name'], "FAILED", "Test did not pass comparison or encountered an error", failed_log_file)
    finally:
        if passed_log_file: passed_log_file.close()
        if failed_log_file: failed_log_file.close()

    if not test_cases and args.test_file : # Specific file was requested but no tests loaded
        print(f"\nNo tests executed. Check if '{args.test_file}' is a valid test file with a 'test_cases' list.")
        sys.exit(1)
    elif not test_cases: # No specific file, and no tests found generally
        print(f"\nNo tests found or executed.")
        sys.exit(0) # Or 1 if this is considered an error state

    print(f"\n--- Test Summary ---")
    if args.regenerate:
        print(f"Casi di test processati per la rigenerazione: {num_regenerated + num_failed_regeneration}")
        print(f"Files successfully regenerated: {num_regenerated}")
        print(f"Files failed to regenerate: {num_failed_regeneration}")
        sys.exit(0 if num_failed_regeneration == 0 else 1)
    else:
        print(f"Total tests: {num_tests}")
        print(f"Tests passed: {num_passed}")
        print(f"Tests failed: {num_tests - num_passed}")
        sys.exit(0 if num_passed == num_tests else 1)
