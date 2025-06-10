import os, sqlite3
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
from agent import agent

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_methods=["*"], allow_headers=["*"])

print(os.getenv("FRONTEND_URL"))  
# Tool expuesta
@app.get("/invoices/{dni}")
def get_invoices(dni: str):
    conn = sqlite3.connect("demo.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("SELECT id, fecha, importe, estado FROM facturas WHERE dni_abonado = ?", (dni,))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0],"fecha": r[1],"importe": r[2],"estado": r[3]} for r in rows]

# Montar MCP
FastApiMCP(app).mount()

# SSE chat
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    msg = data.get("message", "")
    async def gen():
        for token in agent.stream(msg):
            yield {"event": "message", "data": token}
        yield {"event": "end"}
    return EventSourceResponse(gen())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
