# --- FULL MODIFIED FILE: app/core/agent.py ---

"""
Main Agent Orchestrator
Plan → Execute → Synthesize workflow for geotechnical AI assistant
"""

import asyncio
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
        
        self.system_prompt = get_system_prompt()
        self.planning_prompt = get_planning_prompt()
        self.synthesis_prompt = get_synthesis_prompt()
        
        self.total_requests = 0
        self.tool_calls = 0
        self.retrieval_calls = 0
    
    async def plan(self, question: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
        """Step 1: Analyze question and create execution plan (ASYNC)"""
        logger.info(f"[{trace_id}] ENTERING agent.plan")
        start_time = time.time()
        trace_logger = get_trace_logger(trace_id or "test-trace")
        trace_logger.log_agent_step("planning", "Starting agent planning phase")
        
        try:
            formatted_prompt = self.planning_prompt.format(question=question)
            messages = self.llm_service.create_conversation(system_prompt=self.system_prompt, user_message=formatted_prompt)
            
            logger.info(f"[{trace_id}] AWAITING LLM call in plan...")
            response = await self.llm_service.call_llm(messages)
            logger.info(f"[{trace_id}] LLM call in plan COMPLETED.")
            
            if response["status"] != "success":
                raise Exception(f"LLM planning failed: {response.get('error', 'Unknown error')}")
            
            content = response.get("content", "").strip()
            if content.startswith("```json"):
                content = content.strip("```json").strip("```").strip()
            
            plan = json.loads(content)
            
            duration_ms = (time.time() - start_time) * 1000
            trace_logger.log_agent_step("planning", f"Agent plan created: {plan['action']}", duration_ms=duration_ms)
            logger.info(f"[{trace_id}] EXITING agent.plan")
            return plan
            
        except Exception as e:
            logger.error(f"[{trace_id}] Planning failed: {e}", exc_info=True)
            raise

    # FIXED: Refactored execute to be fully non-blocking
    async def execute(self, plan: Dict[str, Any], question: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
        """Step 2: Execute the planned actions (FULLY ASYNC)"""
        logger.info(f"[{trace_id}] ENTERING agent.execute for action: {plan['action']}")
        start_time = time.time()
        trace_logger = get_trace_logger(trace_id or "test-trace")
        trace_logger.log_agent_step("execution", f"Starting execution for action: {plan['action']}")
        
        action = plan["action"]
        results = {"action_taken": action, "citations": []}

        try:
            if action == "retrieve":
                results.update(await self._execute_retrieval(plan, question, trace_id))
            
            elif action in ["calculate_settlement", "calculate_bearing_capacity"]:
                # Run synchronous tool calls in a separate thread
                calc_results = await asyncio.to_thread(self._execute_calculation, plan)
                results.update(calc_results)

            elif action == "both":
                # Run retrieval and calculation concurrently
                retrieval_task = self._execute_retrieval(plan, question, trace_id)
                calc_task = asyncio.to_thread(self._execute_calculation, plan)
                
                retrieval_results, calc_results = await asyncio.gather(retrieval_task, calc_task)
                
                results.update(retrieval_results)
                results.update(calc_results)

            elif action == "out_of_scope":
                results["out_of_scope"] = True
                results["scope_message"] = "This question is outside our knowledge base scope."

            else:
                raise Exception(f"Unknown action: {action}")

            duration_ms = (time.time() - start_time) * 1000
            trace_logger.log_agent_step("execution", f"Execution completed for action: {action}", duration_ms=duration_ms)
            logger.info(f"[{trace_id}] EXITING agent.execute")
            return results

        except Exception as e:
            logger.error(f"[{trace_id}] Execution failed for action {action}: {e}", exc_info=True)
            results["execution_error"] = str(e)
            return results

    async def _execute_retrieval(self, plan: Dict[str, Any], question: str, trace_id: str) -> Dict[str, Any]:
        """Execute retrieval action"""
        logger.info(f"[{trace_id}] ENTERING _execute_retrieval")
        self.retrieval_calls += 1
        search_query = plan.get("search_query", question)
        
        try:
            logger.info(f"[{trace_id}] AWAITING RAG service search...")
            citations = await self.rag_service.search(
                query=search_query,
                k=self.settings.TOP_K_RETRIEVAL,
                score_threshold=self.settings.SIMILARITY_THRESHOLD
            )
            logger.info(f"[{trace_id}] RAG service search COMPLETED. Found {len(citations)} citations.")
            
            retrieved_texts = [f"Source: {c.source_name}\n{c.content}" for c in citations]
            retrieved_info = "\n\n---\n\n".join(retrieved_texts) if retrieved_texts else "No information retrieved."
            
            logger.info(f"[{trace_id}] EXITING _execute_retrieval")
            return {"retrieved_info": retrieved_info, "citations": citations}
            
        except Exception as e:
            logger.error(f"[{trace_id}] Retrieval execution failed: {e}", exc_info=True)
            return {"retrieved_info": f"Retrieval error: {str(e)}", "citations": []}
    
    def _execute_calculation(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for all calculation tools."""
        tool_params = plan.get("tool_parameters", {})
        action = plan.get("action")

        # Determine which tool to call based on action or parameters
        if action == "calculate_settlement" or ("load" in tool_params and "young_modulus" in tool_params):
            self.tool_calls += 1
            get_metrics_collector().increment_tool_calls()
            required = ["load", "young_modulus"]
            if not all(k in tool_params for k in required):
                raise ValueError("Missing parameters for settlement calculation.")
            params = {k: tool_params[k] for k in required}
            return {"calculation_results": call_tool("settlement_calculator", **params)}

        elif action == "calculate_bearing_capacity" or ("B" in tool_params and "gamma" in tool_params):
            self.tool_calls += 1
            get_metrics_collector().increment_tool_calls()
            required = ["B", "gamma", "Df", "phi"]
            if not all(k in tool_params for k in required):
                raise ValueError("Missing parameters for bearing capacity calculation.")
            params = {k: tool_params[k] for k in required}
            return {"calculation_results": call_tool("bearing_capacity_calculator", **params)}
        
        else:
            logger.warning(f"Could not determine calculation type for plan: {plan}")
            return {"calculation_results": "No specific calculation could be performed."}

    async def synthesize(self, question: str, execution_results: Dict[str, Any], trace_id: Optional[str] = None) -> str:
        """Step 3: Synthesize final answer from execution results (ASYNC)"""
        logger.info(f"[{trace_id}] ENTERING agent.synthesize")
        start_time = time.time()
        trace_logger = get_trace_logger(trace_id or "test-trace")
        trace_logger.log_agent_step("synthesis", "Starting answer synthesis")
        
        try:
            if execution_results.get("out_of_scope"):
                return "I apologize, but this question is outside my knowledge base scope..."
            
            retrieved_info = execution_results.get("retrieved_info", "No information retrieved.")
            calculation_results = execution_results.get("calculation_results", "No calculations performed.")
            
            formatted_prompt = self.synthesis_prompt.format(
                question=question,
                retrieved_info=retrieved_info,
                calculation_results=str(calculation_results)
            )
            
            messages = self.llm_service.create_conversation(system_prompt=self.system_prompt, user_message=formatted_prompt)
            
            logger.info(f"[{trace_id}] AWAITING LLM call in synthesize...")
            response = await self.llm_service.call_llm(messages)
            logger.info(f"[{trace_id}] LLM call in synthesize COMPLETED.")

            if response["status"] != "success":
                raise Exception(f"LLM synthesis failed: {response.get('error', 'Unknown error')}")
            
            final_content = response.get("content", "")
            duration_ms = (time.time() - start_time) * 1000
            trace_logger.log_agent_step("synthesis", f"Answer synthesis completed", duration_ms=duration_ms)
            logger.info(f"[{trace_id}] EXITING agent.synthesize")
            return final_content
            
        except Exception as e:
            logger.error(f"[{trace_id}] Synthesis failed: {e}", exc_info=True)
            raise

    async def run(self, question: str, trace_id: Optional[str] = None) -> AskResponse:
        """Main entry point: Execute full Plan → Execute → Synthesize workflow"""
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        self.total_requests += 1
        langfuse_client = get_langfuse_client()
        langfuse_trace_id = langfuse_client.start_trace("agent_workflow")
        
        with time_request():
            try:
                trace_logger = get_trace_logger(trace_id)
                trace_logger.info(f"Starting agent workflow for question: {question}")
                
                plan = await self.plan(question, trace_id)
                execution_results = await self.execute(plan, question, trace_id)
                final_answer = await self.synthesize(question, execution_results, trace_id)
                
                response = AskResponse(
                    answer=final_answer,
                    citations=execution_results.get("citations", []),
                    trace_id=trace_id
                )
                
                trace_logger.info("Agent workflow completed successfully")
                return response
                
            except Exception as e:
                logger.error(f"[{trace_id}] Agent workflow failed critically: {e}", exc_info=True)
                return AskResponse(
                    answer=f"I apologize, but I encountered a critical error. Error: {str(e)}",
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