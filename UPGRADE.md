# Geotech AI Service - Future Upgrade Plan

## Overview

This document outlines a comprehensive upgrade roadmap for the Geotech AI Service, transforming it from a basic question-answering system into a sophisticated, context-aware engineering assistant with advanced AI capabilities and professional-grade user experience.

---

## Upgrade 1: Advanced Question Analysis Agent

### 1.1 Query Classification & Decomposition Tool
**Problem**: Current system struggles with vague, overly general like "What is Geotech Theory?", or complex multi-part questions.

**Solution**: Implement a specialized Question Analysis Agent that processes queries before entering the main workflow.

#### Technical Implementation:
- **Location**: `app/services/agentic_workflow/tools/question_analyzer.py`
- **Architecture**: Multi-stage analysis pipeline using LLM-based agents
- **Integration**: Insert between API endpoint and existing `agent.plan()` method

#### Components:

**A. Query Classification Agent**
```python
class QueryClassificationTool:
    async def classify_question(self, question: str) -> QuestionClassification:
        # Categories: simple_calculation, complex_calculation, knowledge_retrieval, 
        # hybrid_calculation_retrieval, out_of_scope, unclear
        # Complexity levels: basic, intermediate, advanced
        # Confidence scores for each classification
```

**B. Question Decomposition Agent** 
```python
class QuestionDecompositionTool:
    async def decompose_complex_question(self, question: str) -> DecomposedQuestion:
        # Break down complex questions into:
        # 1. Primary sub-questions
        # 2. Required parameters identification  
        # 3. Execution sequence planning
        # 4. Dependency mapping between sub-questions
```

**C. Parameter Extraction Agent**
```python
class ParameterExtractionAgent:
    async def extract_calculation_params(self, question: str) -> ExtractedParameters:
        # Auto-detect and validate:
        # - Footing dimensions (B, L, Df)
        # - Soil properties (γ, φ, c, E)
        # - Load values and units
        # - Missing parameter identification
```

**D. Clarification Request Generator**
```python
class ClarificationAgent:
    async def generate_clarification(self, question: str, missing_info: List[str]) -> ClarificationResponse:
        # Generate user-friendly clarification requests for:
        # - Vague questions ("What is bearing capacity?" → specify parameters)
        # - Missing parameters ("Calculate settlement" → need load, modulus)
        # - Ambiguous scope ("Tell me about CPT" → analysis methods, equipment, theory?)
```

#### Integration Strategy:
1. **Pre-processing Pipeline**: Insert before existing `agent.plan()`
2. **Question Enhancement**: Enrich original question with decomposed sub-questions
3. **Parameter Auto-detection**: Extract calculation parameters from natural language
4. **Intelligent Routing**: Route to appropriate tools based on classification

---

## Upgrade 2: Conversational Context Intelligence System

### 2.1 Context-Aware Agent Architecture
**Problem**: Current system treats each question independently, losing conversational continuity and requiring users to re-enter parameters.

**Solution**: Implement intelligent contextualization using conversation history and user intent synthesis, enabling natural multi-turn conversations.

#### Technical Implementation:
- **Location**: `app/services/agentic_workflow/context/`
- **Storage**: MongoDB conversation store with semantic indexing
- **Processing**: Multi-turn conversation understanding with LlamaIndex integration

#### Components:

**A. Conversation Memory Manager**
```python
class ConversationMemoryManager:
    async def store_conversation_context(self, user_id: str, session_id: str, 
                                       question: str, response: str, metadata: Dict):
        # Store with semantic embeddings for context retrieval
        
    async def retrieve_relevant_context(self, current_question: str, 
                                      session_history: List[Dict]) -> ContextualInfo:
        # Retrieve contextually relevant previous interactions
        
    async def identify_conversation_threads(self, session_id: str) -> List[ConversationThread]:
        # Group related questions into logical threads
```

**B. Intent Synthesis Agent** 
```python
class IntentSynthesisAgent:
    async def synthesize_intent(self, current_question: str, 
                              conversation_history: List[ChatMessage]) -> SynthesizedIntent:
        # Determines:
        # 1. Reference to previous calculations/results
        # 2. Follow-up question patterns  
        # 3. Parameter continuation (e.g., "Now with phi=30°")
        # 4. Comparative analysis requests
```

