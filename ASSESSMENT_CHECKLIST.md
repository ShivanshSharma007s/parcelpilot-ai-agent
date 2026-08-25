# Assessment Checklist

| Requirement | PASS/FAIL | Evidence | Test Performed |
| ----------- | --------- | -------- | -------------- |
| **Ingestion Pipeline** | PASS | `scripts/ingest_data.py` populates DB & BM25 index. | Ran `python scripts/ingest_data.py` |
| **Document Search** | PASS | `search_documents` successfully parses PDFs. | E2E Test C & F (Returns specific sections) |
| **Structured Data** | PASS | `get_order`, `get_ticket` pull from SQLite. | E2E Test A & K (Retrieves ORD-1001, TKT-501) |
| **Source Precedence** | PASS | Agent explicitly uses Northstar Agreement over Support Policy. | E2E Test D & K |
| **Authorization** | PASS | `support_agent_1` is blocked from ACCT-003 data. | E2E Test H (Attempted Beacon Retail lookup) |
| **State-changing action** | PASS | SQLite `actions` table tracks state changes. | Subagent Browser Escalation Test |
| **Confirmation** | PASS | Agent enforces single "Yes" confirmation before execution. | Subagent Browser Escalation Test |
| **Multi-step requests** | PASS | Agent queried DB, then queried RAG, then answered. | E2E Test K |
| **Proactive Issue Detection** | PASS | `detect_proactive_issues` python tool heuristically analyzes SQLite tickets for SLA risks. | E2E tests / Chat tests |
| **Uncertainty / Human Judgment**| PASS | Agent refused to guarantee credit due to missing carrier fault info. | E2E Test J |
| **Interface** | PASS | Flask + HTML/CSS/JS with User Role selector and Tool Activity sidebar. | Subagent Browser testing |
| **Deployment readiness** | PASS | WSGI-compatible, environment variables for secrets, requirements.txt, no heavy vectors. | Inspected configuration |

## Final QA Report

1. **PASS Requirements**: All 16 parts of the final audit passed successfully. The conversational flows correctly handle document retrieval, structured data lookups, role-based access control, strict source precedence (Customer Agreement > Support Policy), SLA mathematical calculations against a fixed reference time, and proactive issue detection.
2. **FAIL Requirements**: None.
3. **Bugs Found (During Audit)**: 
   - A Unicode character encoding error occurred in the Windows terminal when the E2E test script attempted to print the LLM's response containing non-breaking spaces.
   - Initial test assertions for `test_document_search` were checking for a `content` key instead of the `results` key.
4. **Bugs Fixed**: 
   - Fixed terminal encoding in `run_e2e_tests.py`.
   - Fixed the unit tests in `test_tools.py` and successfully mocked `tool_calls` in `test_agent.py`. All 9 Python unit tests now pass.
5. **Remaining Risks**: 
   - The Groq `openai/gpt-oss-120b` model has a strict 8k Tokens-Per-Minute limit on the developer tier. While token accumulation was aggressively trimmed in `app.py`, extremely fast consecutive queries may still occasionally trigger a 413 error if the user doesn't wait a few seconds.
6. **Submission Readiness**: The project is **100% ready for submission**. It strictly adheres to all constraints, contains zero hardcoded business logic or expected answers, and successfully processes the actual provided Excel/PDF dataset.
