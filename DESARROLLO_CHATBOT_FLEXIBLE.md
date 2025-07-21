# Desarrollo: Chatbot con Modos Flexibles

## Objetivo
Evolucionar el chatbot actual de un sistema rígido de tool calls hacia un sistema más flexible que permita:
- Contexto conversacional
- Respuestas mixtas (generativas + tool calls)
- Múltiples modos de operación
- Mayor interactividad

## Análisis del Sistema Actual

### Arquitectura Actual
```
Usuario → Router Agent → Agente Especializado → Tool Call → Backend → Respuesta Estructurada
```

### Componentes Principales

#### 1. Router Agent (`orchestrator.py`)
- **Función**: Determina qué agente debe manejar la consulta
- **Modelo**: `llama-3.3-70b-versatile`
- **Entrada**: Consulta del usuario
- **Salida**: Nombre del agente especializado

#### 2. Agentes Especializados (`agent_base.py`)
- **Función**: Procesan consultas específicas de su dominio
- **Herramientas**: Lista de tool calls disponibles
- **Flujo Actual**:
  1. Recibe consulta + entidades detectadas
  2. Decide si usar tool calls o responder directamente
  3. Si usa tool calls → ejecuta y devuelve resultado estructurado
  4. Si no → respuesta de chat simple

#### 3. Backend de Herramientas (`server.py`)
- **Función**: API REST que ejecuta las operaciones reales
- **Endpoints**: Consultas a base de datos, APIs externas, etc.
- **Respuesta**: Datos estructurados en JSON

#### 4. Frontend (`cards.js`, `cards-config.js`)
- **Función**: Renderiza respuestas como tarjetas visuales
- **Tipos**: Subscriber, Facturas, Clima, Incidencias, Deuda
- **Detección**: Automática basada en estructura de datos

### Limitaciones Identificadas

#### 1. Rigidez del Flujo
- **Problema**: O ejecuta tool call O responde con texto
- **Limitación**: No puede combinar ambos enfoques
- **Ejemplo**: No puede explicar por qué una deuda es alta mientras muestra los datos

#### 2. Falta de Contexto
- **Problema**: Cada consulta es independiente
- **Limitación**: No recuerda consultas anteriores
- **Observacion**: Implementado un sistema basado en extracción de entidades clave.
- **Ejemplo**: No puede sugerir acciones basadas en consultas previas

#### 3. Respuestas Limitadas
- **Problema**: Solo muestra datos sin interpretación
- **Limitación**: No puede dar insights, sugerencias o explicaciones
- **Ejemplo**: Muestra facturas pendientes pero no sugiere prioridades

#### 4. Modo Único
- **Problema**: Mismo comportamiento para todos los casos
- **Limitación**: No se adapta al contexto o preferencias del usuario

## Archivos Clave del Sistema

### Core del Sistema
- `/core/agent/orchestrator.py` - Router principal
- `/core/agent/agents/agent_base.py` - Clase base de agentes
- `/core/agent/agent.py` - Punto de entrada
- `/core/config/config.py` - Configuración general

### Backend
- `/core/backend/server.py` - API REST para tool calls
- `/core/backend/demo.db` - Base de datos SQLite

### Frontend
- `/web/static/cards.js` - Renderizado de tarjetas
- `/web/static/cards-config.js` - Configuración de tipos de tarjetas
- `/web/static/app.js` - Lógica del chat frontend
- `/web/main.py` - Servidor web

### Configuración
- `/client_config/agents_config.json` - Configuración de agentes
- `/client_config/tools_schema.json` - Schema de herramientas
- `/client_config/entity_patterns.json` - Patrones de validación

## Propuesta de Mejoras

### 1. Implementar Modos de Operación
- **Modo Consulta**: Solo tool calls, respuestas estructuradas
- **Modo Interactivo**: Tool calls + respuestas generativas

### 2. Sistema de Contexto Conversacional
- Mantener historial de mensajes en sesión
- Permitir referencias a consultas anteriores
- Sugerir acciones basadas en datos consultados

### 3. Middleware de Control
- Capa entre inferencia y ejecución
- Validación de seguridad y privacidad
- Enriquecimiento de respuestas

### 4. Respuestas Enriquecidas
- Interpretación de datos
- Sugerencias contextuales
- Explicaciones y resúmenes