**C. Context-Enhanced Query Processor**
```python
class ContextualQueryProcessor:
    async def enhance_query_with_context(self, query: str, context: ConversationalContext) -> EnhancedQuery:
        # Enhances current query with:
        # - Previous calculation parameters
        # - Referenced values from conversation
        # - Implicit assumptions from context
        # - Multi-turn calculation workflows
```

#### Context-Aware Features:

**A. Parameter Inheritance**
- User: "Calculate bearing capacity for B=3m, gamma=20, Df=2m, phi=35°" 
- *Next*: "What about with phi=30°?" → Auto-inherit B=3m, gamma=20, Df=2m

**B. Result Reference**
- User: "Calculate settlement for load 1000kN, E=25000kPa"
- *Next*: "What's the factor of safety?" → Reference previous parameters and results

**C. Comparative Analysis**
- User: "Compare this with Meyerhof formula" → Auto-detect current calculation context

---

## Upgrade 3: Advanced Context Reranking System

### 3.1 Precision-Focused Reranking Pipeline
**Problem**: As the geotechnical knowledge base grows with extensive documentation (Settle3 manuals, CPT theory, liquefaction guides), the system retrieves too many chunks, diluting response quality and increasing token costs. Current vector search returns 20-50 chunks but only 3-5 are truly relevant.

**Solution**: Implement sophisticated reranking mechanisms to achieve high precision by selecting only the most relevant chunks from large document collections, focusing on semantic accuracy over quantity.

#### Technical Implementation:
- **Location**: `app/services/agentic_workflow/reranking/`
- **Models**: MS-Marco MiniLM-L6-v2 for semantic reranking
- **Architecture**: Two-stage pipeline with cross-encoder scoring and precision filtering

#### Components:

**A. Cross-Encoder Reranking Service**
```python
class GeotechContextReranker:
    def __init__(self):
        # Load MS-Marco MiniLM-L6-v2 model optimized for technical content
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L6-v2')
        self.geotechnical_terms = self._load_domain_vocabulary()
        
    async def rerank_contexts(self, query: str, contexts: List[Context], top_k: int = 3) -> List[RankedContext]:
        # 1. Score all query-context pairs using cross-encoder
        scores = []
        for context in contexts:
            # Enhance scoring for geotechnical-specific content
            base_score = self.reranker.predict(query, context.text)
            domain_boost = self._calculate_domain_relevance(query, context)
            final_score = base_score * (1 + domain_boost)
            scores.append((context, final_score))
        
        # 2. Apply aggressive precision filtering
        sorted_contexts = sorted(scores, key=lambda x: x[1], reverse=True)
        threshold = self._calculate_precision_threshold(sorted_contexts)
        
        # 3. Return only high-confidence, relevant contexts
        return [
            RankedContext(context=ctx, relevance_score=score)
            for ctx, score in sorted_contexts[:top_k] 
            if score > threshold
        ]
    
    def _calculate_domain_relevance(self, query: str, context: Context) -> float:
        # Boost score for geotechnical keywords, formulas, and calculations
        relevance_boost = 0.0
        
        # Keyword matching boost
        query_terms = set(query.lower().split())
        context_terms = set(context.text.lower().split())
        geo_keywords = query_terms.intersection(self.geotechnical_terms)
        if geo_keywords:
            relevance_boost += 0.2 * len(geo_keywords) / len(query_terms)
        
        # Formula/calculation boost
        if any(marker in context.text for marker in ['=', 'kPa', 'kN', 'φ', 'γ', 'Df']):
            relevance_boost += 0.15
            
        # Technical reference boost (CPT, Settle3, Terzaghi, etc.)
        technical_refs = ['CPT', 'Settle3', 'Terzaghi', 'bearing capacity', 'settlement']
        if any(ref.lower() in context.text.lower() for ref in technical_refs):
            relevance_boost += 0.1
            
        return min(relevance_boost, 0.5)  # Cap boost at 50%
```

