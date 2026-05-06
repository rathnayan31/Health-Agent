import os
from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StdioServerParameters,
)
from ..config import create_agent

server_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "mcp_server",
    "mcp_health_server.py",
)

health_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[server_path],
        )
    )
)

step_agent = create_agent(
    name="step_agent",
    description="Tracks daily step count — add, get, or reset steps.",
    instruction="""
You are a fitness tracker.
 
Use MCP tool `manage_steps` when the user mentions walking, steps, pedometer, or movement:
- Adding steps  → manage_steps(action="add", value=<number>)
- Checking total → manage_steps(action="get")
- Resetting      → manage_steps(action="reset")
- DO NOT invent step totals yourself.
 
Examples:
User: "I walked 5000 steps"  → manage_steps(action="add", value=5000)
User: "How many steps today?" → manage_steps(action="get")
""",
    tools=[health_tools],
)