## Plan de Desarrollo

### Fase 1: Análisis Completo
- [x] Documentar arquitectura actual
- [x] Mapear flujo completo de datos
- [x] Identificar puntos de extensión
- [x] Analizar casos de uso

### Fase 2: Diseño de Nuevos Modos
- [x] Definir estructura de modos
- [x] Diseñar middleware de control
- [x] Especificar contexto conversacional
- [x] Planificar migración gradual

### Fase 3: Implementación
- [x] Crear sistema de modos
- [x] Implementar contexto conversacional
- [x] Desarrollar middleware
- [x] Actualizar frontend para nuevos tipos

### Fase 4: Testing y Validación
- [ ] Pruebas de funcionamiento
- [ ] Validación de seguridad
- [ ] Optimización de rendimiento
- [ ] Documentación final

## Notas de Desarrollo

### Fecha: 2025-07-15
- Creada rama `feature/chatbot-flexible-modes`
- Iniciado análisis de arquitectura actual
- Identificadas limitaciones principales
- Definido plan de desarrollo por fases

---

## Próximos Pasos
1. Completar mapeo detallado del flujo de datos
2. Analizar casos de uso específicos para modos flexibles
3. Diseñar la arquitectura del sistema de contexto conversacional

## Mapeo Detallado del Flujo de Datos

### 1. Usuario envía mensaje
- **Frontend** (`app.js`, `index.html`)
  - El usuario escribe y envía una consulta en la interfaz web.
  - El mensaje se envía vía HTTP (fetch/AJAX) al backend conversacional.

### 2. Recepción y routing
- **Backend Conversacional** (`main.py` o endpoint de agente)
  - Recibe el mensaje y lo pasa al `Orchestrator`.

### 3. Orquestador decide agente
- **Orchestrator** (`core/agent/orchestrator.py`)
  - Usa el modelo de routing (`llama-3.3-70b-versatile`) para decidir qué agente especializado debe responder.
  - Devuelve el nombre del agente adecuado.

### 4. Extracción de entidades
- **Agente Especializado** (`core/agent/agents/agent_base.py`)
  - Extrae entidades relevantes usando patrones (`client_config/entity_patterns.json`).
  - Construye el prompt y contexto para el modelo.

### 5. Inferencia y decisión de tool call
- **Agente Especializado**
  - Envía el mensaje y entidades al modelo (`GROQ_MODEL`).
  - El modelo decide si debe ejecutar una tool call o responder directamente.

### 6. Ejecución de tool call (si aplica)
- **Agente Especializado**
  - Si hay tool call:
    - Valida argumentos y patrones.
    - Llama al endpoint correspondiente del backend de herramientas (`core/backend/server.py`).
    - Recibe respuesta estructurada (JSON).
  - Si no hay tool call:
    - Devuelve respuesta generativa del modelo.

### 7. Respuesta al frontend
- **Backend Conversacional**
  - Envía la respuesta (datos o texto) al frontend.

### 8. Renderizado visual
- **Frontend** (`cards.js`, `cards-config.js`)
  - Detecta el tipo de respuesta y renderiza la tarjeta adecuada.
  - Muestra la respuesta al usuario.

---

### Diagrama Resumido
```
Usuario → Frontend → Backend Conversacional → Orchestrator → Agente Especializado → [Tool Call → Backend Herramientas] → Respuesta → Frontend
```

### Archivos Clave en Cada Paso
- **Frontend:** `app.js`, `cards.js`, `cards-config.js`, `index.html`
- **Backend Conversacional:** `main.py`, `orchestrator.py`, `agent_base.py`, `config.py`
- **Backend Herramientas:** `server.py`, `demo.db`
- **Configuración:** `tools_schema.json`, `entity_patterns.json`, `agents_config.json`

---

### Observaciones
- El flujo es lineal y seguro, pero poco flexible para interactividad avanzada.
- El contexto conversacional no se mantiene entre mensajes (cada consulta es independiente).
- La validación y ejecución de tool calls es robusta, pero no permite respuestas mixtas ni enriquecidas.

---

## Puntos de Extensión en el Sistema

### 1. Frontend (Interfaz de Usuario)
- **app.js**
  - Permite modificar la forma en que se envían y reciben mensajes.
  - Se puede añadir lógica para seleccionar el modo (consulta/interactivo) desde la UI.
  - Posible integración de historial de conversación y sugerencias contextuales.

