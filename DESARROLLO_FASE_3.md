# Desarrollo Fase 3: Implementación Chatbot Flexible

## Objetivo de la Fase 3
Documentar y guiar la implementación de la nueva arquitectura flexible del chatbot, siguiendo la planificación de migración gradual y las mejores prácticas de desarrollo colaborativo.

---

## 1. Análisis Previo

### Comentario GitHub Copilot:
El sistema actual está bien modularizado, con separación clara entre orquestador, agentes, backend y frontend. La gestión de entidades se realiza por patrones en JSON, lo que facilita la extensibilidad y evita lógica rígida. Sin embargo, la falta de contexto conversacional y la rigidez en la ejecución de tool calls limitan la experiencia del usuario y la capacidad de personalización.

- El orquestador es el punto de entrada ideal para la gestión de modos y contexto, permitiendo fallback y control centralizado.
- Los agentes especializados están preparados para ser extendidos, pero requieren adaptación para manejar contexto y multi tools.
- El middleware de control aún no existe, pero su diseño como capa independiente permitirá centralizar validaciones y enriquecimiento.
- El frontend está listo para recibir respuestas compuestas, aunque requerirá ajustes para nuevos tipos y modos.

**Sugerencia:**
Antes de modificar el core, conviene auditar los flujos de datos y dependencias, asegurando que los cambios no afecten la robustez actual. Recomiendo empezar por pruebas de regresión y definir claramente los puntos de extensión en cada módulo.

¿Quieres añadir tus observaciones o dudas sobre el análisis previo antes de avanzar a la siguiente sección?

## 2. Sugerencias de Implementación
- Utilizar ramas de desarrollo específicas en GitHub para cada fase y feature (`feature/chatbot-flexible-modes`, `feature/contexto-conversacional`, etc.).
- Realizar commits pequeños, descriptivos y frecuentes.
- Documentar cada avance en este archivo y en los PRs.
- Usar issues y milestones para organizar tareas y asignar responsables.
- Mantener la opción de fallback al sistema anterior en cada fase.
- Priorizar la compatibilidad y la seguridad.

## 3. Primeros Pasos Técnicos
- Crear rama de desarrollo para la fase 3.
- Auditar el sistema actual y definir pruebas de regresión.
- Implementar la lectura dinámica de modos desde JSON/YAML.
- Extender el orquestador y agentes para distinguir modos.
- Diseñar la estructura base del middleware de control.
- Planificar la integración progresiva del contexto conversacional.

## 4. Buenas Prácticas con GitHub
- Usar `pull requests` para revisión y validación de código.
- Documentar en cada PR los cambios, motivaciones y pruebas realizadas.
- Etiquetar y asignar revisores según el área afectada.
- Mantener el historial de cambios y documentación actualizada.
- Realizar revisiones de seguridad y optimización antes de mergear a `main`.

## 5. Siguientes Acciones
- Analizar el sistema actual y definir el alcance de los primeros cambios.
- Crear issues para cada tarea técnica y de documentación.
- Iniciar la implementación de la gestión de modos y contexto conversacional.
- Documentar sugerencias, retos y decisiones en este archivo.

## 6. Comentarios y Discusión de Resultados

Este apartado servirá para registrar el intercambio de ideas, observaciones y decisiones entre los participantes del desarrollo durante la Fase 3. Aquí se documentarán los comentarios relevantes, dudas, sugerencias y acuerdos alcanzados, asegurando transparencia y trazabilidad en el proceso.

### Ejemplo de dinámica:
- **Participante 1:** "Propongo que la gestión de modos se implemente primero en el orquestador, para facilitar el fallback."
- **Participante 2:** "De acuerdo, pero sugiero validar la compatibilidad con el frontend antes de avanzar."
- **GitHub Copilot:** "Recomiendo documentar cada decisión en este apartado y vincularla a los PRs correspondientes."

---

## Registro de Avances y Decisiones
- [ ] Documentar el análisis inicial y dependencias.
- [ ] Registrar sugerencias técnicas y de arquitectura.
- [ ] Anotar retos encontrados y soluciones propuestas.
- [ ] Actualizar el plan de desarrollo según el progreso.

---

**Nota:** Este archivo servirá como bitácora y guía colaborativa para la Fase 3, asegurando trazabilidad, transparencia y calidad en el desarrollo.

---

## Análisis detallado del sistema actual

El sistema está compuesto por los siguientes módulos principales:

- **Orquestador (`core/agent/orchestrator.py`):**
  - Centraliza el routing de consultas y decide qué agente responde.
  - Actualmente no gestiona modos ni contexto conversacional.
  - Punto de extensión ideal para añadir lógica de modos y contexto.

