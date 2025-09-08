"""
Agent Test Runner
Convenient script to run different categories of agent tests
"""

import sys
import subprocess
from pathlib import Path

def run_tests(test_category=None, verbose=True, coverage=False):
    """Run agent tests with specified options"""
    
    # Base command
    cmd = ["python", "-m", "pytest"]
    
    # Test file selection
    if test_category:
        test_categories = {
            "comprehensive": "tests/test_agent_comprehensive.py",
            "basic": "tests/test_agent.py",
            "rag_eval": "tests/test_rag_quality_evaluation.py",
            "unit": "tests/test_agent_comprehensive.py -m unit",
            "integration": "tests/test_agent_comprehensive.py -m integration",
            "edge_cases": "tests/test_agent_comprehensive.py -m edge_cases",
            "real_llm": "tests/test_agent_comprehensive.py -m real_llm",
            "all_agent": "tests/test_agent_comprehensive.py tests/test_agent.py"
        }
        
        if test_category in test_categories:
            cmd.extend(test_categories[test_category].split())
        else:
            print(f"Unknown test category: {test_category}")
            print(f"Available categories: {', '.join(test_categories.keys())}")
            return False
    else:
        # Run all agent tests by default
        cmd.append("tests/test_agent_comprehensive.py")
    
    # Verbosity
    if verbose:
        cmd.append("-v")
    
    # Coverage
    if coverage:
        cmd.extend(["--cov=app.core.agent", "--cov-report=html", "--cov-report=term"])
    
    # Additional options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings",
        "--color=yes"
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 70)
    
    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        test_category = sys.argv[1]
    else:
        test_category = None
    
    print("GEOTECH AGENT TEST RUNNER")
    print("=" * 70)
    
    success = run_tests(test_category, verbose=True)
    
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed. Check output above.")
        sys.exit(1)

def show_help():
    """Show available test categories"""
    print("""
Geotech Agent Test Runner

Usage: python tests/run_agent_tests.py [category]

Available test categories:
  comprehensive - Full comprehensive test suite (default)
  basic        - Original basic agent tests
  rag_eval     - RAG quality evaluation tests
  unit         - Unit tests only
  integration  - Integration tests only  
  edge_cases   - Edge case tests only
  all_agent    - All agent-related tests

Examples:
  python tests/run_agent_tests.py                    # Run comprehensive tests
  python tests/run_agent_tests.py unit              # Run only unit tests
  python tests/run_agent_tests.py edge_cases        # Run only edge case tests
  python tests/run_agent_tests.py all_agent         # Run all agent tests

Test Coverage:
- Agent initialization and setup
- Planning for all scenarios (in-scope, out-of-scope, calculations)
- Execution testing (success/failure cases)
- Synthesis with different contexts
- Full workflow integration tests
- Edge cases and error handling

Query Coverage:
- In-scope: Settle3, CPT analysis, liquefaction, calculations
- Out-of-scope: General engineering, personal, non-geotechnical
- Edge cases: Invalid params, missing data, malicious inputs
- Calculations: Settlement and bearing capacity with validation
- Mixed queries: Combined calculation + retrieval requests
""")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        show_help()
    else:
        main()