### 2. Orchestrator (Routing y Delegación)
- **core/agent/orchestrator.py**
  - Punto ideal para decidir el modo de operación antes de delegar al agente especializado.
  - Puede almacenar y pasar contexto conversacional entre agentes.
  - Permite lógica para combinar respuestas de varios agentes.

### 3. Agentes Especializados
- **core/agent/agents/agent_base.py**
  - Lugar para implementar lógica de decisión entre tool call y respuesta generativa.
  - Se puede extender para manejar contexto conversacional y memoria de sesión.
  - Permite enriquecer respuestas con explicaciones, sugerencias, o resúmenes.
  - Middleware entre inferencia y ejecución de tool calls.

### 4. Middleware de Control
- **Nuevo módulo sugerido**
  - Capa entre la inferencia del modelo y la ejecución de tool calls.
  - Validación de seguridad, privacidad y enriquecimiento de respuestas.
  - Puede decidir si mostrar solo datos, generar explicaciones, o ambas cosas.

### 5. Backend de Herramientas
- **core/backend/server.py**
  - Se puede extender para devolver metadatos, sugerencias, o resúmenes junto con los datos.
  - Permite lógica de negocio adicional antes de devolver la respuesta.

### 6. Configuración y Extensibilidad
- **client_config/tools_schema.json, agents_config.json**
  - Permite definir nuevos modos, agentes, y herramientas sin modificar el core.
  - Se puede añadir configuración para el comportamiento de cada modo.

---

### Resumen Visual
```
[Frontend] → [Orchestrator] → [Middleware] → [Agente Especializado] → [Backend Herramientas]
```
- Cada bloque puede ser extendido para soportar modos flexibles y contexto conversacional.

---

### Recomendaciones
- Centraliza la lógica de modo y contexto en el Orchestrator y Middleware.
- Mantén los agentes especializados simples y enfocados en su dominio.
- Permite al frontend mostrar y seleccionar el modo de operación.
- Documenta cada punto de extensión para facilitar futuras mejoras.

---

## Análisis de Casos de Uso para Modos Flexibles

### 1. Modo Consulta (Solo Tool Calls)
- **Caso:** El usuario pregunta "¿Cuál es mi deuda total?"
  - El sistema ejecuta la tool call correspondiente.
  - Devuelve la respuesta estructurada (ej: {deuda: 300}).
  - El frontend muestra la tarjeta de deuda.
  - **Ventaja:** Respuesta precisa, segura y auditable.
  - **Limitación:** No explica el origen de la deuda ni sugiere acciones.

### 2. Modo Interactivo (Generativo + Tool Calls)
- **Caso:** El usuario pregunta "¿Por qué tengo tanta deuda? ¿Qué puedo hacer?"
  - El sistema ejecuta la tool call de deuda y facturas pendientes.
  - El modelo generativo analiza los datos y genera una explicación:
    - "Tienes una deuda de 300€ porque hay 2 facturas pendientes. Puedes pagar online o solicitar un plan de pago. ¿Te gustaría ver los detalles?"
  - El usuario puede seguir la conversación, pedir detalles, recibir sugerencias, etc.
  - **Ventaja:** Experiencia enriquecida, contexto conversacional, recomendaciones.
  - **Limitación:** Requiere control de privacidad y lógica para no exponer datos sensibles.

### 3. Casos de Uso Avanzados
- **Seguimiento de contexto:**
  - Usuario: "¿Y la dirección de ese abonado?"
  - Sistema: Usa el contexto de la consulta anterior para saber a qué abonado se refiere.
- **Sugerencias proactivas:**
  - Tras mostrar la deuda, el sistema sugiere: "¿Quieres ver el detalle de las facturas o contactar con soporte?"
- **Validación y seguridad:**
  - Si el usuario pide datos sensibles, el sistema solicita confirmación o verifica permisos antes de mostrar la información.

---

### Estado Actual: Capacidades Avanzadas
- El sistema ya soporta **contexto previo**: por ejemplo, si el usuario consulta primero el DNI, puede pedir después "dame todas sus facturas" y el sistema utiliza el contexto guardado para responder correctamente.
- **Pendiente de implementar:** la ejecución de **multi tools en una sola llamada**. Actualmente, si el usuario pide "dame todos sus datos y todas sus facturas", el sistema solo ejecuta una tool call por consulta. Implementar esta capacidad permitirá respuestas compuestas y flujos conversacionales más naturales.