- **Agentes Especializados (`core/agent/agents/agent_base.py`):**
  - Ejecutan tool calls y procesan entidades extraídas.
  - No combinan respuestas ni gestionan contexto entre turnos.
  - Requieren adaptación para soportar multi tools y contexto conversacional.

- **Middleware de Control (pendiente de crear):**
  - No existe en el sistema actual.
  - Su implementación permitirá centralizar validaciones, enriquecimiento y filtrado de respuestas.

- **Backend de Herramientas (`core/backend/server.py`):**
  - Expone las tool calls como API REST.
  - Responde con datos estructurados en JSON.

- **Frontend (`web/static/app.js`, `cards.js`, `cards-config.js`):**
  - Renderiza respuestas como tarjetas visuales.
  - Listo para recibir nuevos tipos de respuesta, pero requiere ajustes para respuestas compuestas y modos flexibles.

- **Configuración (`client_config/*.json`):**
  - Define agentes, herramientas y patrones de entidades.
  - Permite extensibilidad sin modificar el core.

---

### Estrategia para empezar a modificar el código

1. **Auditoría y pruebas de regresión:**
   - Revisar los tests existentes y crear nuevos para los flujos principales.
   - Garantizar que los cambios no rompen la funcionalidad actual.

2. **Gestión de modos en el orquestador:**
   - Añadir lectura de modos desde JSON/YAML.
   - Implementar lógica para seleccionar el modo activo por consulta.
   - Mantener fallback al modo consulta rígida.

3. **Extensión de agentes para contexto y multi tools:**
   - Adaptar la base de agentes para recibir y gestionar contexto.
   - Permitir la ejecución de varias tool calls por consulta.

4. **Diseño e integración del middleware de control:**
   - Crear el módulo y definir su interfaz.
   - Integrar validaciones, filtrado y enriquecimiento de respuestas.

5. **Ajustes en frontend y configuración:**
   - Actualizar el frontend para mostrar respuestas compuestas y modos activos.
   - Revisar y ampliar los archivos de configuración para soportar nuevos modos y entidades.

---

## Resumen de la Fase 3 y Estrategia de Implementación

En la Fase 3 se inicia la transformación del chatbot hacia una arquitectura flexible y extensible. El sistema actual está bien modularizado, pero presenta limitaciones clave: solo ejecuta una tool call por consulta, no mantiene contexto conversacional real, y no distingue modos de operación. 

**Principales acciones y cambios:**
- Auditar y probar el sistema actual para asegurar que los cambios no rompan la funcionalidad existente.
- Añadir gestión de modos en el orquestador, leyendo la configuración desde JSON/YAML y permitiendo fallback al modo consulta rígida.
- Adaptar los agentes para gestionar contexto y ejecutar varias tool calls por consulta.
- Crear el middleware de control para centralizar validaciones, enriquecimiento y filtrado de respuestas.
- Actualizar el frontend para mostrar respuestas compuestas y modos activos.
- Ampliar los archivos de configuración para soportar nuevos modos y entidades.

**Estrategia:**
- Modificar primero el orquestador para la gestión de modos y contexto.
- Extender los agentes y diseñar el middleware de control.
- Validar cada avance con pruebas automáticas y mantener la opción de fallback.
- Documentar cada cambio y decisión en el repositorio y en este archivo.

Este enfoque garantiza una migración segura, escalable y trazable hacia la nueva arquitectura flexible.

---

## Primera Modificación: Gestión de Modos en el Orquestador

Para iniciar el desarrollo, el primer cambio debe centrarse en el orquestador (`core/agent/orchestrator.py`):

**Objetivo:**
- Permitir la gestión dinámica de modos de operación (consulta rígida/flexible) leyendo la configuración desde un archivo JSON (`client_config/modes.json`).
- Mantener la opción de fallback al modo consulta rígida si no se especifica modo o hay error en la configuración.
- Preparar el orquestador para pasar el modo activo y el contexto conversacional al agente especializado.

**Pasos sugeridos:**
1. Crear o actualizar `client_config/modes.json` con la definición de modos.
2. Modificar el orquestador para leer los modos al iniciar y seleccionar el modo activo por consulta (por defecto consulta rígida).
3. Añadir lógica para pasar el modo y contexto al agente especializado.
4. Documentar el cambio y crear pruebas automáticas para validar el comportamiento.

**Preguntas para el desarrollo:**
- ¿Cómo debe decidir el orquestador el modo activo en cada consulta? ¿Por configuración, por usuario, por tipo de consulta?
- ¿Qué estructura de datos y funciones serán necesarias para mantener y actualizar el contexto conversacional?
- ¿Qué impacto tendrá este cambio en los agentes y el frontend?

