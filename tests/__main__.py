from subprocess import run
from sys import executable
from typing import Dict, List


def run_test_module(module_path: str) -> bool:
    """
    Run a single test module and return the result.

    Parameters:
        module_path (str): The module path to run as a test.

    Returns:
        bool: True if the test passed, False otherwise.
    """
    print(f"\n{'='*70}")
    print(f"Running: {module_path}")
    print(f"{'='*70}")

    try:
        result = run(
            [executable, "-m", module_path],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {module_path}: {e}")
        return False

def main() -> None:
    """Run all test modules."""
    # List of test modules to run
    test_modules: List[str] = [
        "tests.actions.edit_test",
        "tests.actions.login_test",
        "tests.actions.logout_test",
        "tests.actions.register_test",
        "tests.core.action_registry_test",
        "tests.core.action_response_test",
        "tests.core.action_runner_test",
        "tests.core.action_schema_test",
        "tests.core.database_test",
        "tests.core.plugboard_client_test",
        "tests.events.phx_join_event_test",
        "tests.events.request_event_test"
    ]

    print("Running all tests...")

    results: Dict[str, bool] = {}

    for module in test_modules:
        success = run_test_module(module)
        results[module] = success

    # Print summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")

    passed = 0
    failed = 0

    for module, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{module}: {status}")
        if success:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {len(test_modules)} | Passed: {passed} | Failed: {failed}")

    if failed > 0:
        print(f"\n{failed} test module(s) failed!")
        exit(1)
    else:
        print("\nAll tests passed!")
        exit(0)

if __name__ == "__main__":
    main()
