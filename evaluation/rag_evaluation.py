"""
Comprehensive RAG Evaluation with CSV Output
Test retrieval with top 5-10 chunks, compare answers, save results to CSV
"""

import json
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.agent import GeotechAgent
from app.services.agentic_workflow.retrieval.rag_service import RAGService
from app.core.config.settings import get_settings

def load_questions_from_dataset() -> List[Dict[str, Any]]:
    """Load questions and expected answers from dataset.json"""
    dataset_path = Path(__file__).parent / "dataset.json"
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data["qa_pairs"]

def test_retrieval_chunks(rag_service: RAGService, question: str, k: int = 10, threshold: float = 0.6) -> List[Dict]:
    """Test retrieval and return detailed chunk information"""
    citations = rag_service.search(
        query=question,
        k=k,
        score_threshold=threshold
    )
    
    chunks_info = []
    for i, citation in enumerate(citations):
        chunks_info.append({
            "rank": i + 1,
            "source": citation.source_name,
            "score": citation.confidence_score,
            "content_preview": citation.content[:200].replace('\n', ' '),
            "page_index": citation.page_index,
            "content_length": len(citation.content)
        })
    
    return chunks_info

def calculate_answer_similarity(generated_answer: str, expected_answer: str) -> Dict[str, float]:
    """Calculate similarity metrics between generated and expected answers"""
    
    # Convert to lowercase for comparison
    gen_words = set(generated_answer.lower().split())
    exp_words = set(expected_answer.lower().split())
    
    # Jaccard similarity (intersection over union)
    intersection = len(gen_words.intersection(exp_words))
    union = len(gen_words.union(exp_words))
    jaccard_score = intersection / union if union > 0 else 0
    
    # Word overlap percentage
    overlap_score = intersection / len(exp_words) if exp_words else 0
    
    # Check for key technical terms presence
    technical_terms = ["CPT", "liquefaction", "bearing capacity", "settlement", "shear strength", 
                      "friction angle", "consolidation", "Terzaghi", "formula", "equation"]
    
    exp_technical = [term for term in technical_terms if term.lower() in expected_answer.lower()]
    gen_technical = [term for term in technical_terms if term.lower() in generated_answer.lower()]
    
    technical_overlap = len(set(exp_technical).intersection(set(gen_technical)))
    technical_score = technical_overlap / len(exp_technical) if exp_technical else 1.0
    
    return {
        "jaccard_similarity": round(jaccard_score, 3),
        "word_overlap_score": round(overlap_score, 3),
        "technical_terms_score": round(technical_score, 3),
        "expected_technical_terms": len(exp_technical),
        "generated_technical_terms": len(gen_technical),
        "technical_match_count": technical_overlap
    }

