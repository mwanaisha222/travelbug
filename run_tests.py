"""
Test runner script for the TravelBug application.
Runs all test suites and provides comprehensive coverage reporting.
"""
import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings


def run_tests():
    """Run all test suites for the TravelBug application."""
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TravelBucket.settings')
    django.setup()
    
    # Get the Django test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Define test modules to run
    test_modules = [
        'explorer.test_models',
        'explorer.test_views', 
        'explorer.test_forms',
        'explorer.test_integration',
        'explorer.test_regression'
    ]
    
    print("=" * 70)
    print("TRAVELBUG APPLICATION TEST SUITE")
    print("=" * 70)
    print()
    
    # Run each test module
    total_failures = 0
    results = {}
    
    for module in test_modules:
        print(f"Running tests in {module}...")
        print("-" * 50)
        
        try:
            failures = test_runner.run_tests([module])
            results[module] = {
                'status': 'PASSED' if failures == 0 else 'FAILED',
                'failures': failures
            }
            total_failures += failures
            
        except Exception as e:
            print(f"Error running {module}: {e}")
            results[module] = {
                'status': 'ERROR',
                'failures': 1,
                'error': str(e)
            }
            total_failures += 1
        
        print()
    
    # Print summary
    print("=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for module, result in results.items():
        status_symbol = "✓" if result['status'] == 'PASSED' else "✗"
        print(f"{status_symbol} {module}: {result['status']}")
        if result['status'] == 'ERROR' and 'error' in result:
            print(f"   Error: {result['error']}")
        elif result['failures'] > 0:
            print(f"   Failures: {result['failures']}")
    
    print()
    print(f"Total test modules: {len(test_modules)}")
    print(f"Passed: {sum(1 for r in results.values() if r['status'] == 'PASSED')}")
    print(f"Failed: {sum(1 for r in results.values() if r['status'] != 'PASSED')}")
    print(f"Total failures: {total_failures}")
    
    if total_failures == 0:
        print("\n🎉 All tests passed! Your application is working correctly.")
        return 0
    else:
        print(f"\n❌ {total_failures} test(s) failed. Please review the failures above.")
        return 1


def run_specific_test_category(category):
    """Run a specific category of tests."""
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TravelBucket.settings')
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    category_modules = {
        'models': ['explorer.test_models'],
        'views': ['explorer.test_views'],
        'forms': ['explorer.test_forms'],
        'integration': ['explorer.test_integration'],
        'regression': ['explorer.test_regression']
    }
    
    if category not in category_modules:
        print(f"Invalid category. Available categories: {', '.join(category_modules.keys())}")
        return 1
    
    modules = category_modules[category]
    print(f"Running {category} tests...")
    
    total_failures = 0
    for module in modules:
        failures = test_runner.run_tests([module])
        total_failures += failures
    
    return total_failures


if __name__ == '__main__':
    if len(sys.argv) > 1:
        category = sys.argv[1]
        sys.exit(run_specific_test_category(category))
    else:
        sys.exit(run_tests())