**Siguiente acción:**
Leer el código actual del orquestador y proponer el primer ejemplo de código para la gestión de modos y contexto.

---

### Propuesta: Gestión de Modos basada en Roles y Configuración

La selección del modo activo en el orquestador debe seguir una lógica similar a la gestión de roles en los agentes (`allowed_roles`). La configuración de modos (por ejemplo, en `client_config/modes.json`) define:
- Qué modos están habilitados (ej: "rigido", "flexible").
- Qué roles pueden cambiar el modo (ej: solo "admin" o "soporte").

**Lógica recomendada:**
- Si solo hay un modo habilitado, se fuerza ese modo y se bloquea el cambio tanto en backend como en frontend.
- Si hay dos o más modos habilitados, solo los usuarios con roles permitidos pueden alternar entre ellos. Los demás quedan bloqueados en el modo por defecto.
- El orquestador debe leer los modos y roles permitidos desde la configuración y exponer el modo activo en cada consulta.

**Ejemplo de estructura JSON para modos:**
```json
{
  "enabled_modes": ["rigido", "flexible"],
  "default_mode": "rigido",
  "allowed_roles_to_change_mode": ["admin", "soporte"]
}
```

**Ventajas:**
- Control granular y extensible, igual que en los agentes.
- Permite bloquear o habilitar modos según el contexto y el usuario.
- Facilita la trazabilidad y la seguridad en la gestión de modos.

**Siguiente paso:**
- Implementar la lectura de esta configuración en el orquestador y documentar el proceso.

---

**Avance registrado:**
- Se ha creado el archivo `client_config/modes.json` con la estructura recomendada para la gestión de modos y roles.
- Se ha adaptado el orquestador (`core/agent/orchestrator.py`) para cargar la configuración de modos, exponer el modo activo y permitir el cambio de modo solo si el rol lo permite y el modo está habilitado.
- La lógica fuerza el modo si solo hay uno habilitado y bloquea el cambio para roles no permitidos.

**Siguiente paso:**
- Integrar la selección de modo en el flujo principal del orquestador y documentar cómo se pasa el modo activo al agente y al frontend.
- Crear pruebas automáticas para validar el comportamiento de la gestión de modos.

---

**Avance incremental registrado:**
- Se ha integrado la selección y exposición del modo activo en el método `responder` del orquestador.
- El modo activo se pasa al agente y se devuelve en la respuesta para el frontend, permitiendo trazabilidad y control.
- Se mantiene el fallback y el cambio es incremental, sin afectar la lógica principal.
- Se ha corregido el tipo de parámetro para evitar errores de compilación.

**Siguiente paso:**
- Validar el flujo con pruebas automáticas y documentar cómo el frontend puede consumir el modo activo.
- Continuar con la integración progresiva del contexto y la gestión de multi tools.

---

**Corrección incremental registrada:**
- El orquestador ahora envuelve la respuesta del agente para asegurar que siempre incluya el campo `mode`.
- Esto facilita la integración con el frontend y la trazabilidad del modo activo en cada respuesta.
- El cambio es compatible con el fallback y no afecta la lógica principal.

**Siguiente paso:**
- Validar que el frontend consuma correctamente el campo `mode` y mostrar el modo activo al usuario.
- Continuar con la integración progresiva de contexto y multi tools.

---

**Integración visual de modos en el frontend:**
- Se añade un botón en la interfaz para cambiar el modo de operación del chatbot (por ejemplo, entre "rígido" y "flexible"), solo si el rol del usuario lo permite según la configuración.
- El botón mostrará el modo activo y permitirá alternar entre los modos disponibles.
- El cambio de modo se enviará al backend y se reflejará en la respuesta del chatbot.
- Esta integración es incremental y no afecta la lógica principal del sistema.

**Pasos realizados:**
1. Añadido el botón de cambio de modo en el frontend (`index.html` y `app.js`).
2. Documentada la lógica para mostrar el modo activo y permitir el cambio solo si el rol lo permite.
3. El siguiente paso será implementar la lógica funcional para que el modo afecte el comportamiento del chatbot.

---

**Avance visual registrado:**
- El botón para cambiar el modo de operación está completamente implementado e integrado en la interfaz, con estilos y lógica visual adaptados.
- El usuario puede alternar entre modos desde la barra lateral, y el sistema refleja el modo activo correctamente.
- El frontend envía el modo seleccionado al backend en cada consulta, permitiendo la trazabilidad y el control centralizado.
- El diseño y la experiencia de usuario han sido validados y mejorados.

**Siguiente paso:**
- Definir y desarrollar la lógica funcional para que el modo afecte el comportamiento del chatbot y los agentes.
- Documentar cómo cada modo modifica el flujo y las respuestas del sistema.

---
