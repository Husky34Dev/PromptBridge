from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Union
import json
import os
import sys
import uvicorn

# Agregar el directorio raíz al path para los imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.agent.agent import responder

app = FastAPI(title="Agente Cliente", description="Asistente virtual personalizado")

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="web/static"), name="static")

class ChatRequest(BaseModel):
    message: str
    user_role: str = "cliente"
    mode: str = "rigido"

class ChatResponse(BaseModel):
    type: str
    response: Optional[str] = None
    agent: Optional[str] = None
    results: Optional[List] = None
    error: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Sirve la interfaz web principal"""
    try:
        with open("web/static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: Frontend no encontrado</h1>", status_code=404)

@app.get("/api/branding")
async def get_branding():
    """Devuelve la configuración de branding del cliente"""
    try:
        with open("client_config/branding.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "company_name": "Asistente Virtual",
            "primary_color": "#2563eb",
            "secondary_color": "#64748b"
        }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Endpoint principal del chat - usa tu lógica actual"""
    if not request.message:
        raise HTTPException(status_code=400, detail="Mensaje requerido")
    try:
        response = responder(request.message, request.user_role, request.mode)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check para monitoring"""
    return {"status": "ok", "service": "agente-cliente"}

@app.get("/api/config")
async def get_config():
    """Endpoint para obtener configuración (solo para debug)"""
    try:
        with open("client_config/agents_config.json", "r", encoding="utf-8") as f:
            agents = json.load(f)
        return {
            "agents_count": len(agents),
            "available_agents": [a.get("name", "unknown") for a in agents]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Iniciando Agente Cliente...")
    print("📱 Interfaz web: http://localhost:8080")
    print("🔧 API: http://localhost:8080/docs")
    print("❤️  Health check: http://localhost:8080/api/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