**B. Precision Threshold Calculator**
```python
class PrecisionThresholdCalculator:
    async def calculate_optimal_threshold(self, ranked_contexts: List[Tuple], query_type: str) -> float:
        # Dynamically adjust thresholds for maximum precision
        scores = [score for _, score in ranked_contexts]
        
        if query_type == "calculation":
            # Higher threshold for calculations - need precise formulas
            return max(0.7, np.percentile(scores, 80)) if scores else 0.7
        elif query_type == "theory":
            # Moderate threshold for theoretical questions
            return max(0.5, np.percentile(scores, 70)) if scores else 0.5
        else:
            # Standard threshold for mixed queries
            return max(0.4, np.percentile(scores, 60)) if scores else 0.4
```

**C. Geotechnical Content Optimizer**
```python
class GeotechnicalContentOptimizer:
    async def optimize_for_domain(self, contexts: List[Context], query: str) -> List[OptimizedContext]:
        optimized_contexts = []
        
        for context in contexts:
            # 1. Extract and prioritize technical formulas
            formula_sections = self._extract_formulas(context.text)
            
            # 2. Preserve calculation examples and numerical values
            calculation_sections = self._extract_calculations(context.text)
            
            # 3. Maintain proper technical terminology and units
            technical_content = self._preserve_technical_terms(context.text)
            
            # 4. Remove redundant explanatory text that doesn't add value
            optimized_text = self._remove_redundancy(technical_content, query)
            
            optimized_contexts.append(OptimizedContext(
                original_context=context,
                optimized_text=optimized_text,
                formula_sections=formula_sections,
                calculation_examples=calculation_sections,
                priority_score=context.relevance_score
            ))
        
        return optimized_contexts
    
    def _extract_formulas(self, text: str) -> List[str]:
        # Extract mathematical formulas and equations
        formula_patterns = [
            r'q_ult\s*=\s*[^.]+',  # Bearing capacity formulas
            r'settlement\s*=\s*[^.]+',  # Settlement formulas  
            r'[A-Za-z_]+\s*=\s*[0-9.]+\s*\*\s*[A-Za-z_0-9\s\*\+\-\.]+',  # General formulas
        ]
        formulas = []
        for pattern in formula_patterns:
            formulas.extend(re.findall(pattern, text, re.IGNORECASE))
        return formulas
```

#### Integration with Existing RAG:
1. **Post-Retrieval Pipeline**: Insert after vector/keyword search, before synthesis
2. **Two-Stage Process**:
   ```
   Vector Search (20-50 chunks) → Cross-Encoder Reranking → Precision Filtering → Synthesis (3-5 high-quality chunks)
   ```

3. **Performance Monitoring**:
   - Track precision@3 and precision@5 metrics
   - Monitor token usage reduction from fewer, higher-quality chunks
   - Measure response accuracy improvement with focused context

---

## Upgrade 4: Enhanced Frontend UI/UX Experience

### 4.1 Modern Conversational Interface
**Problem**: Current frontend is basic and doesn't provide an engaging, professional user experience for geotechnical engineers.

**Solution**: Redesign frontend with modern UI/UX principles, specialized features for engineering workflows, and improved visual communication.

#### Technical Implementation:
- **Framework**: Upgrade to modern React with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Zustand for conversation and session management
- **Real-time**: WebSocket integration for streaming responses

#### UI/UX Components:

**A. Professional Engineering Interface**
```typescript
// Specialized input components for geotechnical parameters
interface ParameterInputPanel {
  soilProperties: SoilParameterInputs;  // φ, γ, c, E with unit selectors
  footingGeometry: FootingInputs;       // B, L, Df with visual diagrams
  loadConditions: LoadInputs;           // Loads, moments with direction indicators
  quickTemplates: CalculationTemplates; // Pre-filled common scenarios
}
```

**B. Interactive Calculation Visualization**
```typescript
interface CalculationDisplay {
  formulaRenderer: MathJaxComponent;     // Render mathematical equations
  parameterTable: ParameterSummaryTable; // Clear input/output organization
  diagramGenerator: GeotechnicalDiagrams; // Foundation sketches, soil profiles  
  resultsComparison: ComparisonCharts;   // Multiple calculation scenarios
}
```

**C. Intelligent Input Assistance**
```typescript
interface SmartInputFeatures {
  autoComplete: GeotechnicalTerms;       // CPT, Settle3, Terzaghi suggestions
  parameterValidation: RealTimeValidation; // Range checking, unit conversion
  exampleQuestions: ContextualSuggestions; // Based on current inputs
  calculationHistory: SessionPersistence;  // Previous calculations access
}
```

