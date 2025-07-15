import logging
import os
import json
from core.config.config import GROQ_API_KEY, GROQ_MODEL, ROUTING_MODEL, SERVER_URL
from core.agent.tools.entidades import extract_entities
from core.agent.tools.context_manager import ContextManager
from core.agent.agents.agent_base import AgentBase
from core.agent.orchestrator import Orchestrator

# Asegurar que la carpeta logs existe
log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "agent_debug.log")
logging.basicConfig(filename=log_path, level=logging.DEBUG)

# Cargar tools desde archivo local - AHORA DESDE client_config
with open("client_config/tools_schema.json", "r", encoding="utf-8") as f:
    tools = json.load(f)

# Inicializar el ContextManager con los paths de los JSON - AHORA DESDE client_config
patterns_path = "client_config/entity_patterns.json"
reference_map_path = "client_config/reference_map.json"
context_manager = ContextManager(patterns_path, reference_map_path)

# Cargar agentes dinámicamente desde client_config/agents_config.json
def load_agents_from_config(config_path):
    """
    Carga la configuración de agentes desde un archivo JSON y crea instancias de AgentBase.
    
    Args:
        config_path (str): Ruta al archivo de configuración de agentes.
    
    Returns:
        list: Lista de instancias de AgentBase.
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    # No añadir allowed_roles por defecto, solo usar lo que venga en el JSON
    return [AgentBase(**cfg) for cfg in configs]

agents_config_path = "client_config/agents_config.json"
agents = load_agents_from_config(agents_config_path)

# Identificar router_agent y agentes normales
router_agent = next((a for a in agents if a.name == "router_agent"), None)
user_agents = [a for a in agents if a.name != "router_agent"]

# Crear el orquestador
orchestrator = Orchestrator(user_agents, router_agent, tools, context_manager)

def responder(user_input: str, user_role: str = "cliente") -> dict:
    """
    Función principal de entrada para procesar la petición del usuario.
    Llama al orquestador para obtener la respuesta adecuada según el rol y la entrada.
    
    Args:
        user_input (str): Entrada del usuario.
        user_role (str, opcional): Rol del usuario. Por defecto es 'cliente'.
    
    Returns:
        dict: Respuesta generada por el orquestador.
    """
    return orchestrator.responder(user_input, user_role=user_role)