---

### Resumen
- Cada modo responde a necesidades distintas: eficiencia, interacción, personalización.
- El sistema debe ser capaz de alternar modos según el contexto, la consulta y las preferencias del usuario.
- La arquitectura propuesta permite implementar estos casos de uso de forma modular y escalable.

---

## Fase de Desarrollo: Soporte Multi Tools

### Descripción del reto
Actualmente, el sistema solo permite ejecutar una tool call por consulta. Esto limita la capacidad de responder a preguntas compuestas o de ofrecer respuestas enriquecidas que combinen datos de varias fuentes.

### Objetivo
Implementar la capacidad de ejecutar múltiples tool calls en una sola consulta, permitiendo:
- Respuestas compuestas (ej: "dame todos sus datos y todas sus facturas")
- Flujos conversacionales más naturales
- Mayor flexibilidad en los modos interactivo y mixto

### Componentes afectados
- **Orchestrator:** Deberá analizar la consulta y decidir qué herramientas ejecutar, permitiendo múltiples tool calls por mensaje.
- **Agentes Especializados:** Adaptar la lógica para manejar y combinar resultados de varias tool calls.
- **Middleware de Control:** Validar, enriquecer y combinar respuestas antes de enviarlas al frontend.
- **Frontend:** Actualizar la lógica de renderizado para mostrar respuestas compuestas y permitir la selección de modo.

### Consideraciones para la implementación
- Definir el formato de las respuestas compuestas (JSON, tarjetas múltiples, etc.)
- Gestionar el contexto conversacional para encadenar tool calls y mantener coherencia en la sesión
- Validar la seguridad y privacidad al combinar datos de diferentes fuentes
- Documentar el flujo y los cambios en cada componente

### Planificación
- Este reto será abordado en la **Fase 3: Implementación** del plan de desarrollo.
- Se recomienda iniciar con pruebas en el orquestador y agentes, seguido de la integración con el middleware y frontend.
- Documentar los avances y retos encontrados durante la implementación.

---

### Soporte Multi Tools: Reto y Planificación para Fase 3

Actualmente, el sistema ejecuta una sola tool call por consulta, lo que limita la capacidad de generar respuestas compuestas y flujos conversacionales más ricos. El soporte para **multi tools en una sola llamada** permitirá que el chatbot procese peticiones complejas como "dame todos sus datos y todas sus facturas" y devuelva una respuesta integrada, combinando resultados de varias herramientas.

**Beneficios esperados:**
- Respuestas más completas y naturales.
- Reducción de pasos para el usuario.
- Mejor experiencia en modos interactivo y mixto.
- Posibilidad de enriquecer la respuesta con explicaciones, sugerencias y datos cruzados.

**Retos técnicos:**
- Orquestar la ejecución de varias tool calls en paralelo o secuencia.
- Unificar y estructurar la respuesta para el frontend.
- Mantener la coherencia del contexto conversacional entre tool calls.
- Validar seguridad y privacidad en cada llamada.

**Relación con los modos flexibles:**
- El soporte multi tools es clave para el modo interactivo y mixto, donde se espera que el sistema combine datos y explicaciones.
- Permite que el middleware decida cuándo y cómo ejecutar varias herramientas según el contexto y la consulta.

**Planificación:**
- Este reto será abordado en la **Fase 3: Implementación**.
- Se diseñará una interfaz y lógica de orquestación para soportar múltiples tool calls.
- Se documentará el proceso y los puntos de extensión para facilitar futuras mejoras.

---

## Decisión de Modos: Consulta Rígida y Flexible

Para simplificar y potenciar la arquitectura, se trabajará únicamente con dos modos principales:

1. **Modo Consulta Rígido:**
   - Ejecuta exclusivamente tool calls directas según la consulta del usuario.
   - No interpreta, comenta ni combina resultados.
   - Ejemplo: "¿Cuál es mi deuda?" → Ejecuta la tool correspondiente y devuelve el dato tal cual.

