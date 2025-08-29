# 🔍 Observability Setup Guide

This guide walks you through setting up comprehensive observability for the Geotechnical AI Service.

## 📊 What's Already Working

The observability system is **fully functional** out of the box:

✅ **Structured JSON Logging** → `logs/info.log` and `logs/error.log`  
✅ **Real-time Metrics** → `GET /metrics` endpoint  
✅ **Request Tracing** → Every request has a unique `trace_id`  
✅ **Agent Workflow Monitoring** → Planning → Execution → Synthesis steps tracked  
✅ **Performance Metrics** → Response times, success rates, throughput  

## 🚀 Quick Start (5 minutes)

### Step 1: Copy Environment Configuration
```bash
cp .env.example .env
```

### Step 2: Configure Required API Keys
Edit `.env` file:
```env
# Required - Get from OpenAI
OPENAI_API_KEY="sk-your_openai_key_here"

# Required - Get from Google AI Studio  
GOOGLE_GENAI_API_KEY="your_google_genai_key_here"

# Optional - Leave empty for now
LANGFUSE_PUBLIC_KEY=""
LANGFUSE_SECRET_KEY=""
```

### Step 3: Test the System
```bash
# Test core components
python test_observability_setup.py

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test endpoints (in another terminal)
curl http://localhost:8000/health      # Should return {"status":"ok"}
curl http://localhost:8000/metrics     # Should return detailed metrics
```

## 📈 Monitoring Your Service

### Real-time Metrics Dashboard
Access comprehensive metrics at: `GET /metrics`

```json
{
  "total_requests": 42,
  "tool_calls": 15,
  "retrieval_calls": 27, 
  "successful_requests": 40,
  "failed_requests": 2,
  "average_response_time": 1247.5,
  "success_rate": 95.2,
  "uptime_seconds": 3600,
  "requests_per_minute": 0.7
}
```

### Structured Logs
All logs are written as structured JSON to:
- `logs/info.log` - General application logs
- `logs/error.log` - Error logs only

Example log entry:
```json
{
  "timestamp": "2025-08-29T04:34:13.216051+00:00",
  "level": "INFO",
  "trace_id": "abc-123-def",
  "agent_step": "planning", 
  "duration_ms": 145.2,
  "message": "Agent planning completed"
}
```

### Request Correlation
Every request gets a unique `trace_id` that appears in:
- All log entries for that request
- API response body
- LangFuse traces (if configured)

## 🔗 Optional: LangFuse Visual Tracing

LangFuse provides beautiful visual dashboards for your AI workflows.

### Step 1: Create Free Account
1. Visit https://cloud.langfuse.com
2. Sign up (free tier available)
3. Create a new project

### Step 2: Get API Keys
1. Go to Settings → API Keys
2. Copy your Public Key (`pk-lf-...`)
3. Copy your Secret Key (`sk-lf-...`)

### Step 3: Update Configuration
Edit your `.env` file:
```env
LANGFUSE_PUBLIC_KEY="pk-lf-your_actual_public_key"
LANGFUSE_SECRET_KEY="sk-lf-your_actual_secret_key"
LANGFUSE_HOST="https://cloud.langfuse.com"
```

### Step 4: Restart and Test
```bash
# Restart the server to pick up new environment
# Ctrl+C then restart
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Send a test request
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is settlement calculation?"}'
```

### Step 5: View in LangFuse
1. Go to your LangFuse dashboard
2. You should see traces appearing under "Traces"
3. Click on a trace to see the full agent workflow

## 🐳 Docker Deployment

### Step 1: Update docker-compose.yml
```yaml
version: '3.8'
services:
  geotech-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_GENAI_API_KEY=${GOOGLE_GENAI_API_KEY}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_HOST=${LANGFUSE_HOST}
      - LOG_LEVEL=INFO
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs  # Persist logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Step 2: Deploy
```bash
docker-compose up -d
```

## 📊 Production Monitoring

### Health Checks
- **Endpoint:** `GET /health`
- **Expected:** `{"status": "ok"}`
- **Use for:** Container orchestration health checks

### Operational Metrics  
- **Endpoint:** `GET /metrics`
- **Frequency:** Every 30-60 seconds
- **Alerts on:** 
  - `success_rate < 95%`
  - `average_response_time > 5000ms`
  - `failed_requests` increasing

### Log Monitoring
- **Files:** `logs/info.log`, `logs/error.log`
- **Rotation:** Automatic at 10MB per file
- **Retention:** 5 backup files kept
- **Format:** Structured JSON for easy parsing

## 🔧 Advanced Configuration

### Log Levels
```env
LOG_LEVEL=DEBUG    # Very verbose
LOG_LEVEL=INFO     # Default (recommended)
LOG_LEVEL=WARNING  # Minimal logging
LOG_LEVEL=ERROR    # Errors only
```

### Custom Metrics Collection
The metrics collector is extensible:

```python
from app.services.observability import get_metrics_collector

metrics = get_metrics_collector()
metrics.increment_tool_calls()        # Track tool usage
metrics.increment_retrieval_calls()   # Track RAG usage  
metrics.record_response_time(123.4)   # Track timing
```

## 🚨 Troubleshooting

### "LangFuse package not installed"
- **Issue:** LangFuse not available
- **Solution:** `pip install langfuse==2.60.5` or leave keys empty to disable

### "Address already in use"
- **Issue:** Port 8000 is busy
- **Solution:** Change port: `uvicorn app.main:app --port 8001`

### "Invalid credentials" in LangFuse
- **Issue:** Wrong API keys or host
- **Solution:** Double-check keys in LangFuse dashboard Settings

### Empty metrics response
- **Issue:** No requests processed yet
- **Solution:** Send a test request to `/ask` endpoint first

## 🎯 Key Benefits

### 🔍 **Request Tracing**
- Every request tracked end-to-end
- Unique trace_id for correlation
- Visual workflow in LangFuse

### ⚡ **Performance Monitoring**
- Real-time response times
- Success/failure rates
- Agent step timing

### 🐛 **Debugging Support**
- Structured JSON logs
- Error correlation by trace_id
- Step-by-step agent execution logs

### 📈 **Operational Insights**
- Usage patterns (tools vs retrieval)
- Performance trends over time
- Resource utilization metrics

---

🎉 **Your Geotechnical AI Service now has enterprise-grade observability!**

For questions or issues, check the logs in `logs/` directory or the metrics at `/metrics` endpoint.