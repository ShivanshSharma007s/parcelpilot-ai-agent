import unittest
import os
import sys
import json
from unittest.mock import Mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.agent import execute_tool

class TestAgent(unittest.TestCase):
    
    def _create_mock_tool(self, name, args):
        mock_func = Mock()
        mock_func.name = name
        mock_func.arguments = json.dumps(args)
        mock_tool = Mock()
        mock_tool.function = mock_func
        return mock_tool

    def test_execute_tool_unknown(self):
        tool = self._create_mock_tool("unknown_tool", {})
        res = execute_tool(tool, "support_agent_1")
        self.assertIn("error", res)
        self.assertIn("Unknown tool", res["error"])
        
    def test_execute_tool_get_order(self):
        tool = self._create_mock_tool("get_order", {"order_id": "ORD-1001"})
        res = execute_tool(tool, "operations_admin")
        self.assertIn("order", res)
        
    def test_execute_tool_detect_proactive(self):
        tool = self._create_mock_tool("detect_proactive_issues", {})
        res = execute_tool(tool, "operations_admin")
        self.assertIn("issues", res)

if __name__ == "__main__":
    unittest.main()
