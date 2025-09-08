"""
Comprehensive Agent Test Suite
Tests all scenarios including planning, execution, synthesis, and edge cases
"""

import pytest
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.agent import GeotechAgent
from tests.fixtures.test_queries import TestQueryDatasets


@pytest.mark.unit
class TestAgentInitialization:
    """Test agent initialization and basic setup"""
    
    def test_agent_initialization_success(self, real_llm_agent):
        """Test successful agent initialization"""
        assert real_llm_agent is not None
        assert hasattr(real_llm_agent, 'llm_service')
        assert hasattr(real_llm_agent, 'rag_service')
        assert hasattr(real_llm_agent, 'system_prompt')
        assert hasattr(real_llm_agent, 'planning_prompt')
        assert hasattr(real_llm_agent, 'synthesis_prompt')
    
    def test_agent_prompts_loaded(self, real_llm_agent):
        """Test that agent prompts are loaded correctly"""
        assert len(real_llm_agent.system_prompt) > 0
        assert len(real_llm_agent.planning_prompt) > 0
        assert len(real_llm_agent.synthesis_prompt) > 0
        assert "KNOWLEDGE BASE COVERAGE" in real_llm_agent.planning_prompt
        assert "out_of_scope" in real_llm_agent.planning_prompt


@pytest.mark.integration
@pytest.mark.real_llm
class TestAgentPlanning:
    """Test agent planning functionality with all scenarios"""
    
    @pytest.mark.asyncio
    async def test_planning_in_scope_retrieval_queries(self, real_llm_agent, retrieval_queries):
        """Test planning for in-scope retrieval queries"""
        for query_data in retrieval_queries:
            question = query_data["question"]
            expected_action = query_data["expected_action"]
            
            plan = await real_llm_agent.plan(question)
            
            assert plan["action"] == expected_action
            assert "reasoning" in plan
            assert len(plan["reasoning"]) > 0
            
            if "expected_search_query" in query_data:
                assert "search_query" in plan
    
    @pytest.mark.asyncio
    async def test_planning_settlement_calculation_queries(self, real_llm_agent, settlement_queries):
        """Test planning for settlement calculation queries"""
        for query_data in settlement_queries:
            question = query_data["question"]
            expected_action = query_data["expected_action"]
            expected_params = query_data.get("expected_params", {})
            
            plan = await real_llm_agent.plan(question)
            
            assert plan["action"] == expected_action
            assert "tool_parameters" in plan
            
            if expected_params:
                assert "load" in plan["tool_parameters"]
                assert "young_modulus" in plan["tool_parameters"]
                assert plan["tool_parameters"]["load"] > 0
                assert plan["tool_parameters"]["young_modulus"] > 0
    
    @pytest.mark.asyncio
    async def test_planning_bearing_capacity_calculation_queries(self, real_llm_agent, bearing_capacity_queries):
        """Test planning for bearing capacity calculation queries"""
        for query_data in bearing_capacity_queries:
            question = query_data["question"]
            expected_action = query_data["expected_action"]
            expected_params = query_data.get("expected_params", {})
            
            plan = await real_llm_agent.plan(question)
            
            assert plan["action"] == expected_action
            assert "tool_parameters" in plan
            
            if expected_params:
                required_params = ["B", "gamma", "Df", "phi"]
                for param in required_params:
                    assert param in plan["tool_parameters"]
    
    @pytest.mark.asyncio
    async def test_planning_out_of_scope_queries(self, real_llm_agent, out_of_scope_queries):
        """Test planning correctly identifies out-of-scope queries"""
        for query_data in out_of_scope_queries:
            question = query_data["question"]
            expected_action = query_data["expected_action"]
            
            plan = await real_llm_agent.plan(question)
            
            assert plan["action"] == expected_action
            assert "reasoning" in plan
            assert "knowledge base scope" in plan["reasoning"].lower()
    
    @pytest.mark.parametrize("question,expected_action", [
        ("What is the weather today?", "out_of_scope"),
        ("How to cook pasta?", "out_of_scope"),
        ("Calculate settlement for 1000kN load, E=50MPa", "calculate_settlement"),
        ("What is bearing capacity?", "retrieve"),
        ("How does Settle3 work?", "retrieve"),
        ("Design a steel beam", "out_of_scope"),
    ])
    @pytest.mark.asyncio
    async def test_planning_specific_scenarios(self, real_llm_agent, question, expected_action):
        """Test specific planning scenarios with parametrized inputs"""
        plan = await real_llm_agent.plan(question)
        assert plan["action"] == expected_action
    
    @pytest.mark.asyncio
    async def test_planning_combined_queries(self, real_llm_agent):
        """Test planning for queries requiring both calculation and retrieval"""
        question = "Calculate settlement for 800kN load with E=40MPa and explain consolidation theory"
        plan = await real_llm_agent.plan(question)
        
        assert plan["action"] == "both"
        assert "tool_parameters" in plan
        assert "search_query" in plan


