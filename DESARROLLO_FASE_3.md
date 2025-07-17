### [PASO 6] Middleware flexible: integración con LLM (Groq)
- El middleware flexible ahora construye un prompt con la consulta, el historial público y los resultados de las tool calls, y lo pasa a Groq para que el modelo genere la respuesta final.
- Se elimina la lógica hardcodeada de combinación de resultados: ahora el LLM puede razonar, sumar, explicar y responder de forma natural y conversacional.
- Si hay error en la llamada al LLM, se muestra el prompt usado para facilitar el debug.
### [PASO 5] Middleware flexible: combinación de tool calls y respuesta generativa
- El middleware ahora, en modo flexible, detecta si la respuesta es resultado de tool calls y genera una respuesta explicativa tipo `chat` combinando los resultados (por ejemplo, suma de facturas).
- Si no hay lógica específica, devuelve un resumen genérico de los resultados.
- Este punto de entrada permite extender la lógica generativa y de combinación de resultados según las necesidades del negocio.
### [PASO 4] Preparación para delegación avanzada al middleware
- El orquestador ahora está preparado para que el middleware tome el control total de la generación de respuestas explicativas en modo flexible.
- Esto permite que la lógica de combinación de tool calls y generación de respuestas naturales se implemente de forma desacoplada y extensible en el middleware.
# Fase 3: Arquitectura Flexible, Contexto y Privacidad

## Histórico de avances y decisiones


### Hitos y cambios incrementales
- Se creó la rama de desarrollo específica para la fase 3.
- Se auditó el sistema y se definieron pruebas de regresión.
- Se implementó la lectura dinámica de modos desde `client_config/modes.json`.
- El orquestador fue adaptado para exponer el modo activo y permitir el cambio solo si el rol lo permite.
- Se integró la selección de modo en el flujo principal y se documentó cómo se pasa el modo al agente y al frontend.
- Se añadió el botón de cambio de modo en el frontend, mostrando el modo activo y permitiendo alternar si el rol lo permite.
- El frontend envía el modo seleccionado al backend en cada consulta, permitiendo trazabilidad y control centralizado.
- Se validó la integración visual y funcional del cambio de modo.
- Se refactorizó el orquestador para separar contexto público y privado, delegando la gestión de entidades y normalización en `ContextManager`.
- Se implementó la lógica de multi-tool orchestration en los agentes, permitiendo respuestas compuestas.
- Se añadió logging explícito del historial público en cada turno.
- Se documentó la estrategia de privacidad y filtrado en los agentes.
- [2024-06-10] **FIX: Propagación de modo desde frontend a backend**. Ahora el modo seleccionado en la interfaz se envía como parte del payload al endpoint `/api/chat`, el backend lo recibe y lo pasa explícitamente al orquestador y middleware. Esto permite que el cambio de modo (rígido/flexible) se respete de extremo a extremo y se refleje en la lógica de respuesta.

#### Detalle técnico:
- Se actualizó el modelo `ChatRequest` y el endpoint `/api/chat` en `web/main.py` para aceptar el campo `mode`.
- Se modificó la función `responder` en `core/agent/agent.py` para aceptar y propagar el modo solicitado.
- El frontend ya enviaba el modo en el payload, pero el backend ahora lo recibe y lo utiliza correctamente.
- El orquestador y el middleware ya soportaban la lógica de modos, por lo que ahora la selección de modo es efectiva y auditable.

---

## Estado actual y cambios principales

### Arquitectura y modularidad
- El sistema está modularizado: orquestador, agentes, backend y frontend.
- La gestión de entidades y patrones es extensible mediante archivos JSON.

### Gestión de modos
- El orquestador gestiona modos dinámicamente leyendo `client_config/modes.json`.
- El modo activo se expone en cada respuesta y solo roles permitidos pueden cambiarlo.
- El frontend permite alternar modos si el rol lo permite.

### Integración visual de modos
- El frontend incluye un botón para alternar modos, visible solo para roles permitidos.
- El modo activo se muestra en la interfaz y se envía al backend en cada consulta.
- El sistema refleja el modo seleccionado en las respuestas y en el historial.

