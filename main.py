# backend/main.py
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from agent import agent  # Tu instancia de tiny-agent, con las tools definidas

app = FastAPI()

# Conexión a la base de datos (puedes mejorar con pool si hace falta)
def get_db():
    conn = sqlite3.connect("demo.db", check_same_thread=False)
    return conn

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    # Función generadora de tokens
    async def event_generator():
        # tiny-agent puede dar streaming si lo configuras así
        for token in agent.stream(message):
            yield {"event": "message", "data": token}
        # Finaliza el stream con un evento de cierre
        yield {"event": "end"}

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
