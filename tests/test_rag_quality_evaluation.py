import json
import csv
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.agent import GeotechAgent
from app.core.llms.gemini import GeminiService
from app.core.config.settings import GeotechSettings
from app.core.config.constants import RAGConstants


# Constants
DATASET_PATH = Path("evaluation/dataset.json")
RESULTS_PATH = Path("evaluation/rag_evaluation_results.csv")
MAX_CONCURRENT_EVALUATIONS = 3
VERBOSE_DEBUG = False  # Set to True for detailed debug output

def debug_print(*args, **kwargs):
    """Print only if verbose debug is enabled"""
    if VERBOSE_DEBUG:
        print(*args, **kwargs)

class RAGQualityEvaluator:
    
    def __init__(self):
        self.settings = GeotechSettings()
        debug_print(f"DEBUG: Evaluator settings SIMILARITY_THRESHOLD = {self.settings.SIMILARITY_THRESHOLD}")
        self.agent = GeotechAgent()
        debug_print(f"DEBUG: Agent settings SIMILARITY_THRESHOLD = {self.agent.settings.SIMILARITY_THRESHOLD}")
        self.gemini_service = GeminiService(api_key=self.settings.GOOGLE_GENAI_API_KEY)
        self.results = []
    
    def load_dataset(self) -> List[Dict[str, Any]]:
        """Load Q&A pairs from dataset.json"""
        try:
            with open(DATASET_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('qa_pairs', [])
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset file not found: {DATASET_PATH}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in dataset file: {e}")
    
    async def generate_answer(self, question: str) -> Dict[str, Any]:
        """Generate answer using GeotechAgent"""
        print(f"\nGenerating answer for: {question[:60]}...")
        start_time = time.time()
        try:
            # Run in thread pool to avoid event loop conflict
            loop = asyncio.get_event_loop()
            
            # Log agent workflow steps by temporarily patching agent methods
            original_plan = self.agent.plan
            original_execute = self.agent.execute
            original_synthesize = self.agent.synthesize
            
            def debug_plan(q):
                debug_print(f"🧠 PLANNING STEP:")
                debug_print(f"  → Question: {q}")
                plan_result = original_plan(q)
                debug_print(f"  → Plan result: {plan_result}")
                return plan_result
            
            def debug_execute(plan, q):
                debug_print(f"⚡ EXECUTION STEP:")
                debug_print(f"  → Plan action: {plan.get('action', 'unknown')}")
                
                # Patch RAG service to add detailed logging
                if hasattr(self.agent, 'rag_service'):
                    original_search = self.agent.rag_service.hybrid_search
                    
                    async def debug_hybrid_search(query, score_threshold=None):
                        # Use default threshold from settings if not provided
                        if score_threshold is None:
                            from app.core.config.settings import get_settings
                            settings = get_settings()
                            score_threshold = settings.SIMILARITY_THRESHOLD
                            
                        debug_print(f"    🔍 HYBRID SEARCH DETAILS:")
                        debug_print(f"      → Query: {query}")
                        debug_print(f"      → Score threshold: {score_threshold}")
                        
                        # Get keywords first
                        try:
                            keywords = await self.agent.rag_service.gemini_service.extract_keywords(query)
                            debug_print(f"      → Extracted keywords: {keywords}")
                            debug_print(f"      → Keyword count: {len(keywords)}")
                            
                            if len(keywords) < RAGConstants.MIN_KEYWORDS_THRESHOLD:
                                debug_print(f"      → Using VECTOR-ONLY search (< {RAGConstants.MIN_KEYWORDS_THRESHOLD} keywords)")
                                results = await self.agent.rag_service._vector_search_async(query, RAGConstants.VECTOR_MAX_CHUNKS, score_threshold)
                                debug_print(f"      → Vector search returned {len(results)} chunks")
                            else:
                                debug_print(f"      → Using HYBRID search (≥ {RAGConstants.MIN_KEYWORDS_THRESHOLD} keywords)")
                                vector_results = await self.agent.rag_service._vector_search_async(query, RAGConstants.HYBRID_VECTOR_CHUNKS, score_threshold)
                                keyword_results = await self.agent.rag_service._keyword_search_with_list(keywords, RAGConstants.KEYWORD_CHUNKS)
                                debug_print(f"      → Vector search: {len(vector_results)} chunks")
                                debug_print(f"      → Keyword search: {len(keyword_results)} chunks")
                                
                                # Show search results details
                                debug_print(f"      → VECTOR RESULTS:")
                                for i, result in enumerate(vector_results[:2], 1):
                                    # Handle dict format from RAGService
                                    score = result.get('score', result.get('confidence_score', 0))
                                    source = result.get('metadata', {}).get('source', result.get('source_name', 'unknown'))
                                    content = result.get('content', result.get('text', ''))[:80]
                                    debug_print(f"        {i}. Score: {score:.3f}, Source: {source}")
                                    debug_print(f"           Content: {content}...")
                                
                                debug_print(f"      → KEYWORD RESULTS:")
                                for i, result in enumerate(keyword_results[:2], 1):
                                    source = result.get('metadata', {}).get('source', result.get('source_name', 'unknown'))
                                    content = result.get('content', result.get('text', ''))[:80]
                                    debug_print(f"        {i}. Source: {source}")
                                    debug_print(f"           Content: {content}...")
                                
                                results = self.agent.rag_service._combine_and_deduplicate(vector_results, keyword_results)
                            
                            debug_print(f"      → FINAL COMBINED: {len(results)} unique chunks")
                            return results
                        except Exception as e:
                            debug_print(f"      → Search error: {e}")
                            return []
                    
                    # Temporarily patch hybrid_search
                    self.agent.rag_service.hybrid_search = debug_hybrid_search
                
                execution_result = original_execute(plan, q)
                
                # Restore original search method
                if hasattr(self.agent, 'rag_service') and 'original_search' in locals():
                    self.agent.rag_service.hybrid_search = original_search
                
                # Log retrieval results if available
                if 'citations' in execution_result:
                    debug_print(f"  → Retrieved {len(execution_result['citations'])} chunks:")
                    for i, citation in enumerate(execution_result['citations'][:3], 1):
                        # Handle both Citation objects and dict format
                        if hasattr(citation, 'source_name'):
                            source = citation.source_name
                            score = getattr(citation, 'confidence_score', 0)
                            content = citation.content
                        else:
                            source = citation.get('metadata', {}).get('source', citation.get('source_name', 'unknown'))
                            score = citation.get('score', citation.get('confidence_score', 0))
                            content = citation.get('content', citation.get('text', ''))
                        debug_print(f"    {i}. {source} (score: {score:.3f})")
                        debug_print(f"       Content: {content}...")
                
                # Log tool results if available  
                if 'tool_results' in execution_result:
                    debug_print(f"  → Tool results: {execution_result['tool_results']}")
                    
                return execution_result
                
            def debug_synthesize(q, exec_results):
                debug_print(f"🔬 SYNTHESIS STEP:")
                debug_print(f"  → Input question: {q}")
                if 'citations' in exec_results:
                    debug_print(f"  → Using {len(exec_results['citations'])} context chunks")
                    debug_print(f"  → Context chunks details:")
                    for i, citation in enumerate(exec_results['citations'][:2], 1):
                        # Handle both Citation objects and dict format
                        if hasattr(citation, 'source_name'):
                            source = citation.source_name
                            content = citation.content[:120]
                        else:
                            source = citation.get('metadata', {}).get('source', citation.get('source_name', 'unknown'))
                            content = citation.get('content', citation.get('text', ''))[:120]
                        debug_print(f"    {i}. {source}: {content}...")
                        
                if 'tool_results' in exec_results:
                    debug_print(f"  → Using tool results: {exec_results['tool_results']}")
                
                # Patch LLM service to log synthesis prompt
                original_call_llm = self.agent.llm_service.call_llm
                
                def debug_call_llm(messages, **kwargs):
                    debug_print(f"    📝 SYNTHESIS PROMPT FORMATION:")
                    if isinstance(messages, list) and len(messages) > 0:
                        last_message = messages[-1]
                        if isinstance(last_message, dict) and 'content' in last_message:
                            prompt_content = last_message['content']
                            debug_print(f"      → Prompt length: {len(prompt_content)} chars")
                            debug_print(f"      → Prompt preview: {prompt_content[:200]}...")
                            
                            # Show context injection
                            if 'PROVIDED CONTEXT:' in prompt_content:
                                context_start = prompt_content.find('PROVIDED CONTEXT:')
                                context_section = prompt_content[context_start:context_start+300]
                                debug_print(f"      → Context injection: {context_section}...")
                    
                    response = original_call_llm(messages, **kwargs)
                    
                    debug_print(f"    💬 LLM SYNTHESIS RESPONSE:")
                    debug_print(f"      → Response length: {len(str(response))} chars")
                    debug_print(f"      → Response preview: {str(response)}...")
                    
                    return response
                
                # Temporarily patch call_llm
                self.agent.llm_service.call_llm = debug_call_llm
                    
                synthesis_result = original_synthesize(q, exec_results)
                
                # Restore original call_llm
                self.agent.llm_service.call_llm = original_call_llm
                
                debug_print(f"  → Final synthesized answer: {str(synthesis_result)}...")
                return synthesis_result
            
            # Temporarily patch methods
            self.agent.plan = debug_plan
            self.agent.execute = debug_execute  
            self.agent.synthesize = debug_synthesize
            
            response = await loop.run_in_executor(None, self.agent.run, question)
            
            # Restore original methods
            self.agent.plan = original_plan
            self.agent.execute = original_execute
            self.agent.synthesize = original_synthesize
            
            processing_time = time.time() - start_time
            
            print(f"  → Answer generated ({len(response.answer)} chars, {len(response.citations)} citations, {processing_time:.2f}s)")
            debug_print(f"  → Answer preview: {str(response.answer)[:100]}...")
            
            return {
                "answer": response.answer,
                "citations": [c.source_name for c in response.citations],
                "processing_time": round(processing_time, 2),
                "success": True,
                "error": None
            }
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ GENERATION FAILED: {str(e)}")
            return {
                "answer": "",
                "citations": [],
                "processing_time": round(processing_time, 2),
                "success": False,
                "error": str(e)
            }
    
    async def evaluate_with_gemini(self, question: str, generated_answer: str, expected_answer: str) -> Dict[str, Any]:
        """Evaluate answer quality using Gemini 2.5 Pro"""
        
        evaluation_prompt = f"""Evaluate geotechnical Q&A (1-10 scale):

QUESTION: {question}

GENERATED: {generated_answer}

EXPECTED: {expected_answer}

Rate (integers only):
- ACCURACY: Factual correctness
- COMPLETENESS: Covers all key points from expected answer
- RELEVANCE: Directly addresses the question asked
- CLARITY: Clear and well-structured response
- CITATIONS: Proper use of source references

JSON format:
{{
    "accuracy": <score>,
    "completeness": <score>,
    "relevance": <score>,
    "clarity": <score>,
    "citations": <score>,
    "overall": <average_of_all_scores>,
    "comments": "<brief_note>"
}}"""

        try:
            debug_print(f"  → Evaluation prompt length: {len(evaluation_prompt)} chars")
            # Use Gemini for evaluation by creating a custom method
            response = await asyncio.to_thread(
                self.gemini_service.client.models.generate_content,
                model="models/gemini-2.5-flash",
                contents=evaluation_prompt
            )
            evaluation_result = [response.text.strip()]
            debug_print(f"  → Gemini response: {evaluation_result}")
            
            # Try to parse JSON response
            if evaluation_result and isinstance(evaluation_result, list) and len(evaluation_result) > 0:
                eval_text = str(evaluation_result[0])
                debug_print(f"  → Eval text to parse: {eval_text[:200]}...")
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', eval_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    debug_print(f"  → Extracted JSON: {json_str}")
                    eval_data = json.loads(json_str)
                    debug_print(f"  → Parsed eval_data: {eval_data}")
                    return eval_data
            
            # Fallback if parsing fails
            debug_print("  → Fallback: Evaluation parsing failed")
            return {
                "accuracy": 5,
                "completeness": 5,
                "relevance": 5,
                "clarity": 5,
                "citations": 5,
                "overall": 5,
                "comments": "Evaluation parsing failed"
            }
            
        except Exception as e:
            debug_print(f"  → Exception in evaluation: {str(e)}")
            return {
                "accuracy": 0,
                "completeness": 0,
                "relevance": 0,
                "clarity": 0,
                "citations": 0,
                "overall": 0,
                "comments": f"Evaluation error: {str(e)}"
            }
    
    async def evaluate_single_qa(self, qa_pair: Dict[str, Any], question_id: int) -> Dict[str, Any]:
        """Evaluate a single Q&A pair"""
        question = qa_pair["question"]
        expected_answer = qa_pair["answer"]
        expected_citation = qa_pair.get("citation", "")
        
        print(f"Evaluating Q{question_id}: {question[:60]}...")
        
        # Generate answer using RAG
        generation_result = await self.generate_answer(question)
        if generation_result['success']:
            print(f"  → Success ({len(generation_result['answer'])} chars)")
            debug_print(f"  → Generated answer preview: {generation_result['answer'][:100]}...")
        else:
            print(f"  → Generation failed: {generation_result['error']}")
        
        if not generation_result["success"]:
            return {
                "question_id": question_id,
                "question": question,
                "generated_answer": "",
                "expected_answer": expected_answer,
                "expected_citation": expected_citation,
                "citations_found": [],
                "accuracy": 0,
                "completeness": 0,
                "relevance": 0,
                "clarity": 0,
                "citations": 0,                
                "overall": 0,
                "comments": f"Generation failed: {generation_result['error']}",
                "processing_time": generation_result["processing_time"],
                "evaluation_success": False
            }
        
        # Evaluate with Gemini
        evaluation = await self.evaluate_with_gemini(
            question, 
            generation_result["answer"], 
            expected_answer
        )
        print(f"  → Evaluation: accuracy={evaluation['accuracy']}, overall={evaluation['overall']}")
        
        return {
            "question_id": question_id,
            "question": question,
            "generated_answer": generation_result["answer"],
            "expected_answer": expected_answer,
            "citations_found": generation_result["citations"],
            "accuracy": evaluation["accuracy"],
            "completeness": evaluation["completeness"],
            "relevance": evaluation["relevance"],
            "clarity": evaluation["clarity"],
            "citations": evaluation["citations"],           
            "overall": evaluation["overall"],
            "comments": evaluation["comments"],
            "processing_time": generation_result["processing_time"],
            "evaluation_success": True
        }
    
    async def run_evaluation(self) -> List[Dict[str, Any]]:
        """Run evaluation on all Q&A pairs with concurrency control"""
        qa_pairs = self.load_dataset()
        print(f"Loaded {len(qa_pairs)} Q&A pairs for evaluation")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_EVALUATIONS)
        
        async def evaluate_with_semaphore(qa_pair, question_id):
            async with semaphore:
                return await self.evaluate_single_qa(qa_pair, question_id)
        
        # Run evaluations concurrently
        tasks = [
            evaluate_with_semaphore(qa_pair, i+1) 
            for i, qa_pair in enumerate(qa_pairs)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Evaluation {i+1} failed: {result}")
                valid_results.append({
                    "question_id": i+1,
                    "question": qa_pairs[i]["question"] if i < len(qa_pairs) else "",
                    "generated_answer": "",
                    "expected_answer": "",
                    "expected_citation": "",
                    "citations_found": [],
                    "accuracy": 0,
                    "completeness": 0,
                    "relevance": 0,
                    "citation": 0,
                    "overall": 0,
                    "evaluation_success": False
                })
            else:
                valid_results.append(result)
        
        self.results = valid_results
        return valid_results
    
    def save_results_to_csv(self):
        """Save evaluation results to CSV file"""
        if not self.results:
            print("No results to save")
            return
        
        # Ensure evaluation directory exists
        RESULTS_PATH.parent.mkdir(exist_ok=True)
        
        # Calculate summary statistics
        successful_evals = [r for r in self.results if r["evaluation_success"]]
        
        # Debug: Show first few results
        debug_print(f"\nDebug: First few results:")
        for i, r in enumerate(self.results[:3]):
            debug_print(f"  Result {i+1}: accuracy={r['accuracy']}, overall={r['overall']}, success={r['evaluation_success']}")
        
        if successful_evals:
            avg_accuracy = sum(r["accuracy"] for r in successful_evals) / len(successful_evals)
            avg_completeness = sum(r["completeness"] for r in successful_evals) / len(successful_evals)
            avg_relevance = sum(r["relevance"] for r in successful_evals) / len(successful_evals)
            avg_clarity = sum(r["clarity"] for r in successful_evals) / len(successful_evals)
            avg_citations = sum(r["citations"] for r in successful_evals) / len(successful_evals)
            avg_overall = sum(r["overall"] for r in successful_evals) / len(successful_evals)
            avg_processing_time = sum(r["processing_time"] for r in successful_evals) / len(successful_evals)
            debug_print(f"Debug: Successful evals={len(successful_evals)}, avg_accuracy={avg_accuracy}, avg_overall={avg_overall}")
        else:
            avg_accuracy = avg_completeness = avg_relevance = avg_clarity = avg_citations = avg_overall = avg_processing_time = 0
            debug_print("Debug: No successful evaluations found")
        
        # Write CSV
        with open(RESULTS_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'question_id', 'question', 'generated_answer', 'expected_answer', 
                'citations_found', 'accuracy', 'completeness', 'relevance', 'clarity', 
                'citations', 'overall', 'comments', 'processing_time', 'evaluation_success'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                # Convert list to string for CSV
                result['citations_found'] = '; '.join(result['citations_found'])
                writer.writerow(result)
            
            # Add summary row
            writer.writerow({})
            writer.writerow({
                'question_id': 'SUMMARY',
                'question': f'Total Questions: {len(self.results)}',
                'generated_answer': f'Successful Evaluations: {len(successful_evals)}',
                'expected_answer': f'Success Rate: {len(successful_evals)/len(self.results):.1%}',
                'accuracy': round(avg_accuracy, 1),
                'completeness': round(avg_completeness, 1),
                'relevance': round(avg_relevance, 1),
                'clarity': round(avg_clarity, 1),
                'citations': round(avg_citations, 1),
                'overall': round(avg_overall, 1),
                'processing_time': round(avg_processing_time, 1),
                'evaluation_success': f'{len(successful_evals)}/{len(self.results)}'
            })
        
        print(f"Results saved to: {RESULTS_PATH}")
        print(f"Summary: {len(successful_evals)}/{len(self.results)} successful evaluations")
        print(f"Average Overall Score: {avg_overall:.1f}/10")


async def test_rag_quality_evaluation():
    """Main test function for RAG quality evaluation"""
    evaluator = RAGQualityEvaluator()
    
    print("Starting RAG Quality Evaluation...")
    start_time = time.time()
    
    # Run evaluation
    results = await evaluator.run_evaluation()
    
    # Save results
    evaluator.save_results_to_csv()
    
    total_time = time.time() - start_time
    print(f"Evaluation completed in {total_time:.2f} seconds")
    
    # Assert basic success criteria
    assert len(results) > 0, "No evaluation results generated"
    successful_evaluations = [r for r in results if r["evaluation_success"]]
    success_rate = len(successful_evaluations) / len(results)
    
    print(f"Final Results:")
    print(f"- Questions Evaluated: {len(results)}")
    print(f"- Successful Evaluations: {len(successful_evaluations)}")
    print(f"- Success Rate: {success_rate:.1%}")
    
    if successful_evaluations:
        avg_overall = sum(r["overall"] for r in successful_evaluations) / len(successful_evaluations)
        print(f"- Average Overall Score: {avg_overall:.1f}/10")
        
        # Success criteria
        assert success_rate >= 0.5, f"Success rate too low: {success_rate:.1%}"
        assert avg_overall >= 3.0, f"Average score too low: {avg_overall:.1f}/10"


if __name__ == "__main__":
    asyncio.run(test_rag_quality_evaluation())