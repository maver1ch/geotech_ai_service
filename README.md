# Geotechnical AI Service

A FastAPI-based AI service that answers geotechnical engineering questions through intelligent retrieval from a specialized knowledge base and execution of geotechnical calculation tools.

## 🏗️ Architecture Overview

The service implements a sophisticated **Plan → Execute → Synthesize** workflow:

1. **Plan**: Analyzes incoming questions to determine the appropriate action (retrieve, calculate, or both)
2. **Execute**: Performs retrieval from knowledge base and/or executes calculation tools
3. **Synthesize**: Combines results into professional engineering responses

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Google GenAI API key (for OCR features)
- Optional: Qdrant and MongoDB (or use Docker Compose)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/maver1ch/geotech_ai_service.git
cd geotech_ai_service

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run with Docker Compose (Recommended)

```bash
# Start all services (app + databases)
docker-compose up -d

# Check service health
curl http://localhost:8000/health
```

### 3. Alternative: Run Standalone

```bash
# Build and run the application only
docker build -t geotech-ai .
docker run -p 8000:8000 --env-file .env geotech-ai
```

## 📡 API Usage

### Ask a Question

```bash
# Geotechnical knowledge retrieval
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is CPT analysis and how is it used in Settle3?"
  }'

# Settlement calculation
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Calculate settlement for a load of 1000 kN with Young modulus of 25000 kPa"
  }'

# Bearing capacity calculation  
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Calculate bearing capacity for a 2m footing, soil unit weight 18 kN/m³, depth 1.5m, friction angle 30°"
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
# Returns: {"status": "ok"}
```

### Metrics

```bash
curl http://localhost:8000/metrics
# Returns operational metrics including request counts, timing, success rates
```

## 🧠 Agent Intelligence

The GeotechAgent uses sophisticated decision logic:

### Planning Phase
- Analyzes question intent and domain scope
- Determines if question requires retrieval, calculation, or both
- Validates input parameters for calculations
- Rejects out-of-scope questions with clear explanations

### Execution Phase  
- **Retrieval**: Hybrid search combining vector similarity + keyword matching
- **Calculations**: Two specialized tools with comprehensive validation:
  - **Settlement Calculator**: `settlement = load / young_modulus`
  - **Bearing Capacity Calculator**: Terzaghi formula with bearing capacity factor interpolation

### Synthesis Phase (output answer)
- Combines retrieval and calculation results
- Provides professional, cited responses
- Maintains engineering accuracy and safety

## 🛠️ Geotechnical Tools

### Settlement Calculator
- **Formula**: `settlement = load / young_modulus`
- **Inputs**: Load (kN), Young's modulus (kPa)
- **Validation**: Positive values required
- **Output**: Settlement with calculation details

### Bearing Capacity Calculator  
- **Formula**: `q_ult = γ*Df*Nq + 0.5*γ*B*Nr` (Terzaghi, cohesionless soil)
- **Inputs**: 
  - B: Footing width/diameter (m)
  - γ: Unit weight of soil (kN/m³)  
  - Df: Footing depth (m)
  - φ: Internal friction angle (degrees, 0-40)
- **Features**: Bearing capacity factor interpolation for any angle 0-40°
- **Output**: Ultimate bearing capacity with breakdown of calculations

## 📚 Knowledge Base

Comprehensive geotechnical engineering knowledge base sourced from Rocscience Settle3 documentation:

- **Settle3 CPT Theory Manual**: Cone Penetration Test data interpretation, soil parameter correlations (friction angle, unit weight, overburden stress, shear wave velocity, bearing capacity factors)
- **Settle3 Liquefaction Theory Manual**: Liquefaction assessment methods, cyclic stress ratios (CSR), cyclic resistance ratios (CRR), stress reduction factors, post-liquefaction settlement calculations
- **Settle3 Theory Documentation**: Consolidation theory (primary vs secondary), time-dependent analysis, degree of consolidation calculations, stage modeling
- **Settle3 FAQs**: Common modeling questions, rigid foundations, drainage conditions, pyramid loads, calculation optimization
- **Settle3 Modeling Guide**: Non-horizontal soil layers, multi-layer analysis modes, drainage condition assignments, load types and configurations

### Retrieval System
- **Hybrid Search**: Vector similarity + keyword matching
- **Smart Filtering**: Automatic keyword extraction and relevance scoring
- **Source Attribution**: All responses include source citations
- **Quality Control**: Similarity thresholds and result ranking

## 🔍 Observability

### Logging
- Structured JSON logs with trace IDs
- Request/response tracking with timing
- Agent workflow step logging
- Error tracking with full context

### Metrics
- Request counts and success rates
- Tool usage statistics  
- Response time distributions
- RAG retrieval performance

### Tracing (Optional)
- LangFuse integration for request tracing
- Agent workflow visualization
- Performance monitoring and debugging

## 🛡️ Reliability & Safety

### Error Handling
- Graceful failure recovery
- Comprehensive input validation
- Timeout and retry mechanisms
- Clear error messages for users

### Security
- API input sanitization
- No secrets in code/logs
- Environment-based configuration
- Professional engineering guardrails

### Input Validation
- Calculation parameter bounds checking
- Malicious input detection and rejection
- Domain scope enforcement
- Engineering safety constraints

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run specific test categories
pytest tests/test_observability.py               # Obserability tests
pytest tests/test_geotech_tools.py               # Tool tests
pytest tests/test_rag_logic.py                   # RAG tests  
pytest tests/test_rag_quality.py                 # RAG tests  (report in evaluation)
pytest tests/test_agent_comprehensive.py         # Agent workflow tests
```

### Test Coverage
- ✅ **Tool Tests**: Settlement and bearing capacity calculators
- ✅ **RAG Tests**: Vector search, keyword search, hybrid retrieval
- ✅ **Agent Tests**: Plan-Execute-Synthesize workflow
- ✅ **Integration Tests**: End-to-end question processing

## 🐳 Docker Support

### Multi-Stage Dockerfile
- Optimized Python 3.11-slim base image
- Efficient dependency installation
- Production-ready configuration

### Docker Compose
- Complete stack deployment (app + databases)
- Environment variable management
- Volume persistence for data
- Service health checks

## 📊 Evaluation Results

The system includes comprehensive evaluation of RAG quality:

- **Hit@3 Rate**: 100%+ for domain questions with evaluation/dataset.json
- **Answer Accuracy**: Professional engineering responses with proper citations
- **Response Time**: <10s average for most queries

See `/evaluation/` directory for detailed evaluation scripts and results.

## 🔧 Configuration

Key configuration options (see `.env.example`):

```bash
# Required API Keys
OPENAI_API_KEY="your_key_here"
GOOGLE_GENAI_API_KEY="your_key_here"  

```

## 📝 Engineering Notes

### Design Decisions

1. **Hybrid RAG**: Combines vector similarity with keyword search for better recall
2. **Async Architecture**: Non-blocking operations for scalability
3. **Modular Design**: Clear separation of concerns for maintainability
4. **Professional Guardrails**: Safety-first approach for engineering applications

### Performance Optimizations

- Concurrent retrieval and calculation execution
- Efficient vector search with Qdrant
- Smart keyword extraction to reduce unnecessary searches
- Connection pooling and timeout management

### Safety Measures

- Domain scope enforcement (geotechnical engineering only)
- Input parameter validation with engineering constraints
- Professional tone and uncertainty handling
- Clear source attribution for all responses

---
