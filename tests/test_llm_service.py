#!/usr/bin/env python3
"""
Test script for OpenAI LLM Service
Verify LLM integration, retry logic, and error handling
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from app.core.llms.openai import OpenAIService

def test_basic_llm_call():
    """Test basic LLM functionality"""
    print("=" * 50)
    print("TESTING BASIC LLM CALL")
    print("=" * 50)
    
    # Load environment
    load_dotenv(project_root / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to .env file")
        return False
    
    # Initialize service
    llm_service = OpenAIService(api_key=api_key)
    
    # Test 1: Simple string input
    print("Test 1: Simple string question")
    result = llm_service.call_llm("What is 2 + 2?")
    print(f"Response: {result['content'][:100]}...")
    print(f"Status: {result['status']}")
    print(f"Tokens: {result['usage']['total_tokens']}")
    print(f"Time: {result['response_time']}s")
    
    return result['status'] == 'success'

def test_message_formats():
    """Test different message formats"""
    print("\n" + "=" * 50)
    print("TESTING MESSAGE FORMATS")
    print("=" * 50)
    
    load_dotenv(project_root / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    llm_service = OpenAIService(api_key=api_key)
    
    # Test 2: Message list format
    print("Test 2: Message list format")
    messages = [
        {"role": "system", "content": "You are a helpful geotechnical engineering assistant."},
        {"role": "user", "content": "What is the bearing capacity of soil?"}
    ]
    result = llm_service.call_llm(messages)
    print(f"Response: {result['content'][:100]}...")
    print(f"Status: {result['status']}")
    
    # Test 3: Helper methods
    print("\nTest 3: Using helper methods")
    conversation = llm_service.create_conversation(
        system_prompt="You are a geotech expert. Give brief answers.",
        user_message="Explain soil settlement in one sentence."
    )
    result = llm_service.call_llm(conversation)
    print(f"Response: {result['content']}")
    print(f"Status: {result['status']}")

def test_geotech_specific():
    """Test with geotechnical engineering questions"""
    print("\n" + "=" * 50)
    print("TESTING GEOTECH-SPECIFIC QUESTIONS")
    print("=" * 50)
    
    load_dotenv(project_root / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    llm_service = OpenAIService(api_key=api_key, temperature=0.1)
    
    geotech_questions = [
        "What factors affect the bearing capacity of shallow foundations?",
        "How do you calculate settlement of soil under load?",
        "What is the difference between immediate and consolidation settlement?"
    ]
    
    for i, question in enumerate(geotech_questions, 1):
        print(f"\nGeotech Test {i}: {question}")
        result = llm_service.call_llm(question)
        print(f"Response: {result['content'][:150]}...")
        print(f"Tokens: {result['usage']['total_tokens']}, Time: {result['response_time']}s")

async def test_async_calls():
    """Test async LLM calls"""
    print("\n" + "=" * 50) 
    print("TESTING ASYNC LLM CALLS")
    print("=" * 50)
    
    load_dotenv(project_root / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    llm_service = OpenAIService(api_key=api_key)
    
    # Test concurrent calls
    questions = [
        "What is CPT testing?",
        "Explain soil liquefaction.",
        "What are bearing capacity factors?"
    ]
    
    print("Making 3 concurrent async calls...")
    start_time = asyncio.get_event_loop().time()
    
    tasks = [llm_service.call_llm_async(q) for q in questions]
    results = await asyncio.gather(*tasks)
    
    end_time = asyncio.get_event_loop().time()
    total_time = end_time - start_time
    
    print(f"Completed {len(results)} calls in {total_time:.2f}s")
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}: {result['content'][:80]}... ({result['status']})")

def test_error_handling():
    """Test error handling and edge cases"""
    print("\n" + "=" * 50)
    print("TESTING ERROR HANDLING") 
    print("=" * 50)
    
    load_dotenv(project_root / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    llm_service = OpenAIService(api_key=api_key)
    
    # Test invalid message format
    print("Test: Invalid message format")
    try:
        result = llm_service.call_llm([{"invalid": "format"}])
        print(f"Result: {result}")
    except Exception as e:
        print(f"Caught expected error: {e}")
    
    # Test with very short timeout (might cause timeout)
    print("\nTest: Short timeout")
    result = llm_service.call_llm("Explain soil mechanics in detail.", timeout=1)
    print(f"Status: {result['status']}")
    if result['status'] == 'error':
        print(f"Error: {result['error']}")

def test_statistics():
    """Test usage statistics tracking"""
    print("\n" + "=" * 50)
    print("TESTING STATISTICS TRACKING")
    print("=" * 50)
    
    load_dotenv(project_root / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    llm_service = OpenAIService(api_key=api_key)
    
    # Make a few calls
    for i in range(3):
        result = llm_service.call_llm(f"Count to {i+1}")
        print(f"Call {i+1}: {result['status']}")
    
    # Check statistics
    stats = llm_service.get_statistics()
    print(f"\nStatistics:")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Success rate: {stats['success_rate']}%")
    print(f"Total tokens: {stats['total_tokens_used']}")
    print(f"Avg tokens/request: {stats['average_tokens_per_request']}")

async def main():
    """Run all tests"""
    print("🧪 LLM SERVICE TEST SUITE")
    print("Testing OpenAI integration with retry logic...")
    
    # Check for API key first
    load_dotenv(project_root / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to .env file to run tests")
        return
    
    success = test_basic_llm_call()
    if not success:
        print("❌ Basic test failed - skipping other tests")
        return
    
    test_message_formats()
    test_geotech_specific() 
    await test_async_calls()
    test_error_handling()
    test_statistics()
    
    print("\n" + "=" * 50)
    print("✅ ALL LLM SERVICE TESTS COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())