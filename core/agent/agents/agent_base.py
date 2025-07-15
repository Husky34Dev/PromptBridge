import logging
import json
import requests
from groq import Groq
from core.config.config import GROQ_API_KEY, GROQ_MODEL, SERVER_URL
from jsonschema import validate, ValidationError
import os
import re

class AgentBase:
    """
    Clase base para los agentes conversacionales.
    Define la estructura y el comportamiento general de un agente,
    incluyendo el manejo de mensajes, herramientas y roles permitidos.
    """
    def __init__(self, name, system_prompt, specialization, tools, allowed_roles=None):
        """
        Inicializa un agente base con sus propiedades principales.
        
        Args:
            name (str): Nombre del agente.
            system_prompt (str): Prompt de sistema especializado para el agente.
            specialization (str): Especialización o dominio del agente.
            tools (list): Lista de herramientas que puede usar el agente.
            allowed_roles (list, opcional): Roles permitidos para este agente.
        """
        self.name = name
        self.system_prompt = system_prompt
        self.specialization = specialization
        self.tools = tools
        self.allowed_roles = allowed_roles if allowed_roles is not None else ["cliente", "admin", "soporte"]
        self.client = Groq(api_key=GROQ_API_KEY)

    def handle(self, user_input, entidades, context, tools_schema=None):
        """
        Procesa la entrada del usuario y genera una respuesta usando el modelo y las herramientas disponibles.
        """
        messages = self._build_messages(user_input, entidades)
        tools_to_use = self._select_tools(tools_schema)
        
        try:
            resp = self.client.chat.completions.create(
                model=GROQ_MODEL, # type: ignore
                messages=messages,
                tools=tools_to_use,
                tool_choice="auto",
                max_completion_tokens=1024
            )
            logging.debug(f"[{self.name}] Respuesta cruda: {resp!r}")
            msg = resp.choices[0].message
            if getattr(msg, "tool_calls", None):
                resultados = self._process_tool_calls(msg.tool_calls, tools_to_use, entidades)
                return {"type": "tool_calls", "agent": self.name, "results": resultados}
            if msg.content is not None:
                try:
                    parsed = json.loads(msg.content)
                    if isinstance(parsed, dict):
                        return parsed
                except Exception:
                    pass
            return {"type": "chat", "agent": self.name, "response": msg.content}
        except Exception as e:
            logging.error(f"[{self.name}] Error en la llamada a la API: {e}")
            # Si el modelo falla porque la respuesta no es apropiada para las herramientas disponibles
            if "tool_use_failed" in str(e) or "Failed to call a function" in str(e):
                return {"type": "chat", "agent": self.name, "response": "Lo siento, no puedo ayudarte con esa consulta. ¿Hay algo específico sobre mi especialización en lo que pueda asistirte?"}
            # Para otros errores, devolver un mensaje genérico
            return {"type": "error", "agent": self.name, "error": f"Error procesando la solicitud: {str(e)}"}

    def _build_messages(self, user_input, entidades):
        messages = []
        messages.append({"role": "system", "content": self.system_prompt})
        if entidades:
            messages.append({
                "role": "system",
                "content": f"Entidades detectadas: {json.dumps(entidades)}"
            })
        messages.append({"role": "user", "content": user_input})
        logging.debug(f"[{self.name}] Mensajes enviados: {messages}")
        return messages

    def _select_tools(self, tools_schema):
        if tools_schema is None:
            tools_schema = []
        return [t for t in tools_schema if t["function"]["name"] in self.tools] if tools_schema else []

    def _process_tool_calls(self, tool_calls, tools_to_use, entidades):
        # AHORA BUSCA EN client_config
        patterns_path = "client_config/entity_patterns.json"
        try:
            with open(patterns_path, 'r', encoding='utf-8') as f:
                entity_patterns = json.load(f)
        except Exception:
            entity_patterns = {}
        resultados = []
        for call in tool_calls: # type: ignore
            name = call.function.name
            try:
                args = json.loads(call.function.arguments)
            except Exception:
                logging.exception(f"[{self.name}] Error parseando arguments para {name}")
                resultados.append({"tool": name, "error": "args invalidos"})
                continue
            tool_schema = next((t for t in tools_to_use if t["function"]["name"] == name), None)
            args = self._fill_missing_args(args, tool_schema, entidades)
            if not self._validate_args(args, tool_schema, name, resultados):
                continue
            # Validación de patrones: si falla, responde de forma amable usando el modelo
            pattern_errors = []
            for arg_name, arg_value in args.items():
                if arg_name in entity_patterns:
                    pattern = entity_patterns[arg_name]
                    if not re.fullmatch(pattern, str(arg_value)):
                        pattern_errors.append(f"El valor '{arg_value}' para '{arg_name}' no cumple el formato requerido.")
            if pattern_errors:
                logging.warning(f"[{self.name}] Validación de patrón fallida para {name}: {pattern_errors}")
                # Llamar al modelo para que explique el error de forma concreta y breve
                error_messages = [
                    {"role": "system", "content": "Eres un asistente amable y conciso. Si el usuario comete un error de formato, explica el error de forma clara, breve y directa, sin explicaciones largas ni ejemplos extensos. Solo indica el campo, el valor y que revise el formato."},
                    {"role": "user", "content": f"El usuario intentó consultar '{name}' pero: {'; '.join(pattern_errors)} Por favor, indícale el error de forma breve y concreta."}
                ]
                resp = self.client.chat.completions.create(
                    model=GROQ_MODEL, # type: ignore
                    messages=error_messages, # type: ignore
                    max_completion_tokens=80
                )
                msg = resp.choices[0].message
                return [{"tool": name, "error": msg.content}]
            logging.info(f"[{self.name}] Ejecutando herramienta {name} con args {args}")
            try:
                r = requests.post(f"{SERVER_URL}/{name}", json=args)
                r.raise_for_status()
                out = r.json()
            except Exception:
                logging.exception(f"[{self.name}] Error al llamar al backend para {name}")
                resultados.append({"tool": name, "error": "backend failure"})
                continue
            resultados.append({"tool": name, "params": args, "response": out})
        return resultados

    def _fill_missing_args(self, args, tool_schema, entidades):
        reqs = tool_schema["function"]["parameters"].get("required", []) if tool_schema else []
        for r in reqs:
            if r not in args and r in entidades:
                args[r] = entidades[r]
        return args

    def _validate_args(self, args, tool_schema, name, resultados):
        schema = tool_schema["function"]["parameters"] if tool_schema else None
        if schema:
            try:
                validate(instance=args, schema=schema)
            except ValidationError as e:
                logging.warning(f"[{self.name}] Validación fallida para {name}: {e.message}")
                resultados.append({"tool": name, "error": f"validación fallida: {e.message}"})
                return False
        return True
