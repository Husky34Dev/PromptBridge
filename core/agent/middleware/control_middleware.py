import logging
import json
from groq import Groq
from core.config.config import GROQ_API_KEY, GROQ_MODEL

class ControlMiddleware:
    """
    Middleware de control para procesar y enriquecer respuestas según el modo activo.
    - En modo 'rigido', reenvía la respuesta sin cambios.
    - En modo 'flexible', puede usar el contexto público para enriquecer la respuesta.
    """
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)

    def process(self, consulta, usuario, modo, contexto_publico, respuesta_agente):
        logging.debug(f"[middleware] Modo: {modo} | Consulta: {consulta} | Usuario: {usuario}")
        try:
            if modo == 'rigido':
                return respuesta_agente
            elif modo == 'flexible':
                # Si la respuesta es un resultado de tool_calls, generar prompt y llamar a Groq
                if isinstance(respuesta_agente, dict) and respuesta_agente.get('type') == 'tool_calls' and 'results' in respuesta_agente:
                    results = respuesta_agente['results']
                    prompt = self._construir_prompt_flexible(consulta, results, contexto_publico)
                    try:
                        resp = self.client.chat.completions.create(
                            model=GROQ_MODEL, # type: ignore
                            messages=[
                                {"role": "system", "content": "Eres un asistente experto. Responde de forma clara, natural y explicativa usando los datos proporcionados por herramientas externas. Si hay cálculos, hazlos tú. Si falta información, indícalo educadamente."},
                                {"role": "user", "content": prompt}
                            ],
                            max_completion_tokens=512
                        )
                        content = resp.choices[0].message.content
                    except Exception as e:
                        logging.error(f"[middleware] Error llamando a Groq: {e}")
                        content = f"[ERROR LLM] {e}\n\nPrompt usado:\n{prompt}"
                    return {
                        'type': 'chat',
                        'response': content,
                        'mode': modo
                    }
                
                if isinstance(respuesta_agente, dict) and 'response' in respuesta_agente and respuesta_agente.get('type') == 'chat':
                    respuesta_agente = respuesta_agente.copy()
                    respuesta_agente['response'] = (respuesta_agente['response'] or "")
                    return respuesta_agente
                elif isinstance(respuesta_agente, str):
                    return respuesta_agente
                else:
                    return respuesta_agente
            else:
                logging.warning(f"[middleware] Modo desconocido: {modo}, usando fallback rígido.")
                return respuesta_agente
        except Exception as e:
            logging.error(f"[middleware] Error procesando respuesta en modo {modo}: {e}")
            return respuesta_agente

    def _construir_prompt_flexible(self, consulta, results, contexto_publico):
        """
        Construye un prompt claro para el LLM usando la consulta, el contexto y los resultados de las tool calls.
        """
        prompt = ""
        if contexto_publico:
            prompt += "Historial reciente:\n"
            for m in contexto_publico[-2:]:
                prompt += f"- {m['role']}: {m['content']}\n"
        prompt += f"\nConsulta del usuario: {consulta}\n\nResultados de herramientas (JSON):\n{json.dumps(results, ensure_ascii=False, indent=2)}\n\n"
        prompt += (
            "Eres un asistente experto. Responde de forma clara, natural y CONCISA usando los datos proporcionados por herramientas externas. "
            "Si el usuario pide un dato concreto (correo, teléfono, dirección, deuda, etc.) y está presente en los resultados, responde ÚNICAMENTE con ese dato, sin explicaciones ni frases adicionales. "
            "Si el dato no está disponible, responde solo: 'No se ha encontrado información para ese abonado.' "
            "No expliques si el dato ya estaba consultado ni des mensajes técnicos. "
            "Si hay cálculos, hazlos tú. Si falta información, indícalo de forma breve y natural."
        )
        return prompt
