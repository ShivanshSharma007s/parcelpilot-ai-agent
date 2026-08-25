# Architecture Note

## Overall Architecture
The application is a standard Flask web service serving a JSON API to a vanilla JavaScript frontend. 
The core backend relies on `groq` for LLM inference (tool-calling via Llama 3) and an SQLite database for structured data persistence and mock action states.

## Document Retrieval (RAG)
**Why BM25?**
The assessment explicitly requested not to use FAISS, sentence-transformers, or OpenAI embeddings to keep the footprint small, especially for deployments like PythonAnywhere. 
Therefore, lightweight lexical retrieval using `rank-bm25` (an implementation of BM25/TF-IDF) was selected. 
- The corpus of policies, SOPs, and agreements is highly structured around terminology (e.g., "SLA", "cancellation fee", "Northstar"). BM25 excels at keyword matching on structured terminology.
- The retrieval layer is modular (`tools/document_search.py`), making it trivial to swap out for vector embeddings later if needed.

## Agent Design & Tool Design
The agent uses a ReAct/Tool-calling pattern. It decides which tools to invoke based on the user's query.
1. `search_documents`: Queries the BM25 index. Returns document text and metadata (status, authority, customer).
2. `get_order`, `get_ticket`, `get_account`: Executes parameterized SQL queries. 
3. `prepare_action` & `confirm_and_execute_action`: Manages the state machine for state-changing operations.

## Authorization & Data Privacy
Access control is implemented inside the tool logic (`tools/authorization.py`), NOT just in the prompt. 
When the LLM calls `get_ticket` or `detect_proactive_issues`, the backend intercepts the current user's role. If a `support_agent` requests a ticket belonging to an account they aren't authorized for, the Python function returns an explicit error string to the LLM (e.g., "Unauthorized"). The LLM is then forced to inform the user of the denial.

## Proactive Issue Detection
A specialized Python tool (`tools/proactive.py`) queries SQLite to perform heuristic analysis on operational data.
- **SLA Risks**: Automatically calculates breached open tickets against the dataset reference time (`2026-08-16 11:00`), intelligently applying customer-specific SLAs vs generic policy.
- **Emerging Patterns & Multi-Customer**: Uses keyword clustering on ticket subjects to identify recurring issues (e.g., bulk upload failures) and flags whether they affect single or multiple accounts based on the user's authorized scope.
The tool returns a strict JSON structure that the LLM summarizes into natural language, explicitly framing them as signals rather than confirmed incidents to prevent unauthorized automatic actions.

## Source Precedence & Conflict Handling
The system prompt strictly instructs the agent on source hierarchy:
1. Customer-Specific Agreements override general policies.
2. Current Policies/SOPs.
3. Deprecated policies are explicitly marked in retrieval metadata and the LLM is instructed to ignore them as policy.
If sources conflict and cannot be confidently resolved using the hierarchy, the LLM is instructed to explain the conflict and suggest escalation.

## Action Confirmation Flow
A critical requirement was safe state-changing actions.
- **Phase 1**: LLM uses `prepare_action(type, target, reason)`. SQLite creates a record in `actions` with status `pending_confirmation`.
- **Phase 2**: LLM outputs a response to the user: "Proposed Action: ... Do you confirm?"
- **Phase 3**: User replies "Yes". The LLM recognizes the confirmation and uses `confirm_and_execute_action(action_id)`. SQLite updates the status to `executed`. 

## Technical Trade-offs
- **Lexical vs Semantic Search**: BM25 struggles with severe synonym variations (e.g., "money back" vs "refund"), whereas embeddings excel. However, BM25 guarantees zero external API latency, lower memory footprint, and exact keyword matches for IDs or specialized logistics terminology.
- **Vanilla JS vs React**: A simple HTML/JS frontend minimizes build steps and dependency bloat.
