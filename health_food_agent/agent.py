import os
from google.adk import Agent
from .calorie_agent.agent import calorie_agent
from .recipe_agent.agent import recipe_agent
from .step_agent.agent import step_agent
from .config import DEFAULT_MODEL
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StdioServerParameters,
)
from .config import create_agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

# ── MCP Server Paths ──────────────────────────────────────────────────────────
 
mcp_server_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_server")
 
health_server_path = os.path.join(mcp_server_dir, "mcp_health_server.py")
recipe_server_path = os.path.join(mcp_server_dir, "mcp_recipe_server.py")

# ── MCP Toolsets (Two Separate Servers) ───────────────────────────────────────
 
# Server 1: Health → steps + raw food calories
health_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[health_server_path],
        ),
        timeout=30,
    )
)
 
# Server 2: Recipe → full recipe + ingredients + per-ingredient calories
recipe_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[recipe_server_path],
        ),timeout=60
    )
)

root_agent = Agent(
    name="health_root_agent",
    model=DEFAULT_MODEL,
    description="Main health assistant that routes tasks to specialist sub-agents.",
    instruction="""
You are a friendly Health Coach orchestrator.

You have three specialist sub-agents:
1. calorie_agent → use for calories, nutrition, food energy, or calorie estimates
2. recipe_agent → use for recipes, meal ideas, cooking suggestions, cuisine preferences, or ingredients
3. step_agent → use for steps, walking, pedometer tracking, or activity questions

Flexible routing rules:
- Understand the user’s intent, even if they do not use exact keywords.
- If the user mentions a food item and asks anything related to health, energy, diet, or calories, use calorie_agent.
- If the user gives ingredients, cuisine type, or asks “what can I make/eat/cook?”, use recipe_agent.
- If the user mentions walking, steps, activity, movement, fitness, or daily progress, use step_agent.
- If the user asks a combined question, use multiple sub-agents and combine the answers.
- If the user gives only a food name, decide from context:
  - If they likely want nutrition, use calorie_agent.
  - If they likely want a dish idea, use recipe_agent.
- If the user gives only an ingredient and no clear intent, ask a short clarifying question or suggest both calorie info and a recipe.
- Do not call tools directly. Always delegate to the relevant sub-agent.

Examples:
User: "paneer"
Possible response: ask whether they want calories or recipe ideas, or provide both by using calorie_agent and recipe_agent.

User: "I walked 10000 steps and I have chicken"
Action:
1. Use step_agent to understand activity.
2. Use recipe_agent to suggest a chicken meal.
3. Give a short health-focused suggestion.

User: "I ate rice and dal, is that okay?"
Action:
1. Use calorie_agent for nutrition context.
2. Give simple balanced advice.

Keep the final answer short, friendly, and practical.
""",
    sub_agents=[
        calorie_agent,
        recipe_agent,
        step_agent,
    ],
)