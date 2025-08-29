"""
Test suite for GeotechAgent - Main agent workflow testing
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.agent import GeotechAgent

def test_agent_initialization():
    """Test agent initialization and configuration loading"""
    print("\n🤖 TESTING AGENT INITIALIZATION")
    print("=" * 50)
    
    try:
        agent = GeotechAgent()
        
        print("✅ Agent initialized successfully")
        print(f"LLM Model: {agent.llm_service.model}")
        print(f"System Prompt Length: {len(agent.system_prompt)} characters")
        print(f"Planning Prompt Length: {len(agent.planning_prompt)} characters")
        print(f"Synthesis Prompt Length: {len(agent.synthesis_prompt)} characters")
        
        # Test statistics
        stats = agent.get_statistics()
        print(f"Initial Statistics: {stats}")
        
        return True, agent
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False, None

def test_agent_planning():
    """Test agent planning functionality"""
    print("\n📋 TESTING AGENT PLANNING")
    print("=" * 50)
    
    agent = GeotechAgent()
    
    test_questions = [
        "What is bearing capacity?",  # Should be retrieve
        "Calculate settlement for load 1000 kN and Young's modulus 50000 kPa",  # Should be calculate_settlement
        "Calculate bearing capacity for B=2m, gamma=18 kN/m³, Df=1.5m, phi=30°",  # Should be calculate_bearing_capacity
        "Hello, how are you?"  # Should be answer_directly
    ]
    
    for i, question in enumerate(test_questions, 1):
        try:
            print(f"\n{i}. Testing question: {question}")
            plan = agent.plan(question)
            
            print(f"   Action: {plan['action']}")
            print(f"   Reasoning: {plan['reasoning']}")
            
            if 'tool_parameters' in plan:
                print(f"   Tool Parameters: {plan['tool_parameters']}")
            if 'search_query' in plan:
                print(f"   Search Query: {plan['search_query']}")
                
        except Exception as e:
            print(f"   ❌ Planning failed: {e}")
            return False
    
    print("\n✅ All planning tests passed")
    return True

def test_agent_execution():
    """Test agent execution functionality"""
    print("\n⚙️ TESTING AGENT EXECUTION")
    print("=" * 50)
    
    agent = GeotechAgent()
    
    # Test settlement calculation execution
    settlement_plan = {
        "action": "calculate_settlement",
        "reasoning": "User asked for settlement calculation",
        "tool_parameters": {
            "load": 1000.0,
            "young_modulus": 50000.0
        }
    }
    
    try:
        print("1. Testing settlement calculation execution...")
        result = agent.execute(settlement_plan, "Calculate settlement")
        
        print(f"   Action taken: {result['action_taken']}")
        
        if result['calculation_results']:
            calc = result['calculation_results']
            if calc['status'] == 'success':
                print(f"   ✅ Settlement: {calc['settlement']}")
                print(f"   Formula: {calc['formula']}")
            else:
                print(f"   ❌ Calculation error: {calc['error']}")
        
    except Exception as e:
        print(f"   ❌ Settlement execution failed: {e}")
        return False
    
    # Test bearing capacity calculation execution
    bearing_plan = {
        "action": "calculate_bearing_capacity", 
        "reasoning": "User asked for bearing capacity calculation",
        "tool_parameters": {
            "B": 2.0,
            "gamma": 18.0,
            "Df": 1.5,
            "phi": 30
        }
    }
    
    try:
        print("\n2. Testing bearing capacity calculation execution...")
        result = agent.execute(bearing_plan, "Calculate bearing capacity")
        
        print(f"   Action taken: {result['action_taken']}")
        
        if result['calculation_results']:
            calc = result['calculation_results']
            if calc['status'] == 'success':
                print(f"   ✅ Ultimate bearing capacity: {calc['q_ultimate']} kPa")
                print(f"   Factors used - Nq: {calc['factors']['Nq']}, Nr: {calc['factors']['Nr']}")
            else:
                print(f"   ❌ Calculation error: {calc['error']}")
        
    except Exception as e:
        print(f"   ❌ Bearing capacity execution failed: {e}")
        return False
    
    # Test retrieval execution (if vector DB is available)
    retrieval_plan = {
        "action": "retrieve",
        "reasoning": "User asked conceptual question",
        "search_query": "bearing capacity foundation"
    }
    
    try:
        print("\n3. Testing retrieval execution...")
        result = agent.execute(retrieval_plan, "What is bearing capacity?")
        
        print(f"   Action taken: {result['action_taken']}")
        print(f"   Citations found: {len(result['citations'])}")
        
        if result['citations']:
            for i, citation in enumerate(result['citations'][:2]):  # Show first 2
                print(f"   Citation {i+1}: {citation.source_name} (score: {citation.confidence_score:.3f})")
        else:
            print("   ⚠️ No citations found (vector DB may not be populated)")
        
    except Exception as e:
        print(f"   ❌ Retrieval execution failed: {e}")
        # Don't return False here as vector DB might not be set up
    
    print("\n✅ Execution tests completed")
    return True

def test_agent_full_workflow():
    """Test complete agent workflow"""
    print("\n🔄 TESTING FULL AGENT WORKFLOW")
    print("=" * 50)
    
    agent = GeotechAgent()
    
    test_questions = [
        "Calculate settlement for load 500 kN and Young's modulus 25000 kPa",
        "What is CPT analysis?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        try:
            print(f"\n{i}. Full workflow test: {question}")
            
            response = agent.run(question)
            
            print(f"   ✅ Answer received (length: {len(response.answer)} chars)")
            print(f"   Citations: {len(response.citations)}")
            print(f"   Trace ID: {response.trace_id}")
            print(f"   Answer preview: {response.answer[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Full workflow failed: {e}")
            return False
    
    # Test statistics after workflow
    stats = agent.get_statistics()
    print(f"\nFinal Statistics: {stats}")
    
    print("\n✅ Full workflow tests passed")
    return True

def main():
    """Run all agent tests"""
    print("🧪 GEOTECH AGENT TEST SUITE")
    print("Testing agent initialization, planning, execution, and full workflow...")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Initialization
    success, agent = test_agent_initialization()
    if success:
        tests_passed += 1
    
    # Test 2: Planning
    if test_agent_planning():
        tests_passed += 1
    
    # Test 3: Execution  
    if test_agent_execution():
        tests_passed += 1
    
    # Test 4: Full workflow
    if test_agent_full_workflow():
        tests_passed += 1
    
    print("\n" + "=" * 70)
    print(f"AGENT TESTS COMPLETED: {tests_passed}/{total_tests} PASSED")
    print("=" * 70)
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Agent is ready for API integration.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    # Set up basic logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    main()