2. **Modo Flexible:**
   - El sistema puede decidir qué tool calls ejecutar, comentar, explicar y combinar resultados para dar la mejor respuesta.
   - Permite respuestas enriquecidas, interpretación de datos y selección inteligente de herramientas.
   - Ejemplo: "Dame el correo del abonado 12345678A" → El agente llama a la tool `datos_Abonado`, extrae solo el correo y lo presenta, pudiendo además explicar el origen del dato si es relevante.
   - Si la consulta requiere varios datos, puede ejecutar varias tool calls y combinar los resultados.

**Implicaciones para la arquitectura:**
- El orquestador y los agentes deben poder distinguir el modo activo y adaptar su lógica.
- En modo flexible, el agente puede decidir no solo qué tools ejecutar, sino también cómo presentar y enriquecer la respuesta.
- El frontend debe mostrar claramente el modo activo y adaptar el renderizado según el tipo de respuesta (simple o enriquecida).

**Planificación:**
- El desarrollo se centrará en estos dos modos, eliminando el modo mixto y el modo interactivo como opciones separadas.
- Se actualizará la documentación y la lógica de los componentes para reflejar esta simplificación.
- Se priorizará la capacidad del modo flexible para ejecutar tool calls de forma inteligente y presentar respuestas útiles y comentadas.

---

## Arquitectura Extensible para Modos

Para asegurar que el chatbot pueda adaptarse y escalar a nuevos clientes y funcionalidades (por ejemplo, generación de imágenes, voz, etc.), se recomienda:

1. **Definir los modos como Enum o clase en el backend:**
   - Ejemplo en Python:
     ```python
     from enum import Enum
     class ChatMode(Enum):
         CONSULTA_RIGIDA = "consulta_rigida"
         FLEXIBLE = "flexible"
         # Nuevos modos se añaden aquí
         IMAGEN = "imagen"  # Ejemplo futuro
     ```

2. **Gestionar los modos y su configuración desde archivos externos (JSON/YAML):**
   - Ejemplo de archivo `client_config/modes.json`:
     ```json
     {
       "modes": {
         "consulta_rigida": {
           "description": "Solo tool calls directas",
           "enabled": true
         },
         "flexible": {
           "description": "Tool calls + interpretación",
           "enabled": true
         },
         "imagen": {
           "description": "Generación de imágenes a partir de texto",
           "enabled": false,
           "module": "image_generator.py",
           "config": {
             "provider": "stable_diffusion",
             "max_resolution": "1024x1024"
           }
         }
       }
     }
     ```

3. **El orquestador y los agentes leen los modos y su configuración al arrancar:**
   - Permite activar/desactivar modos por cliente.
   - Permite añadir nuevos modos sin modificar el core, solo agregando el módulo y la config.

4. **Cada modo puede tener su propio módulo y lógica:**
   - Ejemplo: Si se activa el modo "imagen", el sistema carga el módulo `image_generator.py` y usa la config asociada.

**Ventajas:**
- Extensible y personalizable por cliente.
- Permite añadir nuevos modos y funcionalidades fácilmente.
- Mantiene el core desacoplado y limpio.
- Facilita la gestión y despliegue de nuevas capacidades.

---

## Middleware de Control: Concepto y Retos

El **middleware de control** es una capa intermedia entre la inferencia del modelo/agente y la ejecución de tool calls o la generación de respuestas. Su función principal es:

- Decidir, según el modo activo y el contexto, si se debe ejecutar una tool call, generar una respuesta, o combinar ambas.
- Validar la seguridad y privacidad de las respuestas antes de enviarlas al usuario.
- Enriquecer las respuestas con explicaciones, sugerencias, o resúmenes contextuales.
- Filtrar, transformar o combinar los resultados de varias tool calls para ofrecer una respuesta más útil y natural.

**Problemas que resuelve:**
- Evita respuestas automáticas que puedan ser incompletas, inseguras o poco útiles.
- Permite adaptar el comportamiento del sistema según el modo, el usuario y el contexto conversacional.
- Centraliza la lógica de validación y enriquecimiento, evitando duplicidad en los agentes.
- Facilita la integración de nuevas capacidades (ej: validación de permisos, generación de imágenes, sugerencias proactivas).

**Ejemplo de funcionamiento:**
- El usuario pide "¿Por qué tengo tanta deuda?".
  - El agente ejecuta las tool calls necesarias (deuda, facturas).
  - El middleware valida los datos, genera una explicación y sugiere acciones.
  - Solo entonces envía la respuesta enriquecida al frontend.
