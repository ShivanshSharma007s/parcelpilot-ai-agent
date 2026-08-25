# Product Note

## Additional Client Problem Addressed
For this phase, I prioritized robust backend architecture, action confirmation safety, and role-based access control. 
I have now fully implemented **Proactive Issue Detection**. This allows agents to query the system for urgent or unusual issues via natural language. The backend heuristic analysis identifies SLA risks, emerging patterns (like bulk upload failures), and multi-customer signals based on the user's exact authorization scope, presenting them as actionable signals for review.

## Intentionally Left Out
- Deep integration with real ticket platforms (Zendesk, Salesforce). We use SQLite `actions` as a mock.
- Full JWT authentication. We use a mock dropdown selector in the UI for speed of evaluation.

## Primary Product Metric
**Metric**: **Correct Resolution Rate (CRR)**
*Justification*: In internal operations and support, efficiency matters, but accuracy is paramount. A chatbot that resolves issues quickly but hallucinates policies or applies a deprecated SLA will cause severe financial or contractual harm to ParcelPilot. CRR tracks the percentage of agent-provided answers or actions that correctly adhere to the source hierarchy and authorization rules without requiring human correction.
