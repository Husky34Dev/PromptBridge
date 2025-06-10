import os
import sqlite3
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
from agent import agent

load_dotenv()

app = FastAPI()

# Configurar CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tool real para exponer a MCP (consulta facturas)
@app.get("/invoices/{dni}")
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

# Montar servidor MCP en /mcp
tools = FastApiMCP(app)
tools.mount()

# Endpoint de chat
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    async def event_generator():
        for token in agent.stream(message):
            yield {"event": "message", "data": token}
        yield {"event": "end"}

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))