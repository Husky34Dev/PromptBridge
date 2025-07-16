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
