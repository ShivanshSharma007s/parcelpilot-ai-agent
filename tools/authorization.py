# tools/authorization.py

class AuthorizationManager:
    def __init__(self, current_user):
        """
        current_user can be:
        - "support_agent_1" (Allowed Accounts: A101, A102)
        - "support_manager_1" (Allowed Accounts: ALL)
        - "operations_admin" (Allowed Accounts: ALL)
        """
        self.current_user = current_user
        
        self.role_map = {
            "support_agent_1": {
                "role": "support_agent",
                "allowed_accounts": ["ACCT-001", "ACCT-002"]
            },
            "support_manager_1": {
                "role": "support_manager",
                "allowed_accounts": "ALL"
            },
            "operations_admin": {
                "role": "operations_admin",
                "allowed_accounts": "ALL"
            }
        }
        
    def get_user_role(self):
        user_info = self.role_map.get(self.current_user)
        return user_info["role"] if user_info else "unknown"

    def can_access_account(self, account_id):
        user_info = self.role_map.get(self.current_user)
        if not user_info:
            return False
            
        if user_info["allowed_accounts"] == "ALL":
            return True
            
        return account_id in user_info["allowed_accounts"]
