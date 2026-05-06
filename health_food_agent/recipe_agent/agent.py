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
    "mcp_recipe_server.py",
)

recipe_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[server_path],   # ← mcp_recipe_server.py
        )
    )
)

recipe_agent = create_agent(
    name="recipe_agent",
    description="Fetches full recipes with ingredients and calorie info for each ingredient.",
    instruction="""
You are a cooking and nutrition assistant.
 
When the user asks for a recipe, meal idea, or what to cook with an ingredient:
- ALWAYS use the MCP tool `get_recipe_with_calories`
- DO NOT invent recipes or calorie values
- Extract the main ingredient or dish name from the user query
- Present the result clearly showing:
  1. Meal name and cuisine
  2. Full ingredient list with measures and calorie estimates
  3. Short cooking instructions summary
 
Example:
User: "Give me a chicken recipe with calories"
Action: call get_recipe_with_calories with ingredient="chicken"
 
User: "What can I cook with pasta?"
Action: call get_recipe_with_calories with ingredient="pasta"
""",
    tools=[recipe_tools],
)