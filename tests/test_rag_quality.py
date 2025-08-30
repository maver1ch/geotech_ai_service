import json
import csv
import asyncio
import time
import types
from pathlib import Path
from typing import Dict, List, Any
import sys
import pytest
import pytest_asyncio

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
VERBOSE_DEBUG = False

def debug_print(*args, **kwargs):
    """Print only if verbose debug is enabled with Unicode handling"""
    if VERBOSE_DEBUG:
        try:
            print(*args, **kwargs)
        except UnicodeEncodeError:
            # Fallback for Windows console Unicode issues
            safe_args = []
            for arg in args:
                try:
                    safe_args.append(str(arg).encode('ascii', 'replace').decode('ascii'))
                except:
                    safe_args.append(repr(arg))
            print(*safe_args, **kwargs)

def safe_print(*args, **kwargs):
    """Safe print with Unicode handling for all output"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback for Windows console Unicode issues
        safe_args = []
        for arg in args:
            try:
                safe_args.append(str(arg).encode('ascii', 'replace').decode('ascii'))
            except:
                safe_args.append(repr(arg))
        print(*safe_args, **kwargs)

class RAGQualityEvaluator:
    
    def __init__(self):
        self.settings = GeotechSettings()
        debug_print(f"DEBUG: Evaluator settings SIMILARITY_THRESHOLD = {self.settings.SIMILARITY_THRESHOLD}")
        self.agent = GeotechAgent()
        debug_print(f"DEBUG: Agent settings SIMILARITY_THRESHOLD = {self.agent.settings.SIMILARITY_THRESHOLD}")
        self.gemini_service = GeminiService(api_key=self.settings.GOOGLE_GENAI_API_KEY)
        self.results = []
    
    def calculate_hit_at_k(self, retrieved_citations: List[str], expected_citation: str, k: int = 3) -> Dict[str, Any]:
        """
        Calculate Hit@k metrics using frequency-based ranking with tied ranks
        
        Args:
            retrieved_citations: List of source names from RAG retrieval
            expected_citation: Ground truth source name from dataset
            k: Number of top ranks to consider (max 3: Hit@1, Hit@2, Hit@3)
        
        Returns:
            Dict with hit@k metrics and frequency analysis
        """
        if not retrieved_citations or not expected_citation:
            return {
                "hit_at_1": False,
                "hit_at_2": False,
                "hit_at_3": False,
                "rank": -1,
                "frequency": 0,
                "total_retrieved": len(retrieved_citations) if retrieved_citations else 0,
                "expected_source": expected_citation,
                "analysis": "No citations retrieved or no expected citation"
            }
        
        # Normalize citation names for matching
        def normalize_citation(citation: str) -> str:
            return citation.lower().replace(" ", "").replace("_", "").replace(".md", "")
        
        expected_normalized = normalize_citation(expected_citation)
        
        # Count frequency of each source
        source_frequency = {}
        for cite in retrieved_citations:
            normalized = normalize_citation(cite)
            source_frequency[normalized] = source_frequency.get(normalized, 0) + 1
        
        # Sort by frequency (descending), then maintain original order for ties
        unique_sources = []
        seen = set()
        for cite in retrieved_citations:
            normalized = normalize_citation(cite)
            if normalized not in seen:
                unique_sources.append((normalized, source_frequency[normalized], cite))
                seen.add(normalized)
        
        # Sort by frequency descending, original order for ties
        unique_sources.sort(key=lambda x: (-x[1], retrieved_citations.index(x[2])))
        
        # Assign ranks with ties
        current_rank = 1
        ranked_sources = []
        
        for i, (normalized, freq, original) in enumerate(unique_sources):
            if i > 0 and freq != unique_sources[i-1][1]:
                # Different frequency, update rank to next position
                current_rank = len(ranked_sources) + 1
            
            ranked_sources.append((normalized, freq, original, current_rank))
        
        # Find expected source rank and frequency
        expected_rank = -1
        expected_freq = 0
        
        for normalized, freq, original, rank in ranked_sources:
            if expected_normalized in normalized or normalized in expected_normalized:
                expected_rank = rank
                expected_freq = freq
                break
        
        # Calculate Hit@k for k=1,2,3
        hit_at_1 = expected_rank == 1 if expected_rank > 0 else False
        hit_at_2 = expected_rank <= 2 if expected_rank > 0 else False  
        hit_at_3 = expected_rank <= 3 if expected_rank > 0 else False
        
        # Analysis message
        if expected_rank > 0:
            analysis = f"Expected source ranked #{expected_rank} with {expected_freq} chunks"
            
            # Show frequency distribution for context
            freq_info = []
            for _, freq, orig, rank in ranked_sources[:3]:  # Top 3 sources
                freq_info.append(f"Rank {rank}: {freq} chunks")
            analysis += f" (Top sources: {'; '.join(freq_info)})"
        else:
            analysis = f"Expected source '{expected_citation}' not found in retrieved sources"
        
        return {
            "hit_at_1": hit_at_1,
            "hit_at_2": hit_at_2,
            "hit_at_3": hit_at_3,
            "rank": expected_rank,
            "frequency": expected_freq,
            "total_retrieved": len(retrieved_citations),
            "unique_sources_count": len(unique_sources),
            "expected_source": expected_citation,
            "frequency_ranking": [(orig, freq, rank) for _, freq, orig, rank in ranked_sources[:5]],  # Top 5 for debugging
            "analysis": analysis
        }
    
    def load_dataset(self) -> List[Dict[str, Any]]:
        """Load Q&A pairs from dataset.json"""
        try:
            with open(DATASET_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both formats: direct array or object with qa_pairs key
                if isinstance(data, list):
                    return data
                else:
                    return data.get('qa_pairs', [])
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset file not found: {DATASET_PATH}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in dataset file: {e}")
    
    async def generate_answer(self, question: str) -> Dict[str, Any]:
        """Generate answer using GeotechAgent"""
        safe_print(f"\nGenerating answer for: {question[:60]}...")
        start_time = time.time()
        try:
            # Run in thread pool to avoid event loop conflict
            loop = asyncio.get_event_loop()
            
            # Log agent workflow steps by temporarily patching agent methods
            original_plan = self.agent.plan
            original_execute = self.agent.execute
            original_synthesize = self.agent.synthesize
            
            def debug_plan(q, trace_id=None):
                debug_print(f"🧠 PLANNING STEP:")
                debug_print(f"  → Question: {q}")
                plan_result = original_plan(q, trace_id)
                debug_print(f"  → Plan result: {plan_result}")
                return plan_result
            
            def debug_execute(plan, q, trace_id=None):
                debug_print(f"⚡ EXECUTION STEP:")
                debug_print(f"  → Plan action: {plan.get('action', 'unknown')}")
                
                # Patch RAG service to add detailed logging
                if hasattr(self.agent, 'rag_service'):
                    original_search = self.agent.rag_service.hybrid_search
                    
                    async def debug_hybrid_search(query, vector_k, keyword_k, score_threshold):
                        # Parameters match the actual hybrid_search method signature
                            
                        debug_print(f"    🔍 HYBRID SEARCH DETAILS:")
                        debug_print(f"      → Query: {query}")
                        debug_print(f"      → Vector k: {vector_k}, Keyword k: {keyword_k}")
                        debug_print(f"      → Score threshold: {score_threshold}")
                        
                        # Get keywords first
                        try:
                            keywords = await self.agent.rag_service.gemini_service.extract_keywords(query)
                            debug_print(f"      → Extracted keywords: {keywords}")
                            debug_print(f"      → Keyword count: {len(keywords)}")
                            
                            if len(keywords) < RAGConstants.MIN_KEYWORDS_THRESHOLD:
                                debug_print(f"      → Using VECTOR-ONLY search (< {RAGConstants.MIN_KEYWORDS_THRESHOLD} keywords)")
                                results = await self.agent.rag_service._vector_search_async(query, vector_k, score_threshold)
                                debug_print(f"      → Vector search returned {len(results)} chunks")
                            else:
                                debug_print(f"      → Using HYBRID search (≥ {RAGConstants.MIN_KEYWORDS_THRESHOLD} keywords)")
                                vector_results = await self.agent.rag_service._vector_search_async(query, vector_k, score_threshold)
                                keyword_results = await self.agent.rag_service._keyword_search_with_list(keywords, keyword_k)
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
                                
                                # Trim vector results for hybrid mode (use HYBRID_VECTOR_CHUNKS)
                                vector_results_trimmed = vector_results[:RAGConstants.HYBRID_VECTOR_CHUNKS]
                                results = self.agent.rag_service._combine_and_deduplicate(vector_results_trimmed, keyword_results)
                            
                            debug_print(f"      → FINAL COMBINED: {len(results)} unique chunks")
                            return results
                        except Exception as e:
                            debug_print(f"      → Search error: {e}")
                            return []
                    
                    # Temporarily patch hybrid_search
                    self.agent.rag_service.hybrid_search = debug_hybrid_search
                
                execution_result = original_execute(plan, q, trace_id)
                
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
                
            def debug_synthesize(q, exec_results, trace_id=None):
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
                    
                synthesis_result = original_synthesize(q, exec_results, trace_id)
                
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
            
            safe_print(f"  → Answer generated ({len(response.answer)} chars, {len(response.citations)} citations, {processing_time:.2f}s)")
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
            safe_print(f"❌ GENERATION FAILED: {str(e)}")
            return {
                "answer": "",
                "citations": [],
                "processing_time": round(processing_time, 2),
                "success": False,
                "error": str(e)
            }
    
    async def evaluate_with_gemini(self, question: str, generated_answer: str, expected_answer: str) -> Dict[str, Any]:
        """Evaluate answer quality using Gemini 2.5 Pro"""
        
        evaluation_prompt = f"""Evaluate geotechnical Q&A (1-10 scale where 7-8 is good, 9-10 is excellent):

