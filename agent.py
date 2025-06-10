import os
from huggingface_hub.inference._mcp.agent import Agent
from dotenv import load_dotenv

load_dotenv()

# Agente conectado a su propio servidor MCP expuesto en /mcp
agent = Agent(
    provider="local",
    model=f"{os.getenv('BACKEND_URL')}/mcp",
    stream=True,
)