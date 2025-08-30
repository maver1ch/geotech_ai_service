"""
Main Agent Orchestrator
Plan → Execute → Synthesize workflow for geotechnical AI assistant
"""

import json
import uuid
import logging
import time
from typing import Dict, Any, Optional

from app.core.config.settings import get_settings
from app.core.config.config_loader import (
    get_system_prompt, 
    get_planning_prompt, 
    get_synthesis_prompt
)
from app.core.config.logging_config import get_trace_logger
from app.core.llms.openai import OpenAIService
from app.services.agentic_workflow.tools.geotech_calculators import call_tool
from app.services.agentic_workflow.retrieval.rag_service import RAGService
from app.services.observability import (
    get_langfuse_client, 
    get_metrics_collector, 
    time_request
)
from app.api.schema.response import AskResponse

logger = logging.getLogger(__name__)

class GeotechAgent:
    """
    Main Agent for geotechnical engineering questions
    Orchestrates Plan → Execute → Synthesize workflow
    """
    
    def __init__(self):
        self.settings = get_settings()
        
        # Initialize services
        self.llm_service = OpenAIService(
            api_key=self.settings.OPENAI_API_KEY,
            model=self.settings.OPENAI_MODEL,
            timeout=self.settings.LLM_TIMEOUT,
            max_retries=self.settings.LLM_MAX_RETRIES,
            max_completion_tokens=self.settings.LLM_MAX_COMPLETION_TOKENS
        )
        
        self.rag_service = RAGService(
            openai_api_key=self.settings.OPENAI_API_KEY,
            gemini_api_key=self.settings.GOOGLE_GENAI_API_KEY,
            settings=self.settings
        )
        
        # Load prompts
        self.system_prompt = get_system_prompt()
        self.planning_prompt = get_planning_prompt()
        self.synthesis_prompt = get_synthesis_prompt()
        
        # Track statistics
        self.total_requests = 0
        self.tool_calls = 0
        self.retrieval_calls = 0
    
    def plan(self, question: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Step 1: Analyze question and create execution plan
        
        Args:
            question: User's question
            trace_id: Optional trace ID for observability
            
        Returns:
            Dict containing action plan and parameters
        """
        start_time = time.time()
        
        # Get trace logger if trace_id is provided
        trace_logger = get_trace_logger(trace_id or "test-trace")
        trace_logger.log_agent_step("planning", "Starting agent planning phase")
        
        try:
            # Format planning prompt with question
            formatted_prompt = self.planning_prompt.format(question=question)
            
            # Create conversation
            messages = self.llm_service.create_conversation(
                system_prompt=self.system_prompt,
                user_message=formatted_prompt
            )
            
            # Get LLM decision
            response = self.llm_service.call_llm(messages)
            
            logger.info(f"LLM planning response status: {response.get('status')}")
            
            if response["status"] != "success":
                error_msg = response.get('error', 'Unknown error')
                logger.error(f"LLM planning failed: {error_msg}")
                raise Exception(f"LLM planning failed: {error_msg}")
            
            # Parse JSON response
            content = response.get("content", "").strip()
            logger.info(f"Planning response content length: {len(content)} characters")
            
            # Handle potential markdown code blocks
            if content.startswith("```json"):
                content = content.strip("```json").strip("```").strip()
            elif content.startswith("```"):
                content = content.strip("```").strip()
            
            plan = json.loads(content)
            
            # Validate plan structure
            required_fields = ["action", "reasoning"]
            for field in required_fields:
                if field not in plan:
                    raise Exception(f"Missing required field in plan: {field}")
            
            # Log completion with timing
            duration_ms = (time.time() - start_time) * 1000
            trace_logger.log_agent_step("planning", f"Agent plan created: {plan['action']}", duration_ms=duration_ms)
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM plan response: {e}")
            logger.error(f"Raw response: {response.get('content', 'No content')}")
            
            # Fallback to out_of_scope for parsing errors
            return {
                "action": "out_of_scope",
                "reasoning": "Failed to parse structured response, treating as out of scope",
                "fallback": True
            }
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            raise
    
    def execute(self, plan: Dict[str, Any], question: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Step 2: Execute the planned actions
        
        Args:
            plan: Execution plan from planning step
            question: Original user question
            trace_id: Optional trace ID for observability
            
        Returns:
            Dict containing execution results
        """
        start_time = time.time()
        
        # Get trace logger if trace_id is provided
        trace_logger = get_trace_logger(trace_id or "test-trace")
        trace_logger.log_agent_step("execution", f"Starting execution for action: {plan['action']}")
        action = plan["action"]
        results = {
            "action_taken": action,
            "retrieved_info": None,
            "calculation_results": None,
            "citations": []
        }
        
        try:
            if action == "retrieve":
                results.update(self._execute_retrieval(plan, question))
                
            elif action == "calculate_settlement":
                results.update(self._execute_settlement_calculation(plan))
                
            elif action == "calculate_bearing_capacity":
                results.update(self._execute_bearing_capacity_calculation(plan))
                
            elif action == "both":
                # Execute both retrieval and calculation
                retrieval_results = self._execute_retrieval(plan, question)
                calc_results = self._execute_calculation(plan)
                
                results.update(retrieval_results)
                results.update(calc_results)
                
            elif action == "out_of_scope":
                # Question is outside knowledge base scope
                results["out_of_scope"] = True
                results["scope_message"] = "This question is outside our knowledge base scope which covers only Settle3, CPT analysis, liquefaction analysis, and basic geotechnical calculations."
                
            else:
                raise Exception(f"Unknown action: {action}")
            
            # Log completion with timing
            duration_ms = (time.time() - start_time) * 1000
            trace_logger.log_agent_step("execution", f"Execution completed for action: {action}", duration_ms=duration_ms)
            
            return results
            
        except Exception as e:
            logger.error(f"Execution failed for action {action}: {e}")
            results["execution_error"] = str(e)
            return results
    
    def _execute_retrieval(self, plan: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Execute retrieval action"""
        self.retrieval_calls += 1
        get_metrics_collector().increment_retrieval_calls()
        
        # Use search_query from plan or fallback to original question
        search_query = plan.get("search_query", question)
        
        citations = self.rag_service.search(
            query=search_query,
            k=self.settings.TOP_K_RETRIEVAL,
            score_threshold=self.settings.SIMILARITY_THRESHOLD
        )
        
        # Combine retrieved text
        retrieved_texts = []
        for citation in citations:
            retrieved_texts.append(f"Source: {citation.source_name}\n{citation.content}")
        
        retrieved_info = "\n\n---\n\n".join(retrieved_texts) if retrieved_texts else "No relevant information found."
        
        return {
            "retrieved_info": retrieved_info,
            "citations": citations
        }
    
    def _execute_settlement_calculation(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute settlement calculation"""
        self.tool_calls += 1
        get_metrics_collector().increment_tool_calls()
        
        tool_params = plan.get("tool_parameters", {})
        if not tool_params:
            raise Exception("Settlement calculation requires tool_parameters with 'load' and 'young_modulus'")
        
        result = call_tool("settlement_calculator", **tool_params)
        
        return {"calculation_results": result}
    
    def _execute_bearing_capacity_calculation(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bearing capacity calculation"""
        self.tool_calls += 1
        get_metrics_collector().increment_tool_calls()
        
        tool_params = plan.get("tool_parameters", {})
        if not tool_params:
            raise Exception("Bearing capacity calculation requires tool_parameters with 'B', 'gamma', 'Df', 'phi'")
        
        result = call_tool("bearing_capacity_calculator", **tool_params)
        
        return {"calculation_results": result}
    
    def _execute_calculation(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calculation based on tool parameters"""
        tool_params = plan.get("tool_parameters", {})
        
        # Determine calculation type from parameters
        if "load" in tool_params and "young_modulus" in tool_params:
            return self._execute_settlement_calculation(plan)
        elif "B" in tool_params and "gamma" in tool_params:
            return self._execute_bearing_capacity_calculation(plan)
        else:
            raise Exception("Cannot determine calculation type from tool_parameters")
    
    def synthesize(self, question: str, execution_results: Dict[str, Any], trace_id: Optional[str] = None) -> str:
        """
        Step 3: Synthesize final answer from execution results
        
        Args:
            question: Original user question
            execution_results: Results from execution step
            trace_id: Optional trace ID for observability
            
        Returns:
            Final synthesized answer
        """
        start_time = time.time()
        
        # Get trace logger if trace_id is provided
        trace_logger = get_trace_logger(trace_id or "test-trace")
        trace_logger.log_agent_step("synthesis", "Starting answer synthesis")
        
        try:
            # Check if question is out of scope
            if execution_results.get("out_of_scope"):
                scope_message = execution_results.get("scope_message", "This question is outside our knowledge base scope.")
                trace_logger.log_agent_step("synthesis", "Question out of scope - returning standard message")
                return f"I apologize, but this question is outside my knowledge base scope. I can only assist with the following geotechnical engineering topics:\n\n- **Settle3 software**: Theory manuals, modeling guides, FAQs, and troubleshooting\n- **CPT analysis**: Cone Penetration Test data interpretation and correlations\n- **Liquefaction analysis**: Assessment methods, safety factors, and correlations\n- **Consolidation theory**: Primary and secondary consolidation concepts\n- **Settlement calculations**: Basic elastic settlement formulas\n- **Bearing capacity**: Terzaghi bearing capacity analysis for cohesionless soils\n\nPlease ask questions related to these specific geotechnical topics."
            
            # Extract results
            retrieved_info = execution_results.get("retrieved_info") or "No information retrieved."
            calculation_results = execution_results.get("calculation_results", "No calculations performed.")
            execution_error = execution_results.get("execution_error")
            
            # Handle execution errors
            if execution_error:
                retrieved_info += f"\n\nExecution Error: {execution_error}"
            
            # Format synthesis prompt
            formatted_prompt = self.synthesis_prompt.format(
                question=question,
                retrieved_info=retrieved_info,
                calculation_results=str(calculation_results)
            )
            
            logger.debug(f"--- SYNTHESIS PROMPT ---\nSystem: {self.system_prompt}\nUser: {formatted_prompt}\n--------------------")

            # Create conversation
            messages = self.llm_service.create_conversation(
                system_prompt=self.system_prompt,
                user_message=formatted_prompt
            )
            
            # Generate final answer
            response = self.llm_service.call_llm(messages)
            
            logger.info(f"LLM synthesis response status: {response.get('status')}")
            
            if response["status"] != "success":
                error_msg = response.get('error', 'Unknown error')
                logger.error(f"LLM synthesis failed: {error_msg}")
                raise Exception(f"LLM synthesis failed: {error_msg}")
            
            final_content = response.get("content", "")
            
            # Log completion with timing
            duration_ms = (time.time() - start_time) * 1000
            trace_logger.log_agent_step("synthesis", f"Answer synthesis completed ({len(final_content)} chars)", duration_ms=duration_ms)
            
            return final_content
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            # Fallback response
            return f"I apologize, but I encountered an error while processing your question about geotechnical engineering. Error: {str(e)}"
    
    def run(self, question: str, trace_id: Optional[str] = None) -> AskResponse:
        """
        Main entry point: Execute full Plan → Execute → Synthesize workflow
        
        Args:
            question: User's question
            trace_id: Optional trace ID for observability
            
        Returns:
            AskResponse with answer and citations
        """
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        self.total_requests += 1
        
        # Initialize observability
        langfuse_client = get_langfuse_client()
        langfuse_trace_id = langfuse_client.start_trace("agent_workflow")
        
        # Use request timer for metrics
        with time_request():
            try:
                # Create LangFuse span for overall workflow
                workflow_span_id = langfuse_client.create_span(
                    trace_id=langfuse_trace_id,
                    span_name="agent_workflow", 
                    span_type="WORKFLOW",
                    input_data={"question": question, "trace_id": trace_id}
                )
                
                trace_logger = get_trace_logger(trace_id)
                trace_logger.info(f"Starting agent workflow for question: {question}")
                
                # Step 1: Plan
                planning_span_id = langfuse_client.create_span(
                    trace_id=langfuse_trace_id,
                    span_name="planning",
                    span_type="AGENT_STEP"
                )
                plan = self.plan(question, trace_id)
                langfuse_client.update_span(planning_span_id, {"plan": plan})
                
                # Step 2: Execute
                execution_span_id = langfuse_client.create_span(
                    trace_id=langfuse_trace_id,
                    span_name="execution",
                    span_type="AGENT_STEP"
                )
                execution_results = self.execute(plan, question, trace_id)
                langfuse_client.update_span(execution_span_id, {"results": execution_results})
                
                # Step 3: Synthesize
                synthesis_span_id = langfuse_client.create_span(
                    trace_id=langfuse_trace_id,
                    span_name="synthesis",
                    span_type="AGENT_STEP"
                )
                final_answer = self.synthesize(question, execution_results, trace_id)
                langfuse_client.update_span(synthesis_span_id, {"answer_length": len(final_answer)})
                
                # Create response
                response = AskResponse(
                    answer=final_answer,
                    citations=execution_results.get("citations", []),
                    trace_id=trace_id
                )
                
                # Update workflow span with final results
                langfuse_client.update_span(
                    workflow_span_id, 
                    {"response": {"answer_length": len(final_answer), "citations_count": len(response.citations)}},
                    "SUCCESS"
                )
                langfuse_client.end_trace(langfuse_trace_id, "SUCCESS")
                
                trace_logger.info("Agent workflow completed successfully")
                return response
                
            except Exception as e:
                trace_logger.error(f"Agent workflow failed: {e}")
                
                # Update spans with error
                langfuse_client.update_span(workflow_span_id, {"error": str(e)}, "ERROR")
                langfuse_client.end_trace(langfuse_trace_id, "ERROR")
                
                # Return error response  
                return AskResponse(
                    answer=f"I apologize, but I encountered an error while processing your question. Please try rephrasing your question or contact support. Error: {str(e)}",
                    citations=[],
                    trace_id=trace_id
                )
    
    def get_statistics(self) -> Dict[str, int]:
        """Get agent usage statistics"""
        return {
            "total_requests": self.total_requests,
            "tool_calls": self.tool_calls,
            "retrieval_calls": self.retrieval_calls,
            "llm_requests": self.llm_service.request_count,
            "llm_errors": self.llm_service.error_count
        }
    
    def reset_statistics(self):
        """Reset all usage statistics"""
        self.total_requests = 0
        self.tool_calls = 0
        self.retrieval_calls = 0
        self.llm_service.reset_statistics()