QUESTION: {question}

GENERATED: {generated_answer}

EXPECTED: {expected_answer}

Rate (integers only) - Be generous with good answers:
- ACCURACY: Factual correctness (8-10 if facts are correct)
- COMPLETENESS: Covers all key points from expected answer (8-10 if all main points covered)  
- RELEVANCE: Directly addresses the question asked (8-10 if on-topic and focused)
- CLARITY: Clear and well-structured response (8-10 if easy to understand)

Guidelines:
- 8-10: Excellent answers that meet/exceed expectations
- 6-7: Good answers with minor issues
- 4-5: Adequate answers with some problems
- 1-3: Poor answers with major issues

JSON format:
{{
    "accuracy": <score>,
    "completeness": <score>,
    "relevance": <score>,
    "clarity": <score>,
    "comments": "<brief_explanation>"
}}"""

        try:
            debug_print(f"  → Evaluation prompt length: {len(evaluation_prompt)} chars")
            
            # Define JSON schema for structured output
            import json
            response_schema = {
                "type": "object",
                "properties": {
                    "accuracy": {"type": "integer", "minimum": 1, "maximum": 10},
                    "completeness": {"type": "integer", "minimum": 1, "maximum": 10},
                    "relevance": {"type": "integer", "minimum": 1, "maximum": 10},
                    "clarity": {"type": "integer", "minimum": 1, "maximum": 10},
                    "comments": {"type": "string", "maxLength": 200}
                },
                "required": ["accuracy", "completeness", "relevance", "clarity", "comments"],
                "additionalProperties": False
            }
            
            # Enhanced prompt with strict JSON requirements
            strict_prompt = f"""{evaluation_prompt}

