import sqlite3
from tiny_agent import Agent, Tool

# Tool para obtener facturas por DNI
# Devuelve una lista de dicts con id, fecha, importe y estado

def get_invoices_by_dni(dni: str):
    conn = sqlite3.connect("demo.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, fecha, importe, estado FROM facturas WHERE dni_abonado = ?",
        (dni,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "fecha": r[1], "importe": r[2], "estado": r[3]}
        for r in rows
    ]

# Lista de tools disponibles
tools = [
    Tool(
        name="get_invoices_by_dni",
        func=get_invoices_by_dni,
        description="Obtiene las facturas del abonado dado su DNI, devolviendo id, fecha, importe y estado."
    ),
    # puedes añadir más tools aquí
]

# Configuración del agente
agent = Agent(
    llm="openai/gpt-3.5-turbo",  # o un modelo local si prefieres
    tools=tools,
    stream=True,                    # habilita streaming de tokens
    temperature=0.0,
    max_tokens=512,
)