import os, sqlite3
from fastapi import FastAPI, Request, Response # Added Response import
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
from agent import agent

load_dotenv()
app = FastAPI()

# IMPORTANT: Ensure this is the first middleware for CORS to work correctly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://demo-chatbot-frontend.onrender.com"],
    allow_methods=["*"], # Allow all methods including OPTIONS
    allow_headers=["*"], # Allow all headers including Content-Type for JSON
    allow_credentials=True # Added: Often needed for more complex scenarios with headers/cookies
)

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

# Explicit OPTIONS route for /chat
# This helps ensure the OPTIONS preflight request is handled with a 200 OK
# before CORSMiddleware injects the necessary CORS headers.
@app.options("/chat")
async def options_chat():
    return Response(status_code=200) # CORSMiddleware will add the Access-Control-Allow-Origin etc. headers

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