CRITICAL: You MUST respond with ONLY valid JSON matching this exact schema:
{json.dumps(response_schema, indent=2)}

NO additional text, explanations, or markdown. ONLY the JSON object."""

            # Call Gemini using the same pattern as GeminiService
            response = await asyncio.to_thread(
                self.gemini_service.client.models.generate_content,
                model=self.gemini_service.model_name,
                contents=strict_prompt
            )
            
            response_text = response.text.strip()
            debug_print(f"  → Gemini JSON response: {response_text[:200]}...")
            
            # Clean and parse JSON response (handle markdown wrapping)
            clean_text = response_text
            if clean_text.startswith('```json'):
                clean_text = clean_text.replace('```json', '').replace('```', '').strip()
            elif clean_text.startswith('```'):
                clean_text = clean_text.replace('```', '').strip()
            
            eval_data = json.loads(clean_text)
            debug_print(f"  → Parsed eval_data: {eval_data}")
            
            # Validate required fields
            required_fields = ["accuracy", "completeness", "relevance", "clarity", "comments"]
            for field in required_fields:
                if field not in eval_data:
                    raise ValueError(f"Missing required field: {field}")
                    
            # Validate score ranges
            score_fields = ["accuracy", "completeness", "relevance", "clarity"]
            for field in score_fields:
                score = eval_data[field]
                if not isinstance(score, int) or not (1 <= score <= 10):
                    raise ValueError(f"Invalid {field} score: {score} (must be integer 1-10)")
            
            return eval_data
            
        except json.JSONDecodeError as e:
            debug_print(f"  → JSON parsing failed: {str(e)}")
            raise Exception(f"Gemini returned invalid JSON: {str(e)}")
            
        except Exception as e:
            debug_print(f"  → Evaluation failed: {str(e)}")
            raise Exception(f"Evaluation failed: {str(e)}")
    
    async def evaluate_single_qa(self, qa_pair: Dict[str, Any], question_id: int) -> Dict[str, Any]:
        """Evaluate a single Q&A pair"""
        question = qa_pair["question"]
        expected_answer = qa_pair["answer"]
        expected_citation = qa_pair.get("citation", "")
        
        safe_print(f"Evaluating Q{question_id}: {question[:60]}...")
        
        # Generate answer using RAG
        generation_result = await self.generate_answer(question)
        if generation_result['success']:
            safe_print(f"  → Success ({len(generation_result['answer'])} chars)")
            debug_print(f"  → Generated answer preview: {generation_result['answer'][:100]}...")
        else:
            safe_print(f"  → Generation failed: {generation_result['error']}")
        
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
                "comments": f"Generation failed: {generation_result['error']}",
                "processing_time": generation_result["processing_time"],
                "evaluation_success": False
            }
        
        # Calculate Hit@k metrics (frequency-based ranking)
        hit_metrics = self.calculate_hit_at_k(
            retrieved_citations=generation_result["citations"],
            expected_citation=expected_citation,
            k=3  # Only Hit@1, Hit@2, Hit@3
        )
        
        # Evaluate with Gemini
        evaluation = await self.evaluate_with_gemini(
            question, 
            generation_result["answer"], 
            expected_answer
        )
        print(f"  → Evaluation: accuracy={evaluation['accuracy']}, completeness={evaluation['completeness']}, relevance={evaluation['relevance']}, clarity={evaluation['clarity']}")
        print(f"  → Hit@k: Hit@1={hit_metrics['hit_at_1']}, Hit@2={hit_metrics['hit_at_2']}, Hit@3={hit_metrics['hit_at_3']}, Rank={hit_metrics['rank']}, Freq={hit_metrics['frequency']}")
        
        return {
            "question_id": question_id,
            "question": question,
            "generated_answer": generation_result["answer"],
            "expected_answer": expected_answer,
            "citations_found": generation_result["citations"],
            "expected_citation": expected_citation,
            # Hit@k metrics (frequency-based)
            "hit_at_1": hit_metrics["hit_at_1"],
            "hit_at_2": hit_metrics["hit_at_2"],
            "hit_at_3": hit_metrics["hit_at_3"],
            "citation_rank": hit_metrics["rank"],
            "citation_frequency": hit_metrics["frequency"],
            "retrieval_analysis": hit_metrics["analysis"],
            # Gemini evaluation scores
            "accuracy": evaluation["accuracy"],
            "completeness": evaluation["completeness"],
            "relevance": evaluation["relevance"],
            "clarity": evaluation["clarity"],
            "comments": evaluation["comments"],
            "processing_time": generation_result["processing_time"],
            "evaluation_success": True
        }
    
    async def run_evaluation(self) -> List[Dict[str, Any]]:
        """Run evaluation on all Q&A pairs with concurrency control"""
        qa_pairs = self.load_dataset()
        safe_print(f"Loaded {len(qa_pairs)} Q&A pairs for evaluation")
        
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
                    "clarity": 0,
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
            debug_print(f"  Result {i+1}: accuracy={r['accuracy']}, success={r['evaluation_success']}")
        
        if successful_evals:
            # Gemini evaluation averages
            avg_accuracy = sum(r["accuracy"] for r in successful_evals) / len(successful_evals)
            avg_completeness = sum(r["completeness"] for r in successful_evals) / len(successful_evals)
            avg_relevance = sum(r["relevance"] for r in successful_evals) / len(successful_evals)
            avg_clarity = sum(r["clarity"] for r in successful_evals) / len(successful_evals)
            # Calculate average scores (no citations/overall needed)
            avg_score = (avg_accuracy + avg_completeness + avg_relevance + avg_clarity) / 4
            avg_processing_time = sum(r["processing_time"] for r in successful_evals) / len(successful_evals)
            
            # Hit@k averages (frequency-based)
            hit_at_1_rate = sum(1 for r in successful_evals if r.get("hit_at_1", False)) / len(successful_evals)
            hit_at_2_rate = sum(1 for r in successful_evals if r.get("hit_at_2", False)) / len(successful_evals)  
            hit_at_3_rate = sum(1 for r in successful_evals if r.get("hit_at_3", False)) / len(successful_evals)
            avg_citation_rank = sum(r.get("citation_rank", -1) for r in successful_evals if r.get("citation_rank", -1) > 0) / max(1, sum(1 for r in successful_evals if r.get("citation_rank", -1) > 0))
            avg_citation_freq = sum(r.get("citation_frequency", 0) for r in successful_evals) / len(successful_evals)
            
            debug_print(f"Debug: Successful evals={len(successful_evals)}, avg_accuracy={avg_accuracy}")
            debug_print(f"Debug: Hit@1={hit_at_1_rate:.2%}, Hit@2={hit_at_2_rate:.2%}, Hit@3={hit_at_3_rate:.2%}, Avg_Rank={avg_citation_rank:.1f}, Avg_Freq={avg_citation_freq:.1f}")
        else:
            avg_accuracy = avg_completeness = avg_relevance = avg_clarity = avg_processing_time = 0
            hit_at_1_rate = hit_at_2_rate = hit_at_3_rate = avg_citation_rank = avg_citation_freq = 0
            debug_print("Debug: No successful evaluations found")
        
        # Write CSV
        with open(RESULTS_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'question_id', 'question', 'generated_answer', 'expected_answer', 
                'expected_citation', 'citations_found', 
                # Hit@k metrics (frequency-based)
                'hit_at_1', 'hit_at_2', 'hit_at_3', 'citation_rank', 'citation_frequency', 'retrieval_analysis',
                # Gemini evaluation scores  
                'accuracy', 'completeness', 'relevance', 'clarity', 'comments', 
                'processing_time', 'evaluation_success'
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
                'expected_citation': f'Hit@1: {hit_at_1_rate:.1%}',
                'citations_found': f'Hit@2: {hit_at_2_rate:.1%}; Hit@3: {hit_at_3_rate:.1%}', 
                # Hit@k summary (frequency-based)
                'hit_at_1': f'{hit_at_1_rate:.1%}',
                'hit_at_2': f'{hit_at_2_rate:.1%}',
                'hit_at_3': f'{hit_at_3_rate:.1%}',
                'citation_rank': round(avg_citation_rank, 1) if avg_citation_rank > 0 else 'N/A',
                'citation_frequency': round(avg_citation_freq, 1),
                'retrieval_analysis': f'Avg Rank: {avg_citation_rank:.1f}, Avg Freq: {avg_citation_freq:.1f}' if avg_citation_rank > 0 else 'No hits',
                # Gemini evaluation summary
                'accuracy': round(avg_accuracy, 1),
                'completeness': round(avg_completeness, 1),
                'relevance': round(avg_relevance, 1),
                'clarity': round(avg_clarity, 1),
                'comments': 'Summary statistics',
                'processing_time': round(avg_processing_time, 1),
                'evaluation_success': f'{len(successful_evals)}/{len(self.results)}'
            })
        
        print(f"Results saved to: {RESULTS_PATH}")
        print(f"Summary: {len(successful_evals)}/{len(self.results)} successful evaluations")
        print(f"Average Accuracy: {avg_accuracy:.1f}/10")
        print(f"Retrieval Quality: Hit@1={hit_at_1_rate:.1%}, Hit@2={hit_at_2_rate:.1%}, Hit@3={hit_at_3_rate:.1%}")
        if avg_citation_rank > 0:
            print(f"Average Citation Rank: {avg_citation_rank:.1f}, Average Frequency: {avg_citation_freq:.1f}")


@pytest.fixture
async def evaluator():
    """Create RAGQualityEvaluator instance for testing"""
    return RAGQualityEvaluator()

@pytest.fixture
def evaluation_results_path():
    """Provide path for evaluation results"""
    return Path("evaluation/test_rag_evaluation_results.csv")

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.rag
@pytest.mark.timeout(600)  # 10 minutes timeout
class TestRAGQualityEvaluation:
    """Test class for RAG quality evaluation using pytest"""
    
    async def test_dataset_loading(self, evaluator):
        """Test that dataset can be loaded successfully"""
        qa_pairs = evaluator.load_dataset()
        
        assert len(qa_pairs) > 0, "Dataset should contain Q&A pairs"
        assert all("question" in pair for pair in qa_pairs), "All pairs should have questions"
        assert all("answer" in pair for pair in qa_pairs), "All pairs should have answers"
    
    @pytest.mark.real_llm
    async def test_single_qa_evaluation(self, evaluator):
        """Test evaluation of a single Q&A pair"""
        qa_pairs = evaluator.load_dataset()
        assert len(qa_pairs) > 0, "Need at least one Q&A pair for testing"
        
        # Test with first Q&A pair
        result = await evaluator.evaluate_single_qa(qa_pairs[0], 1)
        
        # Verify result structure
        required_fields = [
            "question_id", "question", "generated_answer", "expected_answer",
            "citations_found", "accuracy", "completeness", "relevance", 
            "clarity", "comments", "processing_time",
            "evaluation_success"
        ]
        
        for field in required_fields:
            assert field in result, f"Result should contain '{field}' field"
        
        # Verify score ranges (0-10)
        score_fields = ["accuracy", "completeness", "relevance", "clarity"]
        for field in score_fields:
            score = result[field]
            assert 0 <= score <= 10, f"{field} score should be between 0-10, got {score}"
    
    @pytest.mark.slow
    @pytest.mark.real_llm
    async def test_full_rag_quality_evaluation(self, evaluator, evaluation_results_path):
        """Main test for full RAG quality evaluation"""
        print("Starting RAG Quality Evaluation...")
        start_time = time.time()
        
        # Run evaluation
        results = await evaluator.run_evaluation()
        
        # Update results path for test
        global RESULTS_PATH
        original_results_path = RESULTS_PATH
        RESULTS_PATH = evaluation_results_path
        
        try:
            # Save results
            evaluator.save_results_to_csv()
        finally:
            # Restore original path
            RESULTS_PATH = original_results_path
        
        total_time = time.time() - start_time
        print(f"Evaluation completed in {total_time:.2f} seconds")
        
        # Basic validation assertions
        assert len(results) > 0, "No evaluation results generated"
        
        successful_evaluations = [r for r in results if r["evaluation_success"]]
        success_rate = len(successful_evaluations) / len(results)
        
        print(f"Final Results:")
        print(f"- Questions Evaluated: {len(results)}")
        print(f"- Successful Evaluations: {len(successful_evaluations)}")
        print(f"- Success Rate: {success_rate:.1%}")
        
        # Success criteria assertions
        assert success_rate >= 0.7, f"Success rate too low: {success_rate:.1%}"
        
        if successful_evaluations:
            avg_accuracy = sum(r["accuracy"] for r in successful_evaluations) / len(successful_evaluations)
            print(f"- Average Accuracy Score: {avg_accuracy:.1f}/10")
            
            # Calculate Hit@k rates for assertions (frequency-based)
            hit_at_1_rate = sum(1 for r in successful_evaluations if r.get("hit_at_1", False)) / len(successful_evaluations)
            hit_at_2_rate = sum(1 for r in successful_evaluations if r.get("hit_at_2", False)) / len(successful_evaluations)
            hit_at_3_rate = sum(1 for r in successful_evaluations if r.get("hit_at_3", False)) / len(successful_evaluations)
            
            print(f"- Retrieval Quality: Hit@1={hit_at_1_rate:.1%}, Hit@2={hit_at_2_rate:.1%}, Hit@3={hit_at_3_rate:.1%}")
            
            # Quality thresholds (frequency-based ranking)
            assert avg_accuracy >= 3.0, f"Average accuracy too low: {avg_accuracy:.1f}/10"
            assert hit_at_3_rate >= 0.6, f"Hit@3 rate too low: {hit_at_3_rate:.1%} (expected ≥60%)"
            assert hit_at_2_rate >= 0.4, f"Hit@2 rate too low: {hit_at_2_rate:.1%} (expected ≥40%)"
            
            # Verify all results have proper structure
            for i, result in enumerate(results):
                assert "question_id" in result, f"Result {i+1} missing question_id"
                assert "evaluation_success" in result, f"Result {i+1} missing evaluation_success"
                assert "processing_time" in result, f"Result {i+1} missing processing_time"
                assert result["processing_time"] > 0, f"Result {i+1} has invalid processing time"
        
        # Verify CSV file was created
        assert evaluation_results_path.exists(), "Results CSV file should be created"
        
        # Verify CSV content
        with open(evaluation_results_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
            assert "SUMMARY" in csv_content, "CSV should contain summary row"
            assert "question_id" in csv_content, "CSV should have proper headers"
    
    @pytest.mark.real_llm
    async def test_gemini_evaluation_integration(self, evaluator):
        """Test Gemini evaluation service integration"""
        sample_question = "What is the bearing capacity formula?"
        sample_generated = "The bearing capacity is calculated using Terzaghi's formula."
        sample_expected = "Bearing capacity uses Terzaghi equation: q_ult = γ*Df*Nq + 0.5*γ*B*Nr"
        
        evaluation = await evaluator.evaluate_with_gemini(
            sample_question, sample_generated, sample_expected
        )
        
        # Verify evaluation structure
        required_fields = ["accuracy", "completeness", "relevance", "clarity", "comments"]
        for field in required_fields:
            assert field in evaluation, f"Evaluation should contain '{field}' field"
        
        # Verify score ranges
        score_fields = ["accuracy", "completeness", "relevance", "clarity"]
        for field in score_fields:
            score = evaluation[field]
            assert 0 <= score <= 10, f"{field} score should be between 0-10, got {score}"


