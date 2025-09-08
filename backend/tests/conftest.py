"""
Shared pytest fixtures and configuration for Geotech AI Service tests
"""

import os
import sys
import pytest
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config.settings import get_settings
from app.core.agent import GeotechAgent
from tests.fixtures.test_queries import TestQueryDatasets

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_settings():
    """Get test settings configuration"""
    return get_settings()

@pytest.fixture(scope="function")
def temp_test_dir(tmp_path):
    """Create temporary directory for test files"""
    return tmp_path

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment - runs automatically for all tests"""
    # Ensure required directories exist
    test_dirs = [
        "tests/reports",
        "evaluation",
        "logs"
    ]
    
    project_root = Path(__file__).parent.parent
    for dir_path in test_dirs:
        (project_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Set environment variables for testing if not already set
    test_env_vars = {
        "ENVIRONMENT": "testing",
        "LOG_LEVEL": "INFO"
    }
    
    for key, value in test_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    yield
    
    # Cleanup after all tests (if needed)
    pass


# Agent-specific fixtures

@pytest.fixture
def real_llm_agent():
    """Create agent with real LLM service for LLM testing"""
    return GeotechAgent()

@pytest.fixture
def test_queries():
    """Provide test query datasets"""
    return TestQueryDatasets

@pytest.fixture
def in_scope_queries(test_queries):
    """Provide in-scope test queries"""
    return test_queries.get_all_in_scope_queries()

@pytest.fixture
def out_of_scope_queries(test_queries):
    """Provide out-of-scope test queries"""
    return test_queries.get_all_out_of_scope_queries()

@pytest.fixture
def edge_case_queries(test_queries):
    """Provide edge case test queries"""
    return test_queries.get_all_edge_case_queries()

@pytest.fixture
def settlement_queries(test_queries):
    """Provide settlement calculation test queries"""
    return [q for q in test_queries.get_all_in_scope_queries() 
            if q.get("expected_action") == "calculate_settlement"]

@pytest.fixture
def bearing_capacity_queries(test_queries):
    """Provide bearing capacity calculation test queries"""
    return [q for q in test_queries.get_all_in_scope_queries()
            if q.get("expected_action") == "calculate_bearing_capacity"]

@pytest.fixture
def retrieval_queries(test_queries):
    """Provide retrieval test queries"""
    return [q for q in test_queries.get_all_in_scope_queries()
            if q.get("expected_action") == "retrieve"]


# Pytest markers for test categorization
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::UserWarning")
]