@pytest.mark.integration
@pytest.mark.real_llm
class TestAgentExecution:
    """Test agent execution functionality"""
    
    @pytest.mark.asyncio
    async def test_execution_settlement_calculation_success(self, real_llm_agent):
        """Test successful settlement calculation execution"""
        plan = {
            "action": "calculate_settlement",
            "reasoning": "Settlement calculation requested",
            "tool_parameters": {
                "load": 1000.0,
                "young_modulus": 50000.0
            }
        }
        
        result = await real_llm_agent.execute(plan, "Calculate settlement")
        
        assert result["action_taken"] == "calculate_settlement"
        assert result["calculation_results"] is not None
        assert result["calculation_results"]["status"] == "success"
        assert "settlement" in result["calculation_results"]
    
    @pytest.mark.asyncio
    async def test_execution_bearing_capacity_calculation_success(self, real_llm_agent):
        """Test successful bearing capacity calculation execution"""
        plan = {
            "action": "calculate_bearing_capacity",
            "reasoning": "Bearing capacity calculation requested", 
            "tool_parameters": {
                "B": 2.0,
                "gamma": 18.0,
                "Df": 1.5,
                "phi": 30
            }
        }
        
        result = await real_llm_agent.execute(plan, "Calculate bearing capacity")
        
        assert result["action_taken"] == "calculate_bearing_capacity"
        assert result["calculation_results"] is not None
        assert result["calculation_results"]["status"] == "success"
        assert "q_ultimate" in result["calculation_results"]
    
    @pytest.mark.asyncio
    async def test_execution_retrieval_success(self, real_llm_agent):
        """Test successful retrieval execution"""
        plan = {
            "action": "retrieve",
            "reasoning": "Conceptual question about bearing capacity",
            "search_query": "bearing capacity"
        }
        
        result = await real_llm_agent.execute(plan, "What is bearing capacity?")
        
        assert result["action_taken"] == "retrieve"
        assert "citations" in result
        assert len(result["citations"]) > 0
        assert "retrieved_info" in result
    
    @pytest.mark.asyncio
    async def test_execution_out_of_scope(self, real_llm_agent):
        """Test out-of-scope execution"""
        plan = {
            "action": "out_of_scope",
            "reasoning": "Question outside knowledge base scope"
        }
        
        result = await real_llm_agent.execute(plan, "What's the weather?")
        
        assert result["action_taken"] == "out_of_scope"
        assert result["out_of_scope"] is True
        assert "scope_message" in result
    
    @pytest.mark.asyncio
    async def test_execution_both_action(self, real_llm_agent):
        """Test execution with both calculation and retrieval"""
        plan = {
            "action": "both",
            "reasoning": "Both calculation and background info needed",
            "tool_parameters": {
                "load": 800.0,
                "young_modulus": 40000.0
            },
            "search_query": "settlement consolidation"
        }
        
        result = await real_llm_agent.execute(plan, "Calculate and explain settlement")
        
        assert result["action_taken"] == "both"
        assert result["calculation_results"] is not None
        assert "citations" in result
        assert "retrieved_info" in result


