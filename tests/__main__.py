from os import environ
from subprocess import run
from sys import executable

environ["ENVIRONMENT"] = "test"

def run_test_module(module_path):
    """Run a single test module and return the result."""
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

def main():
    """Run all test modules."""
    # List of test modules to run
    test_modules = [
        "tests.core.action_registry_test",
        "tests.core.plugboard_client_test"
    ]

    print("Running all tests...")

    results = {}

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