- El usuario pide un dato sensible.
  - El middleware detecta la sensibilidad y solicita confirmación o verifica permisos antes de mostrar la información.

**Retos técnicos:**
- Diseñar una interfaz flexible para que el middleware reciba y procese los resultados de agentes y tool calls.
- Definir reglas y lógica para decidir cuándo y cómo enriquecer, filtrar o combinar respuestas.
- Integrar validaciones de seguridad y privacidad de forma centralizada.
- Mantener la extensibilidad para futuros módulos y modos.

---

### Diagrama y Flujo Técnico del Middleware de Control

**Diagrama simplificado:**
```
Usuario → Frontend → Backend Conversacional → Orchestrator → Agente Especializado → Middleware de Control → Respuesta Final → Frontend
```

**Flujo técnico:**
1. El usuario envía una consulta.
2. El orquestador decide el agente y el modo activo.
3. El agente especializado ejecuta las tool calls necesarias y/o genera una respuesta.
4. El agente envía los resultados (datos, texto, metadatos) al middleware de control junto con el contexto y el modo.
5. El middleware:
   - Valida la seguridad y privacidad de los datos.
   - Decide si debe enriquecer, filtrar o combinar los resultados según el modo y reglas configurables.
   - Puede invocar módulos adicionales (explicaciones, sugerencias, imágenes, etc.) si el modo lo requiere.
   - Devuelve la respuesta final lista para el frontend.
6. El frontend renderiza la respuesta según el tipo y el modo.

**Ejemplo de interfaz técnica (Python):**
```python
# core/agent/middleware/control_middleware.py
class ControlMiddleware:
    def process(self, consulta, usuario, modo, resultados, contexto):
        # Validar seguridad
        # Enriquecer o filtrar resultados
        # Combinar tool calls si es necesario
        # Invocar módulos extra según modo
        # Devolver respuesta final
        pass
```

**Ventajas del enfoque:**
- El middleware centraliza la lógica avanzada y reglas de negocio.
- Los agentes se simplifican: solo ejecutan y devuelven datos.
- Permite añadir nuevas capacidades (validaciones, enriquecimiento, módulos) sin modificar el core ni los agentes.
- Facilita la personalización y extensibilidad por cliente y por modo.

---

## Optimización de Tokens y Gestión de Contexto Conversacional

Para garantizar eficiencia y minimizar costes, el sistema debe:

- **Contexto conversacional optimizado:**
  - Guardar únicamente entidades clave (ej: abonado, DNI, factura) y el historial mínimo necesario para la comprensión.
  - Resumir y deduplicar el historial, evitando enviar mensajes del sistema repetidos o información irrelevante.
  - Limitar la longitud del contexto transmitido al modelo, priorizando los datos más recientes y relevantes.

- **Gestión precisa de entidades y referencias:**
  - El contexto debe asociar cada entidad (abonado, DNI, factura) a la consulta activa.
  - Si el usuario cambia de abonado/DNI, el sistema debe actualizar el contexto y descartar referencias anteriores para evitar mezclas.
  - Ejemplo técnico:
    ```python
    # Ejemplo de estructura de contexto
    contexto = {
        "usuario_id": "123",
        "modo": "flexible",
        "entidades": {
            "abonado": "12345678A",
            "factura": None,
            "dni": "12345678A"
        },
        "historial": [
            {"consulta": "¿Cuál es mi deuda?", "entidades": {"abonado": "12345678A"}},
            {"consulta": "Dame todas sus facturas", "entidades": {"abonado": "12345678A"}}
        ]
    }
    # Si el usuario pregunta por otro abonado:
    contexto["entidades"]["abonado"] = "87654321B"
    contexto["entidades"]["dni"] = "87654321B"
    # Se descartan referencias previas para evitar mezclas.
    contexto["historial"] = []
    ```

- **Reglas para evitar mezclas de contexto:**
  - Detectar cambios de entidad principal (abonado/DNI) y reiniciar el contexto asociado.
  - No mezclar datos de diferentes abonados/facturas en la misma respuesta.
  - El middleware debe validar que las entidades en la respuesta corresponden al contexto actual.