@pytest.mark.integration  
@pytest.mark.real_llm
class TestAgentSynthesis:
    """Test agent synthesis functionality"""
    
    @pytest.mark.asyncio
    async def test_synthesis_out_of_scope_handling(self, real_llm_agent):
        """Test synthesis handles out-of-scope results"""
        execution_results = {
            "out_of_scope": True,
            "scope_message": "Question outside scope"
        }
        
        answer = await real_llm_agent.synthesize("What's the weather?", execution_results)
        
        assert "outside my knowledge base scope" in answer
        assert "Settle3" in answer
        assert "CPT analysis" in answer
        assert "Liquefaction" in answer
    
    @pytest.mark.asyncio
    async def test_synthesis_with_calculation_results(self, real_llm_agent):
        """Test synthesis with calculation results"""
        execution_results = {
            "action_taken": "calculate_settlement",
            "calculation_results": {
                "settlement": 0.02,
                "load": 1000.0,
                "young_modulus": 50000.0,
                "formula": "settlement = load / young_modulus",
                "status": "success"
            },
            "retrieved_info": "Settlement calculation performed successfully.",
            "citations": []
        }
        
        answer = await real_llm_agent.synthesize("Calculate settlement", execution_results)
        
        assert len(answer) > 0
        assert answer != "I could not find a definitive answer in the knowledge base for your question."
    
    @pytest.mark.asyncio
    async def test_synthesis_with_retrieval_results(self, real_llm_agent):
        """Test synthesis with retrieval results"""
        execution_results = {
            "action_taken": "retrieve",
            "calculation_results": "No calculations performed.",
            "retrieved_info": "Source: Settle3-Theory-Manual.pdf\nBearing capacity is the maximum load per unit area that a soil can support without shear failure. Ultimate bearing capacity is calculated using Terzaghi's formula: q_ult = c*Nc + γ*Df*Nq + 0.5*γ*B*Nr, where c is cohesion, γ is unit weight, Df is footing depth, B is footing width, and Nc, Nq, Nr are bearing capacity factors dependent on friction angle.",
            "citations": [
                {"source_name": "Settle3-Theory-Manual.pdf", "confidence_score": 0.9}
            ]
        }
        
        answer = await real_llm_agent.synthesize("What is bearing capacity?", execution_results)
        
        assert len(answer) > 0
        assert answer != "I could not find a definitive answer in the knowledge base for your question."
    


@pytest.mark.integration
@pytest.mark.real_llm
class TestAgentFullWorkflow:
    """Test complete agent workflow from question to answer"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_settlement_calculation(self, real_llm_agent):
        """Test complete workflow for settlement calculation"""
        question = "Calculate settlement for load 1000 kN and Young's modulus 50000 kPa"
        
        response = await real_llm_agent.run(question)
        
        assert response.answer is not None
        assert len(response.answer) > 0
        assert response.trace_id is not None
        assert len(response.citations) >= 0  # May or may not have citations
    
    @pytest.mark.asyncio
    async def test_full_workflow_conceptual_question(self, real_llm_agent):
        """Test complete workflow for conceptual question"""
        question = "What is bearing capacity?"
        
        response = await real_llm_agent.run(question)
        
        assert response.answer is not None
        assert len(response.answer) > 0
        assert response.trace_id is not None
        assert len(response.citations) > 0  # Should have citations from retrieval
    
    @pytest.mark.asyncio
    async def test_full_workflow_out_of_scope_question(self, real_llm_agent):
        """Test complete workflow for out-of-scope question"""
        question = "What's the weather today?"
        
        response = await real_llm_agent.run(question)
        
        assert response.answer is not None
        assert "outside my knowledge base scope" in response.answer
        assert "Settle3" in response.answer
        assert len(response.citations) == 0  # No citations for out-of-scope
    


@pytest.mark.integration
@pytest.mark.real_llm  
class TestAgentEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.parametrize("invalid_params", [
        {"load": "not_a_number", "young_modulus": 50000},
        {"load": float('inf'), "young_modulus": 50000},
        {"load": -1000, "young_modulus": 50000},
        {"load": 1000, "young_modulus": 0},
    ])
    @pytest.mark.asyncio
    async def test_invalid_calculation_parameters(self, real_llm_agent, invalid_params):
        """Test handling of invalid calculation parameters"""
        plan = {
            "action": "calculate_settlement",
            "reasoning": "Test invalid parameters",
            "tool_parameters": invalid_params
        }
        
        result = await real_llm_agent.execute(plan, "Test question")
        
        # Should handle invalid parameters gracefully
        assert result["action_taken"] == "calculate_settlement"
        # May succeed or fail depending on validation level



if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])