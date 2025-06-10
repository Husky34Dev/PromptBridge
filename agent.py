# agent.py
import os
from dotenv import load_dotenv
from huggingface_hub.inference._mcp.agent import Agent

load_dotenv()

agent = Agent(
    provider="local",
    model=f"{os.getenv('BACKEND_URL')}/mcp"
)
