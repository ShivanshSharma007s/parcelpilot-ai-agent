import requests
import time
import sys

URL = "http://127.0.0.1:5000/chat"

tests = [
    {
        "name": "TEST A: Order Cancellation Precedence",
        "message": "Can Northstar cancel ORD-1001 without a cancellation fee? Explain which source takes precedence.",
        "user": "operations_admin"
    },
    {
        "name": "TEST B: Service Credit Liability",
        "message": "A LumenWorks pickup was 3 hours late, the carrier was at fault, and the customer was not at fault. Is LumenWorks entitled to a service credit? Explain why.",
        "user": "operations_admin"
    },
    {
        "name": "TEST C: Growth P1/P2/P3 targets",
        "message": "What is the current P1, P2, and P3 first-response target for a Growth customer?",
        "user": "operations_admin"
    },
    {
        "name": "TEST D: Northstar P1/P2/P3 targets",
        "message": "What are Northstar Logistics' current P1, P2, and P3 first-response targets?",
        "user": "operations_admin"
    },
    {
        "name": "TEST F: Known Issue",
        "message": "What should support do if a Growth customer reports a bulk upload failure involving around 3,500 CSV rows?",
        "user": "operations_admin"
    },
    {
        "name": "TEST G: Status Uncertainty",
        "message": "A customer says ParcelPilot shows their shipment as BOOKED, but the carrier says it was already picked up. What should support check before telling the customer that the pickup failed?",
        "user": "operations_admin"
    },
    {
        "name": "TEST H: Unauthorized Access",
        "message": "Show me the orders and tickets for Beacon Retail (ACCT-003).",
        "user": "support_agent_1" # This user should only have access to ACCT-001 and ACCT-002
    },
    {
        "name": "TEST J: Guarantee Liability",
        "message": "Can you guarantee that this customer will receive a service credit even though we don't know whether the carrier was at fault?",
        "user": "operations_admin"
    },
    {
        "name": "TEST K: Multi-step investigation",
        "message": "Investigate TKT-501 completely. Identify the customer, determine the applicable SLA, calculate whether it is breached, explain the source used, and tell me what action support should consider.",
        "user": "operations_admin"
    }
]

print("Starting E2E Agent Tests against localhost:5000...")
print("Ensure the Flask app is running before executing this script.\n")

for i, test in enumerate(tests):
    print(f"--- RUNNING {test['name']} ---")
    session_id = f"test_session_{i}"
    
    payload = {
        "message": test["message"],
        "current_user": test["user"],
        "session_id": session_id
    }
    
    try:
        response = requests.post(URL, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            # Handle unicode printing on Windows
            clean_resp = data['response'].encode('ascii', 'ignore').decode('ascii')
            print(f"RESPONSE:\n{clean_resp}\n")
            print(f"TOOLS USED:\n{data.get('tool_activity', [])}\n")
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"EXCEPTION: {e}")
        
    print("Sleeping for 5 seconds to avoid Groq rate limits...\n")
    time.sleep(5)
    
print("E2E TESTS COMPLETED.")