### Contexto conversacional y privacidad
- Separación explícita entre contexto público (historial de preguntas/respuestas) y contexto privado (entidades y datos sensibles).
- El contexto público se acumula y se envía al modelo externo (Groq/OpenAI) para mejorar la comprensión conversacional.
- El contexto privado se gestiona solo localmente en `ContextManager` y nunca se expone fuera del backend.
- Recuperación referencial de entidades (ej: DNI) funciona correctamente y es case-insensitive.

### Multi-tool orchestration
- Los agentes pueden ejecutar varias tool calls por consulta.
- El sistema soporta respuestas compuestas y la lógica de multi-tool está documentada en los logs y en este archivo.

### Logging y trazabilidad
- El historial público se loguea explícitamente en cada turno, permitiendo auditoría y trazabilidad completa.
- Los logs muestran claramente la separación de contexto y la ejecución de herramientas.

### Privacidad y filtrado
- Los agentes filtran consultas sensibles y bloquean respuestas fuera de su especialización, garantizando privacidad.

---

## Ejemplo real de traza: Contexto público y privado

### Flujo de consulta y contexto

1. **Consulta directa del usuario:**
   - Usuario: `Dame todos los datos del abonado 12345678A`
   - El sistema extrae la entidad `dni` y la normaliza: `{'dni': '12345678A'}`
   - El contexto privado se actualiza: `private_context = {'dni': '12345678A'}`
   - El contexto público (historial) se actualiza:
     ```python
     public_context = [
         {"role": "user", "content": "Dame todos los datos del abonado 12345678A"}
     ]
     ```
   - El modelo recibe solo el historial público y, si corresponde, un mensaje `system` con entidades detectadas:
     ```python
     messages = [
         {"role": "system", "content": "Entidades detectadas: {\"dni\": \"12345678A\"}"},
         {"role": "user", "content": "Dame todos los datos del abonado 12345678A"}
     ]
     ```
   - El modelo nunca recibe el contexto privado completo ni datos sensibles adicionales.

2. **Consulta referencial y multi-tool:**
   - Usuario: `dame todos sus datos y todas sus facturas`
   - El sistema busca en el contexto privado y recupera el `dni` previamente extraído: `{'dni': '12345678A'}`
   - El contexto público se actualiza:
     ```python
     public_context = [
         {"role": "user", "content": "Dame todos los datos del abonado 12345678A"},
         {"role": "assistant", "content": "{'type': 'tool_calls', 'agent': 'datos_agent', ...}"},
         {"role": "user", "content": "dame todos sus datos y todas sus facturas"}
     ]
     ```
   - El agente ejecuta varias tool calls (ejemplo: `datos_abonado`, `todas_las_facturas`) usando el contexto privado.
   - El historial público se actualiza con la respuesta compuesta:
     ```python
     public_context.append({"role": "assistant", "content": "{'type': 'tool_calls', 'agent': 'datos_agent', ...}"})
     ```

---

## Estrategia de privacidad y control

- El contexto público acumulado permite que el sistema sea extensible y que el modelo externo pueda tener contexto conversacional si se decide enviar más mensajes en el prompt.
- El historial público está limitado a los últimos 5 mensajes para evitar crecimiento indefinido y facilitar la gestión de memoria y privacidad.
- El contexto privado garantiza privacidad y control sobre los datos sensibles.
- El sistema es robusto, extensible y fácil de auditar.

---

## Fragmento relevante de código

```python
# En __init__ del orquestador
self.public_context = []  # Historial de mensajes pregunta/respuesta

# En responder()
self.public_context.append({"role": "user", "content": user_input})
entidades = self.context_manager.extract_and_update(user_input)
# Recuperación referencial y normalización, todo gestionado en ContextManager
# ... lógica de selección y ejecución de agente ...
self.public_context.append({"role": "assistant", "content": respuesta.get("response", str(respuesta))})
```

---

## Resumen final

- El sistema implementa una arquitectura flexible, con gestión de modos, contexto público/privado, multi-tool orchestration y privacidad garantizada.
- Toda la lógica de entidades, normalización y recuperación referencial es extensible y configurable en `ContextManager`.
- El orquestador queda limpio, profesional y preparado para escalar y mantener.
- El sistema sigue siendo incremental, robusto y compatible con el backend actual.

