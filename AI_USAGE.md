# AI Usage Note

In accordance with the assessment instructions to "honestly describe AI coding tools used," the following outlines the AI assistance leveraged to build this project:

- **AI Pair Programmer:** The entire architecture, logic, and testing suite was built using an advanced agentic coding assistant (Antigravity/DeepMind agent) acting as a senior Python full-stack engineer.
- **Workflow:** I prompted the agent with the precise requirements from the `ParcelPilot_Assessment_Data` pack. The agent independently scaffolded the Flask application, implemented the ETL ingestion scripts, constructed the `rank-bm25` lexical search, and wrote the system prompts for the Groq LLM integration.
- **Iterative Refinement:** After initial implementations, I directed the AI to debug issues, such as:
    - Replacing the buggy `PyMuPDF` library with `pypdf` for Windows compatibility.
    - Resolving a Groq TPM rate limit by optimizing the chat history token accumulation.
    - Tuning the `agent/prompts.py` logic to eliminate double-confirmation loops.
    - Enforcing strict source precedence (Customer Agreement > General Policy) to fix SLA calculation bugs.
- **Testing:** The AI assistant authored the `run_e2e_tests.py` script and the unit tests, and I commanded it to run them autonomously to verify the assessment requirements.
- **Manual Adjustments:** I reviewed the LLM's architecture choices (such as using SQLite instead of FAISS to remain lightweight and PythonAnywhere-compatible) and approved them. I also provided environment variables (like `GROQ_API`) directly to the environment.
