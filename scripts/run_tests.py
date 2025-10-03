#!/usr/bin/env python3
"""
Test runner script with various testing options
"""
import sys
import os
import argparse
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd, description):
    """Run a command and handle output"""
    print(f"🚀 {description}...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found. Make sure required tools are installed.")
        return False


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests"""
    cmd = ['python', '-m', 'pytest', 'tests/unit']

    if verbose:
        cmd.append('-v')

    if coverage:
        cmd.extend(['--cov=app', '--cov=config', '--cov-report=html'])

    return run_command(cmd, "Running unit tests")


def run_integration_tests(verbose=False):
    """Run integration tests"""
    cmd = ['python', '-m', 'pytest', 'tests/integration']

    if verbose:
        cmd.append('-v')

    return run_command(cmd, "Running integration tests")


def run_all_tests(verbose=False, coverage=False):
    """Run all tests"""
    cmd = ['python', '-m', 'pytest', 'tests']

    if verbose:
        cmd.append('-v')

    if coverage:
        cmd.extend(['--cov=app', '--cov=config', '--cov-report=html', '--cov-report=term-missing'])

    return run_command(cmd, "Running all tests")


def run_linting():
    """Run code linting"""
    commands = [
        (['python', '-m', 'flake8', 'app.py', 'config/', 'src/', 'tests/'], "Running flake8 linting"),
        (['python', '-m', 'isort', '--check-only', '--diff', 'app.py', 'config/', 'src/', 'tests/'], "Checking import sorting"),
        (['python', '-m', 'black', '--check', '--diff', 'app.py', 'config/', 'src/', 'tests/'], "Checking code formatting")
    ]

    all_passed = True
    for cmd, description in commands:
        if not run_command(cmd, description):
            all_passed = False

    return all_passed


def run_type_checking():
    """Run type checking with mypy"""
    cmd = ['python', '-m', 'mypy', 'app.py', 'config/', 'src/']
    return run_command(cmd, "Running type checking")


def run_security_check():
    """Run security checks"""
    cmd = ['python', '-m', 'bandit', '-r', 'app.py', 'config/', 'src/']
    return run_command(cmd, "Running security checks")


def fix_formatting():
    """Fix code formatting issues"""
    commands = [
        (['python', '-m', 'isort', 'app.py', 'config/', 'src/', 'tests/'], "Fixing import sorting"),
        (['python', '-m', 'black', 'app.py', 'config/', 'src/', 'tests/'], "Fixing code formatting")
    ]

    all_passed = True
    for cmd, description in commands:
        if not run_command(cmd, description):
            all_passed = False

    return all_passed


def run_full_quality_check():
    """Run comprehensive quality checks"""
    print("🔍 Running comprehensive quality checks...")
    print("=" * 60)

    checks = [
        (run_linting, "Code linting"),
        (run_type_checking, "Type checking"),
        (run_security_check, "Security analysis"),
        (lambda: run_all_tests(coverage=True), "Test suite with coverage")
    ]

    results = []
    for check_func, name in checks:
        print(f"\n📊 {name}")
        print("-" * 40)
        success = check_func()
        results.append((name, success))
        print()

    # Summary
    print("=" * 60)
    print("📋 QUALITY CHECK SUMMARY")
    print("=" * 60)

    passed = 0
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if success:
            passed += 1

    print(f"\n🎯 Results: {passed}/{len(results)} checks passed")

    if passed == len(results):
        print("🎉 All quality checks passed!")
        return True
    else:
        print("⚠️  Some quality checks failed. Please review and fix issues.")
        return False


def create_test_report():
    """Create a detailed test report"""
    cmd = [
        'python', '-m', 'pytest',
        'tests/',
        '--cov=app',
        '--cov=config',
        '--cov-report=html:htmlcov',
        '--cov-report=xml',
        '--junitxml=test-results.xml',
        '--html=test-report.html',
        '--self-contained-html'
    ]

    success = run_command(cmd, "Generating detailed test report")

    if success:
        print("\n📊 Test reports generated:")
        print("  • HTML Coverage: htmlcov/index.html")
        print("  • XML Coverage: coverage.xml")
        print("  • Test Results: test-results.xml")
        print("  • HTML Report: test-report.html")

    return success


def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(description='EMODnet Viewer Test Runner')

    # Test type options
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument('--unit', action='store_true', help='Run unit tests only')
    test_group.add_argument('--integration', action='store_true', help='Run integration tests only')
    test_group.add_argument('--all', action='store_true', help='Run all tests (default)')

    # Quality check options
    parser.add_argument('--lint', action='store_true', help='Run code linting')
    parser.add_argument('--type-check', action='store_true', help='Run type checking')
    parser.add_argument('--security', action='store_true', help='Run security checks')
    parser.add_argument('--quality', action='store_true', help='Run full quality check suite')

    # Formatting options
    parser.add_argument('--fix', action='store_true', help='Fix formatting issues')

    # Report options
    parser.add_argument('--report', action='store_true', help='Generate detailed test report')

    # Test options
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Generate coverage report')

    args = parser.parse_args()

    # If no specific action is specified, run all tests
    if not any([args.unit, args.integration, args.lint, args.type_check,
                args.security, args.quality, args.fix, args.report]):
        args.all = True

    success = True

    # Handle formatting fixes first
    if args.fix:
        success &= fix_formatting()

    # Handle quality checks
    if args.quality:
        success &= run_full_quality_check()
    else:
        if args.lint:
            success &= run_linting()

        if args.type_check:
            success &= run_type_checking()

        if args.security:
            success &= run_security_check()

        # Handle test execution
        if args.unit:
            success &= run_unit_tests(args.verbose, args.coverage)
        elif args.integration:
            success &= run_integration_tests(args.verbose)
        elif args.all:
            success &= run_all_tests(args.verbose, args.coverage)

    # Generate detailed report if requested
    if args.report:
        success &= create_test_report()

    # Exit with appropriate code
    if success:
        print("\n🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some operations failed. Please review the output above.")
        sys.exit(1)


if __name__ == '__main__':
    main()