---


## Problema detectado en la implementación actual (2025-07-17)

### Resumen del problema
Actualmente, el modo flexible no implementa la lógica conversacional avanzada descrita en la documentación. Tanto en modo rígido como flexible, el sistema ejecuta tool calls y devuelve el resultado estructurado (tipo `tool_calls`), sin combinar resultados ni generar respuestas explicativas tipo `chat` usando esos datos.

#### Lo que falta según la visión/documentación:
- En modo flexible, el sistema debe poder:
  - Ejecutar varias tool calls por detrás (por ejemplo, obtener todas las facturas, sumar importes, etc.).
  - Generar una respuesta natural y explicativa (tipo `chat`) usando esos datos, aunque por detrás haya habido tool calls.
  - Responder a preguntas abiertas o no cubiertas por endpoints directos, combinando datos de varias fuentes.

#### Ejemplo esperado:
Usuario: “¿Cuánto debe el abonado 12345678A?”
→ El sistema obtiene todas las facturas, suma los importes pendientes y responde:
“El abonado 12345678A tiene una deuda total de 301,25€ repartida en 2 facturas pendientes.”

### Zonas donde hay que cambiar cosas
1. **Orquestador (`core/agent/orchestrator.py`)**: Añadir lógica para que, en modo flexible, tras ejecutar tool calls, se combinen los resultados y se genere una respuesta tipo `chat` (no solo devolver el resultado crudo).
2. **Middleware (`core/agent/middleware/control_middleware.py`)**: Enriquecer la función `process` para que, en modo flexible, pueda detectar cuándo se requiere una respuesta generativa, combinar/interpetar resultados y devolver una respuesta tipo `chat` explicativa.
3. **Agentes (`core/agent/agents/agent_base.py` y derivados)**: (Opcional) Permitir que los agentes devuelvan resultados intermedios que el middleware/orquestador pueda combinar.
4. **Documentación y logging**: Documentar la diferencia entre modo rígido y flexible, y cómo el flexible ahora puede combinar tool calls y dar respuestas generativas.

---

## Plan de implementación del middleware y modos (Fase 3)

### Objetivo
Implementar un middleware que permita alternar entre un modo rígido (sin contexto conversacional) y un modo flexible (con uso de contexto y lógica enriquecida), asegurando siempre la posibilidad de fallback seguro y cambios iterativos.

### Estrategia general
- **Iteraciones pequeñas y seguras:** Cada cambio debe ser incremental, con fallback al comportamiento anterior si algo falla.
- **Modo rígido:** El sistema funciona como hasta ahora, sin usar el contexto público para el prompt ni para la lógica de agentes. Solo se ejecutan tool calls directas.
- **Modo flexible:** El middleware decide, según el contexto público y la consulta, si ejecutar tool calls, responder generativamente, o combinar ambos enfoques. El contexto público se pasa al modelo y puede influir en la respuesta.
- **Middleware desacoplado:** El middleware será una clase/módulo aparte (`control_middleware.py`) que recibirá la consulta, el modo, el contexto y la respuesta del agente, y decidirá cómo procesar y devolver la respuesta final.
- **Fallback garantizado:** Si el middleware falla o el modo flexible no está disponible, el sistema vuelve automáticamente al modo rígido.
- **Documentación y logging:** Cada iteración debe estar documentada y logueada para facilitar auditoría y debugging.

### Pasos de implementación
1. **Crear el módulo `control_middleware.py`**
   - Inicialmente, solo reenvía la respuesta sin modificarla.
   - Añadir logging para trazar el flujo.
2. **Modificar el orquestador para usar el middleware**
   - Antes de devolver la respuesta al frontend, pasarla siempre por el middleware.
   - El middleware recibe: consulta, usuario, modo, contexto público, respuesta del agente.
3. **Activar el modo flexible**
   - Si el modo es flexible, el middleware puede modificar la respuesta usando el contexto público.
   - Si el modo es rígido, el middleware solo reenvía la respuesta.