- **Filtrado y compactación antes de inferencia:**
  - Antes de enviar el contexto al modelo, aplicar funciones de filtrado y resumen para reducir el número de tokens.
  - Ejemplo técnico:
    ```python
    def compactar_contexto(contexto):
        # Mantener solo entidades activas y el último turno relevante
        entidades = contexto["entidades"]
        ultimo_turno = contexto["historial"][-1] if contexto["historial"] else None
        return {
            "entidades": entidades,
            "ultimo_turno": ultimo_turno
        }
    ```

- **Evitar redundancias y repeticiones:**
  - No enviar mensajes del sistema repetidos ni prompts innecesarios.
  - El middleware debe deduplicar instrucciones y mensajes antes de cada inferencia.

- **Validación de seguridad y privacidad:**
  - El middleware debe verificar que los datos sensibles solo se envían si el usuario tiene permisos y el contexto es correcto.

---

**Resumen:**
La gestión eficiente del contexto conversacional y la optimización de tokens son clave para reducir costes y evitar errores. El sistema debe asociar cada consulta y entidad al contexto activo, reiniciando y filtrando cuando el usuario cambia de referencia (ej: nuevo abonado/DNI). El middleware centraliza la validación, compactación y deduplicación antes de cada inferencia, garantizando respuestas precisas y seguras.

---

**Gestión de entidades basada en configuración externa (JSON):**

Para mantener la flexibilidad y evitar lógica específica hardcodeada en la aplicación, la detección y validación de entidades (abonado, DNI, factura, etc.) debe gestionarse siempre desde archivos de configuración externos (por ejemplo, `client_config/entity_patterns.json`).

---

## Planificación de Migración Gradual hacia la Nueva Arquitectura

La migración debe realizarse por fases para minimizar riesgos, asegurar compatibilidad y permitir validación continua. Se recomienda el siguiente enfoque:

### 1. Fase de Preparación
- Auditar el sistema actual y documentar dependencias, puntos críticos y flujos principales.
- Definir claramente los componentes que serán reemplazados o extendidos (modos, contexto, middleware, frontend).
- Crear pruebas de regresión para asegurar que las funcionalidades actuales no se pierdan.

### 2. Fase de Integración de Modos
- Implementar la lectura y gestión de modos desde configuración externa (JSON/YAML).
- Adaptar el orquestador y los agentes para distinguir y operar según el modo activo.
- Validar que el sistema sigue funcionando en modo consulta rígida como fallback.

### 3. Fase de Contexto Conversacional
- Extender el sistema de contexto para guardar historial y entidades clave, optimizando tokens.
- Integrar lógica de actualización y reinicio de contexto al cambiar de entidad principal.
- Validar que no se mezclan datos entre abonados/DNI y que el contexto es preciso.

### 4. Fase de Middleware de Control
- Desarrollar el middleware como capa independiente entre agentes y frontend.
- Centralizar validaciones, enriquecimiento y filtrado de respuestas.
- Integrar el middleware de forma opcional, permitiendo fallback al flujo anterior.

### 5. Fase de Soporte Multi Tools
- Permitir la ejecución de varias tool calls por consulta en el orquestador y agentes.
- Adaptar el middleware y frontend para combinar y mostrar respuestas compuestas.
- Validar la coherencia y seguridad en respuestas multi-tool.

### 6. Fase de Validación y Optimización
- Realizar pruebas funcionales, de seguridad y de rendimiento en cada fase.
- Optimizar la gestión de tokens y el filtrado de contexto.
- Documentar cambios y actualizar manuales de usuario y desarrollador.

### 7. Fase de Despliegue y Monitorización
- Desplegar la nueva arquitectura en entorno controlado (staging).
- Monitorizar logs, métricas y feedback de usuarios.
- Corregir incidencias y ajustar configuraciones según resultados.

---

**Recomendaciones clave:**
- Mantener siempre la opción de fallback al sistema anterior hasta validar cada fase.
- Documentar exhaustivamente cada cambio y decisión.
- Priorizar la compatibilidad y la seguridad en cada paso.
- Involucrar a usuarios clave en la validación y feedback.

---

**Resumen:**
La migración gradual permite evolucionar el chatbot sin perder funcionalidad ni seguridad, validando cada avance y asegurando una transición controlada y escalable hacia la nueva arquitectura flexible y eficiente.
