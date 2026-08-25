import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_db_connection
from tools.authorization import AuthorizationManager

def get_order(order_id, current_user):
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    
    if not order:
        return {"error": f"Order {order_id} not found."}
        
    order_dict = dict(order)
    
    auth = AuthorizationManager(current_user)
    if not auth.can_access_account(order_dict['account_id']):
        return {"error": f"Unauthorized. You do not have permission to access records for account {order_dict['account_id']}."}
        
    return {"order": order_dict}

def get_account(account_id, current_user):
    auth = AuthorizationManager(current_user)
    if not auth.can_access_account(account_id):
        return {"error": f"Unauthorized. You do not have permission to access account {account_id}."}

    conn = get_db_connection()
    account = conn.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,)).fetchone()
    conn.close()
    
    if not account:
        return {"error": f"Account {account_id} not found."}
        
    return {"account": dict(account)}

def get_ticket(ticket_id, current_user):
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
    conn.close()
    
    if not ticket:
        return {"error": f"Ticket {ticket_id} not found."}
        
    ticket_dict = dict(ticket)
    
    auth = AuthorizationManager(current_user)
    if not auth.can_access_account(ticket_dict['account_id']):
        return {"error": f"Unauthorized. You do not have permission to access records for account {ticket_dict['account_id']}."}
        
    return {"ticket": ticket_dict}

def get_customer_tickets(account_id, current_user):
    auth = AuthorizationManager(current_user)
    if not auth.can_access_account(account_id):
        return {"error": f"Unauthorized. You do not have permission to access account {account_id}."}
        
    conn = get_db_connection()
    tickets = conn.execute("SELECT * FROM tickets WHERE account_id = ?", (account_id,)).fetchall()
    conn.close()
    
    if not tickets:
        return {"message": f"No tickets found for account {account_id}."}
        
    return {"tickets": [dict(t) for t in tickets]}