4. **Iterar y enriquecer el middleware**
   - [2025-07-17] Primera iteración: el middleware, en modo flexible, añade una nota al final de la respuesta indicando que se ha usado el contexto público, mostrando un resumen de los últimos mensajes del historial. Esto permite auditar visualmente el uso del contexto y sienta la base para lógica más avanzada.
   - Añadir lógica para decidir cuándo usar contexto, cuándo ejecutar tool calls adicionales, cómo combinar respuestas, etc.
   - Mantener siempre la opción de fallback seguro.
5. **Actualizar la documentación y los tests**
   - Documentar cada iteración y validar que el sistema sigue funcionando en modo rígido.


### Ejemplo de interfaz del middleware (actualizado)
```python
# core/agent/middleware/control_middleware.py
class ControlMiddleware:
    def process(self, consulta, usuario, modo, contexto_publico, respuesta_agente):
        # Si modo es 'rigido', devolver respuesta_agente sin cambios
        # Si modo es 'flexible', añadir una nota con el contexto público reciente
        # Siempre loguear el flujo y permitir fallback
        try:
            if modo == 'rigido':
                return respuesta_agente
            elif modo == 'flexible':
                nota_contexto = "\n\n[Nota: Respuesta enriquecida usando el contexto público. Historial reciente: "
                ultimos = contexto_publico[-2:] if contexto_publico else []
                resumen = "; ".join([f"{m['role']}: {m['content']}" for m in ultimos])
                nota_contexto += resumen + "]"
                if isinstance(respuesta_agente, dict) and 'response' in respuesta_agente and respuesta_agente.get('type') == 'chat':
                    respuesta_agente = respuesta_agente.copy()
                    respuesta_agente['response'] = (respuesta_agente['response'] or "") + nota_contexto
                    return respuesta_agente
                elif isinstance(respuesta_agente, str):
                    return respuesta_agente + nota_contexto
                else:
                    return respuesta_agente
            else:
                return respuesta_agente
        except Exception:
            return respuesta_agente
```

### Buenas prácticas
- Mantener el middleware lo más desacoplado posible del orquestador y los agentes.
- No modificar la lógica de agentes ni orquestador salvo para delegar en el middleware.
- Añadir tests y logs en cada iteración.
- Documentar claramente qué hace cada modo y cómo se activa.

---


## Refactorización: separación de responsabilidades y middleware

-### [PASO 2] Refactor: logging estructurado y funciones auxiliares en el orquestador
- Se ha extraído la lógica de logging a funciones auxiliares privadas (`_log_public_context`, `_log_router_selection`, `_log_extracted_entities`, `_log_agent_response`) en el orquestador.
- Esto mejora la legibilidad, centraliza el control del logging y facilita su ajuste futuro.
- El logging ahora es más estructurado y menos redundante, cumpliendo el objetivo de calidad y trazabilidad.

### [PASO 3] Refactor: gestión de contexto público/privado en métodos dedicados
- Se ha separado la gestión del contexto público (`_add_to_public_context`) y la actualización del contexto privado (`_update_private_context`) en métodos auxiliares del orquestador.
- Esto mejora la claridad, facilita la mantenibilidad y prepara la arquitectura para futuras extensiones en la gestión de contexto.
- Se ha extraído la lógica de logging a funciones auxiliares privadas (`_log_public_context`, `_log_router_selection`, `_log_extracted_entities`, `_log_agent_response`) en el orquestador.
- Esto mejora la legibilidad, centraliza el control del logging y facilita su ajuste futuro.
- El logging ahora es más estructurado y menos redundante, cumpliendo el objetivo de calidad y trazabilidad.

- Se ha creado el módulo `core/agent/middleware/control_middleware.py` para centralizar la lógica de procesamiento de respuestas según el modo activo.
- El orquestador ahora delega el procesamiento final de la respuesta en el middleware, cumpliendo el principio de unicidad y facilitando la extensión y el mantenimiento.
- El middleware permite que el modo 'rígido' funcione como hasta ahora (sin usar contexto público) y que el modo 'flexible' pueda enriquecerse progresivamente.
- Toda la lógica de decisión sobre el uso de contexto, enriquecimiento o fallback queda centralizada y desacoplada del orquestador y los agentes.
- Cada cambio y refactorización está documentado en este archivo para trazabilidad y auditoría.

---