def run_comprehensive_evaluation():
    """Run comprehensive RAG evaluation and save to CSV"""
    
    print("🧪 COMPREHENSIVE RAG EVALUATION WITH CSV OUTPUT")
    print("=" * 70)
    
    # Load questions from dataset
    qa_pairs = load_questions_from_dataset()
    print(f"Loaded {len(qa_pairs)} questions from dataset.json")
    
    # Initialize services
    try:
        settings = get_settings()
        agent = GeotechAgent()
        rag_service = RAGService(
            openai_api_key=settings.OPENAI_API_KEY,
            gemini_api_key=settings.GOOGLE_GENAI_API_KEY,
            qdrant_host=settings.QDRANT_HOST,
            qdrant_port=settings.QDRANT_PORT,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            mongodb_host=settings.MONGODB_HOST,
            mongodb_port=settings.MONGODB_PORT,
            mongodb_database=settings.MONGODB_DATABASE,
            mongodb_collection=settings.MONGODB_COLLECTION
        )
        print("✅ Agent and RAG service initialized")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Evaluation parameters
    TOP_K = 5
    SCORE_THRESHOLD = 0.2
    
    print(f"Evaluation parameters: top_k={TOP_K}, threshold={SCORE_THRESHOLD}")
    
    # Results storage
    detailed_results = []
    
    print("\n" + "=" * 70)
    print("PROCESSING QUESTIONS")
    print("=" * 70)
    
    for i, qa_pair in enumerate(qa_pairs, 1):
        question = qa_pair["question"]
        expected_answer = qa_pair["answer"]
        
        print(f"\n{i}. Processing question: {question[:80]}...")
        
        try:
            # Step 1: Test retrieval chunks
            chunks_info = test_retrieval_chunks(rag_service, question, TOP_K, SCORE_THRESHOLD)
            chunks_count = len(chunks_info)
            
            print(f"   Retrieved {chunks_count} chunks (threshold: {SCORE_THRESHOLD})")
            
            # Show top chunks
            for chunk in chunks_info[:3]:  # Show top 3
                print(f"     #{chunk['rank']}: {chunk['source']} (score: {chunk['score']:.3f})")
            
            # Step 2: Get agent response
            response = agent.run(question)
            generated_answer = response.answer
            
            print(f"   Generated answer length: {len(generated_answer.split())} words")
            
            # Step 3: Calculate similarity
            similarity = calculate_answer_similarity(generated_answer, expected_answer)
            
            print(f"   Similarity scores - Jaccard: {similarity['jaccard_similarity']}, "
                  f"Overlap: {similarity['word_overlap_score']}, "
                  f"Technical: {similarity['technical_terms_score']}")
            
            # Step 4: Store detailed results
            result = {
                "question_id": i,
                "question": question,
                "expected_answer": expected_answer,
                "generated_answer": generated_answer,
                "chunks_retrieved": chunks_count,
                "top_chunk_score": chunks_info[0]["score"] if chunks_info else 0,
                "top_chunk_source": chunks_info[0]["source"] if chunks_info else "None",
                "citations_used": len(response.citations),
                "trace_id": response.trace_id,
                **similarity,
                "chunks_details": json.dumps(chunks_info)  # Store as JSON string
            }
            
            detailed_results.append(result)
            
        except Exception as e:
            print(f"   ❌ Error processing question {i}: {e}")
            
            # Add error result
            error_result = {
                "question_id": i,
                "question": question,
                "expected_answer": expected_answer,
                "generated_answer": f"ERROR: {str(e)}",
                "chunks_retrieved": 0,
                "top_chunk_score": 0,
                "top_chunk_source": "ERROR",
                "citations_used": 0,
                "trace_id": "ERROR",
                "jaccard_similarity": 0,
                "word_overlap_score": 0,
                "technical_terms_score": 0,
                "expected_technical_terms": 0,
                "generated_technical_terms": 0,
                "technical_match_count": 0,
                "chunks_details": "[]"
            }
            detailed_results.append(error_result)
    
    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"rag_evaluation_results_{timestamp}.csv"
    csv_path = Path(__file__).parent / csv_filename
    
    print(f"\n📊 SAVING RESULTS TO CSV: {csv_filename}")
    print("=" * 70)
    
    # CSV headers
    csv_headers = [
        "question_id", "question", "expected_answer", "generated_answer",
        "chunks_retrieved", "top_chunk_score", "top_chunk_source",
        "citations_used", "trace_id", "jaccard_similarity", 
        "word_overlap_score", "technical_terms_score",
        "expected_technical_terms", "generated_technical_terms", 
        "technical_match_count", "chunks_details"
    ]
    
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            writer.writeheader()
            writer.writerows(detailed_results)
        
        print(f"✅ Results saved to: {csv_path}")
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")
    
    # Calculate summary statistics
    valid_results = [r for r in detailed_results if r["chunks_retrieved"] > 0]
    
    if valid_results:
        avg_chunks = sum(r["chunks_retrieved"] for r in valid_results) / len(valid_results)
        avg_jaccard = sum(r["jaccard_similarity"] for r in valid_results) / len(valid_results)
        avg_overlap = sum(r["word_overlap_score"] for r in valid_results) / len(valid_results)
        avg_technical = sum(r["technical_terms_score"] for r in valid_results) / len(valid_results)
        
        print(f"\n📈 SUMMARY STATISTICS")
        print("=" * 30)
        print(f"Total questions: {len(qa_pairs)}")
        print(f"Successful evaluations: {len(valid_results)}")
        print(f"Success rate: {len(valid_results)/len(qa_pairs):.1%}")
        print(f"Average chunks retrieved: {avg_chunks:.1f}")
        print(f"Average Jaccard similarity: {avg_jaccard:.3f}")
        print(f"Average word overlap: {avg_overlap:.3f}")
        print(f"Average technical terms score: {avg_technical:.3f}")
        
        # Performance rating
        overall_score = (avg_jaccard + avg_overlap + avg_technical) / 3
        print(f"Overall performance score: {overall_score:.3f}")
        
        if overall_score >= 0.7:
            print("🎉 EXCELLENT performance!")
        elif overall_score >= 0.5:
            print("✅ GOOD performance")
        elif overall_score >= 0.3:
            print("⚠️ FAIR performance - needs improvement")
        else:
            print("❌ POOR performance - significant improvements needed")
    
    return {
        "csv_file": str(csv_path),
        "results_count": len(detailed_results),
        "valid_results": len(valid_results),
        "detailed_results": detailed_results
    }

def main():
    """Main evaluation function"""
    import logging
    logging.basicConfig(level=logging.INFO)  # Show INFO logs for debugging
    
    try:
        return run_comprehensive_evaluation()
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return None

if __name__ == "__main__":
    main()