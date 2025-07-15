import logging
import json
from groq import Groq
from core.config.config import GROQ_API_KEY, GROQ_MODEL, ROUTING_MODEL, SERVER_URL
from core.agent.agents.agent_base import AgentBase
from core.agent.tools.context_manager import ContextManager

class Orchestrator:
    """
    Clase principal para la coordinación de agentes y el enrutamiento de peticiones.
    Se encarga de seleccionar el agente adecuado según el rol del usuario y la entrada,
    gestionar el contexto y delegar la respuesta al agente correspondiente o al modelo general.
    """
    def __init__(self, agents, router_agent, tools_schema, context_manager):
        """
        Inicializa el orquestador con los agentes disponibles, el agente router,
        el esquema de herramientas y el gestor de contexto.
        
        Args:
            agents (list): Lista de instancias de agentes disponibles.
            router_agent (AgentBase): Agente encargado de decidir el enrutamiento.
            tools_schema (dict): Esquema de herramientas disponibles para los agentes.
            context_manager (ContextManager): Gestor de contexto y entidades.
        """
        self.agents = agents
        self.router_agent = router_agent
        self.tools_schema = tools_schema
        self.context_manager = context_manager
        self.context = {}
        self.client = Groq(api_key=GROQ_API_KEY)

    def get_allowed_agents(self, user_role):
        """
        Filtra y retorna los agentes permitidos según el rol del usuario.
        
        Args:
            user_role (str): Rol del usuario (por ejemplo, 'cliente', 'admin', 'soporte').
        
        Returns:
            list: Lista de agentes permitidos para el rol dado.
        """
        return [a for a in self.agents if not hasattr(a, 'allowed_roles') or user_role in getattr(a, 'allowed_roles', ['cliente','admin','soporte'])]

    def route(self, user_input, entidades, agent_name=None, allowed_agents=None):
        """
        Determina y ejecuta el agente adecuado para manejar la petición del usuario.
        
        Args:
            user_input (str): Entrada del usuario.
            entidades (dict): Entidades extraídas del contexto.
            agent_name (str, optional): Nombre del agente específico a usar.
            allowed_agents (list, optional): Lista de agentes permitidos.
        
        Returns:
            dict: Respuesta generada por el agente seleccionado.
        """
        agents_to_use = allowed_agents if allowed_agents is not None else self.agents
        if agent_name:
            agent = next((a for a in agents_to_use if a.name == agent_name), None)
            if agent:
                return agent.handle(user_input, entidades, self.context, self.tools_schema)
            else:
                raise Exception(f"Agente '{agent_name}' no encontrado o no permitido")
        for agent in agents_to_use:
            for tool in getattr(agent, 'tools', []):
                if tool.replace('_', ' ') in user_input.lower():
                    return agent.handle(user_input, entidades, self.context, self.tools_schema)
        return agents_to_use[0].handle(user_input, entidades, self.context, self.tools_schema)

    def responder(self, user_input: str, user_role: str = "cliente") -> dict:
        """
        Procesa la entrada del usuario, selecciona el agente adecuado y retorna la respuesta.
        Si ningún agente es adecuado, responde usando el modelo general.
        
        Args:
            user_input (str): Entrada del usuario.
            user_role (str, opcional): Rol del usuario. Por defecto es 'cliente'.
        
        Returns:
            dict: Respuesta generada por el agente o el modelo general.
        """
        allowed_agents = self.get_allowed_agents(user_role)
        router_prompt = f"Usuario: {user_input}\nRespuesta:"
        resp = self.client.chat.completions.create(
            model=ROUTING_MODEL, # type: ignore
            messages=[
                {"role": "system", "content": self.router_agent.system_prompt},
                {"role": "user", "content": router_prompt}
            ],
            max_completion_tokens=10
        )
        agent_name = resp.choices[0].message.content.strip() # type: ignore
        logging.debug(f"[router_agent] Seleccionado: {agent_name}")
        agent_name_normalized = agent_name.strip().lower()
        allowed_names_normalized = [a.name.strip().lower() for a in allowed_agents]
        logging.debug(f"[responder] Nombres de agentes permitidos: {allowed_names_normalized}")
        if agent_name_normalized in allowed_names_normalized:
            entidades = self.context_manager.extract_and_update(user_input)
            for entidad in self.context_manager.patterns.keys():
                if entidad not in entidades:
                    referencia = self.context_manager.resolve_reference(user_input)
                    if entidad in referencia:
                        entidades[entidad] = referencia[entidad]
            logging.debug(f"Entidades extraídas: {entidades}")
            try:
                # Buscar el agente real usando el nombre normalizado
                idx = allowed_names_normalized.index(agent_name_normalized)
                agente_obj = allowed_agents[idx]
                respuesta = self.route(user_input, entidades, agent_name=agente_obj.name, allowed_agents=allowed_agents)
                logging.debug(f"[responder] Respuesta del agente '{agente_obj.name}': {respuesta}")
            except Exception as e:
                logging.exception("Error en la coordinación de agentes")
                return {"type": "error", "error": str(e)}
            return respuesta
        else:
            logging.debug(f"[responder] No se encontró agente válido para '{agent_name}', usando asistente general.")
            resp = self.client.chat.completions.create(
                model=GROQ_MODEL, # type: ignore
                messages=[
                    {"role": "system", "content": "Eres un chatbot asistente general. Si no puedes ayudar con la petición, responde de forma breve y educada, por ejemplo: 'Lo siento, no tengo acceso a esa información.' o 'No puedo ayudarte con eso.' Da respuestas cortas y claras."},
                    {"role": "user", "content": user_input}
                ]
            )
            return {"type": "chat", "response": resp.choices[0].message.content}
