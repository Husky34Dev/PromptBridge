import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
from agent import agent, get_invoices_by_dni

# Carga variables de entorno
o = load_dotenv()

app = FastAPI()

# Configurar CORS para permitir llamadas solo desde el frontend
domains = [os.getenv("FRONTEND_URL")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=domains,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar el servidor MCP que expone tus endpoints como tools
mcp = FastApiMCP(app)
# Por defecto monta en "/mcp"
mcp.mount()

# Endpoint REST que también puedes llamar directamente o desde el agente
@app.get("/invoices/{dni}")
def read_invoices(dni: str):
    return get_invoices_by_dni(dni)

# Endpoint de chat con streaming SSE que invoca al agente MCP
@app.post("/chat")
async def chat(request: Request):
    payload = await request.json()
    message = payload.get("message", "")

    async def event_generator():
        for token in agent.stream(message):
            yield {"event": "message", "data": token}
        yield {"event": "end"}

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
    )