**D. Enhanced Response Presentation**
```typescript
interface ResponseInterface {
  streamingDisplay: TypewriterEffect;    // Real-time response streaming
  citationTooltips: SourcePreview;       // Hover for citation details
  calculationSteps: StepByStepBreakdown; // Detailed calculation process
  exportOptions: PDFReportGeneration;    // Professional calculation reports
}
```

#### Advanced Features:

**A. Conversation Management**
- **Session Organization**: Group related calculations into projects
- **History Search**: Find previous calculations with semantic search
- **Calculation Templates**: Save and reuse common parameter sets
- **Export Capabilities**: Generate professional calculation reports

**B. Visual Enhancements**  
- **Mathematical Rendering**: MathJax for proper equation display
- **Geotechnical Diagrams**: Auto-generate foundation and soil profile sketches
- **Results Visualization**: Charts for parameter sensitivity analysis
- **Progress Indicators**: Visual feedback for complex calculations

**C. Mobile-Responsive Design**
- **Adaptive Interface**: Optimized for tablets and mobile devices
- **Touch-Friendly Controls**: Large input areas for parameter entry
- **Offline Capability**: Cache recent calculations for field use
- **Quick Actions**: Swipe gestures for common operations

**D. Accessibility Features**
- **Screen Reader Support**: Full ARIA compliance for accessibility
- **Keyboard Navigation**: Complete keyboard-only operation
- **High Contrast Mode**: Enhanced visibility options
- **Multi-Language Support**: Vietnamese and English interfaces

---

## Upgrade 5: Cost/Latency Optimization & Reliability Systems

### 5.1 Intelligent Cost Management & Performance Optimization
**Problem**: As the system scales, LLM API costs and response latency become critical bottlenecks, especially for geotechnical calculations that may require multiple LLM calls for planning, synthesis, and context evaluation.

**Solution**: Implement comprehensive cost/latency optimization strategies with reliability patterns including intelligent caching, circuit breakers, and adaptive model selection.

#### Technical Implementation:
- **Location**: `app/core/optimization/` and `app/core/reliability/`
- **Architecture**: Multi-layer optimization with reliability patterns
- **Integration**: System-wide optimization layer with fallback mechanisms

#### Components:

**A. Multi-Layer LLM Caching System**
- **Redis Cache**: Fast in-memory caching for exact query matches
- **Semantic Similarity Cache**: Cache similar questions using embedding similarity
- **Partial Context Cache**: Reuse responses for overlapping context chunks
- **Cache Invalidation**: Smart cache expiry based on content freshness

**B. Circuit Breaker for LLM Services**
- **Failure Detection**: Monitor LLM service failures and response times
- **State Management**: CLOSED/OPEN/HALF_OPEN states for service health
- **Fallback Strategies**: Cached responses, lightweight local models, rule-based responses
- **Automatic Recovery**: Smart retry logic with exponential backoff

**C. Adaptive Model Selection for Cost Optimization**
- **Cost-Quality Analysis**: Dynamic model selection based on query complexity and budget
- **Model Performance Tracking**: Monitor latency, accuracy, and cost per model
- **Budget-Aware Routing**: Route simple queries to cheaper models, complex queries to premium models
- **Quality Thresholds**: Ensure minimum quality requirements for geotechnical calculations

**D. Response Latency Optimization**
- **Parallel Processing**: Concurrent execution of independent operations
- **Connection Pooling**: Reuse HTTP connections for multiple requests
- **Streaming Responses**: Real-time response streaming for better user experience
- **Request Batching**: Batch similar requests for efficiency

#### Integration Strategy:
1. **System-Wide Integration**: Apply optimization at every LLM interaction point
2. **Graceful Degradation**: Ensure system remains functional even when optimizations fail
3. **Monitoring & Adaptation**: Continuously optimize based on usage patterns and costs

#### Reliability Tactics Implemented:
- **Circuit Breaker Pattern**: Prevents cascade failures when LLM services are down
- **Multi-Layer Caching**: Redis + SQLite + Semantic similarity caching
- **Fallback Mechanisms**: Local models and rule-based responses
- **Health Monitoring**: Real-time service health checks and automatic failover
- **Load Balancing**: Distribute requests across multiple LLM providers

---

