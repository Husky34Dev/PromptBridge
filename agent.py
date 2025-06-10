import sqlite3
import os
from huggingface_hub.inference._mcp.agent import Agent, Tool
from dotenv import load_dotenv

# Carga variables de entorno
load_dotenv()

# Tool: consulta facturas por DNI
def get_invoices_by_dni(dni: str):
    conn = sqlite3.connect("demo.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, fecha, importe, estado FROM facturas WHERE dni_abonado = ?", (dni,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "fecha": r[1], "importe": r[2], "estado": r[3]}
        for r in rows
    ]

# Definición de herramientas para el agente MCP local
tools = [
    Tool(
        name="get_invoices_by_dni",
        func=get_invoices_by_dni,
        description="Consulta facturas de un abonado por su DNI (id, fecha, importe, estado)."
    ),
]

# Instancia del agente MCP que se conecta al LLM remoto
agent = Agent(
    provider=os.getenv("MCP_PROVIDER"),
    model=os.getenv("MCP_MODEL"),
    servers=[{
        "type": "stdio",
        "config": {
            "command": "npx",
            "args": ["mcp-remote", os.getenv("MCP_SERVER_URL")]
        }
    }],
    tools=tools,
    stream=True,
    temperature=0.0,
    max_tokens=512,
)