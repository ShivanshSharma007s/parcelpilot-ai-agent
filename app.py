from flask import Flask, request, jsonify, render_template
import os
import sys

# Ensure proper paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.agent import run_agent

app = Flask(__name__)

# Basic in-memory storage for active sessions' message history
session_histories = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    current_user = data.get("current_user", "support_agent_1")
    session_id = data.get("session_id", "default")
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
        
    if session_id not in session_histories:
        session_histories[session_id] = []
        
    # Append the new user message
    session_histories[session_id].append({"role": "user", "content": user_message})
    
    # Keep only the last 6 interactions (user/assistant) to avoid TPM limits
    chat_history = session_histories[session_id][-6:]
    
    # Create a fresh message list for the agent run (History only, run_agent will prepend System)
    messages_for_agent = list(chat_history)
    
    # Run the agent (it will add tool calls to messages_for_agent internally for this turn only)
    result = run_agent(messages_for_agent, current_user)
    
    if "error" in result:
        # If it failed, we remove the user message so they can try again
        session_histories[session_id].pop()
        return jsonify({"error": result["error"], "tool_activity": result.get("tool_activity", [])}), 500
        
    # Append ONLY the final assistant response to the persistent history
    session_histories[session_id].append({"role": "assistant", "content": result["response"]})
    
    return jsonify({
        "response": result["response"],
        "tool_activity": result["tool_activity"]
    })

@app.route("/clear", methods=["POST"])
def clear_chat():
    data = request.json
    session_id = data.get("session_id", "default")
    if session_id in session_histories:
        session_histories[session_id] = []
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
