import sqlite3
import uuid
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_db_connection

def prepare_action(action_type, target, reason, current_user):
    """
    Creates a pending action in the database and returns the action_id.
    This does NOT execute the action. It requires user confirmation.
    """
    action_id = "ACT-" + str(uuid.uuid4())[:8].upper()
    created_at = datetime.now().isoformat()
    
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO actions (action_id, actor, created_at, action_type, target, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (action_id, current_user, created_at, action_type, target, reason, 'pending_confirmation'))
    conn.commit()
    conn.close()
    
    return {
        "status": "pending_confirmation",
        "action_id": action_id,
        "action_type": action_type,
        "target": target,
        "reason": reason,
        "message": "Action prepared. Await explicit confirmation from the user before proceeding."
    }

def confirm_and_execute_action(action_id, current_user):
    """
    Executes a pending action after explicit confirmation.
    """
    conn = get_db_connection()
    action = conn.execute("SELECT * FROM actions WHERE action_id = ?", (action_id,)).fetchone()
    
    if not action:
        conn.close()
        return {"error": f"Action {action_id} not found."}
        
    if action['status'] != 'pending_confirmation':
        conn.close()
        return {"error": f"Action {action_id} cannot be executed. Current status is '{action['status']}'."}
        
    # Simulate execution of the action (e.g. creating an escalation ticket, etc.)
    # In a real app, this would integrate with JIRA, Salesforce, etc.
    
    conn.execute("UPDATE actions SET status = 'executed' WHERE action_id = ?", (action_id,))
    conn.commit()
    conn.close()
    
    return {
        "status": "executed",
        "action_id": action_id,
        "message": f"Action {action_id} ({action['action_type']}) has been successfully confirmed and executed."
    }
