import os
import sys
import json
from groq import Groq
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.prompts import SYSTEM_PROMPT
from tools.document_search import search_documents
from tools.structured_data import get_order, get_account, get_ticket, get_customer_tickets
from tools.actions import prepare_action, confirm_and_execute_action
from tools.proactive import detect_proactive_issues

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_API")
client = Groq(api_key=api_key)

# Define tools for Groq
tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "detect_proactive_issues",
            "description": "Analyze operational data (tickets, orders) to automatically detect SLA risks, recurring ticket patterns, and multi-customer issues. Returns structured signals.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search current policies, SOPs, agreements, and deprecated policies based on a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query (e.g., 'cancellation fee', 'Northstar SLA')."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Look up an order by ID from the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "The order ID, e.g., 'ORD-1001'."}
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_account",
            "description": "Look up an account by ID from the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "The account ID, e.g., 'A101'."}
                },
                "required": ["account_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ticket",
            "description": "Look up a support ticket by ID from the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "The ticket ID, e.g., 'T-101'."}
                },
                "required": ["ticket_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_tickets",
            "description": "Look up all tickets for a specific account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "The account ID."}
                },
                "required": ["account_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "prepare_action",
            "description": "Prepare a state-changing action (like create_escalation or update_ticket) for user confirmation. Returns a pending action_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_type": {"type": "string", "description": "Type of action: 'create_escalation', 'update_ticket', or 'create_follow_up_task'."},
                    "target": {"type": "string", "description": "Target ID, e.g., order ID or ticket ID."},
                    "reason": {"type": "string", "description": "Why this action is being taken."}
                },
                "required": ["action_type", "target", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "confirm_and_execute_action",
            "description": "Execute a prepared action after explicit user confirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_id": {"type": "string", "description": "The pending action_id returned by prepare_action."}
                },
                "required": ["action_id"]
            }
        }
    }
]

def execute_tool(tool_call, current_user):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    
    if name == "search_documents":
        return search_documents(args["query"])
    elif name == "get_order":
        return get_order(args["order_id"], current_user)
    elif name == "get_account":
        return get_account(args["account_id"], current_user)
    elif name == "get_ticket":
        return get_ticket(args["ticket_id"], current_user)
    elif name == "get_customer_tickets":
        return get_customer_tickets(args["account_id"], current_user)
    elif name == "prepare_action":
        return prepare_action(args["action_type"], args["target"], args["reason"], current_user)
    elif name == "confirm_and_execute_action":
        return confirm_and_execute_action(args["action_id"], current_user)
    elif name == "detect_proactive_issues":
        return detect_proactive_issues(current_user)
    else:
        return {"error": f"Unknown tool {name}"}

def run_agent(messages, current_user):
    # Ensure system prompt is present
    if not any(m.get("role") == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        
    tool_activity = []
        
    while True:
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                tools=tools_definition,
                tool_choice="auto",
                max_tokens=2048,
            )
        except Exception as e:
            return {"error": str(e), "messages": messages, "tool_activity": tool_activity}
            
        message = response.choices[0].message
        
        if not message.tool_calls:
            # Agent finished reasoning and produced a response
            messages.append({"role": "assistant", "content": message.content})
            return {"response": message.content, "messages": messages, "tool_activity": tool_activity}
            
        # Add the assistant's tool call message to history
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in message.tool_calls
            ]
        })
        
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            tool_activity.append(f"Used tool: {name}")
            
            result = execute_tool(tool_call, current_user)
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": name,
                "content": json.dumps(result)
            })
