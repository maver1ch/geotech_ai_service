**Build a small service** that answers technical questions by 

(a) retrieving from a tiny local knowledge base and/or 

(b) calling a calculation tool when appropriate. Expose a simple API or DLL. Keep scope tight

Preferred language to build: Python, or REACT.js or similar. 

Build a chatbot with simple UI that is easy to run and test the features (i.e. a clear set up instruction with requirements and env file that just needs API keys – after this it should run without much issues) 

**Requirements**

1. **API (FastAPI or similar)**

   * POST /ask → {question, context?} → {answer, citations\[\], trace\_id}

   * GET /health → {status:"ok"}

   * GET /metrics → basic counters (requests, tool\_calls, total number of questions asked for the session)

2. **Agent with tool use**

   * Must decide when to **retrieve** vs **call a tool** (or both).

   * Provide **Two tools**:

     * **General track:** A settlement calculator for immediate settlement calculation: settlement \= load / Young’s modulus.

     * **Geotech track:** implement **Terzaghi bearing capacity analysis**   
       **(cohesionless)**: A simple lookup in the table of values below  
       **Parameters:**  
        ![A table of numbers with numbersAI-generated content may be incorrect.][image1]  
       equation for bearing capacity (simplified):  
       **Inputs:**   
       B \= diameter of footing  
       gamma, γ \= unit weight  
       Df \= depth of footing

       φ \= Friction Angle (to look up N value)

       **Equation:**  
       q\_ult \= γ\*Df\*Nq \+ 0.5\*γ\*B\*Nr

   * Return a **structured trace** of steps taken (retrieval → tool → final).

3. **Retrieval (RAG)**

   * Local/vector store of **5–8 short markdown notes** (you write them; \~200–400 words each). Topics that needs to be in the system are:

     * [CPT analysis for settle3](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https:/static.rocscience.cloud/assets/verification-and-theory/Settle3/Settle3-CPT-Theory-Manual.pdf) in rocscience website.

     * [Liquefaction analysis for settle3](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https:/static.rocscience.cloud/assets/verification-and-theory/Settle3/Settle3-Liquefaction-Theory-Manual.pdf) in Rocscience website.

     * [Settle3 help page](https://www.rocscience.com/help/settle3/documentation).

   * Implement chunking, embeddings, top-k. Include **source file names** in citations.

   * Provide a tiny **offline evaluation set** (5–8 Q/A pairs) and a script that prints **hit@k** (did the correct source appear in top-k?) and a naive answer match (e.g., keyword overlap). Show the score of the confidence score of the context pulled. Main sources should be from **Rocscience website \+ documentation for CPT and liquefaction analysis listed** and relevant to geotechnical engineering field.

4. **Reliability & safety**

   * Timeouts \+ single retry on external/model calls (mock if needed).

   * Input sanitization (reject obviously malicious tool args), max tokens/characters.

   * Never log secrets; include .env.example.

5. **Observability**

   * **Logs** with trace\_id per request and per step (retrieve, tool\_call, answer), plus ms durations.

   * GET /metrics returns simple aggregates from in-process counters.

6. **Packaging & docs**

   * Dockerfile (app runs on docker run \-p 8000:8000 …).

   * README.md with: how to run, example curl calls, design choices, and tradeoffs.

   * **Tests**: at least 2 unit tests (one for the tool, one for the retriever).

**Constraints & Notes**

* You may use any open LLM API **or** mock LLM calls (return deterministic strings) if you prefer fully-local. Document your choice.

* Use any embedding lib/store; local file-based is fine.

* Keep the UI to **command-line/cURL** (no frontend required, but would be preferred).

**What to submit**

* Link to repo (or zip), plus a **1–2 page “Engineering Notes”** covering:

  * Architecture sketch and control flow

  * Retrieval choices (chunk size, k) and **eval results**

  * Safety/guardrails implemented

  * If geotech: your assumptions for Nq, Nγ or reference you used.

---

**Rubric (100 pts)**

* **Correctness & API behavior (20)** – endpoints work; sensible responses; errors handled.

* **Agent/tool orchestration (20)** – correct decision to retrieve vs compute; clear step trace.

* **Retrieval quality (15)** – citations, top-k tuning, eval script \+ numbers reported.

* **Reliability (10)** – timeouts, retries, graceful failures, idempotent behavior.

* **Observability (10)** – structured logs, trace ids, basic metrics.

* **Security/Secrets (5)** – .env.example, no secrets in code, minimal input validation.

* **Tests (5)** – unit tests pass and are meaningful.

* **Docs (10)** – crisp README, setup, curl examples, assumptions.

* **Polish (5)** – Docker works; repo tidy; consistent code style.

**Senior lens:** same deliverable, but we expect a brief design note on eval strategy (e.g., how you’d add a reranker or auto-evals), cost/latency tradeoffs, and a small reliability tactic (e.g., caching, circuit breaker). **Optional extension:** package CPT-analysis correlations (From [Settle3 CPT analysis documentation](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https:/static.rocscience.cloud/assets/verification-and-theory/Settle3/Settle3-CPT-Theory-Manual.pdf)) as a standalone tool/service and have the agent invoke it to compute outputs. This showcases complex tool-calling and systems integration.