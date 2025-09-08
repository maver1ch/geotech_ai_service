# Geotech AI Service with Simple Web UI

A geotechnical engineering AI assistant with a simple React chatbot interface for easy testing.

## Quick Setup (Easy Testing)

### Prerequisites
- Docker & Docker Compose
- Your API keys

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=your_openai_key_here
# GOOGLE_GENAI_API_KEY=your_gemini_key_here
```

### 2. Start Everything
```bash
# One command starts everything (backend + frontend + databases)
docker-compose up --build

# Wait for services to start, then access:
# Frontend UI: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### 3. Test the Chatbot
- Open http://localhost:3000 in your browser
- You'll see a clean chat interface with example questions
- Ask geotechnical questions like:
  - "How does Settle3 calculate bearing capacity?"
  - "Calculate settlement for load 100 kN and Young's modulus 20000 kPa"
  - "What is liquefaction analysis?"
  - "Explain CPT analysis methods"
- The AI will show "Plan → Execute → Synthesize" workflow
- Responses include source citations with confidence scores

## Development Mode (Optional)

### Backend Only
```bash
cd backend
pip install -r requirements.txt
python app/main.py
# Runs on http://localhost:8000
```

### Frontend Only  
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

## Architecture

```
geotech_ai_service/
├── backend/          # FastAPI + RAG + Geotechnical Tools
├── frontend/         # Simple React Chat UI
└── docker-compose.yml # One-command startup
```

**That's it!** The UI is intentionally simple for easy testing of the AI assistant capabilities.