#!/usr/bin/env python3
"""
End-to-End Observability Test
Tests the complete observability system with actual API calls
"""

import json
import time
import requests
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

def test_server_availability():
    """Test if the server is running and accessible"""
    print("🔍 Testing server availability...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print("  ✅ Server is running and healthy")
                return True
            else:
                print(f"  ❌ Server returned unexpected health status: {data}")
                return False
        else:
            print(f"  ❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Cannot connect to server: {e}")
        return False

def test_metrics_endpoint():
    """Test the metrics endpoint and validate structure"""
    print("\n📊 Testing metrics endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=5)
        if response.status_code != 200:
            print(f"  ❌ Metrics endpoint failed with status {response.status_code}")
            return False
        
        metrics = response.json()
        expected_fields = [
            "total_requests", "tool_calls", "retrieval_calls",
            "successful_requests", "failed_requests", "average_response_time",
            "uptime_seconds", "requests_per_minute"
        ]
        
        missing_fields = [field for field in expected_fields if field not in metrics]
        if missing_fields:
            print(f"  ❌ Missing metrics fields: {missing_fields}")
            return False
        
        print("  ✅ Metrics endpoint working correctly")
        print(f"  📈 Current metrics preview:")
        print(f"    - Total requests: {metrics['total_requests']}")
        print(f"    - Average response time: {metrics['average_response_time']:.2f}ms")
        print(f"    - Uptime: {metrics['uptime_seconds']:.1f}s")
        
        return True
    except Exception as e:
        print(f"  ❌ Error testing metrics endpoint: {e}")
        return False

def test_ask_endpoint_and_tracing():
    """Test the main /ask endpoint and verify observability integration"""
    print("\n🤖 Testing /ask endpoint with observability...")
    
    test_cases = [
        {
            "name": "Simple Question",
            "question": "What is settlement analysis?",
            "expected_fields": ["answer", "citations", "trace_id"]
        },
        {
            "name": "Tool Calculation Request", 
            "question": "Calculate settlement for load 1000 kN and Young's modulus 50000 kPa",
            "expected_fields": ["answer", "citations", "trace_id"]
        }
    ]
    
    results = {"passed": 0, "total": len(test_cases)}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Test {i}/{len(test_cases)}: {test_case['name']}")
        
        try:
            # Record metrics before request
            metrics_before = requests.get(f"{BASE_URL}/metrics", timeout=5).json()
            
            # Send request
            payload = {"question": test_case["question"]}
            print(f"    Question: {test_case['question']}")
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/ask", 
                json=payload, 
                headers={"Content-Type": "application/json"},
                timeout=TEST_TIMEOUT
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code != 200:
                print(f"    ❌ Request failed with status {response.status_code}")
                print(f"    Response: {response.text}")
                continue
            
            # Parse response
            result = response.json()
            
            # Validate response structure
            missing_fields = [field for field in test_case["expected_fields"] if field not in result]
            if missing_fields:
                print(f"    ❌ Missing response fields: {missing_fields}")
                continue
            
            # Validate trace_id
            trace_id = result.get("trace_id", "")
            if not trace_id or len(trace_id) < 10:
                print(f"    ❌ Invalid trace_id: {trace_id}")
                continue
            
            # Check metrics after request
            time.sleep(0.5)  # Allow metrics to update
            metrics_after = requests.get(f"{BASE_URL}/metrics", timeout=5).json()
            
            # Verify metrics increased
            requests_increased = metrics_after["total_requests"] > metrics_before["total_requests"]
            if not requests_increased:
                print(f"    ⚠️  Request metrics didn't increase (before: {metrics_before['total_requests']}, after: {metrics_after['total_requests']})")
            
            # Display results
            answer_preview = result["answer"][:100] + "..." if len(result["answer"]) > 100 else result["answer"]
            print(f"    ✅ Response received successfully")
            print(f"    📝 Answer preview: {answer_preview}")
            print(f"    🔗 Trace ID: {trace_id}")
            print(f"    ⏱️  Response time: {response_time:.0f}ms")
            print(f"    📚 Citations: {len(result.get('citations', []))}")
            
            results["passed"] += 1
            
        except requests.exceptions.Timeout:
            print(f"    ❌ Request timed out after {TEST_TIMEOUT}s")
        except Exception as e:
            print(f"    ❌ Request failed: {e}")
    
    print(f"\n  📊 Ask endpoint test results: {results['passed']}/{results['total']} passed")
    return results["passed"] == results["total"]

def test_log_files():
    """Test that log files are being created and contain proper data"""
    print("\n📝 Testing log file generation...")
    
    logs_dir = Path(__file__).parent / "logs"
    
    if not logs_dir.exists():
        print("  ❌ Logs directory doesn't exist")
        return False
    
    info_log = logs_dir / "info.log" 
    error_log = logs_dir / "error.log"
    
    # Check info log
    if not info_log.exists():
        print("  ❌ info.log doesn't exist")
        return False
    
    try:
        with open(info_log, 'r') as f:
            lines = f.readlines()
            if not lines:
                print("  ❌ info.log is empty")
                return False
            
            # Check recent lines for JSON structure
            recent_lines = lines[-5:]  # Check last 5 lines
            json_count = 0
            trace_id_count = 0
            
            for line in recent_lines:
                try:
                    log_entry = json.loads(line.strip())
                    json_count += 1
                    if "trace_id" in log_entry:
                        trace_id_count += 1
                except json.JSONDecodeError:
                    continue
            
            print(f"  ✅ info.log exists with {len(lines)} lines")
            print(f"  ✅ JSON structured entries: {json_count}/5 recent lines")
            print(f"  ✅ Trace ID correlation: {trace_id_count}/5 recent lines")
            
            # Show sample log entry
            if recent_lines:
                try:
                    sample = json.loads(recent_lines[-1].strip())
                    print(f"  📄 Latest log entry:")
                    print(f"    - Timestamp: {sample.get('timestamp', 'N/A')}")
                    print(f"    - Level: {sample.get('level', 'N/A')}")
                    print(f"    - Trace ID: {sample.get('trace_id', 'N/A')}")
                    print(f"    - Message: {sample.get('message', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"  📄 Latest log (raw): {recent_lines[-1].strip()[:100]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error reading log files: {e}")
        return False

def test_final_metrics():
    """Get final metrics after all tests"""
    print("\n📈 Final metrics summary...")
    
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=5)
        if response.status_code == 200:
            metrics = response.json()
            
            print("  🎯 Final System Metrics:")
            print(f"    📊 Total requests: {metrics['total_requests']}")
            print(f"    ✅ Successful requests: {metrics['successful_requests']}")
            print(f"    ❌ Failed requests: {metrics['failed_requests']}")
            print(f"    ⏱️  Average response time: {metrics['average_response_time']:.2f}ms")
            print(f"    🔧 Tool calls: {metrics['tool_calls']}")
            print(f"    📚 Retrieval calls: {metrics['retrieval_calls']}")
            print(f"    ⏳ Uptime: {metrics['uptime_seconds']:.1f}s")
            print(f"    📊 Requests/minute: {metrics['requests_per_minute']:.2f}")
            
            return True
    except Exception as e:
        print(f"  ❌ Error getting final metrics: {e}")
        
    return False

def main():
    """Run complete end-to-end observability test"""
    print("🚀 Geotechnical AI Service - Full Observability Test")
    print("=" * 60)
    
    tests = [
        ("Server Availability", test_server_availability),
        ("Metrics Endpoint", test_metrics_endpoint), 
        ("Ask Endpoint & Tracing", test_ask_endpoint_and_tracing),
        ("Log Files", test_log_files),
        ("Final Metrics", test_final_metrics),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: CRASHED - {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 60)
    
    print(f"\n🎯 FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL OBSERVABILITY TESTS PASSED!")
        print("\n✅ Your Geotechnical AI Service observability is fully functional:")
        print("  🔍 Request tracing with unique trace_id")
        print("  📊 Real-time metrics collection")
        print("  📝 Structured JSON logging")
        print("  🚀 Production-ready monitoring")
        print("\n📋 Next Steps:")
        print("  1. Optional: Set up LangFuse for visual tracing")
        print("  2. Deploy with Docker: docker-compose up -d")
        print("  3. Monitor via /metrics endpoint")
        print("  4. Check logs in logs/ directory")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("  1. Ensure server is running: uvicorn app.main:app --reload")
        print("  2. Check server logs for error messages")
        print("  3. Verify .env configuration is complete")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)