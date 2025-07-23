import os
from dotenv import load_dotenv
from huggingface_hub.inference._mcp.agent import Agent

load_dotenv()
agent = Agent(
    provider="local",
    model=os.getenv("MCP_MODEL"),
    servers=[{"type": "http", "url": os.getenv("MCP_SERVER_URL")}]
)
